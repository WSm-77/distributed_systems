export async function executeEvict(args: string[]) {
  const id = args[0];
  if (!id) {
    console.error("Usage: evict <id>");
    return;
  }

  // Stub: in a full implementation this would call a management interface
  // on the server to evict the servant and persist its state.
  console.log(`(stub) Evicting servant for id=${id}`);
}
