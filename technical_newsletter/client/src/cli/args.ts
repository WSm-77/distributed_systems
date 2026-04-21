export interface CliOptions {
  address: string;
  clientId: string;
  events: string;
  skills: string;
  help: boolean;
}

export interface MutationCliOptions {
  address: string;
  clientId: string;
  events: string;
  skills: string;
  help: boolean;
}

export function parseArgs(argv: string[]): CliOptions {
  const parsed: CliOptions = {
    address: "localhost:50051",
    clientId: `node-client-${Date.now()}`,
    events: "",
    skills: "",
    help: false,
  };

  for (let index = 2; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === undefined) {
      continue;
    }

    if (arg === "--help" || arg === "-h") {
      parsed.help = true;
      continue;
    }

    if (!arg.startsWith("--")) {
      throw new Error(`Unexpected argument: ${arg}`);
    }

    const [flag, inlineValue] = arg.split("=", 2);
    const nextValue = inlineValue ?? argv[index + 1];

    if (inlineValue === undefined) {
      index += 1;
    }

    if (!nextValue) {
      throw new Error(`Missing value for ${flag}`);
    }

    switch (flag) {
      case "--address":
        parsed.address = nextValue;
        break;
      case "--client-id":
        parsed.clientId = nextValue;
        break;
      case "--events":
        parsed.events = nextValue;
        break;
      case "--skills":
        parsed.skills = nextValue;
        break;
      default:
        throw new Error(`Unknown flag: ${flag}`);
    }
  }

  return parsed;
}

export function printUsage(): void {
  console.log(`Usage:\n  npm run subscribe -- --events WORKSHOP,MEETUP --skills BEGINNER,ADVANCED [--address localhost:50051] [--client-id my-client]\n\nExamples:\n  npm run subscribe -- --events HACKATHON --skills INTERMEDIATE\n  npm run subscribe -- --events WORKSHOP,CONFERENCE --skills BEGINNER,INTERMEDIATE --address localhost:50051`);
}

export function parseMutationArgs(argv: string[]): MutationCliOptions {
  const parsed: MutationCliOptions = {
    address: "localhost:50051",
    clientId: "",
    events: "",
    skills: "",
    help: false,
  };

  for (let index = 2; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === undefined) {
      continue;
    }

    if (arg === "--help" || arg === "-h") {
      parsed.help = true;
      continue;
    }

    if (!arg.startsWith("--")) {
      throw new Error(`Unexpected argument: ${arg}`);
    }

    const [flag, inlineValue] = arg.split("=", 2);
    const nextValue = inlineValue ?? argv[index + 1];

    if (inlineValue === undefined) {
      index += 1;
    }

    if (!nextValue) {
      throw new Error(`Missing value for ${flag}`);
    }

    switch (flag) {
      case "--address":
        parsed.address = nextValue;
        break;
      case "--client-id":
        parsed.clientId = nextValue;
        break;
      case "--events":
        parsed.events = nextValue;
        break;
      case "--skills":
        parsed.skills = nextValue;
        break;
      default:
        throw new Error(`Unknown flag: ${flag}`);
    }
  }

  return parsed;
}

export function printMutationUsage(scriptName: "add-subscriptions" | "remove-subscriptions"): void {
  console.log(`Usage:\n  npm run ${scriptName} -- --client-id my-client --events WORKSHOP,MEETUP --skills BEGINNER,ADVANCED [--address localhost:50051]\n\nExamples:\n  npm run ${scriptName} -- --client-id alice --events WORKSHOP\n  npm run ${scriptName} -- --client-id alice --skills INTERMEDIATE,ADVANCED`);
}
