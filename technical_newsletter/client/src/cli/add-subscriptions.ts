#!/usr/bin/env node

import * as grpc from "@grpc/grpc-js";
import { invertMap, parseEnumList } from "./enums";
import { parseMutationArgs, printMutationUsage } from "./args";
import {
  AddSubscriptionFiltersRequest,
  NotificationServiceClient,
  eventTypes,
  skillLevels,
} from "./proto";

function getErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function run(): void {
  let args;
  try {
    args = parseMutationArgs(process.argv);
  } catch (error) {
    console.error(`Argument error: ${getErrorMessage(error)}`);
    printMutationUsage("add-subscriptions");
    process.exitCode = 1;
    return;
  }

  if (args.help) {
    printMutationUsage("add-subscriptions");
    return;
  }

  if (!args.clientId) {
    console.error("--client-id is required.");
    printMutationUsage("add-subscriptions");
    process.exitCode = 1;
    return;
  }

  let categories: number[] = [];
  let selectedSkillLevels: number[] = [];

  try {
    if (args.events) {
      categories = parseEnumList(args.events, eventTypes, "events");
    }
    if (args.skills) {
      selectedSkillLevels = parseEnumList(args.skills, skillLevels, "skills");
    }
  } catch (error) {
    console.error(`Filter error: ${getErrorMessage(error)}`);
    process.exitCode = 1;
    return;
  }

  if (categories.length === 0 && selectedSkillLevels.length === 0) {
    console.error("At least one of --events or --skills must be provided.");
    printMutationUsage("add-subscriptions");
    process.exitCode = 1;
    return;
  }

  const client = new NotificationServiceClient(
    args.address,
    grpc.credentials.createInsecure(),
  );

  const request = new AddSubscriptionFiltersRequest();
  request.setClientId(args.clientId);
  request.setCategoriesList(categories);
  request.setSkillLevelList(selectedSkillLevels);

  client.addSubscriptionFilters(request, (error, response) => {
    if (error) {
      console.error("Add-subscriptions RPC failed:", error.message);
      client.close();
      process.exit(1);
      return;
    }

    console.log("Add-subscriptions result:", {
      success: response.getSuccess(),
      clientId: response.getClientId(),
      categories: response.getCategoriesList(),
      skillLevels: response.getSkillLevelList(),
      message: response.getMessage(),
    });

    client.close();
  });
}

run();
