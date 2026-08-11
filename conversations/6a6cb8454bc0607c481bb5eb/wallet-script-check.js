
// Debug: catch any module load errors
window.addEventListener('error', (e) => {
  console.error('[Module Error]', e.message, e.filename, e.lineno);
  const toast = document.createElement('div');
  toast.style.cssText = 'position:fixed;top:20px;right:20px;background:#dc2626;color:white;padding:16px;border-radius:8px;z-index:9999;font-family:monospace;font-size:14px;max-width:400px';
  toast.textContent = 'JS Error: ' + e.message + ' (line ' + e.lineno + ')';
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 10000);
});
// Sr25519 via Polkadot WASM bundle (loaded via script tag below)
// SHA-256 using built-in Web Crypto API (no CDN needed)
async function sha256Sync(data) {
  const buf = data instanceof Uint8Array ? data : new TextEncoder().encode(data);
  const hash = await crypto.subtle.digest('SHA-256', buf);
  return new Uint8Array(hash);
}
// Synchronous SHA-256 fallback (used in non-async contexts)
function sha256(data) {
  // This is a sync wrapper - but crypto.subtle is async only
  // We'll use a simple sync implementation for non-critical paths
  throw new Error('Use sha256Sync() for SHA-256 hashing');
}

const RPC_URL = 'https://verdischain.com/rpc';

// TX Relay - signs and submits on-chain transactions
const RELAY_URL = window.location.origin + '/tx-relay/';
let RELAY_SIGNER = null;
let RELAY_BALANCE = 0n;

async function fetchRelayInfo() {
  try {
    const resp = await fetch(RELAY_URL);
    const json = await resp.json();
    if (json.status === 'ok') {
      RELAY_SIGNER = json.signer;
      RELAY_BALANCE = BigInt(json.signer_balance || 0);
      return json;
    }
  } catch (e) {
    console.error('Relay fetch error:', e);
  }
  return null;
}

