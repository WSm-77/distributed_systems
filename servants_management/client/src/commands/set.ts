import { withCommunicator, proxyStub } from "../lib/ice.ts";

export async function executeSet(args: string[]) {
  const id = args[0];
  const value = args[1];
  if (!id || value === undefined) {
    console.error("Usage: set <id> <value>");
    return;
  }

  await withCommunicator(async (communicator) => {
    console.log(`(stub) Setting object ${id} to ${value}`);
    const proxy = proxyStub(id);
    // TODO: call generated Slice bindings to set the value.
    console.log("(stub) OK");
  });
}
