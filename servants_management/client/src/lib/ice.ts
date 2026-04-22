import { Ice } from "@zeroc/ice";

/**
 * Helper to manage Ice communicator lifecycle.
 * Replace stubs in commands with real generated Slice proxy usage.
 */
export async function withCommunicator(fn: (communicator: any) => Promise<void>) {
  const communicator = Ice.initialize(process.argv);
  try {
    await fn(communicator);
  } finally {
    try {
      await communicator.destroy();
    } catch (e) {
      // ignore destroy errors
    }
  }
}

export function proxyStub(identity: string) {
  // Small helper returning a human-readable proxy placeholder.
  // Replace with actual proxy creation using generated Slice bindings.
  return { identity };
}
