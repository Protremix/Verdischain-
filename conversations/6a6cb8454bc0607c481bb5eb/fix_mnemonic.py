#!/usr/bin/env python3
"""Add mnemonic generation to WalletManager and fix the create-mnemonic endpoint."""

# 1. Patch wallet.js to add generateMnemonic method
wallet_path = "/opt/verdis/app/dist/wallet/wallet.js"
with open(wallet_path) as f:
    wallet_code = f.read()

# Add generateMnemonic method after createWallet
mnemonic_method = '''
    /**
     * Generates a 12-word mnemonic phrase and derives a wallet from it.
     * The private key is derived from SHA-256 of the normalized mnemonic.
     */
    generateMnemonic() {
        const wordlist = [
            "abandon","ability","able","about","above","absent","absorb","abstract","absurd","abuse",
            "access","accident","account","accuse","achieve","acid","acoustic","acquire","across","act",
            "action","actor","actress","actual","adapt","add","addict","address","adjust","admit",
            "adult","advance","advice","aerobic","affair","afford","afraid","again","age","agent",
            "agree","ahead","aim","air","airport","aisle","alarm","album","alcohol","alert",
            "alien","all","alley","allow","almost","alone","alpha","already","also","alter",
            "always","amateur","amazing","among","amount","amused","analyst","anchor","ancient","anger",
            "angle","angry","animal","ankle","announce","annual","another","answer","antenna","antique",
            "anxiety","any","apart","apology","appear","apple","approve","april","arch","arctic",
            "area","arena","argue","arm","armed","armor","army","around","arrange","arrest",
            "arrive","arrow","art","artefact","artist","artwork","ask","aspect","assault","asset",
            "assist","assume","asthma","athlete","atom","attack","attend","attention","attitude","attract",
            "auction","audit","august","aunt","author","auto","autumn","average","avocado","avoid",
            "awake","aware","away","awesome","awful","awkward","axis","baby","bachelor","bacon",
            "badge","bag","balance","balcony","ball","bamboo","banana","banner","bar","barely",
            "bargain","barrel","base","basic","basket","battle","beach","bean","beauty","because",
            "become","beef","before","begin","behave","behind","believe","below","belt","bench",
            "benefit","best","betray","better","between","beyond","bicycle","bid","bike","bind",
            "biology","bird","birth","bitter","black","blade","blame","blanket","blast","bleak",
            "bless","blind","blood","blossom","blouse","blue","blur","blush","board","boat",
            "body","boil","bomb","bone","bonus","book","boost","border","boring","borrow",
            "boss","bottom","bounce","box","boy","bracket","brain","brand","brass","brave",
            "bread","breeze","brick","bridge","brief","bright","bring","brisk","broccoli","broken",
            "bronze","broom","brother","brown","brush","bubble","buddy","budget","buffalo","build",
            "bulb","bulk","bullet","bundle","bunker","burden","burger","burst","bus","business",
            "busy","butter","buyer","buzz","cabbage","cabin","cable","cactus","cage","cake",
            "call","calm","camera","camp","can","canal","cancel","candy","cannon","canoe",
            "canvas","canyon","capable","capital","captain","car","carbon","card","cargo","carpet",
            "carry","cart","case","cash","casino","castle","casual","cat","catalog","catch",
            "category","cattle","caught","cause","caution","cave","ceiling","celery","cement","census",
            "century","cereal","certain","chair","chalk","champion","change","chaos","chapter","charge",
            "chase","chat","cheap","check","cheese","chef","cherry","chest","chicken","chief",
            "child","chimney","choice","choose","chronic","chuckle","chunk","churn","cigar","cinnamon",
            "circle","citizen","city","civil","claim","clap","clarify","claw","clay","clean",
            "clerk","clever","click","client","cliff","climb","clinic","clip","clock","clog",
            "close","cloth","cloud","clown","club","clump","cluster","clutch","coach","coast",
            "coconut","code","coffee","coil","coin","collect","color","column","combine","come",
            "comfort","comic","common","company","concert","conduct","confirm","congress","connect","consider",
            "control","convince","cook","cool","copper","copy","coral","core","corn","correct",
            "cost","cotton","couch","country","couple","course","cousin","cover","coyote","crack",
            "cradle","craft","cram","crane","crash","crater","crawl","crazy","cream","credit",
            "creek","crew","cricket","crime","crisp","critic","crop","cross","crouch","crowd",
            "crucial","cruel","cruise","crumble","crunch","crush","cry","crystal","cube","culture",
            "cup","cupboard","curious","current","curtain","curve","cushion","custom","cute","cycle",
            "dad","damage","damp","dance","danger","daring","dash","daughter","dawn","day",
            "deal","debate","debris","decade","december","decide","decline","decorate","decrease","deer",
            "defense","define","defy","degree","delay","deliver","demand","demise","denial","dentist",
            "deny","depart","depend","deposit","depth","deputy","derive","describe","desert","design",
            "desk","despair","destroy","detail","detect","develop","device","devote","diagram","dial",
            "diamond","diary","dice","diesel","differ","digest","digital","dignity","dilemma","dinner",
            "dinosaur","direct","dirt","disagree","discover","disease","dish","dismiss","disorder","display",
            "distance","divert","divide","divorce","dizzy","doctor","document","dog","doll","dolphin",
            "domain","donate","donkey","donor","door","dose","double","dove","draft","dragon",
            "drama","drastic","draw","dream","dress","drift","drill","drink","drip","drive",
            "drop","drum","dry","duck","dumb","dune","during","dust","dutch","duty",
            "dwarf","dynamic","eager","eagle","early","earn","earth","easily","east","easy",
            "echo","ecology","economy","edge","edit","edit","educate","effect","effort","egg",
            "eight","either","elbow","elder","elect","elegant","element","elephant","elevator","elite",
            "else","embark","embody","embrace","emerge","emotion","employ","empower","empty","enable",
            "enact","enclose","encounter","encourage","endless","enemy","energy","enforce","engage","engine",
            "enjoy","enlist","enough","enrich","enroll","ensure","enter","entire","entry","envelope",
            "episode","equal","equip","era","erase","erode","erosion","error","erupt","escape",
            "essay","essence","estate","eternal","ethics","evidence","evil","evoke","evolve","exact",
            "example","exceed","exchange","excite","exclude","excuse","execute","exercise","exhaust","exhibit",
            "exile","exist","exit","exotic","expand","expect","expire","explain","expose","express",
            "extend","extra","eye","eyebrow","fabric","face","faculty","fade","faint","faith",
            "falcon","fall","false","fame","family","famous","fan","fancy","fantasy","farm",
            "fashion","fat","fatal","father","fatigue","fault","favorite","feature","february","federal",
            "fee","feed","feel","female","fence","festival","fetch","fever","few","fiber",
            "fiction","field","figure","file","film","filter","final","find","fine","finger",
            "finish","fire","firm","first","fiscal","fish","fit","fitness","fix","flag",
            "flame","flash","flat","flavor","flee","flight","flip","float","flock","floor",
            "flower","fluid","flush","fly","foam","focus","fog","foil","fold","follow",
            "food","foot","force","forest","forget","fork","fortune","forum","forward","fossil",
            "foster","found","fox","fragile","frame","frequent","fresh","friend","fringe","frog",
            "front","frost","frown","frozen","fruit","fuel","fun","funny","furnace","fury",
            "future","gadget","gain","galaxy","gallery","game","gap","garage","garbage","garden",
            "garlic","garment","gas","gasp","gate","gather","gauge","gaze","general","genius",
            "genre","gentle","genuine","gesture","ghost","giant","gift","giggle","ginger","giraffe",
            "girl","give","glad","glance","glare","glass","glide","globe","gloom","glory",
            "glove","glow","glue","goat","goddess","gold","golf","good","goose","gorilla",
            "gospel","gossip","govern","grace","grain","grand","grant","grape","grass","great",
            "green","grid","grief","grit","grocery","group","grow","grunt","guard","guess",
            "guide","guilt","guitar","gun","gym","habit","hair","half","hammer","hamster",
            "hand","happy","harbor","hard","harsh","harvest","hat","have","hawk","hazard",
            "head","health","heart","heavy","hedgehog","height","hello","helmet","hidden","hi",
            "high","highway","hike","hill","hint","hippy","hire","history","hobby","hockey",
            "hold","hole","holiday","hollow","home","honey","hood","hope","horizon","horse",
            "hospital","host","hostile","hotel","house","hover","huge","human","humble","humor",
            "hundred","hungry","hunt","hurdle","hurry","hurt","husband","hybrid","ice","icon",
            "idea","identify","idle","ignore","illegal","illness","image","imitate","immense","impact",
            "import","impose","improve","impulse","inch","include","income","increase","index","indicate",
            "indoor","industry","infant","inflict","inform","inhale","inherit","initial","inject","injury",
            "inland","inner","insect","insert","inside","inspire","install","intact","interest","into",
            "invite","involve","iron","island","isolate","issue","item","ivory","jacket","jaguar",
            "jar","jazz","jealous","jeans","jelly","jewel","job","join","joke","journey",
            "joy","judge","juice","jump","jungle","junior","junk","just","kangaroo","keen",
            "keep","ketchup","key","kick","kid","kidney","kind","kingdom","kiss","kit",
            "kitchen","kite","kitten","kiwi","knee","knife","knock","know","lab","label",
            "labor","ladder","lady","lake","lamp","language","laptop","large","later","latin",
            "laugh","laundry","lava","law","lawn","lawsuit","layer","lazy","leader","leaf",
            "learn","leave","lecture","left","leg","legal","legend","leisure","lemon","lend",
            "length","lens","leopard","lesson","letter","level","liar","liberty","library","license",
            "life","lift","light","like","limb","limit","link","lion","liquid","list",
            "live","lizard","load","lobster","local","lock","lodge","lonely","long","loop",
            "lottery","loud","love","loyal","lucky","lumber","lunar","machine","mad","magic",
            "magnet","maiden","major","make","mammal","manage","many","map","marble","march",
            "margin","marine","market","marriage","mask","mass","master","match","material","math",
            "matter","maximum","mayor","meadow","mean","measure","meat","media","medicine","meet",
            "melon","member","memory","mention","menu","mercy","merge","merit","merry","message",
            "metal","method","middle","midnight","milk","million","mimic","mind","minimize","minor",
            "minute","miracle","mirror","misery","miss","mistake","mix","mixed","mobile","model",
            "modify","mom","moment","monitor","monkey","monster","month","moon","moral","more",
            "morning","mosquito","mother","motion","motor","mount","mouse","move","movie","much",
            "muffin","mule","muscle","museum","music","must","mutual","myself","mystery","myth",
            "naive","name","napkin","narrow","nasty","nation","nature","near","neck","need",
            "negative","neglect","neither","nephew","nerve","nest","net","network","neutral","never",
            "news","next","nice","night","ninja","nitrogen","noble","noise","noodle","normal",
            "north","nose","note","notice","novel","now","nuclear","number","nurse","nut",
            "oak","obey","object","obscure","observe","obtain","obvious","occur","ocean","october",
            "odor","off","offer","office","often","oil","okay","old","olive","olympic",
            "omit","once","one","onion","online","only","open","opera","opinion","oppose",
            "option","orange","orbit","orchard","order","organ","origin","ostrich","other","outdoor",
            "outer","output","outside","oval","oven","over","own","oxygen","oyster","ozone",
            "paddle","page","pair","palace","palm","pan","panel","panic","panther","paper",
            "parade","parent","park","parrot","party","pass","patch","path","patient","patrol",
            "pattern","pause","pave","peace","peanut","pear","peasant","pelican","pen","penalty",
            "pencil","people","pepper","perfect","permit","person","pet","phone","photo","phrase",
            "physical","piano","picnic","picture","piece","pig","pigeon","pill","pilot","pine",
            "pioneer","pink","pipe","pistol","pitch","pizza","place","planet","plant","plastic",
            "plate","play","please","pledge","pluck","plug","plunge","poem","poet","point",
            "polar","pole","police","policy","pond","pony","pool","popular","portion","position",
            "possible","post","potato","pottery","poverty","powder","power","practice","praise","predict",
            "prefer","prepare","present","pretty","prevent","price","pride","primary","prince","print",
            "prior","prison","private","prize","problem","process","produce","profit","program","project",
            "promote","proof","proper","property","prosper","protect","proud","provide","public","pudding",
            "pull","pulp","pulse","pumpkin","punch","pupil","puppy","purchase","purity","purpose",
            "purse","push","put","puzzle","pyramid","quality","quantum","quarter","queen","quick",
            "quit","quiz","quote","rabbit","raccoon","race","radar","radio","rail","rain",
            "raise","rally","ramp","ranch","random","range","rapid","rare","rate","rather",
            "ratio","raven","ready","real","reason","rebel","rebuild","recall","receive","recipe",
            "record","recycle","reduce","reflect","reform","refuse","region","regret","regular","reject",
            "relax","release","relief","rely","remain","remember","remind","remove","render","renew",
            "rent","reopen","repair","repeat","replace","report","require","rescue","resemble","resist",
            "resource","response","result","retire","retreat","return","reveal","review","reward","rhythm",
            "rib","ribbon","rice","rich","ride","ridge","rifle","right","rigid","ring",
            "riot","ripple","risk","rival","river","roast","rob","robot","robust","rocket",
            "romance","roof","rookie","room","rose","rotate","rough","round","route","royal",
            "rubber","rude","rug","rugby","rule","runner","rural","saddle","sad","safe",
            "sail","salad","salmon","salon","salt","salute","same","sample","sand","satisfy",
            "satoshi","sauce","sausage","save","say","scale","scan","scar","scare","scatter",
            "scene","scheme","school","science","scope","score","scout","screen","script","scroll",
            "sea","search","season","seat","second","secret","section","secure","seed","seek",
            "segment","select","sell","seminar","senior","sense","sentence","series","service","session",
            "settle","setup","seven","severe","shadow","shaft","shallow","share","shed","shell",
            "shepherd","shield","shift","shine","ship","shiver","shock","shoe","shoot","shop",
            "short","should","shoulder","shout","shower","shrimp","shrug","shuffle","shy","sibling",
            "sick","side","siege","sight","sign","silent","silk","silly","silver","similar",
            "simple","since","sing","siren","sister","situate","six","size","skate","sketch",
            "ski","skill","skin","skirt","skull","slam","sleep","slender","slice","slide",
            "slight","slim","slogan","slot","slow","slush","small","smart","smile","smoke",
            "smooth","snack","snake","snap","sniff","snow","soap","soccer","social","sock",
            "soda","soft","solar","soldier","solid","solution","solve","someone","song","soon",
            "sorry","sort","soul","sound","soup","source","south","space","spare","spatial",
            "spawn","speak","special","speed","spell","spend","sphere","spice","spider","spike",
            "spin","spirit","splash","split","spoil","sponsor","spoon","sport","spot","spray",
            "spread","spring","spy","square","squeeze","squirrel","stable","stadium","staff","stage",
            "stairs","stamp","stand","star","start","state","stay","steady","steel","stem",
            "step","stereo","stick","still","sting","stock","stomach","stone","stool","story",
            "stove","strategy","street","strike","strong","struggle","student","stuff","stumble","style",
            "subject","submit","subway","success","such","sudden","suffer","sugar","suggest","suit",
            "summer","sun","sunny","sunset","super","supply","sure","surface","surge","surprise",
            "surround","survey","survive","suspect","sustain","swallow","swamp","swap","swarm","swear",
            "sweet","swift","swim","swing","switch","sword","symbol","symptom","syrup","system",
            "table","tackle","tag","tail","talent","talk","tank","tape","target","task",
            "taste","tattoo","taxi","teach","team","tell","ten","tenant","tennis","tent",
            "term","test","text","thank","that","theme","then","theory","there","they",
            "thing","this","thought","three","thrive","throw","thumb","thunder","ticket","tide",
            "tiger","tilt","timber","time","tiny","tip","tired","tissue","title","toast",
            "tobacco","today","toddler","toe","together","toilet","token","tomato","tomorrow","tone",
            "tongue","tonight","tool","tooth","top","topic","topple","torch","tornado","tortoise",
            "total","tough","tour","toward","tower","town","toy","track","trade","traffic",
            "tragic","train","trap","travel","treat","trend","trial","tribe","trick","trigger",
            "trim","trip","trophy","trouble","truck","true","truly","trumpet","trust","truth",
            "try","tube","tuition","tumble","tuna","tunnel","turn","turtle","twelve","twenty",
            "twice","twin","twist","two","type","typical","ugly","umbrella","unable","unaware",
            "uncle","under","undergo","uniform","unique","unit","universe","unknown","unlock","until",
            "unusual","unveil","update","upgrade","upon","upper","upset","urban","urge","usage",
            "use","used","useful","useless","utility","vacant","vacuum","vague","valid","valley",
            "value","van","vanish","vapor","various","vast","vault","version","veto","victim",
            "victory","video","view","village","vintage","violin","virtual","virus","visa","visit",
            "visual","vital","vivid","vocal","voice","void","volcano","volume","vote","voyage",
            "wage","wagon","wait","walk","wall","walnut","want","warfare","warm","warn",
            "wash","waste","watch","water","wave","way","wealth","weapon","wear","weasel",
            "weather","weave","web","wedding","weekend","weird","welcome","west","wet","whale",
            "what","wheat","wheel","when","where","whip","while","whisper","whistle","white",
            "whole","wide","widow","width","wild","will","win","window","wine","wing",
            "winter","wire","wisdom","wise","wish","witness","wolf","woman","wonder","wood",
            "wool","word","work","world","worry","worth","wrap","wreck","wrestle","wrist",
            "write","wrong","yard","year","yellow","you","young","youth","zebra","zero",
            "zone","zoo"
        ];
        const crypto = require("crypto");
        // Generate 128 bits of entropy (16 bytes) -> 12 words
        const entropy = crypto.randomBytes(16);
        // Add checksum: first 4 bits of SHA-256(entropy)
        const hash = crypto.createHash("sha256").update(entropy).digest();
        const checksumBits = (hash[0] >> 4) & 0x0F;
        // Combine entropy (128 bits) + checksum (4 bits) = 132 bits = 12 x 11-bit words
        const totalBits = Buffer.concat([entropy, Buffer.from([(checksumBits << 4) & 0xFF])]);
        const words = [];
        for (let i = 0; i < 12; i++) {
            const bitStart = i * 11;
            const byteIndex = Math.floor(bitStart / 8);
            const bitOffset = bitStart % 8;
            // Extract 11 bits starting at bitStart
            let value = (totalBits[byteIndex] << 8);
            if (byteIndex + 1 < totalBits.length) value |= totalBits[byteIndex + 1];
            if (byteIndex + 2 < totalBits.length) value |= (totalBits[byteIndex + 2] >> 8);
            value = (value >> (16 - 11 - bitOffset)) & 0x7FF;
            words.push(wordlist[value % wordlist.length]);
        }
        const mnemonic = words.join(" ");
        // Derive private key from mnemonic
        const { sha256 } = require("@noble/hashes/sha256");
        const { hex } = require("@noble/hashes/utils");
        const seed = sha256(Buffer.from(mnemonic, "utf8"));
        const privateKey = "0x" + hex(seed);
        const publicKey = (0, crypto_2.getPublicKeyFromPrivateKey)(privateKey);
        const address = (0, crypto_2.getAddressFromPublicKey)(publicKey);
        const wallet = { privateKey, publicKey, address, balance: 0, staked: 0, mnemonic };
        this.wallets.set(address, wallet);
        return wallet;
    }
'''

