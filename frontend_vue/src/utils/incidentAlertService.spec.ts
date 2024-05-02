import {
  formatLabels,
  removeNullEmptyObjectsAndArrays,
} from './incidentAlertService';

describe('formatLabels', () => {
  it('should format incident details object correctly', () => {
    const incidentDetails = {
      geo_info: {
        org: 'string',
        city: 'string',
        something_else: 'value',
      },
      is_tor_relay: true,
      token_type: 'aws_keys',
    };

    const expectedResult = {
      'Geo info': {
        Organisation: 'string',
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
});

describe('removeNullEmptyObjectsAndArrays', () => {
  it('should remove null, empty objects, and empty arrays from an object', () => {
    const incidentDetails = {
      custom_key: 'value',
      geo_info: {
        org: 'string',
        city: 'string',
      },
      key: null,
      emptyObject: {},
      undefinedVal: undefined,
      emptyArray: [],
      nestedObject: {
        nestedKey: null,
        nestedEmptyObject: {},
        nestedEmptyArray: [],
      },
    };
    const expectedResult = {
      custom_key: 'value',
      geo_info: {
        org: 'string',
        city: 'string',
      },
    };

    // @ts-ignore
    const result = removeNullEmptyObjectsAndArrays(incidentDetails);

    expect(result).toEqual(expectedResult);
  });
});
