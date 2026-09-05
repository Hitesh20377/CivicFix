import { test, expect } from '@playwright/test';

test.describe('Field Worker Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login as field worker before each test
    await page.goto('/login');
    await page.fill('input[type="email"]', 'worker1@example.com');
    await page.fill('input[type="password"]', 'dummy');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/issues/);
  });

  test('Field worker can view assigned issues and add comments', async ({ page }) => {
    // Wait for the issue to appear (as it is seeded in the test database)
    await expect(page.locator('text=Test Pothole').first()).toBeVisible();
    
    await page.locator('text=Test Pothole').first().click();
    await expect(page).toHaveURL(/\/issues\/\d+/);
    
    // Test adding a comment if the comment input exists
    const commentInput = page.locator('input[placeholder="Write a comment..."]');
    
    // In our test, we expect the comment input to be present for a field worker
    await expect(commentInput).toBeVisible();
    await commentInput.fill('Worker inspecting the issue.');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=Worker inspecting the issue.').first()).toBeVisible();
  });
});
