#!/usr/bin/env node

import * as grpc from "@grpc/grpc-js";
import { parseArgs, printUsage } from "./args";
import { parseEnumList, invertMap } from "./enums";
import { formatEvent } from "./format";
import {
  eventTypes,
  skillLevels,
  NotificationServiceClient,
  SubscriptionRequest,
  UnsubscriptionRequest,
} from "./proto";

function getErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function run(): void {
  let args;
  try {
    args = parseArgs(process.argv);
  } catch (error) {
    console.error(`Argument error: ${getErrorMessage(error)}`);
    printUsage();
    process.exitCode = 1;
    return;
  }

  if (args.help) {
    printUsage();
    return;
  }

  if (!args.events || !args.skills) {
    console.error("Both --events and --skills are required.");
    printUsage();
    process.exitCode = 1;
    return;
  }

  const eventTypesByValue = invertMap(eventTypes);
  const skillLevelsByValue = invertMap(skillLevels);

  let categories: number[];
  let selectedSkillLevels: number[];
  try {
    categories = parseEnumList(args.events, eventTypes, "events");
    selectedSkillLevels = parseEnumList(args.skills, skillLevels, "skills");
  } catch (error) {
    console.error(`Filter error: ${getErrorMessage(error)}`);
    process.exitCode = 1;
    return;
  }

  const client = new NotificationServiceClient(
    args.address,
    grpc.credentials.createInsecure(),
  );

  const request = new SubscriptionRequest();
  request.setClientId(args.clientId);
  request.setCategoriesList(categories);
  request.setSkillLevelList(selectedSkillLevels);

  console.log("Subscribing with filters:", {
    clientId: args.clientId,
    address: args.address,
    categories: categories.map((value) => eventTypesByValue[String(value)]),
    skillLevels: selectedSkillLevels.map((value) => skillLevelsByValue[String(value)]),
  });

  const stream = client.subscribe(request);

  stream.on("data", (event) => {
    console.log("Received event:", formatEvent(event, eventTypesByValue, skillLevelsByValue));
  });

  stream.on("error", (error) => {
    console.error("Subscription stream error:", error.message);
  });

  stream.on("end", () => {
    console.log("Subscription stream ended.");
    client.close();
  });

  let shuttingDown = false;
  const shutdown = (): void => {
    if (shuttingDown) {
      return;
    }
    shuttingDown = true;

    console.log("Unsubscribing...");

    const unsubscribeRequest = new UnsubscriptionRequest();
    unsubscribeRequest.setClientId(args.clientId);

    client.unsubscribe(unsubscribeRequest, (error, response) => {
      if (error) {
        console.error("Unsubscribe RPC failed:", error.message);
      } else {
        console.log("Unsubscribe result:", { success: response.getSuccess() });
      }
      stream.cancel();
      client.close();
      process.exit(0);
    });
  };

  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);
}

run();
