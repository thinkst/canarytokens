import { mount, VueWrapper } from '@vue/test-utils';
import { vi } from 'vitest';
import BaseButton from './BaseButton.vue';

let wrapper: VueWrapper;

describe('BaseButton', () => {
  beforeEach(() => {
    wrapper = mount(BaseButton);
  });

  test('is called', () => {
    expect(wrapper.exists()).toBeTruthy();
  });

  test('render correctly', () => {
    expect(wrapper.html()).toMatchSnapshot();
  });

  test('emits an event when clicked', async () => {
    const onClick = vi.fn();
    wrapper = mount(BaseButton, {
      attrs: { onClick: onClick },
    });
    await wrapper.find('button').trigger('click');
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  test('renders button with primary variant by default', async () => {
    expect(wrapper.classes()).toContain('primary');
  });

  test('renders button with secondary variant', async () => {
    wrapper = mount(BaseButton, {
      props: {
        variant: 'secondary',
      },
    });
    expect(wrapper.classes()).toContain('secondary');
  });

  test('renders button with primary variant when prop has a wrong name', async () => {
    wrapper = mount(BaseButton, {
      props: {
        //@ts-ignore
        variant: 'wrong-prop-name',
      },
    });
    expect(wrapper.classes()).toContain('primary');
  });

  test('renders button with text variant', () => {
    const wrapper = mount(BaseButton, {
      props: { variant: 'text' },
    });
    expect(wrapper.classes()).toContain('text');
  });
});
