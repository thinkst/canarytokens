import { mount } from '@vue/test-utils';
import BaseLabel from './BaseLabel.vue';

describe('BaseLabel.vue', () => {
  it('shows asterisk when required', () => {
    const modelValue = 'initialText';
    const id = 'custom id';

    const wrapper = mount(BaseLabel, {
      props: { label: 'Required Field', required: true, modelValue, id },
    });
    expect(wrapper.html()).toContain('<span class="text-green-500"> *</span>');
  });
});
