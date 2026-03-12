import { test, expect } from '@playwright/test';
import { waitForApiSuccess } from './utils/common';
import { takeScreenshot } from './utils/screenshots';
// import { tokenServices } from '../src/utils/tokenServices';

test.describe('Create Token', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('Can create Web bug Canarytoken', async ({ page }) => {
    const webBugCard = page.getByText('Web bug');
    await expect(webBugCard).toBeVisible();
    await webBugCard.click();

    await expect(page.getByRole('heading', { name: 'Create Web bug Token' })).toBeVisible();
    await expect(page.getByText('Mail me here when the alert fires')).toBeVisible();
    await page.locator('#email').fill('test@example.com');
    await expect(page.getByText('Remind me of this when the alert fires')).toBeVisible();
    await page.locator('#memo').fill('This is a reminder for the Web bug Canarytoken alert.');
    await takeScreenshot(page, 'web-bug/token-form');

    const createBtn = page.getByRole('button', { name: 'Create Canarytoken' });
    await expect(createBtn).toBeVisible();
    await createBtn.click();

    await waitForApiSuccess({
      page,
      url: '/d3aece8093b71007b5ccfedad91ebb11/generate',
      callback: async () => {
        await expect(page.getByText('Your Web bug Canarytoken is active!')).toBeVisible();
        await expect(page.getByRole('button', { name: 'Manage Canarytoken' })).toBeVisible();
        await takeScreenshot(page, 'web-bug/token-created')
      },
    })
  });
});
