const puppeteer = require("puppeteer");
const url = process.argv[2] || "https://www.google.com";

(async () => {
  // Launch the browser
  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: false, // run with a visible browser window
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });

  // Use the first tab. Open a new window.
  const [page] = await browser.pages();

  // Go to Google
  await page.goto(url);

  console.log(`Opened ${url}!`);

  // Close the browser
  await browser.close();
})();
