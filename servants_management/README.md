# Servants Management

> Small demo showing a Python ZeroC ICE server exposing servants and a TypeScript/Node client using generated Slice proxies.

## Prerequisites
- `uv` dependency manager
- `bun` JavaScript runtime

## Server

1. Install dependencies

```bash
uv sync --active
```

2. Generate Slice bindings

```bash
cd server
uv run slice2py -I/usr/share/Ice/slice --output-dir src/generated ../slice/servants.ice
```

3. Start the server

```bash
cd server
uv run --active server
```

## Client

1. Install dependencies:

```bash
cd client
bun install
```

2. Generate Slice bindings

```bash
cd client
./node_modules/.bin/slice2js -I/usr/share/Ice/slice --output-dir src/generated ../slice/servants.ice
```

3. Run the CLI (examples):

```bash
bun run src/cli.ts counter-get counter1
bun run src/cli.ts counter-inc counter2
bun run src/cli.ts counter-inc counter2
bun run src/cli
bun run src/cli.ts set intwrapper1 9
bun run src/cli.ts set intwrapper2 4
bun run src/cli.ts get intwrapper1
bun run src/cli.ts get intwrapper2
```