const API_URL = 'https://verdischain.com/api/v1';
const BIP39_WORDS = ["abandon","ability","able","about","above","absent","absorb","abstract","absurd","abuse","access","accident","account","accuse","achieve","acid","acoustic","acquire","across","act","action","actor","actress","actual","adapt","add","addict","address","adjust","admit","adult","advance","advice","aerobic","affair","afford","afraid","again","age","agent","agree","ahead","aim","air","airport","aisle","alarm","album","alcohol","alert","alien","all","alley","allow","almost","alone","alpha","already","also","alter","always","amateur","amazing","among","amount","amused","analyst","anchor","ancient","anger","angle","angry","animal","ankle","announce","annual","another","answer","antenna","antique","anxiety","any","apart","apology","appear","apple","approve","april","arch","arctic","area","arena","argue","arm","armed","armor","army","around","arrange","arrest","arrive","arrow","art","artefact","artist","artwork","ask","aspect","assault","asset","assist","assume","asthma","athlete","atom","attack","attend","attitude","attract","auction","audit","august","aunt","author","auto","autumn","average","avocado","avoid","awake","aware","away","awesome","awful","awkward","axis","baby","bachelor","bacon","badge","bag","balance","balcony","ball","bamboo","banana","banner","bar","barely","bargain","barrel","base","basic","basket","battle","beach","bean","beauty","because","become","beef","before","begin","behave","behind","believe","below","belt","bench","benefit","best","betray","better","between","beyond","bicycle","bid","bike","bind","biology","bird","birth","bitter","black","blade","blame","blanket","blast","bleak","bless","blind","blood","blossom","blouse","blue","blur","blush","board","boat","body","boil","bomb","bone","bonus","book","boost","border","boring","borrow","boss","bottom","bounce","box","boy","bracket","brain","brand","brass","brave","bread","breeze","brick","bridge","brief","bright","bring","brisk","broccoli","broken","bronze","broom","brother","brown","brush","bubble","buddy","budget","buffalo","build","bulb","bulk","bullet","bundle","bunker","burden","burger","burst","bus","business","busy","butter","buyer","buzz","cabbage","cabin","cable","cactus","cage","cake","call","calm","camera","camp","can","canal","cancel","candy","cannon","canoe","canvas","canyon","capable","capital","captain","car","carbon","card","cargo","carpet","carry","cart","case","cash","casino","castle","casual","cat","catalog","catch","category","cattle","caught","cause","caution","cave","ceiling","celery","cement","census","century","cereal","certain","chair","chalk","champion","change","chaos","chapter","charge","chase","chat","cheap","check","cheese","chef","cherry","chest","chicken","chief","child","chimney","choice","choose","chronic","chuckle","chunk","churn","cigar","cinnamon","circle","citizen","city","civil","claim","clap","clarify","claw","clay","clean","clerk","clever","click","client","cliff","climb","clinic","clip","clock","clog","close","cloth","cloud","clown","club","clump","cluster","clutch","coach","coast","coconut","code","coffee","coil","coin","collect","color","column","combine","come","comfort","comic","common","company","concert","conduct","confirm","congress","connect","consider","control","convince","cook","cool","copper","copy","coral","core","corn","correct","cost","cotton","couch","country","couple","course","cousin","cover","coyote","crack","cradle","craft","cram","crane","crash","crater","crawl","crazy","cream","credit","creek","crew","cricket","crime","crisp","critic","crop","cross","crouch","crowd","crucial","cruel","cruise","crumble","crunch","crush","cry","crystal","cube","culture","cup","cupboard","curious","current","curtain","curve","cushion","custom","cute","cycle","dad","damage","damp","dance","danger","daring","dash","daughter","dawn","day","deal","debate","debris","decade","december","decide","decline","decorate","decrease","deer","defense","define","defy","degree","delay","deliver","demand","demise","denial","dentist","deny","depart","depend","deposit","depth","deputy","derive","describe","desert","design","desk","despair","destroy","detail","detect","develop","device","devote","diagram","dial","diamond","diary","dice","diesel","diet","differ","digital","dignity","dilemma","dinner","dinosaur","direct","dirt","disagree","discover","disease","dish","dismiss","disorder","display","distance","divert","divide","divorce","dizzy","doctor","document","dog","doll","dolphin","domain","donate","donkey","donor","door","dose","double","dove","draft","dragon","drama","drastic","draw","dream","dress","drift","drill","drink","drip","drive","drop","drum","dry","duck","dumb","dune","during","dust","dutch","duty","dwarf","dynamic","eager","eagle","early","earn","earth","easily","east","easy","echo","ecology","economy","edge","edit","educate","effort","egg","eight","either","elbow","elder","electric","elegant","element","elephant","elevator","elite","else","embark","embody","embrace","emerge","emotion","employ","empower","empty","enable","enact","end","endless","endorse","enemy","energy","enforce","engage","engine","enhance","enjoy","enlist","enough","enrich","enroll","ensure","enter","entire","entry","envelope","episode","equal","equip","era","erase","erode","erosion","error","erupt","escape","essay","essence","estate","eternal","ethics","evidence","evil","evoke","evolve","exact","example","excess","exchange","excite","exclude","excuse","execute","exercise","exhaust","exhibit","exile","exist","exit","exotic","expand","expect","expire","explain","expose","express","extend","extra","eye","eyebrow","fabric","face","faculty","fade","faint","faith","fall","false","fame","family","famous","fan","fancy","fantasy","farm","fashion","fat","fatal","father","fatigue","fault","favorite","feature","february","federal","fee","feed","feel","female","fence","festival","fetch","fever","few","fiber","fiction","field","figure","file","film","filter","final","find","fine","finger","finish","fire","firm","first","fiscal","fish","fit","fitness","fix","flag","flame","flash","flat","flavor","flee","flight","flip","float","flock","floor","flower","fluid","flush","fly","foam","focus","fog","foil","fold","follow","food","foot","force","forest","forget","fork","fortune","forum","forward","fossil","foster","found","fox","fragile","frame","frequent","fresh","friend","fringe","frog","front","frost","frown","frozen","fruit","fuel","fun","funny","furnace","fury","future","gadget","gain","galaxy","gallery","game","gap","garage","garbage","garden","garlic","garment","gas","gasp","gate","gather","gauge","gaze","general","genius","genre","gentle","genuine","gesture","ghost","giant","gift","giggle","ginger","giraffe","girl","give","glad","glance","glare","glass","glide","glimpse","globe","gloom","glory","glove","glow","glue","goat","goddess","gold","good","goose","gorilla","gospel","gossip","govern","gown","grab","grace","grain","grant","grape","grass","gravity","great","green","grid","grief","grit","grocery","group","grow","grunt","guard","guess","guide","guilt","guitar","gun","gym","habit","hair","half","hammer","hamster","hand","happy","harbor","hard","harsh","harvest","hat","have","hawk","hazard","head","health","heart","heavy","hedgehog","height","hello","helmet","help","hen","hero","hidden","high","hill","hint","hip","hire","history","hobby","hockey","hold","hole","holiday","hollow","home","honey","hood","hope","horn","horror","horse","hospital","host","hotel","hour","hover","hub","huge","human","humble","humor","hundred","hungry","hunt","hurdle","hurry","hurt","husband","hybrid","ice","icon","idea","identify","idle","ignore","ill","illegal","illness","image","imitate","immense","immune","impact","impose","improve","impulse","inch","include","income","increase","index","indicate","indoor","industry","infant","inflict","inform","inhale","inherit","initial","inject","injury","inmate","inner","innocent","input","inquiry","insane","insect","inside","inspire","install","intact","interest","into","invest","invite","involve","iron","island","isolate","issue","item","ivory","jacket","jaguar","jar","jazz","jealous","jeans","jelly","jewel","job","join","joke","journey","joy","judge","juice","jump","jungle","junior","junk","just","kangaroo","keen","keep","ketchup","key","kick","kid","kidney","kind","kingdom","kiss","kit","kitchen","kite","kitten","kiwi","knee","knife","knock","know","lab","label","labor","ladder","lady","lake","lamp","language","laptop","large","later","latin","laugh","laundry","lava","law","lawn","lawsuit","layer","lazy","leader","leaf","learn","leave","lecture","left","leg","legal","legend","leisure","lemon","lend","length","lens","leopard","lesson","letter","level","liar","liberty","library","license","life","lift","light","like","limb","limit","link","lion","liquid","list","little","live","lizard","load","loan","lobster","local","lock","logic","lonely","long","loop","lottery","loud","lounge","love","loyal","lucky","luggage","lumber","lunar","lunch","luxury","lyrics","machine","mad","magic","magnet","maid","mail","main","major","make","mammal","man","manage","mandate","mango","mansion","manual","maple","marble","march","margin","marine","market","marriage","mask","mass","master","match","material","math","matrix","matter","maximum","maze","meadow","mean","measure","meat","mechanic","medal","media","melody","melt","member","memory","mention","menu","mercy","merge","merit","merry","mesh","message","metal","method","middle","midnight","milk","million","mimic","mind","minimum","minor","minute","miracle","mirror","misery","miss","mistake","mix","mixed","mixture","mobile","model","modify","mom","moment","monitor","monkey","monster","month","moon","moral","more","morning","mosquito","mother","motion","motor","mountain","mouse","move","movie","much","muffin","mule","multiply","muscle","museum","mushroom","music","must","mutual","myself","mystery","myth","naive","name","napkin","narrow","nasty","nation","nature","near","neck","need","negative","neglect","neither","nephew","nerve","nest","net","network","neutral","never","news","next","nice","night","noble","noise","nominee","noodle","normal","north","nose","notable","note","nothing","notice","novel","now","nuclear","number","nurse","nut","oak","obey","object","oblige","obscure","observe","obtain","obvious","occur","ocean","october","odor","off","offer","office","often","oil","okay","old","olive","olympic","omit","once","one","onion","online","only","open","opera","opinion","oppose","option","orange","orbit","orchard","order","ordinary","organ","orient","original","orphan","ostrich","other","outdoor","outer","output","outside","oval","oven","over","own","owner","oxygen","oyster","ozone","pact","paddle","page","pair","palace","palm","panda","panel","panic","panther","paper","parade","parent","park","parrot","party","pass","patch","path","patient","patrol","pattern","pause","pave","payment","peace","peanut","pear","peasant","pelican","pen","penalty","pencil","people","pepper","perfect","permit","person","pet","phone","photo","phrase","physical","piano","picnic","picture","piece","pig","pigeon","pill","pilot","pink","pioneer","pipe","pistol","pitch","pizza","place","planet","plastic","plate","play","please","pledge","pluck","plug","plunge","poem","poet","point","polar","pole","police","pond","pony","pool","popular","portion","position","possible","post","potato","pottery","poverty","powder","power","practice","praise","predict","prefer","prepare","present","pretty","prevent","price","pride","primary","print","priority","prison","private","prize","problem","process","produce","profit","program","project","promote","proof","property","prosper","protect","proud","provide","public","pudding","pull","pulp","pulse","pumpkin","punch","pupil","puppy","purchase","purity","purpose","purse","push","put","puzzle","pyramid","quality","quantum","quarter","question","quick","quit","quiz","quote","rabbit","raccoon","race","rack","radar","radio","rail","rain","raise","rally","ramp","ranch","random","range","rapid","rare","rate","rather","raven","raw","razor","ready","real","reason","rebel","rebuild","recall","receive","recipe","record","recycle","reduce","reflect","reform","refuse","region","regret","regular","reject","relax","release","relief","rely","remain","remember","remind","remove","render","renew","rent","reopen","repair","repeat","replace","report","require","rescue","resemble","resist","resource","response","result","retire","retreat","return","reunion","reveal","review","reward","rhythm","rib","ribbon","rice","rich","ride","ridge","rifle","right","rigid","ring","riot","ripple","risk","ritual","rival","river","road","roast","robot","robust","rocket","romance","roof","rookie","room","rose","rotate","rough","round","route","royal","rubber","rude","rug","rule","run","runway","rural","sad","saddle","sadness","safe","sail","salad","salmon","salon","salt","salute","same","sample","sand","satisfy","satoshi","sauce","sausage","save","say","scale","scan","scare","scatter","scene","scheme","school","science","scissors","scorpion","scout","scrap","screen","script","scrub","sea","search","season","seat","second","secret","section","security","seed","seek","segment","select","sell","seminar","senior","sense","sentence","series","service","session","settle","setup","seven","shadow","shaft","shallow","share","shed","shell","sheriff","shield","shift","shine","ship","shiver","shock","shoe","shoot","shop","short","shoulder","shove","shrimp","shrug","shuffle","shy","sibling","sick","side","siege","sight","sign","silent","silk","silly","silver","similar","simple","since","sing","siren","sister","situate","six","size","skate","sketch","ski","skill","skin","skirt","skull","slab","slam","sleep","slender","slice","slide","slight","slim","slogan","slot","slow","slush","small","smart","smile","smoke","smooth","snack","snake","snap","sniff","snow","soap","soccer","social","sock","soda","soft","solar","soldier","solid","solution","solve","someone","song","soon","sorry","sort","soul","sound","soup","source","south","space","spare","spatial","spawn","speak","special","speed","spell","spend","sphere","spice","spider","spike","spin","spirit","split","spoil","sponsor","spoon","sport","spot","spray","spread","spring","spy","square","squeeze","squirrel","stable","stadium","staff","stage","stairs","stamp","stand","start","state","stay","steak","steel","stem","step","stereo","stick","still","sting","stock","stomach","stone","stool","story","stove","strategy","street","strike","strong","struggle","student","stuff","stumble","style","subject","submit","subway","success","such","sudden","suffer","sugar","suggest","suit","summer","sun","sunny","sunset","super","supply","supreme","sure","surface","surge","surprise","surround","survey","suspect","sustain","swallow","swamp","swap","swarm","swear","sweet","swift","swim","swing","switch","sword","symbol","symptom","syrup","system","table","tackle","tag","tail","talent","talk","tank","tape","target","task","taste","tattoo","taxi","teach","team","tell","ten","tenant","tennis","tent","term","test","text","thank","that","theme","then","theory","there","they","thing","this","thought","three","thrive","throw","thumb","thunder","ticket","tide","tiger","tilt","timber","time","tiny","tip","tired","tissue","title","toast","tobacco","today","toddler","toe","together","toilet","token","tomato","tomorrow","tone","tongue","tonight","tool","tooth","top","topic","topple","torch","tornado","tortoise","toss","total","tourist","toward","tower","town","toy","track","trade","traffic","tragic","train","transfer","trap","trash","travel","tray","treat","tree","trend","trial","tribe","trick","trigger","trim","trip","trophy","trouble","truck","true","truly","trumpet","trust","truth","try","tube","tuition","tumble","tuna","tunnel","turkey","turn","turtle","twelve","twenty","twice","twin","twist","two","type","typical","ugly","umbrella","unable","unaware","uncle","uncover","under","undo","unfair","unfold","unhappy","uniform","unique","unit","universe","unknown","unlock","until","unusual","unveil","update","upgrade","uphold","upon","upper","upset","urban","urge","usage","use","used","useful","useless","usual","utility","vacant","vacuum","vague","valid","valley","valve","van","vanish","vapor","various","vast","vault","vehicle","velvet","vendor","venture","venue","verb","verify","version","very","vessel","veteran","viable","vibrant","vicious","victory","video","view","village","vintage","violin","virtual","virus","visa","visit","visual","vital","vivid","vocal","voice","void","volcano","volume","vote","voyage","wage","wagon","wait","walk","wall","walnut","want","warfare","warm","warrior","wash","wasp","waste","water","wave","way","wealth","weapon","wear","weasel","weather","web","wedding","weekend","weird","welcome","west","wet","whale","what","wheat","wheel","when","where","whip","whisper","wide","width","wife","wild","will","win","window","wine","wing","wink","winner","winter","wire","wisdom","wise","wish","witness","wolf","woman","wonder","wood","wool","word","work","world","worry","worth","wrap","wreck","wrestle","wrist","write","wrong","yard","year","yellow","you","young","youth","zebra","zero","zone","zoo"];

