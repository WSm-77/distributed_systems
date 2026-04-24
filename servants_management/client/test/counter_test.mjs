import { Ice } from "@zeroc/ice";
import { ServantsManagement } from "@/generated/servants.js";

async function main() {
  const communicator = Ice.initialize();
  try {
    const proxyStr = `counter:tcp -h 127.0.0.1 -p 4061`;
    const base = communicator.stringToProxy(proxyStr);
    const prx = await ServantsManagement.CounterPrx.checkedCast(base);
    console.log('Proxy prototype getCounter:', typeof ServantsManagement.CounterPrx.prototype.getCounter);
    console.log('Proxy instance keys:', Object.keys(prx));
    console.log('Proxy constructor name:', prx && prx.constructor && prx.constructor.name);
    console.log('prx instanceof CounterPrx:', prx instanceof ServantsManagement.CounterPrx);
    if (!prx) {
      console.error("checkedCast failed for Counter proxy");
      return;
    }

    if (typeof prx.getCounter !== 'function') {
      console.error('Proxy does not expose getCounter as a function.');
      return;
    }

    const before = await prx.getCounter();
    console.log("Before:", before);

    await prx.incrementCounter();

    const after = await prx.getCounter();
    console.log("After:", after);
  } finally {
    try {
      await communicator.destroy();
    } catch (e) {
      // ignore destroy errors
    }
  }
}

main().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
