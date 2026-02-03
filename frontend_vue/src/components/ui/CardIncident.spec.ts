import { mount } from '@vue/test-utils';
import CardIncident from './CardIncident.vue';

describe('CardIncident.vue', () => {
  test('is called', () => {
    const wrapper = mount(CardIncident);
    expect(wrapper.exists()).toBeTruthy();
  });

  it('renders the incidentPreviewInfo prop correctly', async () => {
    const incidentPreviewInfo = {
      Date: '2024-03-22 16:01:08.976860',
      IP: '84.138.198.174',
      Channel: 'HTTP',
    };
    const incidentId = '123';

    const wrapper = mount(CardIncident, {
      props: { incidentPreviewInfo, incidentId, lastKey: false },
    });

    expect(wrapper.text()).toContain(incidentPreviewInfo.Date);
    expect(wrapper.text()).toContain(incidentPreviewInfo.IP);
    expect(wrapper.text()).toContain(incidentPreviewInfo.Channel);
  });

  it('emits a "click" event when clicked', async () => {
    const wrapper = mount(CardIncident);

    await wrapper.find('button').trigger('click');

    expect(wrapper.emitted()).toHaveProperty('click');

    expect(wrapper.emitted('click')).toHaveLength(1);
  });
});
