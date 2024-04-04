import { mount } from '@vue/test-utils';
import BaseFormTextField from '@/components/base/BaseFormTextField.vue';

describe('BaseTextField.vue', () => {
  it('renders label when passed', () => {
    const label = 'Test Label';
    const modelValue = 'initialText';
    const id = 'custom id';

    const wrapper = mount(BaseFormTextField, {
      props: { label, modelValue, id },
    });
    expect(wrapper.text()).toMatch(label);
  });

  it('shows asterisk when required', () => {
    const modelValue = 'initialText';
    const id = 'custom id';

    const wrapper = mount(BaseFormTextField, {
      props: { label: 'Required Field', required: true, modelValue, id },
    });
    expect(wrapper.html()).toContain('<span class="text-green-500">*</span>');
  });

  it('switches between input and textarea based on multiline prop', async () => {
    const modelValue = 'initialText';
    const id = 'custom id';

    const wrapper = mount(BaseFormTextField, {
      props: { multiline: false, modelValue, label: 'Label', id },
    });
    expect(wrapper.find('input').exists()).toBe(true);
    expect(wrapper.find('textarea').exists()).toBe(false);

    await wrapper.setProps({ multiline: true });
    expect(wrapper.find('input').exists()).toBe(false);
    expect(wrapper.find('textarea').exists()).toBe(true);
  });

  it('emits update:modelValue event on input', async () => {
    const modelValue = 'initialText';
    const id = 'custom id';

    const wrapper = mount(BaseFormTextField, {
      props: { multiline: false, modelValue, label: 'Label', id },
    });
    const inputElement = wrapper.find('input');
    await inputElement.setValue('new value');
    expect(wrapper.emitted()).toHaveProperty('update:modelValue');
    expect(wrapper.emitted()['update:modelValue'][0]).toEqual(['new value']);
  });

  it('displays error message when hasError is true', () => {
    const modelValue = 'initialText';
    const id = 'custom id';
    const errorMessage = 'Error message';

    const wrapper = mount(BaseFormTextField, {
      props: { hasError: true, errorMessage, modelValue, label: 'Label', id },
    });
    expect(wrapper.text()).toContain(errorMessage);
  });

  it('displays helper message', () => {
    const modelValue = 'initialText';
    const id = 'custom id';
    const helperMessage = 'Helper message';

    const wrapper = mount(BaseFormTextField, {
      props: { helperMessage, modelValue, label: 'Label', id },
    });
    expect(wrapper.text()).toContain(helperMessage);
  });

  it('applies disabled state correctly', async () => {
    const modelValue = 'initialText';
    const id = 'custom id';

    const wrapper = mount(BaseFormTextField, {
      props: { disabled: false, modelValue, label: 'Label', id },
    });
    expect(wrapper.find('input').attributes('disabled')).toBeUndefined();

    await wrapper.setProps({ disabled: true });
    expect(wrapper.find('input').attributes('disabled')).toBeDefined();
  });
});
