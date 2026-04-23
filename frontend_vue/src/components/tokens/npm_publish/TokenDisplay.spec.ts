import { mount } from '@vue/test-utils';
import { vi } from 'vitest';
import TokenDisplay from './TokenDisplay.vue';
import { downloadAsset } from '@/api/main';

vi.mock('@/api/main', () => ({
  downloadAsset: vi.fn(() =>
    Promise.resolve({
      request: { responseURL: 'https://example.com/npm_publish_canary.zip' },
    })
  ),
}));

describe('NPMPublish TokenDisplay', () => {
  const tokenData = {
    auth: 'auth-token',
    token: 'canary-token',
    npm_token: 'npm-test-token',
    npm_package_name: '@thinkst/canary-test',
    npm_package_version: '0.0.2',
  };

  const stubs = {
    BaseCodeSnippet: {
      props: ['code', 'lang', 'label'],
      template: '<pre>{{ code }}</pre>',
    },
    BaseButton: {
      emits: ['click'],
      template: '<button @click="$emit(\'click\')"><slot /></button>',
    },
  };

  test('renders the npm token instructions', () => {
    const wrapper = mount(TokenDisplay, {
      props: { tokenData },
      global: { stubs },
    });

    expect(wrapper.text()).toContain('export NPM_TOKEN=npm-test-token');
    expect(wrapper.text()).toContain('@thinkst/canary-test');
    expect(wrapper.text()).toContain('0.0.2');
  });

  test('downloads the npm workspace when clicked', async () => {
    const wrapper = mount(TokenDisplay, {
      props: { tokenData },
      global: { stubs },
    });

    await wrapper.find('button').trigger('click');

    expect(downloadAsset).toHaveBeenCalledWith({
      fmt: 'npm_publish',
      auth: 'auth-token',
      token: 'canary-token',
    });
  });
});
