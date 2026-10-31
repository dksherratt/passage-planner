const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [svgPath, outPath, mockPath] = process.argv.slice(2);
  const svg = fs.readFileSync(svgPath, 'utf8');
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1100, height: 1400 } });
  await p.setContent(`<html><body style="margin:0">${svg}</body></html>`);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  await p.screenshot({ path: outPath, clip: { x: 0, y: 0, width: 1100, height: 1400 } });

  // pouch mockup
  const art = fs.readFileSync(outPath).toString('base64');
  const mock = `<html><body style="margin:0;background:radial-gradient(ellipse at 50% 35%,#5a5a5e,#2a2a2d 75%)">
  <svg xmlns="http://www.w3.org/2000/svg" width="1300" height="1600" viewBox="0 0 1300 1600">
   <defs>
    <clipPath id="pouch"><path d="M120,120 Q120,100 140,100 L1160,100 Q1180,100 1180,120 L1185,1380 Q1185,1450 1120,1455 Q650,1475 180,1455 Q115,1450 115,1380 Z"/></clipPath>
    <linearGradient id="sheen" x1="0" x2="1">
     <stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset=".07" stop-color="#fff" stop-opacity=".10"/>
     <stop offset=".18" stop-color="#000" stop-opacity="0"/><stop offset=".72" stop-color="#fff" stop-opacity=".06"/>
     <stop offset=".93" stop-color="#000" stop-opacity=".15"/><stop offset="1" stop-color="#000" stop-opacity=".6"/></linearGradient>
    <linearGradient id="vert" x1="0" y1="0" x2="0" y2="1">
     <stop offset="0" stop-color="#fff" stop-opacity=".10"/><stop offset=".2" stop-color="#fff" stop-opacity="0"/>
     <stop offset=".85" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></linearGradient>
    <filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="22"/></filter>
    <filter id="crinkle"><feTurbulence type="fractalNoise" baseFrequency="0.004 0.02" numOctaves="3" seed="4"/>
     <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .5 -.18"/></filter>
   </defs>
   <ellipse cx="650" cy="1480" rx="560" ry="38" fill="#000" opacity=".55" filter="url(#sh)"/>
   <g clip-path="url(#pouch)">
    <image href="data:image/png;base64,${art}" x="105" y="70" width="1100" height="1400" preserveAspectRatio="none"/>
    <rect x="0" y="0" width="1300" height="1600" filter="url(#crinkle)" opacity=".35"/>
    <rect x="100" y="90" width="1100" height="1380" fill="url(#sheen)"/>
    <rect x="100" y="90" width="1100" height="1380" fill="url(#vert)"/>
    <rect x="100" y="100" width="1100" height="70" fill="#000" opacity=".18"/>
    <line x1="120" y1="200" x2="1180" y2="200" stroke="#000" stroke-opacity=".35" stroke-width="5"/>
    <line x1="120" y1="205" x2="1180" y2="205" stroke="#fff" stroke-opacity=".12" stroke-width="2"/>
    <line x1="120" y1="222" x2="1180" y2="222" stroke="#000" stroke-opacity=".3" stroke-width="4"/>
   </g>
  </svg></body></html>`;
  await p.setViewportSize({ width: 1300, height: 1600 });
  await p.setContent(mock);
  await p.waitForTimeout(300);
  await p.screenshot({ path: mockPath });
  await b.close();
})();
