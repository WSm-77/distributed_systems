# Technical Newsletter

See CLI usage and examples: [docs/CLI-usage.md](docs/CLI-usage.md)

## Generating Protobuf Code

**Server**:
```bash
cd server
uv run python -m grpc_tools.protoc -I=../proto --python_out=src/generated --grpc_python_out=src/generated ../proto/event.proto
```

**Client**

```bash
cd client
npx grpc_tools_node_protoc --proto_path=../proto --js_out=import_style=commonjs,binary:src/generated --grpc_out=grpc_js:src/generated --plugin=protoc-gen-grpc=$(pwd)/node_modules/.bin/grpc_tools_node_protoc_plugin ../proto/event.proto
```
