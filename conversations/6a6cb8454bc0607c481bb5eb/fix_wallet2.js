const fs = require('fs');
const path = '/var/www/verdiscan/wallet/index.html';
let content = fs.readFileSync(path, 'utf8');
let lines = content.split('\n');
let fixed = 0;

// Target lines: 746, 754, 761, 769, 774, 782, 783
const targetLines = [746, 754, 761, 769, 774, 782, 783];

for (const targetLine of targetLines) {
  const idx = targetLine - 1;
  if (idx >= lines.length) continue;
  let line = lines[idx];
  if (line.length < 200) continue;
  
  // Strategy: find // that's not a URL, then find code keywords after it
  let slashPos = -1;
  for (let i = 0; i < line.length; i++) {
    if (line[i] === '/' && line[i+1] === '/') {
      const before = line.substring(Math.max(0, i-5), i);
      if (before.includes('http') || before.includes('ttp:')) continue;
      slashPos = i;
      break;
    }
  }
  
  if (slashPos === -1) continue;
  
  // Find code keywords after the //
  const afterSlash = line.substring(slashPos + 2);
  const codeKeywords = ['function ', 'const ', 'let ', 'var ', 'window.', 'async function', 'async ', 'return ', 'if (', 'document.', 'await ', 'try {', 'try{', 'for (', 'for('];
  
  let splitPos = -1;
  for (let j = 0; j < afterSlash.length; j++) {
    for (const kw of codeKeywords) {
      if (afterSlash.substring(j, j + kw.length) === kw) {
        const beforeKw = afterSlash[j-1];
        if (beforeKw === ' ' || beforeKw === '\t' || j === 0) {
          splitPos = slashPos + 2 + j;
          break;
        }
      }
    }
    if (splitPos !== -1) break;
  }
  
  if (splitPos !== -1) {
    const indent = line.match(/^\s*/)[0];
    const before = line.substring(0, splitPos).trim();
    const after = line.substring(splitPos).trim();
    lines[idx] = before + '\n' + indent + after;
    fixed++;
  }
}

fs.writeFileSync(path, lines.join('\n'));
console.log('Fixed ' + fixed + ' additional broken lines');
console.log('Total lines: ' + lines.length);
