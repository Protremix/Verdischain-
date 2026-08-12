const fs = require('fs');
const path = '/var/www/verdiscan/wallet/index.html';
let content = fs.readFileSync(path, 'utf8');
let lines = content.split('\n');

let totalFixed = 0;
let pass = 0;

while (pass < 10) {
  pass++;
  let fixedThisPass = 0;
  
  for (let idx = 0; idx < lines.length; idx++) {
    let line = lines[idx];
    if (line.length < 200) continue;
    
    if (!/\/\/.*(function |const |let |var |window\.|async |return |if \(|document\.|await )/.test(line)) continue;
    
    let slashPos = -1;
    for (let i = 0; i < line.length; i++) {
      if (line[i] === '/' && i + 1 < line.length && line[i + 1] === '/') {
        const before = line.substring(Math.max(0, i - 5), i);
        if (before.includes('http') || before.includes('ttp:')) continue;
        slashPos = i;
        break;
      }
    }
    
    if (slashPos === -1) continue;
    
    const afterSlash = line.substring(slashPos + 2);
    const codeKeywords = ['function ', 'const ', 'let ', 'var ', 'window.', 'async function', 'async ', 'return ', 'if (', 'document.', 'await ', 'try {', 'try{', 'for (', 'for('];
    
    let splitPos = -1;
    for (let j = 0; j < afterSlash.length; j++) {
      for (const kw of codeKeywords) {
        if (afterSlash.substring(j, j + kw.length) === kw) {
          const beforeKw = afterSlash[j - 1];
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
      fixedThisPass++;
      totalFixed++;
    }
  }
  
  lines = lines.join('\n').split('\n');
  if (fixedThisPass === 0) break;
  console.log('Pass ' + pass + ': fixed ' + fixedThisPass + ' lines');
}

fs.writeFileSync(path, lines.join('\n'));
console.log('Total fixed: ' + totalFixed + ', total lines: ' + lines.length);
