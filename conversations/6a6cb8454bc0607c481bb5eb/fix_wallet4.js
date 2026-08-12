const fs = require('fs');
const path = '/var/www/verdiscan/wallet/index.html';
let content = fs.readFileSync(path, 'utf8');
let lines = content.split('\n');
let totalFixed = 0;

// These specific patterns are known to be broken:
// 1. "=====const " -> split before const
// 2. ")fetchRelayInfo" -> not a keyword, but "non-custodialconst " -> split before const
// 3. "globallywindow." -> split before window.

for (let idx = 0; idx < lines.length; idx++) {
  let line = lines[idx];
  if (line.length < 200) continue;
  
  // Only process lines with // that are not URLs
  if (!line.includes('//')) continue;
  if (line.includes('http://') || line.includes('https://')) {
    // Still might have // comments, but let's be careful
  }
  
  // Find // that's not part of a URL
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
  
  // After the //, find code keywords even WITHOUT a space before them
  const afterSlash = line.substring(slashPos + 2);
  
  // More aggressive patterns - look for keywords even glued to text
  const patterns = [
    /=====const /g,
    /=====const\s/g,
    /non-custodialconst /g,
    /globallywindow\./g,
    /needed\)fetchRelayInfo/g,
    /needed\)Make /g,
    /=====const\b/g,
    /custodialconst\b/g,
    /globallywindow\b/g,
  ];
  
  // Also just find any of these keywords after //
  const codeKws = ['const ', 'let ', 'var ', 'window.', 'function ', 'async ', 'return ', 'await ', 'document.', 'if (', 'try {', 'for ('];
  
  let bestPos = -1;
  
  // Strategy: after the //, find the LAST occurrence of // (nested comment)
  // Then look for code keywords after that
  let lastCommentStart = afterSlash.lastIndexOf('//');
  if (lastCommentStart >= 0) {
    const afterLastComment = afterSlash.substring(lastCommentStart + 2);
    for (const kw of codeKws) {
      let pos = afterLastComment.indexOf(kw);
      if (pos >= 0) {
        // Check if this is really code (not inside the comment text)
        // Heuristic: the keyword should be at the end of some text, not in the middle
        // For our specific cases, the keyword is right after comment text with no space
        let absPos = slashPos + 2 + lastCommentStart + 2 + pos;
        if (bestPos === -1 || absPos < bestPos) {
          bestPos = absPos;
        }
      }
    }
  }
  
  // If no nested //, look for keywords in the entire afterSlash
  if (bestPos === -1) {
    for (const kw of codeKws) {
      let pos = afterSlash.indexOf(kw);
      if (pos >= 0) {
        // Make sure it's not part of a URL
        let absPos = slashPos + 2 + pos;
        if (bestPos === -1 || absPos < bestPos) {
          bestPos = absPos;
        }
      }
    }
  }
  
  if (bestPos !== -1) {
    const indent = line.match(/^\s*/)[0];
    const before = line.substring(0, bestPos).trim();
    const after = line.substring(bestPos).trim();
    lines[idx] = before + '\n' + indent + after;
    totalFixed++;
  }
}

// Re-join and re-split to handle newlines
lines = lines.join('\n').split('\n');

// Second pass for any remaining
for (let idx = 0; idx < lines.length; idx++) {
  let line = lines[idx];
  if (line.length < 200) continue;
  if (!line.includes('//')) continue;
  
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
  const codeKws = ['const ', 'let ', 'var ', 'window.', 'function ', 'async ', 'return ', 'await ', 'document.', 'if (', 'try {', 'for ('];
  
  let bestPos = -1;
  for (const kw of codeKws) {
    let pos = afterSlash.indexOf(kw);
    if (pos >= 0) {
      let absPos = slashPos + 2 + pos;
      if (bestPos === -1 || absPos < bestPos) {
        bestPos = absPos;
      }
    }
  }
  
  if (bestPos !== -1 && bestPos > slashPos + 10) {
    const indent = line.match(/^\s*/)[0];
    const before = line.substring(0, bestPos).trim();
    const after = line.substring(bestPos).trim();
    lines[idx] = before + '\n' + indent + after;
    totalFixed++;
  }
}

lines = lines.join('\n').split('\n');

fs.writeFileSync(path, lines.join('\n'));
console.log('Total fixed: ' + totalFixed + ', total lines: ' + lines.length);
