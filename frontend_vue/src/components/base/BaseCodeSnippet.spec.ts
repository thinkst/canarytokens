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
  it('renders label when passed', () => {
    const label = 'Test Label';
    const wrapper = mount(BaseCodeSnippet, {
      props: { label },
    });
    expect(wrapper.text()).toMatch(label);
  });

  it('toggles showAllCode when handleShowAllSnippet is called', async () => {
    const wrapper = mount(BaseCodeSnippet);
    expect(wrapper.vm.showAllCode).toBe(false);
    await wrapper.vm.handleShowAllSnippet();
    expect(wrapper.vm.showAllCode).toBe(true);
  });

  it('renders expand button when showExpandButton is true', () => {
    const wrapper = mount(BaseCodeSnippet, {
      props: { showExpandButton: true },
    });
    expect(wrapper.find('button').isVisible()).toBe(true);
  });

  it('does not render expand button when showExpandButton is false', () => {
    const wrapper = mount(BaseCodeSnippet, {
      props: { showExpandButton: false },
    });
    expect(wrapper.find('show-all-button').exists()).toBe(false);
  });

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