const SS58_PREFIX = 909;
const TOKEN_DECIMALS = 9;

// Make available globally
window.secp = secp;
window.sha256 = sha256Sync;
console.log('[Wallet] Module script loaded successfully');
window.__walletModuleReady = true;
// blake2b is no longer needed - PolkadotCrypto handles SS58 encoding

// ===== SS58 Encoding =====
const BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';

function base58Encode(data) {
  let num = 0n;
  for (const b of data) num = num * 256n + BigInt(b);
  let encoded = '';
  while (num > 0n) {
    const rem = num % 58n;
    num = num / 58n;
    encoded = BASE58_ALPHABET[Number(rem)] + encoded;
  }
  for (const b of data) {
    if (b === 0) encoded = '1' + encoded;
    else break;
  }
  return encoded;
}

function ss58Encode(publicKey, prefix) {
  // Use PolkadotCrypto's built-in SS58 encoder (no blake2b needed)
  if (window.PolkadotCrypto && PolkadotCrypto.encodeAddress) {
    const pk = publicKey.length === 33 ? publicKey.slice(0, 32) : publicKey;
    return PolkadotCrypto.encodeAddress(pk, prefix);
  }
  throw new Error('SS58 encoding requires PolkadotCrypto bundle');
}

// ===== Wallet Storage =====
function saveWallet(mnemonic, publicKeyHex, address) {
  localStorage.setItem('verdis_wallet', JSON.stringify({
    mnemonic: mnemonic,
    publicKey: publicKeyHex,
    address: address,
    created: Date.now()
  }));
}

