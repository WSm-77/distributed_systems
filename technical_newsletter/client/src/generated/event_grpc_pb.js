// GENERATED CODE -- DO NOT EDIT!

'use strict';
var grpc = require('@grpc/grpc-js');
var event_pb = require('./event_pb.js');

function serialize_subscription_AddSubscriptionFiltersRequest(arg) {
  if (!(arg instanceof event_pb.AddSubscriptionFiltersRequest)) {
    throw new Error('Expected argument of type subscription.AddSubscriptionFiltersRequest');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_subscription_AddSubscriptionFiltersRequest(buffer_arg) {
  return event_pb.AddSubscriptionFiltersRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_subscription_Event(arg) {
  if (!(arg instanceof event_pb.Event)) {
    throw new Error('Expected argument of type subscription.Event');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_subscription_Event(buffer_arg) {
  return event_pb.Event.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_subscription_RemoveSubscriptionFiltersRequest(arg) {
  if (!(arg instanceof event_pb.RemoveSubscriptionFiltersRequest)) {
    throw new Error('Expected argument of type subscription.RemoveSubscriptionFiltersRequest');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_subscription_RemoveSubscriptionFiltersRequest(buffer_arg) {
  return event_pb.RemoveSubscriptionFiltersRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_subscription_SubscriptionFiltersResponse(arg) {
  if (!(arg instanceof event_pb.SubscriptionFiltersResponse)) {
    throw new Error('Expected argument of type subscription.SubscriptionFiltersResponse');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_subscription_SubscriptionFiltersResponse(buffer_arg) {
  return event_pb.SubscriptionFiltersResponse.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_subscription_SubscriptionRequest(arg) {
  if (!(arg instanceof event_pb.SubscriptionRequest)) {
    throw new Error('Expected argument of type subscription.SubscriptionRequest');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_subscription_SubscriptionRequest(buffer_arg) {
  return event_pb.SubscriptionRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_subscription_UnsubscribeRequest(arg) {
  if (!(arg instanceof event_pb.UnsubscribeRequest)) {
    throw new Error('Expected argument of type subscription.UnsubscribeRequest');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_subscription_UnsubscribeRequest(buffer_arg) {
  return event_pb.UnsubscribeRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_subscription_UnsubscribeResponse(arg) {
  if (!(arg instanceof event_pb.UnsubscribeResponse)) {
    throw new Error('Expected argument of type subscription.UnsubscribeResponse');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_subscription_UnsubscribeResponse(buffer_arg) {
  return event_pb.UnsubscribeResponse.deserializeBinary(new Uint8Array(buffer_arg));
}


var NotificationServiceService = exports.NotificationServiceService = {
  subscribe: {
    path: '/subscription.NotificationService/Subscribe',
    requestStream: false,
    responseStream: true,
    requestType: event_pb.SubscriptionRequest,
    responseType: event_pb.Event,
    requestSerialize: serialize_subscription_SubscriptionRequest,
    requestDeserialize: deserialize_subscription_SubscriptionRequest,
    responseSerialize: serialize_subscription_Event,
    responseDeserialize: deserialize_subscription_Event,
  },
  unsubscribe: {
    path: '/subscription.NotificationService/Unsubscribe',
    requestStream: false,
    responseStream: false,
    requestType: event_pb.UnsubscribeRequest,
    responseType: event_pb.UnsubscribeResponse,
    requestSerialize: serialize_subscription_UnsubscribeRequest,
    requestDeserialize: deserialize_subscription_UnsubscribeRequest,
    responseSerialize: serialize_subscription_UnsubscribeResponse,
    responseDeserialize: deserialize_subscription_UnsubscribeResponse,
  },
  addSubscriptionFilters: {
    path: '/subscription.NotificationService/AddSubscriptionFilters',
    requestStream: false,
    responseStream: false,
    requestType: event_pb.AddSubscriptionFiltersRequest,
    responseType: event_pb.SubscriptionFiltersResponse,
    requestSerialize: serialize_subscription_AddSubscriptionFiltersRequest,
    requestDeserialize: deserialize_subscription_AddSubscriptionFiltersRequest,
    responseSerialize: serialize_subscription_SubscriptionFiltersResponse,
    responseDeserialize: deserialize_subscription_SubscriptionFiltersResponse,
  },
  removeSubscriptionFilters: {
    path: '/subscription.NotificationService/RemoveSubscriptionFilters',
    requestStream: false,
    responseStream: false,
    requestType: event_pb.RemoveSubscriptionFiltersRequest,
    responseType: event_pb.SubscriptionFiltersResponse,
    requestSerialize: serialize_subscription_RemoveSubscriptionFiltersRequest,
    requestDeserialize: deserialize_subscription_RemoveSubscriptionFiltersRequest,
    responseSerialize: serialize_subscription_SubscriptionFiltersResponse,
    responseDeserialize: deserialize_subscription_SubscriptionFiltersResponse,
  },
};

exports.NotificationServiceClient = grpc.makeGenericClientConstructor(NotificationServiceService, 'NotificationService');
