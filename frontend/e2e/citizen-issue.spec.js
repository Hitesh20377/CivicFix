import { test, expect } from '@playwright/test';

test.describe('Citizen Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login as citizen before each test
    await page.goto('/login');
    await page.fill('input[type="email"]', 'citizen@example.com');
    await page.fill('input[type="password"]', 'dummy');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/issues/);
  });

  test('Citizen can create a new issue', async ({ page }) => {
    await page.goto('/issues/new');
    
    // Fill out the issue form
    await page.fill('input[placeholder="e.g. Pothole on Main Street"]', 'Huge Pothole on 5th Ave');
    await page.selectOption('select', { index: 1 }); // select the first actual category
    await page.fill('textarea', 'There is a massive pothole that needs fixing immediately.');
    
    // Location
    await page.fill('input[placeholder="Latitude (e.g. 34.0522)"]', '40.7128');
    await page.fill('input[placeholder="Longitude (e.g. -118.2437)"]', '-74.0060');
    
    // Submit
    await page.click('button[type="submit"]');
    
    // Expect redirection to issues dashboard
    await expect(page).toHaveURL(/\/issues/);
    
    // Expect the issue to be listed (assuming it shows on the dashboard)
    await expect(page.locator('text=Huge Pothole on 5th Ave').first()).toBeVisible();
  });
});
