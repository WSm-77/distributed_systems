import { withCommunicator } from "../lib/ice.ts";
import { ServantsManagement } from "../generated/servants.js";

export async function executeSet(args: string[]) {
  const id = args[0] || "IntWrapper";
  const value = args[1];
  if (value === undefined) {
    console.error("Usage: set <id> <value>");
    return;
  }
  const host = args[2] || process.env.SERVANTS_HOST || "127.0.0.1";
  const port = args[3] || process.env.SERVANTS_PORT || "10000";

  await withCommunicator(async (communicator) => {
    const proxyStr = `${id}:tcp -h ${host} -p ${port}`;
    const base = communicator.stringToProxy(proxyStr);
    const prx = await ServantsManagement.IntWrapperObjectPrx.checkedCast(base);
    if (!prx) {
      console.error("checkedCast failed for IntWrapperObject");
      return;
    }
    const num = Number(value);
    if (Number.isNaN(num)) {
      console.error("value must be a number");
      return;
    }
    await prx.setValue(num);
    console.log("OK");
  });
}
