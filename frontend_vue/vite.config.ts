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
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
});
