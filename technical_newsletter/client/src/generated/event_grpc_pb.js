// GENERATED CODE -- DO NOT EDIT!

'use strict';
var grpc = require('@grpc/grpc-js');
var event_pb = require('./event_pb.js');

function serialize_subscription_Event(arg) {
  if (!(arg instanceof event_pb.Event)) {
    throw new Error('Expected argument of type subscription.Event');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_subscription_Event(buffer_arg) {
  return event_pb.Event.deserializeBinary(new Uint8Array(buffer_arg));
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

function serialize_subscription_UnsubscriptionRequest(arg) {
  if (!(arg instanceof event_pb.UnsubscriptionRequest)) {
    throw new Error('Expected argument of type subscription.UnsubscriptionRequest');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_subscription_UnsubscriptionRequest(buffer_arg) {
  return event_pb.UnsubscriptionRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_subscription_UnsubscriptionResponse(arg) {
  if (!(arg instanceof event_pb.UnsubscriptionResponse)) {
    throw new Error('Expected argument of type subscription.UnsubscriptionResponse');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_subscription_UnsubscriptionResponse(buffer_arg) {
  return event_pb.UnsubscriptionResponse.deserializeBinary(new Uint8Array(buffer_arg));
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
    requestType: event_pb.UnsubscriptionRequest,
    responseType: event_pb.UnsubscriptionResponse,
    requestSerialize: serialize_subscription_UnsubscriptionRequest,
    requestDeserialize: deserialize_subscription_UnsubscriptionRequest,
    responseSerialize: serialize_subscription_UnsubscriptionResponse,
    responseDeserialize: deserialize_subscription_UnsubscriptionResponse,
  },
};

exports.NotificationServiceClient = grpc.makeGenericClientConstructor(NotificationServiceService, 'NotificationService');
