import { withCommunicator } from "../lib/ice.ts";
import { ServantsManagement } from "../generated/servants.js";

export async function executeGet(args: string[]) {
  const id = args[0] || "IntWrapper";
  const host = args[1] || process.env.SERVANTS_HOST || "127.0.0.1";
  const port = args[2] || process.env.SERVANTS_PORT || "10000";

  await withCommunicator(async (communicator) => {
    const proxyStr = `${id}:tcp -h ${host} -p ${port}`;
    const base = communicator.stringToProxy(proxyStr);
    const prx = ServantsManagement.IntWrapperObjectPrx.checkedCast(base);
    if (!prx) {
      console.error("checkedCast failed for IntWrapperObject");
      return;
    }
    const value = await prx.getValue();
    console.log(value);
  });
}
