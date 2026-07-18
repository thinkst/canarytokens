import { mount } from '@vue/test-utils';
import { Form } from 'vee-validate';

import BaseInputCheckbox from '@/components/base/BaseInputCheckbox.vue';
import GenerateTokenForm from './GenerateTokenForm.vue';

describe('Microsoft Excel GenerateTokenForm', () => {
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
              props: ['id', 'value'],
              template:
                '<textarea :id="id" :value="value" @input="$emit(\'input\', $event)" />',
            },
            BaseSwitch: {
              props: ['id', 'modelValue'],
              emits: ['update:modelValue'],
              template:
                '<input :id="id" type="checkbox" :checked="modelValue" @change="$emit(\'update:modelValue\', $event.target.checked)" />',
            },
            BaseFormSelect: {
              props: ['id', 'options', 'value'],
              template:
                '<select :id="id" :value="value.value"><option v-for="option in options" :key="option.value" :value="option.value">{{ option.label }}</option></select>',
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
    expect(wrapper.find('#text_snippet_placement').exists()).toBe(false);
    expect(wrapper.find('#text_snippet_base64').exists()).toBe(false);

    await wrapper.find('#include_text_snippet').setValue(true);
    expect(wrapper.find('#text_snippet').exists()).toBe(true);
    expect(wrapper.find('#text_snippet_placement').exists()).toBe(true);
    const textSnippetPlacement = wrapper.find<HTMLSelectElement>(
      '#text_snippet_placement'
    );
    expect(textSnippetPlacement.element.value).toBe('plaintext');
    expect(wrapper.find('#text_snippet_base64').exists()).toBe(true);
    expect(
      wrapper.find('#text_snippet_base64').attributes('disabled')
    ).toBeUndefined();

    await wrapper.find('#text_snippet').setValue('Hello there');
    await wrapper.find('#text_snippet_base64').setValue(true);
    const textSnippet = wrapper.find<HTMLTextAreaElement>('#text_snippet');
    expect(textSnippet.element.value).toBe('SGVsbG8gdGhlcmU=');

    await wrapper.find('#text_snippet_base64').setValue(false);
    expect(textSnippet.element.value).toBe('Hello there');

    await wrapper.find('#include_text_snippet').setValue(false);
    expect(wrapper.find('#text_snippet').exists()).toBe(false);
    expect(wrapper.find('#text_snippet_placement').exists()).toBe(false);
    expect(wrapper.find('#text_snippet_base64').exists()).toBe(false);
  });
});
