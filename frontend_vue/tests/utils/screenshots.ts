const VIEWPORTS = {
  large: { width: 1920, height: 1080 },
  desktop: { width: 1280, height: 720 },
  mobile: { width: 375, height: 667 },
};

export const takeScreenshot = async (page: any, name: string, fullPage: boolean = false) => {
  for (const [device, viewport] of Object.entries(VIEWPORTS)) {
    await page.setViewportSize(viewport);
    await page.screenshot({ path: `./tests/screenshots/${device}/${name}.png`, fullPage });
  }
};
