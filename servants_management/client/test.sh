#!/bin/bash

bun run src/cli.ts set intwrapper1 7
sleep 0.2
bun run src/cli.ts get intwrapper1
sleep 0.2
bun run src/cli.ts set intwrapper2 4
sleep 0.2
bun run src/cli.ts get intwrapper2
sleep 0.2
# bun run src/cli.ts get intwrapper1
sleep 0.2
bun run src/cli.ts counter-get counter1
# sleep 0.2
# bun run src/cli.ts counter-inc counter1
# sleep 0.2
# bun run src/cli.ts counter-get counter1
# sleep 0.2
# bun run src/cli.ts counter-inc counter1
sleep 0.2
bun run src/cli.ts counter-inc counter2
# sleep 0.2
# bun run src/cli.ts counter-inc counter1
# sleep 0.2
# bun run src/cli.ts counter-inc counter2
# sleep 0.2
# bun run src/cli.ts counter-inc counter1
sleep 0.2
bun run src/cli.ts counter-inc counter3
# sleep 0.2
# bun run src/cli.ts counter-inc counter3
sleep 0.2
bun run src/cli.ts counter-inc counter4
# sleep 0.2
# bun run src/cli.ts get intwrapper2
# sleep 0.2
# bun run src/cli.ts get intwrapper1
