import { mount } from '@vue/test-utils';
import BaseNotificationBox from '@/components/base/BaseNotificationBox.vue';
import BaseButton from './BaseButton.vue';

describe('BaseNotificationBox', () => {
  it('renders message correctly', () => {
    const message = 'Test message';
    const wrapper = mount(BaseNotificationBox, {
      props: { variant: 'info', message },
      global: {
        stubs: { BaseButton },
      },
    });

    expect(wrapper.text()).toContain(message);
  });

  it('emits click event when button is clicked', async () => {
    const wrapper = mount(BaseNotificationBox, {
      props: { variant: 'info', message: 'Test message', textLink: 'Click me' },
      global: {
        stubs: { BaseButton },
      },
    });

    await wrapper.find('button').trigger('click');

    expect(wrapper.emitted('click')).toBeTruthy();
  });

  it('renders with the correct variant class', () => {
    const wrapper = mount(BaseNotificationBox, {
      props: { variant: 'info', message: 'Info message' },
      global: {
        stubs: { BaseButton },
      },
    });

    expect(wrapper.classes()).toContain('text-blue-700');
  });

  it('displays text link when provided', () => {
    const wrapper = mount(BaseNotificationBox, {
      props: { variant: 'info', message: 'Info message', textLink: 'Click me' },
      global: {
        stubs: { BaseButton },
      },
    });

    expect(wrapper.find('button').text()).toBe('Click me');
  });

  it('does not display text link when not provided', () => {
    const wrapper = mount(BaseNotificationBox, {
      props: { variant: 'warning', message: 'Warning message' },
      global: {
        stubs: { BaseButton },
      },
    });

    expect(wrapper.find('button').exists()).toBe(false);
  });
});
