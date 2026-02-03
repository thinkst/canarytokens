import { mount, shallowMount } from '@vue/test-utils';
import { ref } from 'vue';
import BaseFormTextField from '@/components/base/BaseFormTextField.vue';
import BaseLabelArrow from './BaseLabelArrow.vue';
import BaseLabel from './BaseLabel.vue';

describe('BaseLabelArrow.vue', () => {
  it('renders label when passed', () => {
    const label = 'Test Label';
    const modelValue = 'initialText';
    const id = 'custom_id';

    const wrapper = mount(BaseLabelArrow, {
      props: { label, modelValue, id },
    });
    expect(wrapper.text()).toMatch(label);
  });

  it('adds arrow class to the specified word in the label', () => {
    const arrowWordPosition = 2;
    const label = ref('Test Label Here');
    const arrowVariant = ref('one');

    const wrapper = shallowMount(BaseLabelArrow, {
      //@ts-ignore
      props: { arrowWordPosition, label, arrowVariant },
    });

    //@ts-ignore
    const labelArrowed = wrapper.vm.labelArrowed;

    const expectedOutput =
      'Test <span class="label-arrow label-arrow__one" alt="arrow">Label</span> Here';

    expect(labelArrowed).toBe(expectedOutput);
  });

  it('should not add arrow if no position is provided', () => {
    const label = ref('Test Label Here');
    const arrowVariant = ref('one');

    const wrapper = shallowMount(BaseLabelArrow, {
      //@ts-ignore
      props: { label, arrowVariant },
    });

    //@ts-ignore
    const labelArrowed = wrapper.vm.labelArrowed;

    expect(labelArrowed).toBe('Test Label Here');
  });
});
