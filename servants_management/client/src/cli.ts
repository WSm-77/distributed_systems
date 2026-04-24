import { executeGet } from "@/commands/get.ts";
import { executeSet } from "@/commands/set.ts";
import { executeList } from "@/commands/list.ts";
import { executeCounterGet } from "@/commands/counter-get.ts";
import { executeCounterInc } from "@/commands/counter-inc.ts";

const [, , command, ...rest] = process.argv;

function help() {
  console.log(
`Usage: servants-cli <command> [args]
Commands:
  get <id>        Get the value for object <id>
  set <id> <val>  Set the value for object <id>
  counter-get <id>        Get the counter value for object <id> (default: counter)
  counter-inc <id>        Increment the counter for object <id> and show new value
  list            List known objects (stub)
  evict <id>      Evict a servant (stub)
  help            Show this help`
);
}

if (!command || command === "help" || ["-h", "--help"].includes(command)) {
  help();
  process.exit(0);
}

const main: () => Promise<void> = async function main() {
  try {
    switch (command) {
      case "get":
        await
        executeGet(rest);
        break;
      case "counter-get":
        await executeCounterGet(rest);
        break;
      case "counter-inc":
        await executeCounterInc(rest);
        break;
      case "set":
        await executeSet(rest);
        break;
      case "list":
        await executeList(rest);
        break;
      default:
        console.error("Unknown command:", command);
        help();
        process.exitCode = 2;
    }
  } catch (err) {
    console.error("Error:", err);
    process.exitCode = 1;
  }
};

main();
