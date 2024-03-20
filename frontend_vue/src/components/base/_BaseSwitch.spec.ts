import { mount } from '@vue/test-utils';
import BaseSwitch from './_BaseSwitch.vue';

describe('BaseSwitch.vue', () => {

  test('is called', () => {
    const wrapper = mount(BaseSwitch);
    expect(wrapper.exists()).toBeTruthy();
  });

  test('renders correctly', () => {
    const label = 'Test Label';
    const id = 'test-id';
    const wrapper = mount(BaseSwitch, {
      props: { label, id },
    });
    expect(wrapper.html()).toMatchSnapshot();
  });

  it('renders label when passed', () => {
    const label = 'Test Label';
    const id = 'test-id';
    const wrapper = mount(BaseSwitch, {
      props: { label, id },
    });
    expect(wrapper.text()).toMatch(label);
  });

  it('emits an update:modelValue event when checked', async () => {
    const label = 'Test Label';
    const id = 'test-id';
    const wrapper = mount(BaseSwitch, {
      props: { label, id, modelValue: false },
    });
    const checkbox = wrapper.find('input[type="checkbox"]');
    //@ts-ignore
    await checkbox.setChecked(true);
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([true]);
  });

  it('emits an update:modelValue event when unchecked', async () => {
    const label = 'Test Label';
    const id = 'test-id';
    const wrapper = mount(BaseSwitch, {
      props: { label, id, modelValue: true },
    });
    const checkbox = wrapper.find('input[type="checkbox"]');
    //@ts-ignore
    await checkbox.setChecked(false);
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([false]);
  });

  it('renders a disabled checkbox when disabled is true', () => {
    const label = 'Test Label';
    const id = 'test-id';
    const wrapper = mount(BaseSwitch, {
      props: { label, id, disabled: true },
    });
    const checkbox = wrapper.find('input[type="checkbox"]');
    expect(checkbox.attributes('disabled')).toBeDefined();
  });
});
