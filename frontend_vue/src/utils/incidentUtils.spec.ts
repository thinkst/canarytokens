import { formatLabels, formatTokenTypeLabel } from './incidentUtils';

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

describe('formatTokenTypeLabel', () => {
  it('should return the label of the provided token', () => {
    const mockToken = 'azure_id_config';
    const expectedLabel = 'Azure Entra ID login';

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
