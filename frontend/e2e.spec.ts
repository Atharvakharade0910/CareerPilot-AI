import { test, expect } from "@playwright/test";
import path from "node:path";
const base = "http://localhost:3010";
test("landing and demo interactions, accessible mobile navigation", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto(base);
  await expect(
    page.getByRole("heading", {
      name: "Your next chapter. A clearer direction.",
    }),
  ).toBeVisible();
  await page.getByRole("link", { name: "View demo", exact: true }).click();
  await expect(
    page.getByRole("heading", {
      name: "A little clarity. A lot of possibility.",
    }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Junior AI Engineer", exact: true })
    .click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.getByRole("button", { name: "Save to sample shortlist" }).click();
  await expect(
    page.getByRole("button", { name: "Remove from sample shortlist" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Close analysis" }).click();
  await page.getByRole("button", { name: "Toggle color theme" }).click();
  await expect(page.locator(".workspace")).toHaveClass(/dark/);
  await page.reload();
  await expect(page.locator(".workspace")).toHaveClass(/dark/);
  await page.getByRole("button", { name: "Toggle color theme" }).click();
  await page.keyboard.press("Control+k");
  await expect(page.getByRole("dialog")).toBeVisible();
  await page
    .getByRole("textbox", { name: "Search workspace pages" })
    .fill("Job Discovery");
  await page
    .getByRole("dialog")
    .getByRole("link", { name: "Job Discovery" })
    .click();
  await page
    .getByRole("combobox", { name: "Filter jobs" })
    .selectOption("Remote only");
  await expect(page.locator(".job-card")).toHaveCount(1);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.getByRole("button", { name: "Open navigation" }).click();
  await page
    .locator(".sidebar")
    .getByRole("link", { name: "Overview", exact: true })
    .click();
  await expect(page.locator(".sidebar")).not.toHaveClass(/open/);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  await expect(page.locator(".dashboard-content > div").last()).toBeVisible();
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.screenshot({
    path: "../docs/dashboard-mobile.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.screenshot({
    path: "../docs/dashboard-desktop.png",
    fullPage: true,
  });
  expect(errors).toEqual([]);
});
test("registration, real resume upload, evidence review, persistence and logout", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const email = `browser-${Date.now()}@example.com`,
    password = "Browser-Test-9482!";
  await page.goto(base + "/sign-up");
  await page
    .getByLabel("Full name", { exact: true })
    .fill("Taylor Browser Test");
  await page.getByLabel("Email address").fill(email);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Create your account" }).click();
  await expect(page).toHaveURL(/onboarding/);
  await page.getByLabel("Current location").fill("Pune, India");
  await page.getByRole("button", { name: "Continue", exact: true }).click();
  await page
    .getByLabel("Choose master resume")
    .setInputFiles(path.resolve("../tests/fixtures/sample-resume.docx"));
  await expect(
    page.getByText("sample-resume.docx", { exact: true }),
  ).toBeVisible();
  await page.screenshot({
    path: "../docs/onboarding-upload.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "Continue", exact: true }).click();
  await page.getByRole("button", { name: /^AI Engineer/ }).click();
  await page.getByRole("button", { name: "Continue", exact: true }).click();
  await page.getByLabel("Preferred locations").fill("Pune, Bengaluru");
  await page.getByRole("button", { name: "Continue", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Your story. Your final say." }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Reject Python", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Accept Python", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Accept Python", exact: true })
    .click();
  await page
    .getByLabel("I have reviewed this profile and its source evidence.")
    .check();
  await page.screenshot({
    path: "../docs/onboarding-review.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "Finish my profile" }).click();
  await expect(page).toHaveURL(/dashboard/);
  await expect(page.getByText("100%", { exact: true })).toBeVisible();
  await page.reload();
  await expect(page.getByText("100%", { exact: true })).toBeVisible();
  await page
    .locator(".sidebar")
    .getByRole("link", { name: "Resume Studio", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "sample-resume.docx" }),
  ).toBeVisible();
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("link", { name: "Download original" }).click(),
  ]);
  expect(download.suggestedFilename()).toBe("sample-resume.docx");
  await page.getByRole("button", { name: "Log out", exact: true }).click();
  await expect(page).toHaveURL(base + "/");
  await page.goto(base + "/dashboard");
  await expect(page).toHaveURL(/sign-in/);
  await page.getByLabel("Email address").fill(email);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page).toHaveURL(/dashboard/);
  await expect(page.getByText("100%", { exact: true })).toBeVisible();
  expect(errors).toEqual([]);
});
