import { withCommunicator, proxyStub } from "../lib/ice.ts";

export async function executeGet(args: string[]) {
  const id = args[0];
  if (!id) {
    console.error("Usage: get <id>");
    return;
  }

  await withCommunicator(async (communicator) => {
    console.log(`(stub) Requesting object ${id} using communicator`);
    const proxy = proxyStub(id);
    // TODO: use generated Slice bindings, e.g.:
    // const p = ServantsManagement.CounterPrx.checkedCast(communicator.stringToProxy(proxyString));
    // const value = await p.get();
    console.log(`(stub) value for ${id}: <stub-value>`);
  });
}