# Insert after createWallet method (before importWallet)
insertion_point = wallet_code.find("    /**\n     * Imports an existing wallet")
if insertion_point == -1:
    print("ERROR: Can't find insertion point in wallet.js")
    exit(1)

wallet_code = wallet_code[:insertion_point] + mnemonic_method + "\n    " + wallet_code[insertion_point:]
with open(wallet_path, "w") as f:
    f.write(wallet_code)
print("Added generateMnemonic() to WalletManager")

# 2. Patch server.js to use generateMnemonic and return mnemonic
server_path = "/opt/verdis/app/dist/api/server.js"
with open(server_path) as f:
    server_code = f.read()

old_create_mnemonic = '''        this.app.post("/api/wallet/create-mnemonic", (req, res) => {
            try {
                const { mnemonic, privateKey } = req.body;
                let wallet;
                if (privateKey && privateKey.trim()) {
                    const pk = privateKey.startsWith("0x") ? privateKey : "0x" + privateKey;
                    wallet = this.walletManager.importWallet(pk);
                }
                else if (mnemonic && mnemonic.trim()) {
                    const seed = (0, crypto_1.sha256)(mnemonic.trim());
                    const pk = "0x" + seed;
                    wallet = this.walletManager.importWallet(pk);
                }
                else {
                    wallet = this.walletManager.createWallet();
                }
                res.json({
                    privateKey: wallet.privateKey,
                    publicKey: wallet.publicKey,
                    address: wallet.address,
                    balance: this.blockchain.getTokenSystem().getBalance(wallet.address),
                    staked: this.blockchain.getTokenSystem().getStaked(wallet.address),
                });
            }
            catch (error) {
                res.status(400).json({ error: error.message });
            }
        });'''

