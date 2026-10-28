import { spawn } from 'child_process';
import { writeFileSync } from 'fs';

const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
  '--headless',
  '--disable-gpu',
  '--window-size=1440,900',
  '--remote-debugging-port=9222',
  '--no-first-run',
  '--no-default-browser-check',
  '--user-data-dir=/tmp/chrome_test_profile'
]);

await new Promise(r => setTimeout(r, 1500));

try {
  const targetsRes = await fetch('http://127.0.0.1:9222/json/list');
  const targets = await targetsRes.json();
  const wsUrl = targets[0]?.webSocketDebuggerUrl;

  const ws = new WebSocket(wsUrl);
  let id = 1;
  const pending = new Map();
  const logs = [];

  function send(method, params = {}) {
    return new Promise((resolve) => {
      const curId = id++;
      pending.set(curId, resolve);
      ws.send(JSON.stringify({ id: curId, method, params }));
    });
  }

  await new Promise(r => ws.onopen = r);

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.id && pending.has(msg.id)) {
      pending.get(msg.id)(msg.result);
      pending.delete(msg.id);
    } else if (msg.method === 'Runtime.consoleAPICalled') {
      const text = msg.params.args.map(a => a.value || JSON.stringify(a)).join(' ');
      logs.push(`[Console ${msg.params.type}] ${text}`);
    } else if (msg.method === 'Runtime.exceptionThrown') {
      logs.push(`[Exception] ${msg.params.exceptionDetails.text} ${msg.params.exceptionDetails.exception?.description || ''}`);
    }
  };

  await send('Page.enable');
  await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', {
    width: 1440,
    height: 900,
    deviceScaleFactor: 1,
    mobile: false
  });

  console.log('Navigating to dashboard...');
  await send('Page.navigate', { url: 'http://localhost:4200/#/pages/dashboard' });

  await new Promise(r => setTimeout(r, 6000));

  const diag = await send('Runtime.evaluate', {
    expression: `(() => {
      const spinner = document.getElementById('nb-global-spinner');
      const body = document.body;
      const gaApp = document.querySelector('ga-app');
      const layout = document.querySelector('nb-layout');
      const header = document.querySelector('ngx-header, nb-layout-header');
      const sidebar = document.querySelector('nb-sidebar');
      const main = document.querySelector('nb-layout-column');

      function getInfo(el) {
        if (!el) return null;
        const rect = el.getBoundingClientRect();
        const style = window.getComputedStyle(el);
        return {
          tag: el.tagName,
          rect: { top: rect.top, left: rect.left, width: rect.width, height: rect.height },
          display: style.display,
          visibility: style.visibility,
          opacity: style.opacity,
          zIndex: style.zIndex,
          background: style.backgroundColor,
          color: style.color
        };
      }

      // Check what element is at (200, 200), (700, 400), (50, 50)
      const elAtCenter = document.elementFromPoint(700, 400);
      const elAtSidebar = document.elementFromPoint(100, 200);
      const elAtHeader = document.elementFromPoint(300, 30);

      // Check all overlay elements or fixed position elements
      const allFixed = Array.from(document.querySelectorAll('*')).filter(el => {
        const s = window.getComputedStyle(el);
        return (s.position === 'fixed' || s.position === 'absolute') && (s.zIndex > 100 || s.width === '100%');
      }).map(el => ({
        tag: el.tagName,
        id: el.id,
        className: el.className,
        styleZIndex: window.getComputedStyle(el).zIndex,
        rect: el.getBoundingClientRect(),
        bg: window.getComputedStyle(el).backgroundColor
      })).slice(0, 10);

      return {
        url: window.location.href,
        spinnerInfo: getInfo(spinner),
        bodyStyle: {
          bg: window.getComputedStyle(body).backgroundColor,
          color: window.getComputedStyle(body).color,
          height: body.offsetHeight,
          width: body.offsetWidth
        },
        gaApp: getInfo(gaApp),
        layout: getInfo(layout),
        header: getInfo(header),
        sidebar: getInfo(sidebar),
        main: getInfo(main),
        atCenter: elAtCenter ? { tag: elAtCenter.tagName, id: elAtCenter.id, class: elAtCenter.className } : null,
        atSidebar: elAtSidebar ? { tag: elAtSidebar.tagName, id: elAtSidebar.id, class: elAtSidebar.className } : null,
        atHeader: elAtHeader ? { tag: elAtHeader.tagName, id: elAtHeader.id, class: elAtHeader.className } : null,
        allFixed
      };
    })()`,
    returnByValue: true
  });

  console.log('Diagnostic result:', JSON.stringify(diag.result.value, null, 2));

  // Take screenshot with full window size
  const ss = await send('Page.captureScreenshot', { format: 'png' });
  writeFileSync('/tmp/dashboard_1440.png', Buffer.from(ss.data, 'base64'));
  console.log('Saved /tmp/dashboard_1440.png');

  console.log('Console logs:');
  logs.forEach(l => console.log(l));

  ws.close();
} catch (e) {
  console.error(e);
} finally {
  chrome.kill();
  process.exit(0);
}
