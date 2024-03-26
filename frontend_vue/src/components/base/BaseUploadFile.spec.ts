import { mount } from '@vue/test-utils';
import { describe, it, expect, afterEach, vi } from 'vitest';

import BaseUploadFile from '@/components/base/BaseUploadFile.vue';
import BaseButton from './BaseButton.vue';

describe('BaseUploadFile', () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it('emits file-selected event when a valid file is selected', async () => {
    const wrapper = mount(BaseUploadFile, {
      props: {
        allowedFiles: 'image/jpeg',
        infoAllowedFile: 'JPEG max size 1MB',
        maxSize: 1024 * 1024,
      },
      global: {
        stubs: { BaseButton },
      },
    });

    const file = new File(['file contents'], 'test.jpg', {
      type: 'image/jpeg',
      size: 500000,
    } as File);

    await (wrapper.vm as any).fileValidation(file);
    expect(wrapper.emitted('file-selected')).toBeTruthy();
  });

  it('emits file-upload-error event when an invalid file is selected', async () => {
    const wrapper = mount(BaseUploadFile, {
      props: {
        allowedFiles: 'image/jpeg',
        maxSize: 1024 * 1024,
        infoAllowedFile: 'JPEG max size 1MB',
      },
      global: {
        stubs: { BaseButton },
      },
    });

    const file = new File(['file contents'], 'test.png', {
      type: 'image/png',
      size: 1024 * 1025,
    } as File);

    await (wrapper.vm as any).fileValidation(file);

    expect(wrapper.emitted('file-upload-error')).toBeTruthy();
  });

  it('displays error message when an invalid file format is selected', async () => {
    const wrapper = mount(BaseUploadFile, {
      props: {
        allowedFiles: 'image/png',
        maxSize: 1024 * 1024,
        infoAllowedFile: 'PNG max size 1MB',
      },
      global: {
        stubs: { BaseButton },
      },
    });

    const file = new File(['file contents'], 'test.zip', {
      type: 'application/zip',
      size: 1024 * 1025,
    } as File);

    await (wrapper.vm as any).fileValidation(file);
    expect(wrapper.html()).toContain('application/zip files are not allowed');
  });

  // it('displays error message when file is too big', async () => {
  //   const wrapper = mount(BaseUploadFile, {
  //     props: {
  //       allowedFiles: 'application/zip',
  //       maxSize: 1024 * 1024,
  //       infoAllowedFile: 'ZIP max size 1MB',
  //     },
  //     global: {
  //       stubs: { BaseButton },
  //     },
  //   });

  //   const file = new File(['file contents'], 'test.zip', {
  //     type: 'application/zip',
  //     size: 1024 * 1024 + 1,
  //   } as File);

  //   await (wrapper.vm as any).fileValidation(file);

  //   expect(wrapper.html()).toContain('The file is too big.');
  // });
});
