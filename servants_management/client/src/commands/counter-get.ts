import { withCommunicator } from "@/lib/ice.ts";
import { ServantsManagement } from "@/generated/servants.js";

export async function executeCounterGet(args: string[]) {
  const id = args[0] || "counter";
  const host = args[1] || process.env.SERVANTS_HOST || "127.0.0.1";
  const port = args[2] || process.env.SERVANTS_PORT || "4061";

  await withCommunicator(async (communicator) => {
    const proxyStr = `${id}:tcp -h ${host} -p ${port}`;
    const base = communicator.stringToProxy(proxyStr);
    const prx = await ServantsManagement.CounterPrx.checkedCast(base);
    if (!prx) {
      console.error("checkedCast failed for Counter");
      return;
    }
    const value = await prx.getCounter();
    console.log(`Counter ${id}, got value: ${value}`);
  });
}