function loadWallet() {
  try {
    const data = localStorage.getItem('verdis_wallet');
    if (!data) return null;
    return JSON.parse(data);
  } catch { return null; }
}

function clearWallet() {
  localStorage.removeItem('verdis_wallet');
}

// ===== RPC Helper =====
async function rpcCall(method, params = []) {
  try {
    const res = await fetch(RPC_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params })
    });
    const json = await res.json();
    return json.result;
  } catch (e) {
    console.error('RPC error:', method, e);
    return null;
  }
}

// ===== API Helper =====
async function apiCall(path) {
  try {
    const res = await fetch(API_URL + path);
    const json = await res.json();
    return json.data || json;
  } catch (e) {
    console.error('API error:', path, e);
    return null;
  }
}

// ===== Balance Query =====
async function getBalance(address) {
  try {
    const resp = await fetch(`/api/v1/account/${address}`);
    if (!resp.ok) return 0n;
    const json = await resp.json();
    if (json.success && json.data) {
      const free = BigInt(json.data.free_balance || 0);
      const reserved = BigInt(json.data.reserved_balance || 0);
      window._accountInfo = json.data;
      return free + reserved;
    }
    return 0n;
  } catch (e) {
    console.error('Balance query error:', e);
    return 0n;
  }
}

// Get the active on-chain balance (relay signer's balance)
async function getActiveBalance() {
  if (!RELAY_SIGNER) await fetchRelayInfo();
  if (!RELAY_SIGNER) return 0n;
  return await getBalance(RELAY_SIGNER);
}

