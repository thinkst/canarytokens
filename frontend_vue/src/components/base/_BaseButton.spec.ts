import { mount, VueWrapper } from '@vue/test-utils'
import BaseButton from './_BaseButton.vue'

let wrapper: VueWrapper;

describe('BaseButton', () => {
    beforeEach(() => {
        wrapper = mount(BaseButton)
    })

    test('is called', () => {
        expect(wrapper.exists()).toBeTruthy()
    })

    test('render correctly', () => {
        expect(wrapper.html()).toMatchSnapshot()
    })

    test('emits an event when clicked', async () => {
        const onClick = vi.fn()
        wrapper = mount(BaseButton, {
            attrs: { onClick: onClick }
        })
        await wrapper.find('button').trigger('click')
        expect(onClick).toHaveBeenCalledTimes(1)
    })

    test('renders button with primary variant by default', async () => {
        expect(wrapper.classes()).toContain('bg-green')
    })

    test('renders button with secondary variant', async () => {
        wrapper = mount(BaseButton, {
            props: {
            variant: 'secondary'
            },
        })
        expect(wrapper.classes()).toContain('bg-transparent')
    })

    test('renders button with primary variant when prop has a wrong name', async () => {
        wrapper = mount(BaseButton, {
            props: {
            variant: 'wrong-prop-name'
            },
        })
        expect(wrapper.classes()).toContain('bg-green')
    })

    test('renders button with text variant', () => {
        const wrapper = mount(BaseButton, {
        props: { variant: 'text' }
        })
        const expectedClasses = ['font-semibold', 'hover:text-green-800', 'focus:text-green-800', 'text-grey-500', 'rounded-full', 'px-16', 'py-8'];
        expectedClasses.forEach(expectedClass => {
            expect(wrapper.classes()).toContain(expectedClass);
        });
    })

})
