import { mount } from '@vue/test-utils';
import { vi } from 'vitest';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faCopy, faCheck } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import BaseCopyButton from './BaseCopyButton.vue';

library.add(faCopy, faCheck);
const tooltip = vi.fn();

let copied = false;

const mockCopy = vi.fn(() => {
  copied = true;
});

// Not sure this is the best way to mock the useClipboard hook
// mockCopy seems to not update copied correctly
vi.mock('@vueuse/core', () => ({
  useClipboard: vi.fn().mockImplementation(() => ({
    isSupported: true,
    copy: mockCopy,
    copied: copied,
  })),
}));

describe('BaseCopyButton', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.runOnlyPendingTimers();
    vi.useRealTimers();
  });

  it('is called', () => {
    const wrapper = mount(BaseCopyButton, {
      props: {
        content: 'Test content',
      },
      global: {
        stubs: { FontAwesomeIcon },
      },
      directives: {
        tooltip,
      },
    });
    expect(wrapper.exists()).toBeTruthy();
  });

  it('render correctly', () => {
    const wrapper = mount(BaseCopyButton, {
      props: {
        content: 'Test content',
      },
      global: {
        stubs: { FontAwesomeIcon },
      },
      directives: {
        tooltip,
      },
    });
    expect(wrapper.html()).toMatchSnapshot();
  });

  it('triggers Copy on click', async () => {
    const onClick = vi.fn();

    const wrapper = mount(BaseCopyButton, {
      props: {
        content: 'Test content',
      },
      attrs: { onClick: onClick },
      global: {
        stubs: { FontAwesomeIcon },
      },
      directives: {
        tooltip,
      },
    });
    await wrapper.find('button').trigger('click');
    expect(mockCopy).toHaveBeenCalledTimes(1);
  });

  it('displays the correct initial tooltip text', () => {
    const wrapper = mount(BaseCopyButton, {
      props: {
        content: 'Test content',
      },
      global: {
        stubs: { FontAwesomeIcon },
      },
      directives: {
        tooltip,
      },
    });
    //@ts-ignore
    const tooltipText = wrapper.vm.tooltipText;
    expect(tooltipText).toBe('Copy to clipboard');
  });

  it('displays the correct tooltip text after click', async () => {
    const wrapper = mount(BaseCopyButton, {
      props: {
        content: 'Test content',
      },
      global: {
        stubs: { FontAwesomeIcon },
      },
      directives: {
        tooltip,
      },
    });
    await wrapper.find('button').trigger('click');
    await vi.advanceTimersByTime(300);
    //@ts-ignore
    const tooltipText = wrapper.vm.tooltipText;
    expect(tooltipText).toBe('Copied!');
  });
});
