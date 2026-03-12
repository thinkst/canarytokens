import { expect, Page } from "@playwright/test";

export const waitForApiSuccess = async ({
  page,
  url,
  status = 200,
  callback,
}: {
  page: Page;
  url: string;
  status?: number;
  callback: () => Promise<void>;
}) => {
  const responsePromise = page.waitForResponse(
    (resp) => resp.url().includes(url) && resp.status() === status
  );
  await callback();
  const response = await responsePromise;
  expect(response.status()).toBe(status);
};
