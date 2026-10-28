const fs = require("fs");
const { spawn } = require("child_process");

const CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const USER_DATA_DIR = "/Users/ceooctapus/erp/.chrome_profile_quality_check";
const ARTIFACT_DIR = "/Users/ceooctapus/.gemini/antigravity-ide/brain/8be31d53-8904-4dc3-aa85-2408675dece3";

async function run() {
  const chrome = spawn(CHROME_PATH, [
    "--headless",
    "--disable-gpu",
    "--remote-debugging-port=9266",
    `--user-data-dir=${USER_DATA_DIR}`,
    "--window-size=1600,1000",
    "http://65.1.131.52/#/auth/login"
  ]);

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  await sleep(2500);

  try {
    const listRes = await fetch("http://127.0.0.1:9266/json");
    const pages = await listRes.json();
    const page = pages.find((p) => p.type === "page");
    if (!page) {
      console.error("No browser page found");
      chrome.kill();
      return;
    }

    const ws = new WebSocket(page.webSocketDebuggerUrl);

    let msgId = 1;
    const sendCommand = (method, params = {}) => {
      return new Promise((resolve) => {
        const id = msgId++;
        const handler = (event) => {
          const data = JSON.parse(event.data);
          if (data.id === id) {
            ws.removeEventListener("message", handler);
            resolve(data.result);
          }
        };
        ws.addEventListener("message", handler);
        ws.send(JSON.stringify({ id, method, params }));
      });
    };

    ws.onopen = async () => {
      console.log("Connected to Chrome DevTools Protocol");
      await sleep(3000);

      // 1. Screenshot Login
      const loginScreenshot = await sendCommand("Page.captureScreenshot", { format: "png" });
      fs.writeFileSync(`${ARTIFACT_DIR}/quality_01_login.png`, Buffer.from(loginScreenshot.data, "base64"));
      console.log("Quality Check 1 (Login) saved");

      // Fill in credentials and submit
      const loginEval = await sendCommand("Runtime.evaluate", {
        expression: `(() => {
          // Find Super Admin button or fill inputs
          const buttons = Array.from(document.querySelectorAll('button, div[role="button"]'));
          const superAdminBtn = buttons.find(b => b.innerText && b.innerText.includes('Super Admin'));
          if (superAdminBtn) {
            superAdminBtn.click();
          }
          
          const emailInput = document.querySelector('input[type="email"], input[name="email"], input[placeholder*="email" i], input[type="text"]');
          const passInput = document.querySelector('input[type="password"]');
          if (emailInput && !emailInput.value) {
            emailInput.value = 'admin';
            emailInput.dispatchEvent(new Event('input', { bubbles: true }));
          }
          if (passInput && !passInput.value) {
            passInput.value = 'admin123';
            passInput.dispatchEvent(new Event('input', { bubbles: true }));
          }

          // Click submit button
          setTimeout(() => {
            const submitBtn = document.querySelector('button.submit-btn, button[type="submit"]');
            if (submitBtn) {
              submitBtn.click();
            }
          }, 600);

          return { foundSuperAdmin: !!superAdminBtn, email: emailInput?.value };
        })()`,
        returnByValue: true
      });
      console.log("Login trigger result:", JSON.stringify(loginEval.result?.value));

      // Wait for login and navigation to dashboard
      console.log("Waiting for dashboard navigation...");
      await sleep(8000);

      // Check current URL
      const currentUrlEval = await sendCommand("Runtime.evaluate", {
        expression: `window.location.href`,
        returnByValue: true
      });
      console.log("Current URL after login:", currentUrlEval.result?.value);

      // If still on auth, explicitly navigate to dashboard
      if (currentUrlEval.result?.value?.includes('/auth/login')) {
        console.log("Explicitly navigating to dashboard...");
        await sendCommand("Runtime.evaluate", {
          expression: `window.location.href = 'http://65.1.131.52/#/pages/dashboard'`,
          returnByValue: true
        });
        await sleep(5000);
      }

      // 2. Screenshot Dashboard
      const dashScreenshot = await sendCommand("Page.captureScreenshot", { format: "png" });
      fs.writeFileSync(`${ARTIFACT_DIR}/quality_02_dashboard.png`, Buffer.from(dashScreenshot.data, "base64"));
      console.log("Quality Check 2 (Dashboard) saved");

      // Contrast audit on Dashboard
      const dashAudit = await sendCommand("Runtime.evaluate", {
        expression: `(() => {
          const body = document.body;
          const bodyTheme = body.className;
          const layout = document.querySelector('nb-layout');
          const card = document.querySelector('nb-card');
          const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6, .content-heading')).map(h => ({
            tag: h.tagName,
            text: h.innerText?.trim()?.slice(0, 30),
            color: window.getComputedStyle(h).color,
            fontSize: window.getComputedStyle(h).fontSize
          })).slice(0, 5);
          
          const navItems = Array.from(document.querySelectorAll('.menu-item a, nb-menu a')).map(a => ({
            text: a.innerText?.trim()?.slice(0, 20),
            color: window.getComputedStyle(a).color,
            bg: window.getComputedStyle(a).backgroundColor
          })).slice(0, 5);

          return {
            bodyTheme,
            layoutBg: layout ? window.getComputedStyle(layout).backgroundColor : null,
            cardBg: card ? window.getComputedStyle(card).backgroundColor : null,
            cardColor: card ? window.getComputedStyle(card).color : null,
            cardBorder: card ? window.getComputedStyle(card).borderColor : null,
            headings,
            navItems
          };
        })()`,
        returnByValue: true
      });
      console.log("Dashboard Audit:", JSON.stringify(dashAudit.result?.value, null, 2));

      // 3. Navigate to Employees
      console.log("Navigating to Employees page...");
      await sendCommand("Runtime.evaluate", {
        expression: `window.location.href = 'http://65.1.131.52/#/pages/employees'`,
        returnByValue: true
      });
      await sleep(5000);

      const empScreenshot = await sendCommand("Page.captureScreenshot", { format: "png" });
      fs.writeFileSync(`${ARTIFACT_DIR}/quality_03_employees.png`, Buffer.from(empScreenshot.data, "base64"));
      console.log("Quality Check 3 (Employees) saved");

      const empAudit = await sendCommand("Runtime.evaluate", {
        expression: `(() => {
          const table = document.querySelector('table, ng2-smart-table');
          const th = document.querySelector('th');
          const td = document.querySelector('td');
          const searchInput = document.querySelector('input');
          const addBtn = document.querySelector('button.status-primary, nb-action, button');

          return {
            hasTable: !!table,
            thBg: th ? window.getComputedStyle(th).backgroundColor : null,
            thColor: th ? window.getComputedStyle(th).color : null,
            tdColor: td ? window.getComputedStyle(td).color : null,
            inputBg: searchInput ? window.getComputedStyle(searchInput).backgroundColor : null,
            inputColor: searchInput ? window.getComputedStyle(searchInput).color : null,
            inputBorder: searchInput ? window.getComputedStyle(searchInput).borderColor : null,
            btnBg: addBtn ? window.getComputedStyle(addBtn).backgroundColor : null,
            btnColor: addBtn ? window.getComputedStyle(addBtn).color : null
          };
        })()`,
        returnByValue: true
      });
      console.log("Employees Audit:", JSON.stringify(empAudit.result?.value, null, 2));

      // 4. Navigate to Invoices
      console.log("Navigating to Invoices page...");
      await sendCommand("Runtime.evaluate", {
        expression: `window.location.href = 'http://65.1.131.52/#/pages/invoices'`,
        returnByValue: true
      });
      await sleep(5000);

      const invScreenshot = await sendCommand("Page.captureScreenshot", { format: "png" });
      fs.writeFileSync(`${ARTIFACT_DIR}/quality_04_invoices.png`, Buffer.from(invScreenshot.data, "base64"));
      console.log("Quality Check 4 (Invoices) saved");

      // 5. Mobile Viewport Check
      console.log("Resizing to mobile viewport (390x844)...");
      await sendCommand("Emulation.setDeviceMetricsOverride", {
        width: 390,
        height: 844,
        deviceScaleFactor: 2,
        mobile: true
      });
      await sendCommand("Runtime.evaluate", {
        expression: `window.location.href = 'http://65.1.131.52/#/pages/dashboard'`,
        returnByValue: true
      });
      await sleep(5000);

      const mobScreenshot = await sendCommand("Page.captureScreenshot", { format: "png" });
      fs.writeFileSync(`${ARTIFACT_DIR}/quality_05_mobile_dashboard.png`, Buffer.from(mobScreenshot.data, "base64"));
      console.log("Quality Check 5 (Mobile Dashboard) saved");

      ws.close();
      chrome.kill();
      process.exit(0);
    };
  } catch (err) {
    console.error("Error in verification:", err);
    chrome.kill();
    process.exit(1);
  }
}

run();
