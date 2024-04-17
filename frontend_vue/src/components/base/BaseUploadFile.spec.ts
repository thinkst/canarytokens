import { mount } from '@vue/test-utils';
import { describe, it, expect, afterEach, vi } from 'vitest';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import BaseUploadFile from '@/components/base/BaseUploadFile.vue';
import BaseButton from './BaseButton.vue';

// TODO: add more tests

describe('BaseUploadFile', () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it('emits file-selected event when a valid file is selected', async () => {
    const wrapper = mount(BaseUploadFile, {
      props: {
        id: 'test-id',
      },
      global: {
        stubs: { BaseButton, FontAwesomeIcon },
      },
    });

    const file = new File(['file contents'], 'test.jpg', {
      type: 'image/jpeg',
      size: 500000,
    } as File);

    await (wrapper.vm as any).fileUpload(file);
    expect(wrapper.emitted('file-selected')).toBeTruthy();
  });

  it('triggers the file input when the browse button is clicked', async () => {
    const onClick = vi.fn();
    const wrapper = mount(BaseUploadFile, {
      props: {
        id: 'test-id',
      },
      global: {
        stubs: { BaseButton, FontAwesomeIcon },
      },
    });

    const fileInput = wrapper.find('input[type="file"]');
    expect(fileInput.exists()).toBeTruthy();

    await wrapper.find('button').trigger('click');
    onClick();
    await expect(onClick).toHaveBeenCalledTimes(1);
  });
});
