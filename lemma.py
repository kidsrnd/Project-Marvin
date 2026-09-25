"""간단한 표제어 환원기 — 교육부 목록(대표형)과 본문 단어(변화형)를 맞추기 위한 것"""
import re
IRREGULAR = {
 "am":"be","is":"be","are":"be","was":"be","were":"be","been":"be","being":"be",
 "has":"have","had":"have","having":"have","does":"do","did":"do","done":"do","doing":"do",
 "went":"go","gone":"go","goes":"go","came":"come","saw":"see","seen":"see","said":"say",
 "got":"get","gotten":"get","gave":"give","given":"give","took":"take","taken":"take",
 "made":"make","knew":"know","known":"know","thought":"think","told":"tell","found":"find",
 "felt":"feel","left":"leave","kept":"keep","began":"begin","begun":"begin","ran":"run",
 "wrote":"write","written":"write","read":"read","put":"put","let":"let","sat":"sit",
 "stood":"stand","heard":"hear","held":"hold","brought":"bring","bought":"buy","caught":"catch",
 "taught":"teach","fought":"fight","sought":"seek","lost":"lose","met":"meet","paid":"pay",
 "sent":"send","spent":"spend","built":"build","meant":"mean","led":"lead","fed":"feed",
 "slept":"sleep","wore":"wear","worn":"wear","broke":"break","broken":"break","spoke":"speak",
 "spoken":"speak","chose":"choose","chosen":"choose","drove":"drive","driven":"drive",
 "ate":"eat","eaten":"eat","fell":"fall","fallen":"fall","flew":"fly","flown":"fly",
 "forgot":"forget","forgotten":"forget","grew":"grow","grown":"grow","hid":"hide","hidden":"hide",
 "rode":"ride","ridden":"ride","rose":"rise","risen":"rise","shook":"shake","shaken":"shake",
 "sang":"sing","sung":"sing","sank":"sink","swam":"swim","swum":"swim","threw":"throw","thrown":"throw",
 "woke":"wake","woken":"wake","won":"win","drew":"draw","drawn":"draw","drank":"drink","drunk":"drink",
 "blew":"blow","blown":"blow","froze":"freeze","frozen":"freeze","hung":"hang","lay":"lie","lain":"lie",
 "laid":"lay","shot":"shoot","stuck":"stick","struck":"strike","swung":"swing","tore":"tear","torn":"tear",
 "understood":"understand","rang":"ring","rung":"ring","born":"bear","bore":"bear","borne":"bear","sold":"sell","sought":"seek","swept":"sweep","wept":"weep","crept":"creep","knelt":"kneel","leapt":"leap","shone":"shine","sped":"speed","spun":"spin","stole":"steal","stolen":"steal","strode":"stride","swore":"swear","sworn":"swear","wound":"wind","forgave":"forgive","forgiven":"forgive","froze":"freeze","lent":"lend","spat":"spit","split":"split","spread":"spread","stung":"sting","sprang":"spring","sprung":"spring","became":"become","cut":"cut","hit":"hit","hurt":"hurt","shut":"shut",
 "cost":"cost","set":"set","bit":"bite","bitten":"bite","lit":"light","bent":"bend","bound":"bind",
 "dealt":"deal","dug":"dig","dreamt":"dream","burnt":"burn","learnt":"learn","spelt":"spell",
 "children":"child","men":"man","women":"woman","people":"people","feet":"foot","teeth":"tooth",
 "mice":"mouse","geese":"goose","oxen":"ox","sheep":"sheep","fish":"fish","lives":"life",
 "knives":"knife","wives":"wife","leaves":"leaf","halves":"half","shelves":"shelf","wolves":"wolf",
 "better":"good","best":"good","worse":"bad","worst":"bad","more":"much","most":"much","less":"little",
 "least":"little","further":"far","farther":"far","elder":"old","eldest":"old",
 "me":"i","my":"i","mine":"i","myself":"i","him":"he","his":"he","himself":"he",
 "her":"she","hers":"she","herself":"she","its":"it","itself":"it","us":"we","our":"we","ours":"we",
 "ourselves":"we","them":"they","their":"they","theirs":"they","themselves":"they",
 "your":"you","yours":"you","yourself":"you","yourselves":"you","whom":"who","whose":"who",
 "an":"a","these":"this","those":"that","angry":"anger","hungry":"hunger","thirsty":"thirst","fewer":"few","fewest":"few","cannot":"can","n't":"not","won't":"will","can't":"can","don't":"do","didn't":"do",
 "isn't":"be","wasn't":"be","aren't":"be","weren't":"be","couldn't":"could","wouldn't":"would",
 "shouldn't":"should","hasn't":"have","haven't":"have","hadn't":"have","doesn't":"do",
 "i'm":"i","i'll":"i","i'd":"i","i've":"i","you're":"you","you'll":"you","you've":"you","you'd":"you",
 "he's":"he","he'll":"he","he'd":"he","she's":"she","she'll":"she","she'd":"she","it's":"it","it'll":"it",
 "we're":"we","we'll":"we","we've":"we","we'd":"we","they're":"they","they'll":"they","they've":"they",
 "they'd":"they","that's":"that","there's":"there","here's":"here","what's":"what","who's":"who",
 "let's":"let","o'clock":"clock",
}
SUFFIX_RULES = [  # (접미사, 잘라낸 뒤 붙일 것들) — 후보를 여러 개 만들어 목록에 있는 것을 택함
 ("ies", ["y"]), ("ied",["y"]), ("ier",["y"]), ("iest",["y"]), ("ily",["y"]),
 ("sses",["ss"]), ("shes",["sh"]), ("ches",["ch"]), ("xes",["x"]), ("zes",["z"]),
 ("ing", ["", "e"]), ("ed", ["", "e"]), ("est", ["", "e"]), ("er", ["", "e"]),
 ("ly", ["", "le"]), ("ness", [""]), ("ful", [""]), ("less", [""]), ("es", ["", "e"]), ("s", [""]),
 ("ment",[""]), ("tion",["t","te"]), ("al",["","e"]), ("y",[""]), ("ish",[""]), ("able",["","e"]),
]
def candidates(word):
    w = word.lower()
    yield w
    if w in IRREGULAR: yield IRREGULAR[w]
    for suf, tails in SUFFIX_RULES:
        if w.endswith(suf) and len(w) - len(suf) >= 2:
            stem = w[:-len(suf)]
            for t in tails:
                yield stem + t
            # 자음 중복 (running → run, bigger → big)
            if len(stem) >= 3 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
                yield stem[:-1]
    if w.endswith("'s"): yield w[:-2]
PREFIXES = ["un","in","im","il","ir","en","em","inter","mis","re","dis","non","over","under"]
def lemmatize_compound(word, vocab):
    """접두사 파생(교육부 허용) 또는 두 목록 단어의 합성어이면 (표제어, 합성여부) 반환"""
    w = word.lower()
    for p in PREFIXES:
        if w.startswith(p) and len(w) - len(p) >= 3:
            rest = w[len(p):]
            for c in candidates(rest):
                if c in vocab: return c, "prefix"
    for i in range(3, len(w) - 2):
        a, b = w[:i], w[i:]
        la = next((c for c in candidates(a) if c in vocab), None)
        lb = next((c for c in candidates(b) if c in vocab), None)
        if la and lb: return (la, lb), "compound"
    return None, None
def lemmatize(word, vocab):
    """vocab에 있는 후보를 찾으면 그것을, 없으면 원형 그대로 돌려준다"""
    for c in candidates(word):
        if c in vocab: return c
    return word.lower()
