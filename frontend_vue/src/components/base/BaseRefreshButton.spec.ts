import { mount } from '@vue/test-utils';
import { vi } from 'vitest';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faRotateRight, faCheck } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import BaseRefreshButton from '@/components/base/BaseRefreshButton.vue';

library.add(faRotateRight, faCheck);
const tooltip = vi.fn();

describe('BaseRefreshButton', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.runOnlyPendingTimers();
    vi.useRealTimers();
  });

  it('emits "refresh-token" event when clicked', async () => {
    const wrapper = mount(BaseRefreshButton, {
      global: {
        stubs: { FontAwesomeIcon },
      },
      directives: {
        tooltip,
      },
    });
    await wrapper.find('button').trigger('click');
    expect(wrapper.emitted('refresh-token')).toBeTruthy();
  });

  it('changes tooltip text to "Refreshed!" when showTooltip is called', async () => {
    const wrapper = mount(BaseRefreshButton, {
      global: {
        stubs: { FontAwesomeIcon },
      },
      directives: {
        tooltip,
      },
    });
    await wrapper.find('button').trigger('click');
    await vi.advanceTimersByTime(200);
    //@ts-ignore
    const tooltipText = wrapper.vm.tooltipText;
    expect(tooltipText).toBe('Refreshed!');
  });

  it('resets tooltip text to "Refresh token" after delay', async () => {
    const wrapper = mount(BaseRefreshButton, {
      global: {
        stubs: { FontAwesomeIcon },
      },
      directives: {
        tooltip,
      },
    });
    await wrapper.find('button').trigger('click');
    await vi.advanceTimersByTime(2000);
    //@ts-ignore
    const tooltipText = wrapper.vm.tooltipText;
    expect(tooltipText).toBe('Refreshed!');
  });
});