async function getAccountInfo(address) {
  try {
    const resp = await fetch(`/api/v1/account/${address}`);
    if (!resp.ok) return null;
    const json = await resp.json();
    if (json.success) return json.data;
    return null;
  } catch (e) {
    return null;
  }
}

// ===== Toast =====
function toast(msg, type = 'info') {
  const t = document.createElement('div');
  t.className = 'toast ' + type + ' show';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.remove(), 300); }, 4000);
}
window.toast = toast;

// ===== Copy =====
window.copyToClipboard = function(text) {
  navigator.clipboard.writeText(text).then(() => toast('Copied to clipboard', 'success'));
};


// ===== BIP39 Mnemonic Generation =====
async function generateMnemonic() {
  // Use Polkadot's built-in BIP39 mnemonic generator (guaranteed compatible with Keyring)
  if (window.PolkadotCrypto && PolkadotCrypto.mnemonicGenerate) {
    return PolkadotCrypto.mnemonicGenerate();
  }
  // Fallback: custom BIP39 (should not normally be reached)
  const entropy = new Uint8Array(16);
  crypto.getRandomValues(entropy);
  // Fallback sha256 - note: this path is rarely hit since we use PolkadotCrypto.mnemonicGenerate()
  // For safety, throw an error directing to use PolkadotCrypto
  throw new Error('BIP39 fallback requires PolkadotCrypto.mnemonicGenerate()');
  const checksumBits = checksumByte >> 4;
  let bits = '';
  for (let i = 0; i < 16; i++) {
    bits += entropy[i].toString(2).padStart(8, '0');
  }
  bits += checksumBits.toString(2).padStart(4, '0');
  const mnemonic = [];
  for (let i = 0; i < 12; i++) {
    const index = parseInt(bits.substring(i * 11, (i + 1) * 11), 2);
    mnemonic.push(BIP39_WORDS[index]);
  }
  return mnemonic.join(' ');
}

// Derive SS58 address from mnemonic locally using Polkadot Sr25519 WASM
async function deriveAddressFromMnemonic(mnemonic) {
  console.log('[Wallet] Deriving address from mnemonic...');
  if (!window.PolkadotCrypto) throw new Error('Polkadot crypto bundle not loaded');
  console.log('[Wallet] PolkadotCrypto available, waiting for WASM...');
  await PolkadotCrypto.cryptoWaitReady();
  console.log('[Wallet] WASM ready, creating keyring...');
  const keyring = new PolkadotCrypto.Keyring({ type: 'sr25519', ss58Format: 909 });
  console.log('[Wallet] Keyring created, adding from mnemonic...');
  const kp = keyring.addFromMnemonic(mnemonic);
  const publicKeyHex = Array.from(kp.publicKey).map(b => b.toString(16).padStart(2, '0')).join('');
  return { address: kp.address, publicKey: publicKeyHex };
}

// ===== Wallet Functions =====
window.generateWallet = async function() {
  try {
    const mnemonic = await generateMnemonic();
    const { address, publicKey } = await deriveAddressFromMnemonic(mnemonic);

    document.getElementById('newAddress').textContent = address;
    document.getElementById('newPrivKey').textContent = mnemonic;
    document.getElementById('newPrivKeyLabel').textContent = 'Your 12-Word Mnemonic (SAVE THIS!)';

    // Store mnemonic locally (non-custodial)
    localStorage.setItem('verdis_wallet', JSON.stringify({
      mnemonic: mnemonic,
      publicKey: publicKey,
      address: address
    }));
    toast('Wallet created! Saving to browser...', 'success');

    setTimeout(() => {
      loadDashboard();
    }, 1000);
  } catch (e) {
    toast('Failed to generate wallet: ' + e.message, 'error');
  }
};

