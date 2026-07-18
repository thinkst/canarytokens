import { mount } from '@vue/test-utils';
import { Form } from 'vee-validate';

import BaseInputCheckbox from '@/components/base/BaseInputCheckbox.vue';
import GenerateTokenForm from './GenerateTokenForm.vue';

describe('Microsoft Word GenerateTokenForm', () => {
  it('shows the document text field only when requested', async () => {
    const wrapper = mount(
      {
        components: { Form, GenerateTokenForm },
        template: '<Form><GenerateTokenForm /></Form>',
      },
      {
        global: {
          components: {
            BaseGenerateTokenSettings: {
              template: '<div><slot /></div>',
            },
            BaseInputCheckbox,
            BaseFormTextField: {
              props: ['id'],
              template: '<textarea :id="id" />',
            },
          },
          directives: {
            tooltip: () => undefined,
          },
          stubs: {
            GenerateTokenSettingsNotifications: true,
          },
        },
      }
    );

    expect(wrapper.find('#text_snippet').exists()).toBe(false);
    expect(wrapper.find('#text_snippet_placement_metadata').exists()).toBe(
      false
    );
    expect(wrapper.find('#text_snippet_placement_plaintext').exists()).toBe(
      false
    );
    expect(wrapper.find('#text_snippet_base64').exists()).toBe(false);

    await wrapper.find('#include_text_snippet').setValue(true);
    expect(wrapper.find('#text_snippet').exists()).toBe(true);
    expect(
      wrapper.find('#text_snippet_placement_metadata').attributes('disabled')
    ).toBeUndefined();
    expect(
      wrapper.find('#text_snippet_placement_plaintext').attributes('disabled')
    ).toBeUndefined();
    expect(wrapper.find('#text_snippet_base64').exists()).toBe(true);
    expect(
      wrapper.find('#text_snippet_base64').attributes('disabled')
    ).toBeUndefined();

    await wrapper.find('#include_text_snippet').setValue(false);
    expect(wrapper.find('#text_snippet').exists()).toBe(false);
    expect(wrapper.find('#text_snippet_placement_metadata').exists()).toBe(
      false
    );
    expect(wrapper.find('#text_snippet_placement_plaintext').exists()).toBe(
      false
    );
    expect(wrapper.find('#text_snippet_base64').exists()).toBe(false);
  });
});
