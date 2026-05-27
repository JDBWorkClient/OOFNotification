const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: 'tests',
  timeout: 30 * 1000,
  expect: { timeout: 5000 },
  fullyParallel: false,
  webServer: {
    command: 'python -m http.server 8000',
    port: 8000,
    timeout: 120 * 1000,
    reuseExistingServer: process.env.CI ? false : true,
  },
});
