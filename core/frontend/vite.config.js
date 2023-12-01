import vue from '@vitejs/plugin-vue2';
import { VuetifyResolver } from 'unplugin-vue-components/resolvers';
import Components from 'unplugin-vue-components/vite';
import { defineConfig } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

// Convert the file URL to a file path for __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Use fs to read package.json
const packageJson = JSON.parse(fs.readFileSync(path.join(__dirname, './package.json')));

process.env.PROJECT_NAME = packageJson.name;
process.env.VITE_BUILD_DATE = new Date().toLocaleString();

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      devOptions: {
        enabled: true,
      },
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
    }),
    Components({
      // generate `components.d.ts` global declarations
      // https://github.com/antfu/unplugin-vue-components#typescript
      dts: true,
      // auto import for directives
      directives: false,
      // resolvers for custom components
      resolvers: [
        // Vuetify
        VuetifyResolver(),
      ],
      // https://github.com/antfu/unplugin-vue-components#types-for-global-registered-components
      types: [
        {
          from: 'vue-router',
          names: ['RouterLink', 'RouterView'],
        },
      ],
      // Vue version of project.
      version: 2.7,
    }),
  ],
  assetsInclude: ['**/*.gif', '**/*.glb', '**/*.svg'],
  resolve: {
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue'],
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'index.html'),
      },
    },
  },
  define: {
    'process.env': {},
  },
})
