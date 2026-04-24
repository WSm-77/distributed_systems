# CLI: Live Subscriptions & Filter Mutations

A short, authoritative guide for running the project's CLI helpers that open live subscription streams and mutate subscription filters on the running gRPC server.

## Prerequisites

- Node.js 18+ and npm 9+ (verify with `node --version` and `npm --version`).
- Python 3.12+ (the server pyproject requires >=3.12).
- `uv` (Python project/runner used by the server). Install via pip if needed:
  ```bash
  pip install uv
  ```
- Client dependencies: run `npm --prefix client install`.
- Protobuf / gRPC tooling:
  - Python server uses `grpcio-tools` (invoked via `python -m grpc_tools.protoc`).
  - Client uses `grpc-tools` / `grpc_tools_node_protoc` (invoked via `npx` or the package script).

## Generating protobuf code

Run these exact commands (copied from the repo README) to regenerate server and client stubs after any proto changes.

Server (Python stubs):
```bash
cd server
uv run python -m grpc_tools.protoc -I=../proto --python_out=src/generated --grpc_python_out=src/generated ../proto/event.proto
```

Client (Node / JS stubs):
```bash
cd client
npx grpc_tools_node_protoc --proto_path=../proto --js_out=import_style=commonjs,binary:src/generated --grpc_out=grpc_js:src/generated --plugin=protoc-gen-grpc=$(pwd)/node_modules/.bin/grpc_tools_node_protoc_plugin ../proto/event.proto
```

Always regenerate both sides when you change `proto/event.proto`.

## Starting the server

- Preferred (uses pyproject script):
```bash
cd server
uv sync            # install dependencies from uv.lock (if present)
uv run app
```

## CLI overview

All client CLI scripts live in `client/src/cli` and are exposed via npm scripts in `client/package.json`. From the repository root use the `npm --prefix client run <script> -- [flags]` pattern.

Common flags (both CLI categories)
- `--address` (optional) — gRPC server address (default: `localhost:50051`).
- `--client-id` — client identifier (subscribe defaults to a generated `node-client-<timestamp>`; mutations require an explicit `--client-id`).

1) subscribe
- Purpose: Open a long-lived streaming subscription to receive live events that match the given filters.
- Required: `--events` and `--skills`
- Example:
```bash
  npm --prefix client run subscribe -- --client-id integration-client --events WORKSHOP --skills BEGINNER,INTERMEDIATE
```
- Behavior: Opens a streaming RPC (`Subscribe`) and logs each incoming event to stdout. On SIGINT/SIGTERM the CLI sends an `Unsubscribe` RPC to close server-side state cleanly.

2) add-subscriptions
- Purpose: Add additional event type(s) and/or skill level(s) to an existing subscription without reconnecting the stream.
- Required: `--client-id` and at least one of `--events` or `--skills`
- Example:
```bash
  npm --prefix client run add-subscriptions -- --client-id integration-client --events CONFERENCE --skills INTERMEDIATE
```
- Behavior: Calls `AddSubscriptionFilters`. The CLI prints the `SubscriptionFiltersResponse` summary returned by the server (see examples below).

3) remove-subscriptions
- Purpose: Remove event type(s) and/or skill level(s) from an existing subscription.
- Required: `--client-id` and at least one of `--events` or `--skills`
- Example:
  ```bash
  npm --prefix client run remove-subscriptions -- --client-id integration-client --events WORKSHOP
  ```
- Behavior: Calls `RemoveSubscriptionFilters`. The CLI prints the `SubscriptionFiltersResponse` summary returned by the server.

## Examples

Example sequence 1 — start server, subscribe, add a category, receive new events:

### Server

1) Start the server
```bash
cd server
uv run app
```

### Client

> [!TIP]
>
> Run these commands in `client/` to avoid having to specify `--prefix client` every time.

1) Start two subscribers (in another shells)

```bash
npm run subscribe -- --client-id alice --events WORKSHOP --skills BEGINNER,INTERMEDIATE
npm run subscribe -- --client-id bob --events WORKSHOP --skills BEGINNER,INTERMEDIATE
```

2) While the subscriber stream is active, add a category:

```bash
npm run add-subscriptions -- --client-id alice --events CONFERENCE
```

3) remove subscriptions:
```bash
npm run remove-subscriptions -- --client-id alice --events WORKSHOP
```
