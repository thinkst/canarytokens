import { mount } from '@vue/test-utils';
import { vi } from 'vitest';
import BaseCodeSnippet from '@/components/base/BaseCodeSnippet.vue';
import BaseCopyButton from './BaseCopyButton.vue';
import BaseRefreshButton from './BaseRefreshButton.vue';
import { library } from '@fortawesome/fontawesome-svg-core';
import {
  faRotateRight,
  faCheck,
  faCopy,
} from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

const tooltip = vi.fn();
library.add(faRotateRight, faCheck, faCopy);

describe('BaseCodeSnippet', () => {
  it('emits "refresh-token" event when refresh button is clicked', async () => {
    const code = 'const example = () => { return "Hello World"; }';
    const wrapper = mount(BaseCodeSnippet, {
      props: {
        code: code,
        lang: 'javascript',
        hasRefresh: true,
      },
      global: {
        stubs: { BaseCopyButton, BaseRefreshButton, FontAwesomeIcon },
      },
      directives: {
        tooltip,
      },
    });
    await wrapper.find('.refresh-token').trigger('click');
    expect(wrapper.emitted('refresh-token')).toBeTruthy();
  });
});