new_create_mnemonic = '''        this.app.post("/api/wallet/create-mnemonic", (req, res) => {
            try {
                const { mnemonic, privateKey } = req.body;
                let wallet;
                if (privateKey && privateKey.trim()) {
                    const pk = privateKey.startsWith("0x") ? privateKey : "0x" + privateKey;
                    wallet = this.walletManager.importWallet(pk);
                }
                else if (mnemonic && mnemonic.trim()) {
                    const seed = (0, crypto_1.sha256)(Buffer.from(mnemonic.trim(), "utf8"));
                    const pk = "0x" + Buffer.from(seed).toString("hex");
                    wallet = this.walletManager.importWallet(pk);
                }
                else {
                    wallet = this.walletManager.generateMnemonic();
                }
                res.json({
                    privateKey: wallet.privateKey,
                    publicKey: wallet.publicKey,
                    address: wallet.address,
                    mnemonic: wallet.mnemonic || undefined,
                    balance: this.blockchain.getTokenSystem().getBalance(wallet.address),
                    staked: this.blockchain.getTokenSystem().getStaked(wallet.address),
                });
            }
            catch (error) {
                res.status(400).json({ error: error.message });
            }
        });'''

if old_create_mnemonic in server_code:
    server_code = server_code.replace(old_create_mnemonic, new_create_mnemonic)
    with open(server_path, "w") as f:
        f.write(server_code)
    print("Fixed create-mnemonic endpoint to return mnemonic")
else:
    print("WARNING: Could not find create-mnemonic block in server.js")
    # Try a partial match
    import re
    match = re.search(r'this\.app\.post\("/api/wallet/create-mnemonic".*?\}\);', server_code, re.DOTALL)
    if match:
        print(f"  Found at position {match.start()}-{match.end()}")
        print(f"  First 100 chars: {match.group()[:100]}")
