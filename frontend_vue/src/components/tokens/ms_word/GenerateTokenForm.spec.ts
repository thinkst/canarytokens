import { flushPromises, mount } from '@vue/test-utils';
import { Form } from 'vee-validate';

import BaseInputCheckbox from '@/components/base/BaseInputCheckbox.vue';
import BaseRadioInput from '@/components/base/BaseRadioInput.vue';
import GenerateTokenForm from './GenerateTokenForm.vue';

describe('Microsoft Word GenerateTokenForm', () => {
  it('shows the document text field only when requested', async () => {
    let submittedValues: Record<string, unknown> | undefined;
    const wrapper = mount(
      {
        components: { Form, GenerateTokenForm },
        template: '<Form @submit="onSubmit"><GenerateTokenForm /></Form>',
        setup() {
          return {
            onSubmit: (values: Record<string, unknown>) => {
              submittedValues = values;
            },
          };
        },
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
            BaseRadioInput,
          },
          directives: {
            tooltip: () => undefined,
          },
          stubs: {
            BaseInyoniMessage: true,
            GenerateTokenSettingsNotifications: true,
          },
        },
      }
    );

    expect(wrapper.find('#text_snippet').exists()).toBe(false);
    expect(wrapper.find('#text_snippet_placement').exists()).toBe(false);
    expect(wrapper.find('#text_snippet_base64').exists()).toBe(false);

    await wrapper.find('form').trigger('submit');
    await flushPromises();
    expect(submittedValues).toEqual({
      include_text_snippet: false,
      text_snippet: undefined,
      text_snippet_placement: undefined,
    });

    await wrapper.find('#include_text_snippet').setValue(true);
    expect(wrapper.find('#text_snippet').exists()).toBe(true);
    expect(wrapper.find('#text_snippet_placement').exists()).toBe(true);
    const plaintextPlacement = wrapper.find<HTMLInputElement>(
      '#text_snippet_placement_plaintext'
    );
    const metadataPlacement = wrapper.find<HTMLInputElement>(
      '#text_snippet_placement_metadata'
    );
    expect(plaintextPlacement.element.type).toBe('radio');
    expect(metadataPlacement.element.type).toBe('radio');
    expect(plaintextPlacement.element.checked).toBe(true);

    await metadataPlacement.setValue(true);
    expect(metadataPlacement.element.checked).toBe(true);
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

    await wrapper.find('form').trigger('submit');
    await flushPromises();
    expect(submittedValues).toEqual({
      include_text_snippet: true,
      text_snippet: 'Hello there',
      text_snippet_placement: 'metadata',
    });

    await wrapper.find('#include_text_snippet').setValue(false);
    expect(wrapper.find('#text_snippet').exists()).toBe(false);
    expect(wrapper.find('#text_snippet_placement').exists()).toBe(false);
    expect(wrapper.find('#text_snippet_base64').exists()).toBe(false);
  });
});
