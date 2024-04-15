import { mount } from '@vue/test-utils';
import { vi } from 'vitest';
import BaseButton from './BaseButton.vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

describe('BaseButton', () => {
  test('is called', () => {
    const wrapper = mount(BaseButton, {
      global: {
        stubs: { FontAwesomeIcon },
      },
    });
    expect(wrapper.exists()).toBeTruthy();
  });

  test('render correctly', () => {
    const wrapper = mount(BaseButton, {
      global: {
        stubs: { FontAwesomeIcon },
      },
    });
    expect(wrapper.html()).toMatchSnapshot();
  });

  test('emits an event when clicked', async () => {
    const onClick = vi.fn();
    const wrapper = mount(BaseButton, {
      attrs: { onClick: onClick },
      global: {
        stubs: { FontAwesomeIcon },
      },
    });
    await wrapper.find('button').trigger('click');
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  test('renders button with primary variant by default', async () => {
    const wrapper = mount(BaseButton, {
      global: {
        stubs: { FontAwesomeIcon },
      },
    });
    expect(wrapper.classes()).toContain('primary');
  });

  test('renders button with secondary variant', async () => {
    const wrapper = mount(BaseButton, {
      props: {
        variant: 'secondary',
      },
      global: {
        stubs: { FontAwesomeIcon },
      },
    });
    expect(wrapper.classes()).toContain('secondary');
  });

  test('renders button with primary variant when prop has a wrong name', async () => {
    const wrapper = mount(BaseButton, {
      props: {
        //@ts-ignore
        variant: 'wrong-prop-name',
      },
      global: {
        stubs: { FontAwesomeIcon },
      },
    });
    expect(wrapper.classes()).toContain('primary');
  });

  test('renders button with text variant', () => {
    const wrapper = mount(BaseButton, {
      props: { variant: 'text' },
      global: {
        stubs: { FontAwesomeIcon },
      },
    });
    expect(wrapper.classes()).toContain('text');
  });

  test('renders <a> instead of a button', () => {
    const wrapper = mount(BaseButton, {
      props: { variant: 'text', href: 'http://example.com' },
      global: {
        stubs: { FontAwesomeIcon },
      },
    });
    expect(wrapper.html()).toContain('a');
  });

  test('renders icon', async () => {
    const wrapper = mount(BaseButton, {
      props: { icon: 'arrow-right' },
      global: {
        stubs: { FontAwesomeIcon },
      },
    });
    expect(wrapper.classes()).toContain('flex-row');
    expect(wrapper.findComponent({ name: 'FontAwesomeIcon' }).exists()).toBe(
      true
    );
  });
});
