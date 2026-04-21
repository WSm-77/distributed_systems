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

The server listens on port `50051` by default.

- Preferred (uses pyproject script):
```bash
cd server
uv sync            # install dependencies from uv.lock (if present)
uv run app
```

- Direct Python (works for local development):
```bash
cd server
PYTHONPATH=src python -m src.app.app
```

Either approach starts the gRPC server and a demo publisher that emits sample events.

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

1) Start the server
```bash
cd server
uv run app
```

2) Start a subscriber (in another shell)
```bash
npm --prefix client run subscribe -- --client-id alice --events WORKSHOP --skills BEGINNER,INTERMEDIATE
```

Subscriber console (trimmed):
```
Subscribing with filters: { clientId: 'alice', address: 'localhost:50051', categories: ['WORKSHOP'], skillLevels: ['BEGINNER','INTERMEDIATE'] }
Received event: { id: 'evt-0001', title: 'Intro to Webhooks', category: 'WORKSHOP', skillLevel: 'BEGINNER', location: 'Berlin, DE', date: '2026-04-21' }
```

3) While the subscriber stream is active, add a category:
```bash
npm --prefix client run add-subscriptions -- --client-id alice --events CONFERENCE
```

CLI output (trimmed):
```
Add-subscriptions result: {
  success: true,
  clientId: 'alice',
  categories: ['WORKSHOP','CONFERENCE'],
  skillLevels: ['BEGINNER','INTERMEDIATE'],
  message: 'Filters added'
}
```

After the mutation the running subscriber may show new events matching `CONFERENCE`:
```
Received event: { id: 'evt-0002', title: 'Cloud Conference 2026', category: 'CONFERENCE', skillLevel: 'INTERMEDIATE', location: 'Online', date: '2026-05-10' }
```

Example 2 — remove subscriptions:
```bash
npm --prefix client run remove-subscriptions -- --client-id alice --events WORKSHOP
```

Output (trimmed):
```
Remove-subscriptions result: {
  success: true,
  clientId: 'alice',
  categories: ['CONFERENCE'],
  skillLevels: ['BEGINNER','INTERMEDIATE'],
  message: 'Filters removed'
}
```

Example 3 — mutation against an unknown client
```bash
npm --prefix client run add-subscriptions -- --client-id unknown-client --events HACKATHON
```

Output (trimmed):
```
Add-subscriptions result: {
  success: false,
  clientId: 'unknown-client',
  categories: [],
  skillLevels: [],
  message: 'Client is not subscribed'
}
```

Unsubscribing (graceful shutdown)
- Pressing Ctrl+C in the running `subscribe` process triggers the client to call `Unsubscribe` and will print:
```
Unsubscribe result: { success: true }
Subscription stream ended.
```

## Troubleshooting & notes

- Regenerate stubs after any proto change. Use the exact commands in the "Generating protobuf code" section above.
- Interoperability note (breaking): the server `SubscriptionFiltersResponse` intentionally returns human-readable enum names as repeated strings (e.g., `"WORKSHOP"`, `"BEGINNER"`) rather than packed numeric enum values. This avoids packed enum/binary enum issues with local JS jspb runtimes but is a breaking API change. Update consumers and regenerate client stubs if your code expects numeric enums.
- If a mutation RPC (`AddSubscriptionFilters` / `RemoveSubscriptionFilters`) returns `success: false`, the server is signaling the `client_id` is not a known subscribed client (no active subscription stream). Start or recreate the subscription first.
- If you see `Argument error` from the client CLIs, re-check flag syntax; flags may be given inline (`--events=WORKSHOP`) or as separate args (`--events WORKSHOP`).
- Common fixes:
  - Client: `npm --prefix client install && npm --prefix client run generate:proto` after proto changes.
  - Server: `cd server && uv sync && uv run python -m grpc_tools.protoc ...` (see generation command above).

## Where to look next

- Protobuf definition: [proto/event.proto](../proto/event.proto)
- Server filter/mutation implementation: [server/src/app/service.py](../server/src/app/service.py)
- Client CLI code: [client/src/cli](../client/src/cli)
