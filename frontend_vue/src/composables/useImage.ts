
export default function useImage() {
  const getImgUrl = (name: string): string => {
    const path = `/src/assets/${name}`;
    const modules = import.meta.glob('/src/assets/**', { eager: true });
    // @ts-ignore
    const mod = modules[path] as any;

    if (mod === null || mod === undefined) {
      throw new Error(`Image not found: '/src/assets/${name}'.`);
    }

    return mod.default;
  };

  return {
    getImgUrl,
  };
}
