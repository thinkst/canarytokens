import { mount } from '@vue/test-utils';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faChevronUp } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import vSelect from 'vue-select';
import BaseFormSelect from './BaseFormSelect.vue';

library.add(faChevronUp);

describe('BaseCopyButton', () => {
  it('is called', () => {
    const wrapper = mount(BaseFormSelect, {
      props: {
        options: ['Option 1', 'Option 2', 'Option 3'],
        id: 'my-select',
        label: 'My Select',
        placeholder: 'Select an option',
      },
      global: {
        components: { FontAwesomeIcon, vSelect },
      },
    });
    expect(wrapper.exists()).toBeTruthy();
  });

  it('Shows the correct placeholder', () => {
    const wrapper = mount(BaseFormSelect, {
      props: {
        options: ['Option 1', 'Option 2', 'Option 3'],
        id: 'my-select',
        label: 'My Select',
        placeholder: 'Select an option',
      },
      global: {
        components: { FontAwesomeIcon, vSelect },
      },
    });
    expect(wrapper.html()).toContain('Select an option');
  });

  it('renders the label', () => {
    const wrapper = mount(BaseFormSelect, {
      props: {
        id: 'select',
        label: 'My Select',
        options: ['Option 1', 'Option 2', 'Option 3'],
      },
      global: {
        components: { FontAwesomeIcon, vSelect },
      },
    });

    expect(wrapper.find('label').text()).toBe('My Select');
  });
});
