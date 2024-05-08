import {
  formatLabels,
  isNotEmpty,
  formatTokenTypeLabel,
  buildIncidentDetails,
} from './incidentAlertService';
import type { HitsType } from '@/components/tokens/types.ts';

describe('formatLabels', () => {
  it('should remove underscores and capitalize the first letter of each key', () => {
    const incidentDetails = {
      geo_info: {
        city: 'string',
        something_else: 'value',
      },
      is_tor_relay: true,
      token_type: 'aws_keys',
    };

    const expectedResult = {
      'Geo info': {
        City: 'string',
        'Something else': 'value',
      },
      'Tor Known Exit Node': true,
      'Token type': 'aws_keys',
    };

    // @ts-ignore
    const result = formatLabels(incidentDetails);

    expect(result).toEqual(expectedResult);
  });

  it('should replace labels with custom labels if they exist', () => {
    const incidentDetails = {
      org: 'something',
      is_tor_relay: 'something',
      aws_keys: '1234',
      useragent: 'something',
      src_port: 'something',
      session_index: '1234',
      cmd_user_name: 'something',
      cmd_computer_name: 'something',
      last_used: 'something',
    };

    const expectedResult = {
      'AWS Access Key ID': '1234',
      'Client Handshake ID': '1234',
      'Client Source Port': 'something',
      'Computer executing command': 'something',
      'Key Last Used': 'something',
      Organisation: 'something',
      'Tor Known Exit Node': 'something',
      'User executing command': 'something',
      'User-agent': 'something',
    };

    // @ts-ignore
    const result = formatLabels(incidentDetails);

    expect(result).toEqual(expectedResult);
  });
});

describe('removeNullEmptyObjectsAndArrays', () => {
  it('should return true for non-empty values', () => {
    expect(isNotEmpty(1)).toBe(true);
    expect(isNotEmpty('hello')).toBe(true);
    expect(isNotEmpty(['one', 'two', 'ten'])).toBe(true);
    expect(isNotEmpty({ foo: 'bar' })).toBe(true);
  });

  it('should return false for empty values', () => {
    expect(isNotEmpty(null)).toBe(false);
    expect(isNotEmpty(undefined)).toBe(false);
    expect(isNotEmpty([])).toBe(false);
    expect(isNotEmpty({})).toBe(false);
  });
});

describe('formatTokenTypeLabel', () => {
  it('should return the label of the provided token', () => {
    const mockToken = 'azure_id_config';
    const expectedLabel = 'Azure Entra Config ID';

    const result = formatTokenTypeLabel(mockToken);

    expect(result).toBe(expectedLabel);
  });

  it('should handle unknown tokens gracefully', () => {
    const mockToken = 'unknown_token';
    const expectedLabel = 'unknown_token';

    const result = formatTokenTypeLabel(mockToken);

    expect(result).toBe(expectedLabel);
  });
});

describe('buildIncidentDetails', () => {
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
    input_channel: 'HTTP',
    src_data: null,
    useragent:
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    token_type: 'web_image',
    additional_info: {
      javascript: null,
      browser: null,
      mysql_client: null,
      r: null,
      l: null,
    },
  };

  it('should handle AWS key token', () => {
    const awsAlert: HitsType = {
      ...hitAlert,
      token_type: 'aws_keys',
      additional_info: {
        aws_key_log_data: {
          last_used: 1714637259.126385,
          service_used: 'service name',
        },
      },
    };

    expect(buildIncidentDetails(awsAlert)).toHaveProperty(
      'additional_info.aws_key_log_data.last_used'
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

    expect(buildIncidentDetails(bogonHitAlert)).toHaveProperty(
      'geo_info.bogon'
    );
    expect(buildIncidentDetails(bogonHitAlert)).not.toHaveProperty(
      'geo_info.country'
    );
  });
});
