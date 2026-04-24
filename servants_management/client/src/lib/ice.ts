import { Ice } from "@zeroc/ice";

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
