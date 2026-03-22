import { defineConfig } from "astro/config";

import netlify from "@astrojs/netlify";

export default defineConfig({
  server: {
    host: true,
    port: 4321
  },

  adapter: netlify(),
});