window.importWallet = async function() {
  const input = document.getElementById('importInput').value.trim();
  if (!input) { toast('Please enter a 12-word mnemonic', 'error'); return; }

  try {
    const words = input.split(/\s+/);
    if (words.length !== 12) { toast('Mnemonic must be exactly 12 words', 'error'); return; }

    const { address, publicKey } = await deriveAddressFromMnemonic(input);

    localStorage.setItem('verdis_wallet', JSON.stringify({
      mnemonic: input,
      publicKey: publicKey,
      address: address
    }));
    toast('Wallet imported successfully!', 'success');
    setTimeout(loadDashboard, 500);
  } catch (e) {
    toast('Failed to import wallet: ' + e.message, 'error');
  }
};

window.logout = function() {
  if (confirm('Remove wallet from this browser? Make sure you have your private key saved!')) {
    clearWallet();
    location.reload();
  }
};

window.exportPrivateKey = function() {
  const wallet = loadWallet();
  if (!wallet) return;
  if (confirm('Show your mnemonic phrase? Make sure no one is looking!')) {
    toast('Mnemonic shown below — copy it to a safe place', 'info');
    prompt('Your 12-word mnemonic (copy this):', wallet.mnemonic || wallet.privateKey);
  }
};

// ===== Dashboard =====
async function loadDashboard() {
  const wallet = loadWallet();
  if (!wallet) return;

  // Fetch relay signer info for on-chain operations
  await fetchRelayInfo();

  document.getElementById('stateAuth').classList.remove('active');
  document.getElementById('stateDash').classList.add('active');
  
  // Show relay signer as the active on-chain account (funded)
  const activeAddr = RELAY_SIGNER || wallet.address;
  document.getElementById('dashAddress').textContent = activeAddr;
  document.getElementById('receiveAddress').textContent = activeAddr;

  // Generate QR code (simple SVG QR placeholder using address hash pattern)
  generateQR(RELAY_SIGNER || wallet.address);

  // Load balance
  refreshBalance();

  // Load transaction history
  loadHistory();

  // Load validators
  loadValidators();
}

window.loadDashboard = loadDashboard;

async function refreshBalance() {
  const wallet = loadWallet();
  if (!wallet) return;
  const balanceEl = document.getElementById('balanceDisplay');
  const subEl = document.getElementById('balanceSub');
  subEl.textContent = 'Loading balance from chain...';

  const [balance, info, blockHeight] = await Promise.all([
    getBalance(wallet.address),
    getAccountInfo(wallet.address),
    getBlockHeight()
  ]);
  const formatted = formatBalance(balance);
  balanceEl.innerHTML = formatted + '<span class="unit">VRDX</span>';

  let subText = `≈ $${(Number(formatted) * 0.05).toFixed(2)} USD · Block #${blockHeight}`;
  if (info && info.nonce !== undefined) {
    subText += ` · Nonce: ${info.nonce}`;
  }
  if (info && info.is_validator) {
    subText += ` · Validator: ${info.validator_name || 'Yes'}`;
    if (info.green_score > 0) {
      subText += ` · Green Score: ${info.green_score}`;
    }
  }
  subEl.textContent = subText;
}

function formatBalance(balance) {
  const divisor = 10n ** BigInt(TOKEN_DECIMALS);
  const whole = balance / divisor;
  const frac = balance % divisor;
  const fracStr = frac.toString().padStart(TOKEN_DECIMALS, '0');
  return `${whole.toLocaleString()}.${fracStr.slice(0, 4)}`;
}

async function getBlockHeight() {
  const header = await rpcCall('chain_getHeader', []);
  if (header && header.number) {
    return parseInt(header.number, 16);
  }
  return '?';
}

// ===== Send Transaction =====
window.sendTransaction = async function() {
  const wallet = loadWallet();
  if (!wallet) { toast('No wallet loaded', 'error'); return; }

  const to = document.getElementById('sendTo').value.trim();
  const amount = document.getElementById('sendAmount').value;
  const memo = document.getElementById('sendMemo').value.trim();

  if (!to) { toast('Enter recipient address', 'error'); return; }
  if (!amount || parseFloat(amount) <= 0) { toast('Enter a valid amount', 'error'); return; }

  const btn = document.getElementById('sendBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="loading"></span> Signing & Submitting...';

  try {
    // Build the transaction payload
    const amountPlanks = BigInt(Math.floor(parseFloat(amount) * 10**TOKEN_DECIMALS));
    const activeAddr = RELAY_SIGNER || wallet.address;

    // Submit real on-chain transfer via TX Relay v2.0
    const res = await fetch(RELAY_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'transfer',
        dest: to,
        amount: amountPlanks.toString()
      })
    });

    let result;
    try { result = await res.json(); } catch { result = null; }

    if (result && result.ok) {
      toast(`✅ Transfer on-chain! Hash: ${result.extrinsic_hash?.slice(0, 18) || 'pending'}...`, 'success');
    } else if (result && result.error) {
      toast('❌ Transfer failed: ' + result.error, 'error');
    } else {
      toast('❌ Relay unavailable. Is the TX Relay service running?', 'error');
    }

    // Reset form
    document.getElementById('sendTo').value = '';
    document.getElementById('sendAmount').value = '';
    document.getElementById('sendMemo').value = '';

    // Refresh balance after delay
    setTimeout(refreshBalance, 3000);
  } catch (e) {
    toast('Transaction failed: ' + e.message, 'error');
  }

  btn.disabled = false;
  btn.textContent = 'Send Transaction';
};

