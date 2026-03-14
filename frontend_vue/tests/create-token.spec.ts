import { test, expect } from '@playwright/test';
import { getApiSuccessData } from './utils/common';
// import { takeScreenshot } from './utils/screenshots';
import { tokenServices } from '../src/utils/tokenServices';
import { TOKENS_TYPE } from '../src/components/constants';
import { createTestingJob, registerTokenData } from './utils/services';

const TOKENS_TO_SKIP = [
  TOKENS_TYPE.CREDIT_CARD_V2,
  TOKENS_TYPE.AWS_INFRA,
  TOKENS_TYPE.AZURE_ID,
  TOKENS_TYPE.SQL_SERVER //Mission to set up - later problem
]

const TOKENS_TO_REGISTER_JOB_FOR = [
  TOKENS_TYPE.WEB_BUG,
  TOKENS_TYPE.UNIQUE_EMAIL,
  TOKENS_TYPE.DNS,
  TOKENS_TYPE.AWS_KEYS,
]

test.describe('Create Token', () => {
  let JOB_ID: string | null = null;
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test.beforeAll(async() => {
    await createTestingJob()
      .then(async (jobData) => {
        JOB_ID = jobData.job_id;
      })
      .catch((error) => {
        throw error;
      });
  });

  Object.keys(tokenServices).forEach((service) => {
    if (TOKENS_TO_SKIP.includes(service) || !TOKENS_TO_REGISTER_JOB_FOR.includes(service)) {
      console.warn(`Skipping tests for ${service} Canarytoken`);
      return;
    }
    const tokenObj = tokenServices[service as keyof typeof tokenServices];
    const serviceName = tokenObj.label;

    test(`Can create ${tokenObj.label} Canarytoken`, async ({ page }) => {
      const tokenCard = page.getByText(serviceName).first();
      await expect(tokenCard).toBeVisible();
      await tokenCard.click();

      if (service === TOKENS_TYPE.PWA) {
        await page.locator('label[for="absa"]').click();
        await expect(page.locator('input#absa')).toBeChecked();
      }

      if (service === TOKENS_TYPE.FAST_REDIRECT || service === TOKENS_TYPE.SLOW_REDIRECT) {
        page.getByRole('textbox', { name: 'Redirect URL' }).fill('https://example.com');
      }

      if (service === TOKENS_TYPE.CLONED_WEBSITE || service === TOKENS_TYPE.CSS_CLONED_SITE) {
        page.getByRole('textbox', { name: 'Domain of protected website' }).fill('example.com');
      }

      if (service === TOKENS_TYPE.SENSITIVE_CMD) {
        page.getByRole('textbox', { name: 'Name of the process to monitor' }).fill('whoami.exe');
      }

      if (service === TOKENS_TYPE.WINDOWS_FAKE_FS) {
        page.getByRole('textbox', { name: 'Where will this directory be placed?' }).fill('C:\\Desktop\\FakeFS');
        const industryInput = page.locator('input.vs__search[placeholder="Choose an Industry/Sector"]');
        await industryInput.click();
        await page.getByRole('option', { name: 'Personal Finances' }).click();
      }

      if (service === TOKENS_TYPE.WEBDAV) {
        const WebDavInput = page.locator('input.vs__search[placeholder="Select dummy folder content"]');
        await WebDavInput.click();
        await page.getByRole('option', { name: 'Cyber Security' }).click();
      }

      if (service === TOKENS_TYPE.IDP_APP) {
        const IDPAppInput = page.locator('input.vs__search[placeholder="Select an app"]');
        await IDPAppInput.click();
        await page.getByRole('option', { name: 'Gmail' }).click();
      }

      if (service === TOKENS_TYPE.WEB_IMAGE) {
        await page.locator('input[type="file"]').setInputFiles('tests/upload/WebImage.jpg');
      }

      if (service === TOKENS_TYPE.CUSTOM_EXE) {
        await page.locator('input[type="file"]').setInputFiles('tests/upload/CustomExe.exe');
      }

      if (service === TOKENS_TYPE.AZURE_ID){
        page.getByRole('textbox', { name: 'Azure ID certificate name' }).fill('testingtokens.pem');
      }

      await expect(page.getByText('Mail me here when the alert fires')).toBeVisible();
      await page.locator('#email').fill('test@example.com');
      await expect(page.getByText('Remind me of this when the alert fires')).toBeVisible();
      await page.locator('#memo').fill(`This is a reminder for the ${serviceName} Canarytoken alert.`);
      // await takeScreenshot(page, `${serviceName.toLowerCase()}/token-form`);

      const createBtn = page.getByRole('button', { name: 'Create Canarytoken' });
      await expect(createBtn).toBeVisible();
      await createBtn.click();

      const tokenData = await getApiSuccessData({
        page,
        url: '/d3aece8093b71007b5ccfedad91ebb11/generate',
        callback: async () => {
          await expect(page.getByText(`Your ${serviceName} Canarytoken is active!`)).toBeVisible();
          await expect(page.getByRole('button', { name: 'Manage Canarytoken' })).toBeVisible();
          // await takeScreenshot(page, `${serviceName.toLowerCase()}/token-created`)
        },
      })
      const jobItems = [
        {
          "type": service,
          "domain": "honeypdfs.net",
          "token": tokenData.token,
          "auth": tokenData.auth_token
        },
      ]
      if (JOB_ID && TOKENS_TO_REGISTER_JOB_FOR.includes(service)) {
        await registerTokenData(JOB_ID, jobItems)
          .then((registerResponse) => {
            console.log('Token data registered for testing job:', registerResponse);
          })
          .catch((error) => {
            throw error;
          });
      }
    });

  });

});
