import { mount } from '@vue/test-utils';
import BaseFormTextField from '@/components/base/BaseFormTextField.vue';
import BaseLabelArrow from './BaseLabelArrow.vue';
import BaseLabel from './BaseLabel.vue';

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

  it('renders BaseLabelArrow when hasArrow is true', () => {
    const wrapper = mount(BaseFormTextField, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        hasArrow: true,
      },
      components: { BaseLabelArrow, BaseLabel },
    });

    expect(wrapper.findComponent(BaseLabelArrow).exists()).toBe(true);
    expect(wrapper.findComponent(BaseLabel).exists()).toBe(false);
  });
});