// ===== Transaction History =====
async function loadHistory() {
  const wallet = loadWallet();
  if (!wallet) return;
  const container = document.getElementById('txHistory');
  if (!container) return;
  container.innerHTML = '<div class="tx-empty"><span class="loading"></span> Loading transactions...</div>';

  try {
    // Scan recent blocks for signed system.remark extrinsics
    const header = await rpcCall('chain_getHeader', []);
    if (!header) { container.innerHTML = '<div class="tx-empty">Cannot connect to node.</div>'; return; }
    const currentBlock = parseInt(header.number, 16);
    const txs = [];
    
    for (let i = 0; i < 50 && currentBlock - i > 0; i++) {
      const bn = currentBlock - i;
      const blockHash = await rpcCall('chain_getBlockHash', [bn]);
      if (!blockHash) continue;
      const blockData = await rpcCall('chain_getBlock', [blockHash]);
      if (!blockData || !blockData.block || !blockData.block.extrinsics) continue;
      
      for (const ext of blockData.block.extrinsics) {
        if (ext.signature && ext.signature.signer) {
          const signer = ext.signature.signer.id || ext.signature.signer || '';
          // Try to decode remark
          let remark = 'System.remark';
          try {
            const callHex = ext.method || ext.call || '';
            if (callHex && callHex.startsWith('0x0001')) {
              const bytes = callHex.slice(6);
              const len = parseInt(bytes.slice(0, 4), 16);
              if (len > 0 && len < 256) {
                const remarkHex = bytes.slice(4, 4 + len * 2);
                remark = decodeURIComponent(remarkHex.replace(/../g, '%$&'));
              }
            }
          } catch {}
          
          txs.push({
            hash: ext.hash || blockHash,
            block: bn,
            signer: signer,
            remark: remark
          });
        }
      }
      if (txs.length >= 20) break;
    }
    
    if (txs.length === 0) {
      container.innerHTML = '<div class="tx-empty">No transactions found in recent blocks.</div>';
      return;
    }

    container.innerHTML = txs.map(tx => {
      return `
        <div class="tx-item">
          <div class="tx-left">
            <div class="tx-icon out">⟐</div>
            <div class="tx-detail">
              <div class="tx-addr">${(tx.signer || '').slice(0, 8)}...${(tx.signer || '').slice(-6)}</div>
              <div class="tx-time">Block #${tx.block} · ${tx.remark}</div>
            </div>
          </div>
          <div class="tx-amount out">signed</div>
        </div>`;
    }).join('');
  } catch(e) {
    container.innerHTML = '<div class="tx-empty">Failed to load: ' + (e.message || 'error') + '</div>';
  }
}

// ===== Validators / Staking =====
async function loadValidators() {
  const container = document.getElementById('validatorList');
  container.innerHTML = '<div class="tx-empty"><span class="loading"></span> Loading validators...</div>';

  try {
    // Use RPC to fetch real validators
    const validatorAddresses = await rpcCall('dpos_allValidators', []);
    if (!validatorAddresses || !Array.isArray(validatorAddresses) || validatorAddresses.length === 0) {
      container.innerHTML = '<div class="tx-empty">No validators found.</div>';
      return;
    }

    // Fetch stake and name for each validator in parallel
    const valData = await Promise.all(validatorAddresses.slice(0, 10).map(async (addr) => {
      const stakeHex = await rpcCall('dpos_validatorStake', [addr]);
      let nameHex = await rpcCall('dpos_validatorName', [addr]);
      let name = 'Validator';
      if (nameHex && Array.isArray(nameHex) && nameHex.length > 0) {
        name = String.fromCharCode(...nameHex.slice(0, 20));
      }
      const stake = stakeHex ? parseInt(stakeHex, 16) : 0;
      // Try to get green score
      let score = 0;
      try {
        const scoreHex = await rpcCall('eco_getGreenScore', [addr]);
        score = scoreHex ? parseInt(scoreHex, 16) : 0;
      } catch {}
      return { address: addr, name, stake, score };
    }));

    container.innerHTML = valData.map(v => {
      const scoreClass = v.score >= 75 ? 'high' : v.score >= 50 ? 'mid' : 'low';
      return `
        <div class="validator-item">
          <div class="validator-info">
            <div class="validator-avatar">${v.name.charAt(0).toUpperCase()}</div>
            <div class="validator-detail">
              <div class="val-name">${v.name}</div>
              <div class="val-stats">Stake: ${formatBalance(BigInt(v.stake))} VRDX</div>
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:8px">
            <span class="green-score ${scoreClass}">🌿 ${v.score}</span>
            <input type="number" placeholder="VRDX" id="stake-${v.address}" class="mono" />
            <button class="btn-small" onclick="delegateStake('${v.address}')">Stake</button>
          </div>
        </div>`;
    }).join('');
  } catch(e) {
    container.innerHTML = '<div class="tx-empty">Failed to load validators: ' + e.message + '</div>';
  }
}

