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

export interface UnsubscribeRequestMessage {
  setClientId(clientId: string): void;
}

export interface AddSubscriptionFiltersRequestMessage {
  setClientId(clientId: string): void;
  setCategoriesList(categories: number[]): void;
  setSkillLevelList(skillLevels: number[]): void;
}

export interface RemoveSubscriptionFiltersRequestMessage {
  setClientId(clientId: string): void;
  setCategoriesList(categories: number[]): void;
  setSkillLevelList(skillLevels: number[]): void;
}

export interface UnsubscribeResponseMessage {
  getSuccess(): boolean;
}

export interface SubscriptionFiltersResponseMessage {
  getSuccess(): boolean;
  getClientId(): string;
  getCategoriesList(): string[];
  getSkillLevelList(): string[];
  getMessage(): string;
}

export interface NotificationServiceClient {
  subscribe(request: SubscriptionRequestMessage): grpc.ClientReadableStream<EventMessage>;
  unsubscribe(
    request: UnsubscribeRequestMessage,
    callback: (
      error: grpc.ServiceError | null,
      response: UnsubscribeResponseMessage,
    ) => void,
  ): void;
  addSubscriptionFilters(
    request: AddSubscriptionFiltersRequestMessage,
    callback: (
      error: grpc.ServiceError | null,
      response: SubscriptionFiltersResponseMessage,
    ) => void,
  ): void;
  removeSubscriptionFilters(
    request: RemoveSubscriptionFiltersRequestMessage,
    callback: (
      error: grpc.ServiceError | null,
      response: SubscriptionFiltersResponseMessage,
    ) => void,
  ): void;
  close(): void;
}

interface EventPbModule {
  EventType: Record<string, number>;
  SkillLevel: Record<string, number>;
  SubscriptionRequest: new () => SubscriptionRequestMessage;
  UnsubscribeRequest: new () => UnsubscribeRequestMessage;
  AddSubscriptionFiltersRequest: new () => AddSubscriptionFiltersRequestMessage;
  RemoveSubscriptionFiltersRequest: new () => RemoveSubscriptionFiltersRequestMessage;
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
export const UnsubscribeRequest = eventPb.UnsubscribeRequest;
export const AddSubscriptionFiltersRequest = eventPb.AddSubscriptionFiltersRequest;
export const RemoveSubscriptionFiltersRequest = eventPb.RemoveSubscriptionFiltersRequest;
export const NotificationServiceClient = eventGrpcPb.NotificationServiceClient;
