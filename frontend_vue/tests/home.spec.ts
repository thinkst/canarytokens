import { test, expect } from '@playwright/test';
import { takeScreenshot } from './utils/screenshots';

test.describe('Home Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });
  test('Has Canarytokens title', async ({ page }) => {
    await expect(page).toHaveTitle('Canarytokens');
  });

  test('Has homepage heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Create a Canarytoken. Deploy it somewhere.' })).toBeVisible();
    await takeScreenshot(page, 'homepage');
  });

  test('Home page heading Thinkst Canary link is correct', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'Thinkst Canary' })).toHaveAttribute('href', 'https://canary.tools/');
  });

  test('Home page heading Documentation link is correct', async ({ page }) => {
    const documentationLink = page.getByRole('link', { name: 'Documentation', exact: true, });
    await expect(documentationLink).toHaveAttribute(
      'href',
      'https://docs.canarytokens.org/guide'
    );
  });

  test('Has correct footer', async ({ page }) => {
    const footer = page.locator('footer');
    await expect(footer.getByText(
      'By Using This Service, You Agree to Our Terms of Use.',
    )).toBeVisible();
    await expect(footer.getByText(
      'Read Our Canarytokens Documentation',
    )).toBeVisible();
    await expect(footer.getByRole('link', { name: 'Terms of Use' })).toHaveAttribute('href', '/nest/legal');
    await expect(footer.getByRole('link', { name: 'Canarytokens Documentation' })).toHaveAttribute('href', 'https://docs.canarytokens.org/guide/');
  });
});