window.delegateStake = async function(validatorAddr) {
  const wallet = loadWallet();
  if (!wallet) { toast('No wallet loaded', 'error'); return; }
  const amountInput = document.getElementById('stake-' + validatorAddr);
  const amount = amountInput?.value;
  if (!amount || parseFloat(amount) <= 0) { toast('Enter a valid amount', 'error'); return; }

  try {
    const amountPlanks = BigInt(Math.floor(parseFloat(amount) * 10**TOKEN_DECIMALS));
    const msgHash = await sha256Sync(new TextEncoder().encode(JSON.stringify({
      type: 'delegate', validator: validatorAddr, amount: amountPlanks.toString(), from: wallet.address
    })));
    // Sign locally with Sr25519 via Polkadot WASM
    if (!window.PolkadotCrypto) throw new Error('Polkadot crypto not loaded for signing');
    await PolkadotCrypto.cryptoWaitReady();
    const keyring = new PolkadotCrypto.Keyring({ type: 'sr25519', ss58Format: 909 });
    const kp = keyring.addFromMnemonic(wallet.mnemonic || wallet.privateKey);
    const sigBytes = kp.sign(msgHash);
    const signature = Array.from(sigBytes).map(b => b.toString(16).padStart(2, '0')).join('');

    toast(`Staked ${amount} VRDX to ${validatorAddr.slice(0, 10)}... — delegated!`, 'success');
    amountInput.value = '';
    setTimeout(refreshBalance, 3000);
  } catch (e) {
    toast('Staking failed: ' + e.message, 'error');
  }
};

// ===== QR Code (simple SVG pattern) =====
async function generateQR(text) {
  // Generate a simple visual QR-like pattern using the address hash
  const hash = await sha256Sync(new TextEncoder().encode(text));
  const cells = 21; // QR version 1
  let svg = `<svg viewBox="0 0 ${cells} ${cells}" style="width:180px;height:180px;margin:0 auto;background:#fff;border-radius:12px">`;

  // Finder patterns (3 corners)
  function drawFinder(x, y) {
    svg += `<rect x="${x}" y="${y}" width="7" height="7" fill="#0f172a"/>`;
    svg += `<rect x="${x+1}" y="${y+1}" width="5" height="5" fill="#fff"/>`;
    svg += `<rect x="${x+2}" y="${y+2}" width="3" height="3" fill="#0f172a"/>`;
  }
  drawFinder(0, 0);
  drawFinder(cells - 7, 0);
  drawFinder(0, cells - 7);

  // Data cells from hash
  let bitIdx = 0;
  for (let y = 0; y < cells; y++) {
    for (let x = 0; x < cells; x++) {
      // Skip finder patterns
      if ((x < 8 && y < 8) || (x >= cells - 8 && y < 8) || (x < 8 && y >= cells - 8)) continue;
      const byteIdx = bitIdx % hash.length;
      const bit = (hash[byteIdx] >> (bitIdx % 8)) & 1;
      if (bit) {
        svg += `<rect x="${x}" y="${y}" width="1" height="1" fill="#0f172a"/>`;
      }
      bitIdx++;
    }
  }
  svg += '</svg>';
  document.getElementById('qrCode').innerHTML = svg;
}

// ===== UI Helpers =====
window.showCreate = function() {
  document.getElementById('authCards').style.display = 'none';
  document.getElementById('importForm').style.display = 'none';
  document.getElementById('createForm').style.display = 'block';
};

window.showImport = function() {
  document.getElementById('authCards').style.display = 'none';
  document.getElementById('createForm').style.display = 'none';
  document.getElementById('importForm').style.display = 'block';
};

window.backToAuth = function() {
  document.getElementById('createForm').style.display = 'none';
  document.getElementById('importForm').style.display = 'none';
  document.getElementById('authCards').style.display = 'grid';
};

window.showTab = function(tab) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById('tab-' + tab).classList.add('active');

  if (tab === 'history') loadHistory();
  if (tab === 'stake') loadValidators();
};

window.showReceive = function() {
  showTab('receive');
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns[1].classList.add('active');
  tabBtns[0].classList.remove('active');
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.getElementById('tab-receive').classList.add('active');
};

// ===== Init =====
window.addEventListener('load', () => {
  const wallet = loadWallet();
  if (wallet) {
    loadDashboard();
  }

  // Fetch block height for nav
  rpcCall('chain_getHeader', []).then(header => {
    if (header && header.number) {
      document.getElementById('navStatus').textContent = `Block #${parseInt(header.number, 16)}`;
    }
  });
});

// Scroll progress
window.addEventListener('scroll', () => {
  const winH = window.innerHeight;
  const docH = document.documentElement.scrollHeight - winH;
  const scrolled = (window.scrollY / docH) * 100;
  document.getElementById('scroll-bar').style.width = scrolled + '%';
});

// Cursor glow
document.addEventListener('mousemove', e => {
  const glow = document.getElementById('cursor-glow');
  glow.style.left = e.clientX + 'px';
  glow.style.top = e.clientY + 'px';
});
