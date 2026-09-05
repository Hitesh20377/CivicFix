import { test, expect } from '@playwright/test';

test.describe('Authentication Flows', () => {
  test('Successful login and redirect to issues', async ({ page }) => {
    await page.goto('/login');
    
    // Using placeholder or label to fill the form
    await page.fill('input[type="email"]', 'integration_citizen@example.com');
    await page.fill('input[type="password"]', 'dummy');
    
    // Click Sign In
    await page.click('button[type="submit"]');
    
    // Expect to be redirected to issues page
    await expect(page).toHaveURL(/\/issues/);
  });

  test('Login with invalid credentials shows error message', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('input[type="email"]', 'wrong@example.com');
    await page.fill('input[type="password"]', 'wrongpass');
    
    await page.click('button[type="submit"]');
    
    // Expect error message
    await expect(page.locator('text=Invalid email or password')).toBeVisible();
  });
});
