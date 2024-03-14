/* eslint-env node */
require('@rushstack/eslint-patch/modern-module-resolution')

module.exports = {
  root: true,
  'extends': [
    'plugin:vue/vue3-recommended',
    'eslint:recommended',
    '@vue/eslint-config-typescript',
    "prettier"
  ],
  parser: 'vue-eslint-parser',
  parserOptions: {
    ecmaVersion: 'latest'
  },
  rules: {
    'vue/first-attribute-linebreak': ['error', {
      "singleline": "beside",
      "multiline": "below"
    }]
  }
}
