import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  base: "/park-jungho-voyage/",
  plugins: [react()],
  build: {
    outDir: "../../park-jungho-voyage",
    emptyOutDir: true,
    target: "es2022",
    sourcemap: false,
  },
});
