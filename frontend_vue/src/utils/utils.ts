export function convertUnixTimeStampToDate(unixTimestamp: number) {
  const date = new Date(unixTimestamp * 1000);

  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
    second: 'numeric',
  };
  const formatter = new Intl.DateTimeFormat('en-US', options);
  return formatter.format(date);
}

export const validFileExtensions = {
  image: ['jpg', 'gif', 'png', 'jpeg'],
  exe: ['exe', 'dll'],
};

export function isValidFileType(
  fileName: string | undefined,
  fileType: string[]
): string | boolean | undefined {
  return fileName && fileType.includes(fileName.split('.').pop() as string);
}

export function isObject(val: Record<string, string> | string | number) {
  return val && typeof val === 'object' && Object.keys(val).length > 0;
}

export const sqlInjectionPattern = /\b(or 1=1|OR 1=1)\b/;
