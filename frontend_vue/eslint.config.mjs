import eslintConfigPrettier from 'eslint-config-prettier';
import pluginVue from 'eslint-plugin-vue';
import pluginVuejsAccessibility from 'eslint-plugin-vuejs-accessibility';
import globals from 'globals';
import { withVueTs, vueTsConfigs } from '@vue/eslint-config-typescript';

export default withVueTs(
  {
    name: 'app/files-to-lint',
    files: ['**/*.{vue,js,jsx,cjs,mjs,ts,tsx,cts,mts}'],
  },
  {
    name: 'app/files-to-ignore',
    ignores: [
      'blob-report/**',
      'coverage/**',
      'dist/**',
      'dist-ssr/**',
      'logs/**',
      'playwright-report/**',
      'screenshots/**',
      'test-results/**',
      '.vite/**',
    ],
  },
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
  },
  pluginVue.configs['flat/recommended'],
  vueTsConfigs.recommended,
  pluginVuejsAccessibility.configs['flat/recommended'],
  eslintConfigPrettier,
  {
    rules: {
      '@typescript-eslint/ban-ts-comment': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-unused-vars': 'warn',
      'vue/block-lang': 'off',
      'vuejs-accessibility/label-has-for': 'off',
    },
  },
  {
    files: ['**/*.{js,cjs}'],
    rules: {
      '@typescript-eslint/no-require-imports': 'off',
    },
  }
);
