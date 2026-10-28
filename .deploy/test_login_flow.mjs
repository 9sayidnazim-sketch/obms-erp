import { spawn } from 'child_process';
import { writeFileSync } from 'fs';

// Launch headless Chrome
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
  '--headless',
  '--disable-gpu',
  '--remote-debugging-port=9222',
  '--no-first-run',
  '--no-default-browser-check',
  `--user-data-dir=/tmp/chrome_clean_profile_${Date.now()}`
]);

// Wait for Chrome CDP to be available
let versionData = null;
for (let i = 0; i < 15; i++) {
  try {
    const res = await fetch('http://127.0.0.1:9222/json/version');
    versionData = await res.json();
    if (versionData) break;
  } catch (e) {
    await new Promise(r => setTimeout(r, 500));
  }
}
console.log('Chrome CDP ready:', versionData?.Browser);

try {
  const targetsRes = await fetch('http://127.0.0.1:9222/json/list');
  const targets = await targetsRes.json();
  let wsUrl = targets[0]?.webSocketDebuggerUrl;

  if (!wsUrl) {
    const newTargetRes = await fetch('http://127.0.0.1:9222/json/new?http://localhost:4200');
    const newTarget = await newTargetRes.json();
    wsUrl = newTarget.webSocketDebuggerUrl;
  }

  const ws = new WebSocket(wsUrl);

  let idCounter = 1;
  const pending = new Map();
  const logs = [];

  function send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = idCounter++;
      pending.set(id, { resolve, reject });
      ws.send(JSON.stringify({ id, method, params }));
    });
  }

  await new Promise((resolve) => {
    ws.onopen = resolve;
  });

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve } = pending.get(msg.id);
      pending.delete(msg.id);
      resolve(msg.result);
    } else if (msg.method === 'Console.messageAdded') {
      logs.push(`[Console] ${msg.params.message.level}: ${msg.params.message.text}`);
    } else if (msg.method === 'Runtime.consoleAPICalled') {
      const text = msg.params.args.map(a => a.value || JSON.stringify(a)).join(' ');
      logs.push(`[Log ${msg.params.type}] ${text}`);
    } else if (msg.method === 'Runtime.exceptionThrown') {
      logs.push(`[Exception] ${msg.params.exceptionDetails.text} ${msg.params.exceptionDetails.exception?.description || ''}`);
    } else if (msg.method === 'Network.responseReceived') {
      logs.push(`[Network] ${msg.params.response.status} ${msg.params.response.url}`);
    }
  };

  await send('Page.enable');
  await send('Runtime.enable');
  await send('Network.enable');

  console.log('Navigating to http://localhost:4200/#/auth/login ...');
  await send('Page.navigate', { url: 'http://localhost:4200/#/auth/login' });

  // Wait for Angular to bootstrap
  await new Promise(r => setTimeout(r, 4000));

  // Evaluate page status
  const pageState = await send('Runtime.evaluate', {
    expression: `(() => {
      const emailInput = document.querySelector('input[type="email"], input[name="email"], input[formcontrolname="email"]');
      const passInput = document.querySelector('input[type="password"]');
      const submitBtn = document.querySelector('button[type="submit"]');
      return {
        url: window.location.href,
        hasEmail: !!emailInput,
        emailVal: emailInput?.value,
        hasPass: !!passInput,
        hasSubmit: !!submitBtn,
        title: document.title
      };
    })()`,
    returnByValue: true
  });
  console.log('Initial Page State:', pageState.result.value);

  // Now let's fill in credentials and click login
  console.log('Filling in credentials and submitting...');
  const loginEval = await send('Runtime.evaluate', {
    expression: `(() => {
      const emailInput = document.querySelector('input[type="email"], input[name="email"], input[formcontrolname="email"]');
      const passInput = document.querySelector('input[type="password"]');
      const submitBtn = document.querySelector('button[type="submit"]');
      if (emailInput && passInput && submitBtn) {
        emailInput.value = 'admin';
        emailInput.dispatchEvent(new Event('input', { bubbles: true }));
        emailInput.dispatchEvent(new Event('change', { bubbles: true }));

        passInput.value = 'admin123';
        passInput.dispatchEvent(new Event('input', { bubbles: true }));
        passInput.dispatchEvent(new Event('change', { bubbles: true }));

        submitBtn.click();
        return { clicked: true };
      }
      return { clicked: false, error: 'Elements not found' };
    })()`,
    returnByValue: true
  });
  console.log('Submit Action:', loginEval.result.value);

  // Wait 5 seconds to see what happens post-login
  await new Promise(r => setTimeout(r, 5000));

  const postLoginState = await send('Runtime.evaluate', {
    expression: `(() => {
      return {
        url: window.location.href,
        title: document.title,
        bodySnippet: document.body.innerText.substring(0, 300)
      };
    })()`,
    returnByValue: true
  });
  console.log('Post Login State:', postLoginState.result.value);

  // Take screenshot
  const screenshot = await send('Page.captureScreenshot', { format: 'png' });
  writeFileSync('/tmp/post_login.png', Buffer.from(screenshot.data, 'base64'));
  console.log('Screenshot saved to /tmp/post_login.png');

  console.log('\n--- Collected Logs ---');
  logs.forEach(l => console.log(l));

  ws.close();
} catch (err) {
  console.error('Test error:', err);
} finally {
  chrome.kill();
  process.exit(0);
}
