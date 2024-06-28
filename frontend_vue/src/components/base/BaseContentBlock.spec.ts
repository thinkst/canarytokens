import { mount } from '@vue/test-utils';
import BaseContentBlock from '@/components/base/BaseContentBlock.vue';
import BaseCopyButton from './BaseCopyButton.vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

describe('BaseContentBlock', () => {
  it('renders text correctly', () => {
    const label = 'Card Name';
    const text = 'John Doe';
    const iconName = 'credit-card';
    const wrapper = mount(BaseContentBlock, {
      props: { label, text, iconName, copyContent: true },
      global: {
        stubs: { BaseCopyButton, FontAwesomeIcon },
      },
    });

    expect(wrapper.text()).toContain(label);
    expect(wrapper.text()).toContain(text);
  });

  it('emits click event when button is clicked', async () => {
    const label = 'Card Name';
    const text = 'John Doe';
    const iconName = 'credit-card';
    const wrapper = mount(BaseContentBlock, {
      props: { label, text, iconName, copyContent: true },
      global: {
        stubs: { BaseCopyButton, FontAwesomeIcon },
      },
    });

    await wrapper.find('button').trigger('click');

    expect(wrapper.emitted('click')).toBeTruthy();
  });

	it('does not render copy if copyContent is false', async () => {
    const label = 'Card Name';
    const text = 'John Dude';
    const iconName = 'credit-card';
    const wrapper = mount(BaseContentBlock, {
      props: { label, text, iconName, copyContent: false },
      global: {
        stubs: { BaseCopyButton },
      },
    });

		expect(wrapper.find('button').exists()).toBe(false);;
  });
});
