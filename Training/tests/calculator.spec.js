const { test, expect } = require('@playwright/test');

test('basic addition works', async ({ page }) => {
  await page.goto('http://localhost:8000');
  await page.click('button[data-action="digit"][data-value="1"]');
  await page.click('button[data-action="operator"][data-value="+"]');
  await page.click('button[data-action="digit"][data-value="2"]');
  await page.click('button[data-action="equals"]');
  await expect(page.locator('#display')).toHaveText('3');
});
