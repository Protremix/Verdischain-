const fs = require('fs');
const path = '/var/www/verdiscan/wallet/index.html';
let content = fs.readFileSync(path, 'utf8');
let fixed = 0;

// Find all lines with // comments that swallow code keywords
// Pattern: // some comment text <keyword>...
// We need to insert a newline before the keyword

const codeKeywords = [
  'window\\.', 'function\\s', 'const\\s', 'let\\s', 'var\\s', 
  'async\\s', 'await\\s', 'return\\s', 'throw\\s', 
  'if\\s*\\(', 'else\\s', 'for\\s*\\(', 'while\\s*\\(',
  'document\\.', 'console\\.', 'navigator\\.',
  'try\\s*{', 'catch\\s*\\(', 'finally\\s*{',
  'switch\\s*\\(', 'case\\s', 'break\\s*;', 'continue\\s*;',
  'new\\s+\\w', 'typeof\\s', 'delete\\s', 'void\\s',
  'this\\.', 'super\\.', 'class\\s', 'extends\\s',
  'import\\s', 'export\\s', 'default\\s',
];

// Build a combined regex: // followed by non-newline chars, then a code keyword
// We need to be careful not to match URLs (http://) or string literals
// Strategy: for each line, find // that's not inside a string, then check if code keywords follow

const lines = content.split('\n');
const newLines = [];

for (let i = 0; i < lines.length; i++) {
  let line = lines[i];
  
  // Skip lines that are too short to have the problem
  if (line.length < 100) {
    newLines.push(line);
    continue;
  }
  
  // Find // that's not inside a string literal
  // Simple heuristic: find // that's not preceded by a quote
  // For long lines (>100 chars), check if there are code keywords after //
  
  let modified = false;
  let result = '';
  let pos = 0;
  
  while (pos < line.length) {
    // Find next // 
    let commentStart = line.indexOf('//', pos);
    
    if (commentStart === -1) {
      result += line.substring(pos);
      break;
    }
    
    // Check if this // is inside a string literal
    // Simple check: count quotes before this position
    const before = line.substring(0, commentStart);
    const singleQuotes = (before.match(/'/g) || []).length;
    const doubleQuotes = (before.match(/"/g) || []).length;
    const backtickQuotes = (before.match(/`/g) || []).length;
    
    // If odd number of quotes, we're inside a string - skip
    if (singleQuotes % 2 === 1 || doubleQuotes % 2 === 1 || backtickQuotes % 2 === 1) {
      result += line.substring(pos, commentStart + 2);
      pos = commentStart + 2;
      continue;
    }
    
    // Check if this is a URL (http:// or https://)
    if (commentStart > 0 && line[commentStart - 1] === ':') {
      result += line.substring(pos, commentStart + 2);
      pos = commentStart + 2;
      continue;
    }
    
    // Found a real // comment. Get everything after it on this line
    const afterComment = line.substring(commentStart + 2);
    
    // Check if any code keywords appear in the comment text
    let keywordMatch = null;
    let keywordPos = -1;
    
    for (const kw of codeKeywords) {
      const re = new RegExp(kw);
      const m = re.exec(afterComment);
      if (m && (keywordPos === -1 || m.index < keywordPos)) {
        keywordMatch = m;
        keywordPos = m.index;
      }
    }
    
    if (keywordMatch && keywordPos >= 0) {
      // The comment text before the keyword stays as a comment
      // The keyword and everything after goes on a new line
      const commentText = afterComment.substring(0, keywordPos);
      const codeText = afterComment.substring(keywordPos);
      
      // Add everything up to and including the //
      result += line.substring(pos, commentStart + 2);
      // Add the comment text (stays as comment)
      result += commentText;
      // Add newline and the swallowed code
      result += '\n' + codeText;
      
      pos = line.length; // Done with this line
      modified = true;
      fixed++;
    } else {
      // No code keyword found in comment - keep as is
      result += line.substring(pos, commentStart + 2);
      pos = commentStart + 2;
    }
  }
  
  newLines.push(result);
}

content = newLines.join('\n');
fs.writeFileSync(path, content);
console.log('Fixed ' + fixed + ' lines with swallowed code keywords');

// Verify: check for remaining patterns
const remaining = lines.filter(l => l.length > 100).filter(l => {
  const m = l.match(/\/\/.*(?:window\.|function |const |let |async |return |throw |if \(|else |document\.|console\.)/);
  return m && !l.includes('http://') && !l.includes('https://');
});
console.log('Remaining long lines with potential issues: ' + remaining.length);
