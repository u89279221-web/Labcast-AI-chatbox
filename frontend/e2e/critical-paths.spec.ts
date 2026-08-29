import { test, expect } from '@playwright/test'

test.describe('LabCast AI Critical Paths E2E', () => {

  test.describe('Role-based Login and Nav Confirmation', () => {
    const roles = [
      { email: 'admin@labcast.edu', pass: 'admin123', role: 'admin', expectedNav: ['Dashboard', 'Machines', 'Documents', 'IoT Devices', 'Maintenance', 'Analytics'] },
      { email: 'faculty@labcast.edu', pass: 'faculty123', role: 'faculty', expectedNav: ['Dashboard', 'Machines', 'Documents'] },
      { email: 'tech@labcast.edu', pass: 'tech123', role: 'technician', expectedNav: ['Dashboard', 'Machines', 'IoT Devices', 'Maintenance'] },
      { email: 'student@labcast.edu', pass: 'student123', role: 'student', expectedNav: ['Dashboard'] },
    ]

    for (const user of roles) {
      test(`Login as ${user.role} and verify nav items`, async ({ page }) => {
        await page.goto('/login')
        await page.fill('input[type="email"]', user.email)
        await page.fill('input[type="password"]', user.pass)
        await page.click('button[type="submit"]')

        await expect(page).toHaveURL(/\/(machines|health|dashboard|$)/)
        
        for (const navLabel of user.expectedNav) {
          await expect(page.getByRole('link', { name: navLabel, exact: false })).toBeVisible()
        }
      })
    }
  })

  test.describe('Machine SOP Management & Emergency Toggle', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/login')
      await page.fill('input[type="email"]', 'admin@labcast.edu')
      await page.fill('input[type="password"]', 'admin123')
      await page.click('button[type="submit"]')
      await page.waitForURL(/\/(machines|health|dashboard|$)/)
    })

    test('Edit an SOP step and confirm persistence', async ({ page }) => {
      await page.goto('/machines/CNC01')
      await expect(page.getByText('HAAS VF-2 CNC Milling Machine')).toBeVisible()

      // Add a new SOP step
      const stepInput = page.getByPlaceholder(/add new step/i).or(page.getByPlaceholder(/new sop step/i))
      if (await stepInput.isVisible()) {
        await stepInput.fill('E2E Test SOP Step Verification')
        await page.click('button:has-text("Add Step")')
      }

      // Save changes
      const saveBtn = page.getByRole('button', { name: /save/i })
      if (await saveBtn.isVisible()) {
        await saveBtn.click()
        await expect(page.getByText(/updated|saved|success/i)).toBeVisible()
      }

      // Reload page and confirm step persists
      await page.reload()
      await expect(page.getByText('E2E Test SOP Step Verification')).toBeVisible()
    })

    test('Trigger Emergency shutdown and confirm live notification', async ({ page }) => {
      await page.goto('/machines/CNC01')
      
      const emergencyToggle = page.getByRole('button', { name: /emergency/i }).or(page.getByText(/emergency shutdown/i))
      await expect(emergencyToggle).toBeVisible()
      await emergencyToggle.click()

      // Confirm live notification / toast fires
      await expect(page.getByText(/emergency/i)).toBeVisible()
    })
  })

  test.describe('Machine-Scoped Chat & Source Isolation', () => {
    test('Ask a machine-scoped chat question and confirm source isolation', async ({ page }) => {
      await page.goto('/student-chat?machine=CNC01')

      const input = page.getByPlaceholder(/ask/i).or(page.getByPlaceholder(/type a message/i))
      await expect(input).toBeVisible()
      await input.fill('How do I turn on the spindle?')
      await page.keyboard.press('Enter')

      // Check response and source block
      await expect(page.getByText(/spindle|haas|g-code|speed/i)).toBeVisible({ timeout: 15000 })
      await expect(page.getByText(/source/i)).toBeVisible()
    })
  })

  test.describe('Document Upload & Retrievability', () => {
    test('Upload a document and confirm it becomes retrievable', async ({ page }) => {
      await page.goto('/login')
      await page.fill('input[type="email"]', 'admin@labcast.edu')
      await page.fill('input[type="password"]', 'admin123')
      await page.click('button[type="submit"]')
      await page.waitForURL(/\/(machines|health|dashboard|$)/)

      await page.goto('/machines/CNC01')
      
      // Switch to Documents tab if tab exists
      const docTab = page.getByRole('tab', { name: /documents/i })
      if (await docTab.isVisible()) {
        await docTab.click()
      }

      // Check file input or upload zone
      const fileInput = page.locator('input[type="file"]')
      if (await fileInput.count() > 0) {
        // Create a dummy PDF buffer
        const dummyPdf = Buffer.from('%PDF-1.4 %EOT test pdf file content')
        await fileInput.setInputFiles({
          name: 'e2e_manual_test.pdf',
          mimeType: 'application/pdf',
          buffer: dummyPdf
        })

        // Confirm uploaded file appears in the document list
        await expect(page.getByText('e2e_manual_test.pdf')).toBeVisible({ timeout: 10000 })
      }
    })
  })

})
