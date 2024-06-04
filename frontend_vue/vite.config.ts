import { fileURLToPath, URL } from 'node:url';
import Components from 'unplugin-vue-components/vite';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd());

  const processEnvValues = {
    'process.env': Object.entries(env).reduce((prev, [key, val]) => {
      return {
        ...prev,
        [key]: val,
      };
    }, {}),
  };

  return {
    base: '/nest',
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
    optimizeDeps: {
      include: ['@fawmi/vue-google-maps', 'fast-deep-equal'],
    },
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    define: processEnvValues,
    server: {
      host: '0.0.0.0',
      port: 5173,
      proxy: {
        '^/d3aece8093b71007b5ccfedad91ebb11/*': {
          target: env.VITE_API_URL,
          changeOrigin: true,
        },
      },
    },
  };
});
