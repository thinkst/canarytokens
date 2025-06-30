import { isNotEmpty } from './utils';

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
