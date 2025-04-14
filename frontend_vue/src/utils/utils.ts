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

export function convertISOtoLocalDate(ISODate: string) {
  const date = new Date(ISODate);

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

// Adds transition to the view
// Available only on last versions of Chrome, Edge, Opera
// https://developer.mozilla.org/en-US/docs/Web/API/View_Transitions_API#browser_compatibility
export function addViewTransition(callback: () => void) {
  return new Promise<void>((resolve) => {
    const transitionCallback = () => {
      callback();
      resolve();
    };
    //@ts-ignore
    if (!document.startViewTransition) {
      transitionCallback();
    } else {
      //@ts-ignore
      document.startViewTransition(transitionCallback);
    }
  });
}

export function debounce(fn: () => void, delay: number) {
  let timeoutId: ReturnType<typeof setTimeout>;
  return () => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(fn, delay);
  };
}
