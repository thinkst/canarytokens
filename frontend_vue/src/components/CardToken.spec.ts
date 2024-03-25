import { mount } from '@vue/test-utils';
import { describe, it, expect, afterEach, vi } from 'vitest';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faArrowRight, faQuestion } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import BaseLinkDocumentation from '@/components/base/BaseLinkDocumentation.vue';
import CardToken from './CardToken.vue';

library.add(faArrowRight, faQuestion);

describe('BaseCardToken.vue', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  beforeEach(async () => {
    vi.doMock('@/composables/useImage', () => {
      return {
        getImgUrl: vi.fn().mockReturnValue('/src/assets/'),
      };
    });
    //@ts-ignore
    const { getImgUrl } = await import('@/composables/useImage');

    expect(getImgUrl()).toBe('/src/assets/');
  });

  it('renders props when passed', async () => {
    const title = 'Test title';
    const description = 'Test description';
    const logoImgUrl = 's3_bucket.png';
    const documentationLink = 'Test link';

    const wrapper = mount(CardToken, {
      props: { title, description, logoImgUrl, documentationLink },
      global: {
        stubs: { FontAwesomeIcon, BaseLinkDocumentation },
      },
    });

    expect(wrapper.text()).toContain(title);
    expect(wrapper.text()).toContain(description);
    expect(wrapper.html()).toContain(logoImgUrl);
    expect(wrapper.html()).toContain(documentationLink);
  });

  it('renders default logo when no logo is passed', async () => {
    const title = 'Test title';
    const description = 'Test description';
    const documentationLink = 'Test link';

    const wrapper = mount(CardToken, {
      props: { title, description, documentationLink },
      global: {
        stubs: { FontAwesomeIcon, BaseLinkDocumentation },
      },
    });

    expect(wrapper.text()).toContain(title);
    expect(wrapper.text()).toContain(description);
    expect(wrapper.html()).toContain('default.png');
    expect(wrapper.html()).toContain(documentationLink);
  });

  it('emits click event when card is clicked', async () => {
    const title = 'Test title';
    const description = 'Test description';
    const logoImgUrl = 's3_bucket.png';
    const documentationLink = 'Test link';

    const wrapper = mount(CardToken, {
      props: { title, description, logoImgUrl, documentationLink },
      global: {
        stubs: { FontAwesomeIcon, BaseLinkDocumentation },
      },
    });

    await wrapper.find('button').trigger('click');
    expect(wrapper.emitted()).toHaveProperty('clickToken');
  });
});
