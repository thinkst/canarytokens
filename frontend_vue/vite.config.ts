import { fileURLToPath, URL } from 'node:url';
import Components from 'unplugin-vue-components/vite';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    Components({
      dirs: ['src/components/base'],
      resolvers: [
        //@ts-ignore
        (name) => {
          if (name.startsWith('Base')) {
            return {
              name: name,
              path: `src/components/base/${name}.vue`,
            };
          }
        },
      ],
      // valid file extensions for components.
      extensions: ['vue'],
      dts: true,
      // search for subdirectories
      deep: false,
    }),
  ],
  // fix import error
  // https://github.com/fawmi/vue-google-maps/issues/148#issuecomment-1235143844
  optimizeDeps: {
    include: ['@fawmi/vue-google-maps', 'fast-deep-equal'],
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  define: {
    'import.meta.env': JSON.stringify(process.env),
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '^/api/*': {
        target: process.env.VITE_API_URL,
        changeOrigin: true,
      },
    },
  },
});
