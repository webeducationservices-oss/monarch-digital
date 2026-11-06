#!/usr/bin/env node
// Device-accurate screenshots through the Chrome DevTools Protocol (no npm packages).
//   node _build/shot.mjs <url> <out.png> [width=390] [mobile=1]
// Prints any elements wider than the viewport, so horizontal overflow is caught early.
import { spawn } from "node:child_process";
import { writeFileSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const [url, out, w = "390", mobile = "1"] = process.argv.slice(2);
const width = Number(w);
const isMobile = mobile === "1";
const port = 9300 + Math.floor(Math.random() * 500);
const chrome = spawn("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", [
  "--headless=new", "--disable-gpu", "--hide-scrollbars", `--remote-debugging-port=${port}`,
  `--user-data-dir=${mkdtempSync(join(tmpdir(), "shot-"))}`, "about:blank",
], { stdio: "ignore" });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let target;
for (let i = 0; i < 50 && !target; i++) {
  await sleep(200);
  try { target = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find((t) => t.type === "page"); } catch {}
}
if (!target) { chrome.kill(); throw new Error("Chrome did not start"); }

const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r, { once: true }));
let id = 0;
const pending = new Map();
const events = [];
ws.addEventListener("message", (m) => {
  const msg = JSON.parse(m.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); } else if (msg.method) events.push(msg.method);
});
const send = (method, params = {}) => new Promise((r) => { const n = ++id; pending.set(n, r); ws.send(JSON.stringify({ id: n, method, params })); });

await send("Page.enable");
await send("Emulation.setDeviceMetricsOverride", { width, height: isMobile ? 844 : 900, deviceScaleFactor: isMobile ? 2 : 1, mobile: isMobile });
if (isMobile) await send("Emulation.setUserAgentOverride", { userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1" });
await send("Page.navigate", { url });
for (let i = 0; i < 100 && !events.includes("Page.loadEventFired"); i++) await sleep(150);
await sleep(3200); // let the reveal failsafe and fonts settle

const report = await send("Runtime.evaluate", { returnByValue: true, expression: `(() => {
  const vw = document.documentElement.clientWidth, out = [];
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect();
    if (r.width && r.right > vw + 1 && getComputedStyle(el).position !== 'fixed') {
      out.push((el.className && el.className.baseVal === undefined ? '.' + String(el.className).split(' ').join('.') : el.tagName) + ' right=' + Math.round(r.right));
    }
  }
  return { vw, scrollWidth: document.documentElement.scrollWidth, height: document.documentElement.scrollHeight, offenders: [...new Set(out)].slice(0, 12) };
})()` });
const info = report.result.result.value;
await send("Emulation.setDeviceMetricsOverride", { width, height: Math.min(info.height, 16000), deviceScaleFactor: isMobile ? 2 : 1, mobile: isMobile });
await sleep(800);
const shot = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true });
writeFileSync(out, Buffer.from(shot.result.data, "base64"));
console.log(JSON.stringify(info));
ws.close();
chrome.kill();
