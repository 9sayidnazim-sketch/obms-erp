const fs = require("fs");
const { spawn } = require("child_process");

const CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const USER_DATA_DIR = "/Users/ceooctapus/erp/.chrome_profile_hero_check";
const ARTIFACT_DIR = "/Users/ceooctapus/.gemini/antigravity-ide/brain/8be31d53-8904-4dc3-aa85-2408675dece3";

async function run() {
  const chrome = spawn(CHROME_PATH, [
    "--headless",
    "--disable-gpu",
    "--remote-debugging-port=9277",
    `--user-data-dir=${USER_DATA_DIR}`,
    "--window-size=1600,1000",
    "http://65.1.131.52/#/auth/login"
  ]);

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  await sleep(2500);

  try {
    const listRes = await fetch("http://127.0.0.1:9277/json");
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
      await sleep(4000);

      // Capture Screenshot of Login Page with new Hero illustration
      const screenshot = await sendCommand("Page.captureScreenshot", { format: "png" });
      const outputPath = `${ARTIFACT_DIR}/new_hero_login_verified.png`;
      fs.writeFileSync(outputPath, Buffer.from(screenshot.data, "base64"));
      console.log(`Saved screenshot to ${outputPath}`);

      ws.close();
      chrome.kill();
      process.exit(0);
    };
  } catch (err) {
    console.error("Error:", err);
    chrome.kill();
    process.exit(1);
  }
}

run();
