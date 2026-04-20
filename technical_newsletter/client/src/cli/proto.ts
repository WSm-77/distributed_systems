import * as grpc from "@grpc/grpc-js";

export interface EventMessage {
  getId(): string;
  getTitle(): string;
  getCategory(): number;
  getSkillLevel(): number;
  getLocation(): { getCity(): string; getCountry(): string } | undefined;
  getDate(): string;
}

export interface SubscriptionRequestMessage {
  setClientId(clientId: string): void;
  setCategoriesList(categories: number[]): void;
  setSkillLevelList(skillLevels: number[]): void;
}

export interface UnsubscriptionRequestMessage {
  setClientId(clientId: string): void;
}

export interface UnsubscriptionResponseMessage {
  getSuccess(): boolean;
}

export interface NotificationServiceClient {
  subscribe(request: SubscriptionRequestMessage): grpc.ClientReadableStream<EventMessage>;
  unsubscribe(
    request: UnsubscriptionRequestMessage,
    callback: (
      error: grpc.ServiceError | null,
      response: UnsubscriptionResponseMessage,
    ) => void,
  ): void;
  close(): void;
}

interface EventPbModule {
  EventType: Record<string, number>;
  SkillLevel: Record<string, number>;
  SubscriptionRequest: new () => SubscriptionRequestMessage;
  UnsubscriptionRequest: new () => UnsubscriptionRequestMessage;
}

interface EventGrpcPbModule {
  NotificationServiceClient: new (
    address: string,
    credentials: grpc.ChannelCredentials,
  ) => NotificationServiceClient;
}

const eventPb = require("../generated/event_pb") as EventPbModule;
const eventGrpcPb = require("../generated/event_grpc_pb") as EventGrpcPbModule;

export const eventTypes = eventPb.EventType;
export const skillLevels = eventPb.SkillLevel;

export const SubscriptionRequest = eventPb.SubscriptionRequest;
export const UnsubscriptionRequest = eventPb.UnsubscriptionRequest;
export const NotificationServiceClient = eventGrpcPb.NotificationServiceClient;
