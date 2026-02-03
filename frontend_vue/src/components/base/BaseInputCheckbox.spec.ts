import { mount } from '@vue/test-utils';
import { vi } from 'vitest';

import BaseInputCheckbox from './BaseInputCheckbox.vue';

const tooltip = vi.fn();

describe('BaseInputCheckbox', () => {
  const mountComponent = (customProps = {}) => {
    return mount(BaseInputCheckbox, {
      props: {
        id: 'test-checkbox',
        label: 'Test Checkbox',
        modelValue: false,
        ...customProps,
      },
      directives: {
        tooltip,
      },
    });
  };

  it('renders the label correctly', () => {
    const wrapper = mountComponent();
    expect(wrapper.find('span').text()).toBe('Test Checkbox');
  });

  it('renders the checkbox input with the correct id', () => {
    const wrapper = mountComponent();
    expect(wrapper.find('input[type="checkbox"]').attributes('id')).toBe(
      'test-checkbox'
    );
  });

  it('renders the checkbox as unchecked by default', () => {
    const wrapper = mountComponent();
    const checkbox = wrapper.find('input[type="checkbox"]');
    //@ts-ignore
    expect(checkbox.element.checked).toEqual(false);
  });

  it('renders the checkbox as checked when modelValue is true', async () => {
    const wrapper = mountComponent({ modelValue: true });
    const checkbox = wrapper.find('input[type="checkbox"]');
    //@ts-ignore
    await checkbox.setChecked(true);
    //@ts-ignore
    expect(checkbox.element.checked).toEqual(true);
  });

  it('emits update:modelValue event when the checkbox is clicked', async () => {
    const wrapper = mountComponent();
    const checkbox = wrapper.find('input[type="checkbox"]');
    //@ts-ignore
    await checkbox.setChecked(true);
    //@ts-ignore
    expect(wrapper.emitted('update:modelValue')[0]).toEqual([true]);
    //@ts-ignore
    await checkbox.setChecked(false);
    //@ts-ignore
    expect(wrapper.emitted('update:modelValue')[1]).toEqual([false]);
  });

  it('renders the label as hidden when hideLabel prop is true', () => {
    const wrapper = mountComponent({ hideLabel: true });
    expect(wrapper.find('span').classes()).toContain('sr-only');
  });

  it('renders the tooltip when tooltipContent prop is provided', async () => {
    const wrapper = mountComponent({ tooltipContent: 'This is a tooltip' });
    const checkbox = wrapper.find('input[type="checkbox"]');
    //@ts-ignore
    await checkbox.trigger('mouseenter');
    const tooltipText = wrapper.vm.tooltipContent;
    expect(tooltipText).toBe('This is a tooltip');
  });

  it('disables the checkbox and label when disabled prop is true', () => {
    const wrapper = mountComponent({ disabled: true });
    const checkbox = wrapper.find('input[type="checkbox"]');
    const labelElement = wrapper.find('label');
    expect(checkbox.attributes('disabled')).toBe('');
    expect(labelElement.classes()).toContain('label-disabled');
  });

  it('does not emit update:modelValue event when the disabled checkbox is clicked', async () => {
    const wrapper = mountComponent({ disabled: true });
    const checkbox = wrapper.find('input[type="checkbox"]');
    //@ts-ignore
    await checkbox.setChecked(true);
    //@ts-ignore
    expect(wrapper.emitted('update:modelValue')).toBeUndefined();
  });
});
