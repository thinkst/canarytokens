import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createVfm } from 'vue-final-modal';
import { library } from '@fortawesome/fontawesome-svg-core'
import { faXmark } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import BaseModal from './_BaseModal.vue';


library.add(faXmark)

describe('BaseModal.vue', () => {
    describe(':props', () => {
        let wrapper;

        beforeEach(() => {
            const vfm = createVfm();
            wrapper = mount(BaseModal, {
                props: { title: 'Test', hasBackButton: true },
                global: { plugins: [vfm], stubs: { teleport: true, FontAwesomeIcon } },
            });
        });


        it('to see the teleport!', async () => {
            const container = wrapper.find('.vfm__content');
            console.log(wrapper.html());
            expect(container.element).toHaveClass('sm_max-w-xs');
        });

        // describe(':size', () => {
        //     let container;

        //     beforeEach(() => {
        //         container = wrapper.find('.vfm__content');

        //     });


        // it('sm - sets container to be small', async () => {
        //     await baseModal.setProps({ size: 'sm' });

        //     expect(container.element).toHaveClass('sm_max-w-sm');
        // });

        // it('md - sets container to be medium', async () => {
        //     await baseModal.setProps({ size: 'md' });

        //     expect(container.element).toHaveClass('sm_max-w-md');
        // });

        // it('lg - sets container to be large', async () => {
        //     await baseModal.setProps({ size: 'lg' });

        //     expect(container.element).toHaveClass('sm_max-w-lg');
        // });
    });
});
