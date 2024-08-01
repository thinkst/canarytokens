import { mount } from '@vue/test-utils';
import BaseFormImageSelect from './BaseFormImageSelect.vue';

describe('BaseFormImageSelect.vue', () => {
  const options = [
    { value: 'image1', url: 'path/to/image1.jpg' },
    { value: 'image2', url: 'path/to/image2.jpg' },
  ];

  it('renders the component with the correct label', () => {
    const wrapper = mount(BaseFormImageSelect, {
      props: {
        id: 'image-select',
        label: 'Select an Image',
        options,
      },
    });
    expect(wrapper.find('legend').text()).toBe('Select an Image');
  });

  it('renders the correct number of options', () => {
    const wrapper = mount(BaseFormImageSelect, {
      props: {
        id: 'image-select',
        label: 'Select an Image',
        options,
      },
    });
    const labels = wrapper.findAll('label');
    expect(labels.length).toBe(options.length);
  });

  // it('updates selectedImage when an option is clicked', async () => {
  //   const wrapper = mount(BaseFormImageSelect, {
  //     props: {
  //       label: 'Select an Image',
  //       options,
  //     },
  //   });
  //   const radioInput = wrapper.find('input[type="radio"][value="image1"]');
  //   await radioInput.trigger('click');
  //   expect(wrapper.vm.selectedImage).toBe('image1');
  // });

  it('applies the correct class when an option is selected', async () => {
    const wrapper = mount(BaseFormImageSelect, {
      props: {
        id: 'image-select',
        label: 'Select an Image',
        options,
      },
    });
    const label = wrapper.find('label[for="image1"]');
    // const radioInput = wrapper.find('input[type="radio"][value="image1"]');
    await label.trigger('click');
    const selectedImageRef = wrapper.vm.selectedImage;
    // Check if the selectedImage is updated correctly
    // expect(selectedImageRef.value).toBe('image1');

    // Check if the correct class is applied to the label
    expect(label.classes()).toContain('border-green-500');
  });

  it('emits change event when an option is selected', async () => {
    const wrapper = mount(BaseFormImageSelect, {
      props: {
        id: 'image-select',
        label: 'Select an Image',
        options,
      },
    });
    const radioInput = wrapper.find('input[type="radio"][value="image1"]');
    console.log(radioInput);
    await radioInput.trigger('click');
    expect(wrapper.emitted().change).toBeTruthy();
  });
});
