const fs = require('fs');
const path = '/var/www/verdiscan/wallet/index.html';
let content = fs.readFileSync(path, 'utf8');
let fixed = 0;

// Fix specific glued patterns where // comment swallows code
const replacements = [
  // "pathsthrow new Error" -> "paths\nthrow new Error"
  [/\/\/ We'll use a simple sync implementation for non-critical pathsthrow new Error/g, 
   "// We'll use a simple sync implementation for non-critical paths\n  throw new Error"],
  
  // "on-chain transactionsconst RELAY_URL" -> "on-chain transactions\nconst RELAY_URL"
  [/\/\/ TX Relay - signs and submits on-chain transactionsconst RELAY_URL/g,
   "// TX Relay - signs and submits on-chain transactions\nconst RELAY_URL"],
  
  // "non-custodialconst API_URL" -> "non-custodial\nconst API_URL"
  [/\/\/ fetchRelayInfo removed — relay v3 is non-custodialconst API_URL/g,
   "// fetchRelayInfo removed — relay v3 is non-custodial\nconst API_URL"],
  
  // "globallywindow.sha256" -> "globally\nwindow.sha256"
  [/\/\/ Make available globallywindow\.sha256/g,
   "// Make available globally\nwindow.sha256"],
  
  // "successfully');window.__walletModuleReady" -> "successfully');\nwindow.__walletModuleReady"
  [/console\.log\('\[Wallet\] Module script loaded successfully'\);window\.__walletModuleReady/g,
   "console.log('[Wallet] Module script loaded successfully');\nwindow.__walletModuleReady"],
  
  // "blake2b needed)fetchRelayInfo" -> "blake2b needed)\nfetchRelayInfo" (in ss58Encode)
  [/\(no blake2b needed\)fetchRelayInfo/g,
   "(no blake2b needed)"],
  
  // "blake2b needed)Make available" -> "blake2b needed)\n// Make available"
  [/\(no blake2b needed\)Make available/g,
   "(no blake2b needed)"],
  
  // "blake2b needed)TX Relay" -> "blake2b needed)\n// TX Relay"
  [/\(no blake2b needed\)TX Relay/g,
   "(no blake2b needed)"],
  
  // "encoding// ===== SS58 Encoding =====" is just a nested comment, leave it
  
  // "successfully');const" -> "successfully');\nconst"
  [/successfully'\);const/g, "successfully');\nconst"],
  
  // "successfully');let" -> "successfully');\nlet"
  [/successfully'\);let/g, "successfully');\nlet"],
  
  // "0n;// fetchRelayInfo" is OK (let RELAY_BALANCE = 0n; followed by //)
  // But "0n;// fetchRelayInfo removed" needs the const API_URL on next line
  // Already handled above
  
  // "true;// blake2b" is OK (window.__walletModuleReady = true; followed by //)
  // The issue is the NEXT line after the comment
  
  // Handle "}function " without newline
  [/;function /g, ";\nfunction "],
  [/;const /g, ";\nconst "],
  [/;let /g, ";\nlet "],
  [/;var /g, ";\nvar "],
  [/;window\./g, ";\nwindow."],
  [/;async /g, ";\nasync "],
  [/;console\.log/g, ";\nconsole.log"],
  [/;document\./g, ";\ndocument."],
  [/;return /g, ";\nreturn "],
  [/;await /g, ";\nawait "],
  
  // Also split } followed by code (but not in same expression)
  // Only for lines > 200 chars to avoid breaking normal code
];

for (const [pattern, replacement] of replacements) {
  const matches = content.match(pattern);
  if (matches) {
    content = content.replace(pattern, replacement);
    fixed += matches.length;
  }
}

fs.writeFileSync(path, content);
console.log('Fixed ' + fixed + ' glued patterns');
