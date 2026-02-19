import type { HitsType } from '@/components/tokens/types.ts';
import incidentDetailsService from './incidentDetailsService';

describe('incidentDetailsService', () => {
  const hitAlert: HitsType = {
    time_of_hit: 1714637259.126385,
    src_ip: '87.184.171.140',
    geo_info: {
      loc: '52.5244,13.4105',
      org: 'AS3320 Deutsche Telekom AG',
      city: 'Berlin',
      country: 'DE',
      region: 'Berlin',
      hostname: 'p57b8ab8c.dip0.t-ipconnect.de',
      ip: '87.184.171.140',
      timezone: 'Europe/Berlin',
      postal: '10119',
      readme: 'https://ipinfo.io/missingauth',
      asn: {
        route: '192.168.0.0/24',
        type: 'Private',
        asn: 'AS12345',
        domain: 'example.com',
        name: 'Fake ASN',
      },
    },
    is_tor_relay: false,
    token_type: 'web_image',
    input_channel: 'HTTP',
    src_data: null,
    useragent:
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    additional_info: {
      javascript: null,
      browser: null,
      mysql_client: null,
      r: null,
      l: null,
    },
    location: null,
    alert_status: 'alertable',
  };

  it('should handle AWS key token', () => {
    const awsAlert: HitsType = {
      ...hitAlert,
      token_type: 'aws_keys',
      additional_info: {
        aws_key_log_data: {
          last_used: '2021-12-12T12:12:12Z',
          service_used: 'service name',
        },
      },
    };

    expect(incidentDetailsService(awsAlert, 'aws_keys')).toHaveProperty(
      'additional_info.aws_key_log_data.last_used'
    );
  });

  it('should display AWS API Key Token channel label', () => {
    const alert: HitsType = {
      ...hitAlert,
      token_type: 'aws_keys',
    };

    expect(incidentDetailsService(alert, 'aws_keys')).toHaveProperty(
      'basic_info.input_channel',
      'AWS API Key Token'
    );
  });

  it('should display DNS channel label', () => {
    const alert: HitsType = {
      ...hitAlert,
      token_type: 'dns',
      input_channel: 'DNS',
    };

    expect(incidentDetailsService(alert, 'dns')).toHaveProperty(
      'basic_info.input_channel',
      'DNS'
    );
  });

  it('should handle a bogon geo_info', () => {
    const bogonHitAlert: HitsType = {
      ...hitAlert,
      geo_info: {
        ip: '127.0.0.1',
        bogon: true,
      },
    };

    expect(incidentDetailsService(bogonHitAlert, 'dns')).toHaveProperty(
      'geo_info.bogon'
    );
    expect(incidentDetailsService(bogonHitAlert, 'dns')).not.toHaveProperty(
      'geo_info.country'
    );
  });

  it('should handle coords for PWA', () => {
    const pwaAlert: HitsType = {
      ...hitAlert,
      token_type: 'pwa',
      location: {
        //@ts-ignore
        coords: {
          accuracy: 14.871000289916992,
          altitude: 564.7999877929688,
          altitudeAccuracy: null,
          heading: null,
          latitude: 18.6617495,
          longitude: 73.708745,
          speed: null,
        },
        timestamp: 1723125410760,
      },
    };

    expect(incidentDetailsService(pwaAlert, 'pwa')).toHaveProperty(
      'basic_info.location.accuracy',
      14.871000289916992
    );
  });

  it('should show no tor relay for Credit Card Canarytoken', () => {
    const alert: HitsType = {
      time_of_hit: 1748445301.878416,
      src_ip: null,
      geo_info: null,
      is_tor_relay: null,
      input_channel: 'HTTP',
      src_data: null,
      useragent: null,
      token_type: 'credit_card_v2',
      alert_status: 'alertable',
      additional_info: {
        merchant: 'Amazon.com, New York, United States',
        transaction_amount: '-100',
        transaction_currency: 'USD',
        masked_card_number: '************7259',
        transaction_date: '2025-05-28T15:14:59.755775+00:00',
        transaction_type: 'AUTHORIZATION',
        status: 'FAILED',
      },
    };

    expect(incidentDetailsService(alert, 'credit_card_v2')).not.toHaveProperty(
      'basic_info.is_tor_relay',
      'true'
    );
  });
});
