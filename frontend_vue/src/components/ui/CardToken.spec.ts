import { mount } from '@vue/test-utils';
import { describe, it, expect, afterEach, vi } from 'vitest';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faArrowRight, faQuestion } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import BaseButtonHowToDeploy from '@/components/base/BaseButtonHowToDeploy.vue';
import CardToken from './CardToken.vue';
import BaseSkeletonLoader from '../base/BaseSkeletonLoader.vue';

library.add(faArrowRight, faQuestion);

describe('BaseCardToken.vue', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  beforeEach(async () => {
    vi.doMock('@/utils/getImageUrl', () => {
      return {
        getImageUrl: vi.fn().mockReturnValue('/src/assets/'),
      };
    });
    //@ts-ignore
    const { getImageUrl } = await import('@/utils/getImageUrl');

    expect(getImageUrl()).toBe('/src/assets/');
  });

  it('renders props when passed', async () => {
    const title = 'Test title';
    const description = 'Test description';
    const logoImgUrl = 'aws_keys.png';
    const selectedToken = 'AWS keys';
    const wrapper = mount(CardToken, {
      props: { title, description, logoImgUrl, selectedToken },
      global: {
        stubs: { FontAwesomeIcon, BaseButtonHowToDeploy, BaseSkeletonLoader },
      },
    });

    expect(wrapper.text()).toContain(title);
    expect(wrapper.text()).toContain(description);
    expect(wrapper.vm.logoImgUrl).toBe('aws_keys.png');
  });

  it('renders default logo when no logo is passed', async () => {
    const title = 'Test title';
    const description = 'Test description';
    const selectedToken = 'AWS keys';
    const logoImgUrl = 'aws_keys.png';

    const wrapper = mount(CardToken, {
      props: { title, description, selectedToken, logoImgUrl},
      global: {
        stubs: { FontAwesomeIcon, BaseButtonHowToDeploy, BaseSkeletonLoader },
      },
    });

    expect(wrapper.text()).toContain(title);
    expect(wrapper.text()).toContain(description);
  });

  it('emits click event when card is clicked', async () => {
    const title = 'Test title';
    const description = 'Test description';
    const logoImgUrl = 'aws_keys.png';
    const selectedToken = 'AWS keys';

    const wrapper = mount(CardToken, {
      props: { title, description, logoImgUrl, selectedToken },
      global: {
        stubs: { FontAwesomeIcon, BaseButtonHowToDeploy, BaseSkeletonLoader },
      },
    });

    await wrapper.find('button').trigger('click');
    expect(wrapper.emitted()).toHaveProperty('clickToken');
  });
});
