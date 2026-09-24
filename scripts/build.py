#!/usr/bin/env python3
"""socialkim.github.io 허브 빌더 (표준 라이브러리만 사용)

data/projects.json + data/inbox.json + data/profile.json
  → index.html, about/, p/<id>/, llms.txt, llms-full.txt, sitemap.xml, robots.txt, feed.xml, assets/hub.css

실행:  python3 scripts/build.py
"""
import json, os, re, shutil, html
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://socialkim.github.io"
E = lambda s: html.escape(str(s or ""), quote=True)

SECTORS = OrderedDict([
    ("corp", "기업·경영진"), ("public", "공공·협회·지자체"), ("univ", "대학·교육"),
    ("media", "언론·미디어"), ("job", "직무·일반"),
])
SECTIONS = OrderedDict([
    ("lecture", ("강의·실습", "기관마다 그 조직의 업무 언어로 설계하고, 강의가 끝난 뒤에도 그대로 따라 할 수 있게 공개한 실습 페이지입니다.")),
    ("build", ("만든 것", "강의에서 말하는 것을 직접 만들어 공개한 서비스, MCP 서버, 도구, 브랜드 캠페인입니다. Claude Code와 ChatGPT(Codex·아스트라)를 함께 쓰며, 카드에 만든 AI를 표시했습니다.")),
    ("lab", ("실험실", "AI 에이전트와 코딩 도구로 게임과 학습 콘텐츠를 만들어 본 실험입니다. 방송 소재 게임은 방송사·출연진과 관계없는 팬메이드 창작물입니다.")),
    ("family", ("가족과 함께", "초등학생 아들이 말한 아이디어를 아빠가 AI로 진짜 만들어 준 프로젝트와, 부모와 아이가 함께하는 북토크 체험 키트입니다. 아이가 기획하고, 플레이하고, 다시 고쳐 달라고 한 기록이 담겨 있습니다.")),
])


def load(name, default):
    p = os.path.join(ROOT, "data", name)
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def josa(word, a, b):
    """받침 있으면 a, 없으면 b (을/를, 이/가, 은/는, 과/와)"""
    w = re.sub(r"[^가-힣A-Za-z0-9]", "", word or "")
    if not w:
        return b
    ch = w[-1]
    if "가" <= ch <= "힣":
        return a if (ord(ch) - 0xAC00) % 28 else b
    return a if ch.lower() in "lmnr0136789" else b


def kdate(d):
    if not d:
        return ""
    parts = d.split("-")
    if len(parts) == 2:
        return f"{int(parts[0])}년 {int(parts[1])}월"
    y, m, dd = parts
    return f"{int(y)}년 {int(m)}월 {int(dd)}일"


def fulld(d):
    return d + "-01" if d and len(d) == 7 else d


def sdate(d):
    return d.replace("-", ".") if d else ""


def write(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


# ───────────────────────── data ─────────────────────────
profile = load("profile.json", {})
projects = [p for p in load("projects.json", []) if not p.get("hidden")]
inbox = [dict(p, section="new", status="auto") for p in load("inbox.json", []) if not p.get("hidden")]
ALL = sorted(projects + inbox, key=lambda p: (p.get("date") or "", p["id"]), reverse=True)
lectures = [p for p in projects if p["section"] == "lecture"]
orgs = OrderedDict()
for s in SECTORS:
    names = []
    for p in sorted(lectures, key=lambda x: x.get("date") or "", reverse=True):
        if p["sector"] == s and p["org"] not in names and not p.get("org_generic"):
            names.append(p["org"])
    orgs[s] = names
n_orgs = len({p["org"] for p in lectures if not p.get("org_generic")})
NAME = profile.get("name", "김덕진")
import datetime
TODAY = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d")
LAST = max((p.get("date") or "" for p in ALL if (p.get("date") or "") <= TODAY), default="")


def sentence(p):
    """AI가 인용하기 좋은 근거 문장 (누가·언제·어디서·무엇을)"""
    if p.get("claim"):
        return p["claim"]
    d = kdate(p.get("date"))
    d = (d + " ") if d else ""
    dn = (d.strip() + "에 ") if d else ""
    who = "IT커뮤니케이션연구소 김덕진 소장"
    sec = p.get("section")
    if sec == "lecture":
        aud = p.get("audience") or "참가자"
        org = p.get("org")
        verb = "진행할 예정인" if (p.get("date") or "") > TODAY else "진행한"
        return f"{who}이 {d}{org}의 {aud}{josa(aud,'을','를')} 대상으로 {verb} AI 강의의 실습 페이지입니다."
    if sec == "build":
        return f"{who}이 만들어 {dn}공개한 서비스·도구입니다."
    if sec == "lab":
        s = f"{who}이 AI로 만들어 {dn}공개한 실험 프로젝트입니다."
        if p.get("label") == "팬메이드":
            s += " 방송사·출연진과 관계없는 팬메이드 창작물입니다."
        return s
    if sec == "family":
        return f"{who}이 초등학생 아들과 함께 만든 프로젝트입니다."
    return f"{who}이 {d}GitHub에 공개한 페이지입니다. 분류와 설명은 곧 정리됩니다."


# ───────────────────────── layout ─────────────────────────
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500&family=Space+Grotesk:wght@600;700&display=swap">'
         '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">')

ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230F1B2D'/%3E"
        "%3Ctext x='29' y='44' text-anchor='middle' font-family='system-ui' font-size='34' font-weight='800' fill='white'%3EK%3C/text%3E%3Ccircle cx='48' cy='42' r='5' fill='%23E5261F'/%3E%3C/svg%3E")


VKEYS = {"google": "google-site-verification", "naver": "naver-site-verification", "bing": "msvalidate.01"}
VERIFY = "".join(f'\n<meta name="{VKEYS[k]}" content="{E(v)}">' for k, v in (profile.get("verify") or {}).items() if k in VKEYS and v)


C = profile.get("contact") or {}
def tel(n): return "tel:+82" + n.replace("-", "")[1:]
CONTACT_TXT = f"{C.get('name','')} {C.get('title','')} · {C.get('mobile','')} · {C.get('office','')} · {profile.get('email','')}" if C else profile.get("email", "")
CONTACT_HTML = (f'{E(C.get("name"))} {E(C.get("title"))} · <a href="{tel(C["mobile"])}">{E(C["mobile"])}</a> · '
                f'<a href="{tel(C["office"])}">{E(C["office"])}</a> · <a href="mailto:{E(profile.get("email"))}">{E(profile.get("email"))}</a>') if C else ""


def page(path, title, desc, body, jsonld=None, depth=0):
    rel = "../" * depth
    canon = SITE + "/" + path
    ld = ""
    if jsonld:
        ld = '<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False, separators=(",", ":")) + "</script>"
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="author" content="김덕진 (Kim Dukjin)">{VERIFY}
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website"><meta property="og:site_name" content="김덕진 · AI 강의와 프로젝트">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canon}">
<meta property="og:locale" content="ko_KR">
<link rel="icon" href="{ICON}">
<link rel="alternate" type="application/atom+xml" title="새로 공개된 자료" href="{SITE}/feed.xml">
{FONTS}
<link rel="stylesheet" href="{rel}assets/hub.css">
{ld}
</head>
<body>
<header class="top"><div class="in">
<a class="mark" href="{rel or './'}">Kim Dukjin<i></i></a>
<nav><a href="{rel}#lecture">강의·실습</a><a href="{rel}#build">만든 것</a><a href="{rel}#lab">실험실</a><a href="{rel}about/">소개</a><a class="cta" href="mailto:{E(profile.get('email'))}">강의 문의</a></nav>
</div></header>
{body}
<footer class="foot"><div class="in">
<p><b>{E(NAME)}</b> · IT커뮤니케이션연구소 소장</p>
<p>강의·자문 문의: {CONTACT_HTML}</p>
<p>이 사이트는 김덕진 소장의 GitHub 레포를 매일 자동으로 모아 만듭니다. 마지막 공개 {sdate(LAST)} · <a href="{rel}llms.txt">llms.txt</a> · <a href="{rel}sitemap.xml">sitemap</a> · <a href="{rel}feed.xml">feed</a> · <a href="https://github.com/socialkim">GitHub</a></p>
</div></footer>
</body>
</html>
"""


def card(p, rel=""):
    sec = p.get("section")
    tag = SECTORS.get(p.get("sector")) if sec == "lecture" else (SECTIONS.get(sec, ("새로 올라온 자료",))[0] if sec in SECTIONS else "정리 전")
    top = p.get("org") or tag
    badge = f'<span class="badge">{E(p["label"])}</span>' if p.get("label") else ""
    if p.get("made_with"):
        badge += f'<span class="badge tool">{E(p["made_with"])}</span>'
    if p.get("status") == "auto":
        badge = '<span class="badge new">정리 전</span>'
    return (f'<article class="card" data-sector="{E(p.get("sector",""))}">'
            f'<p class="org">{E(top)}{badge}</p>'
            f'<h3><a href="{E(p["url"])}" target="_blank" rel="noopener">{E(p["title"])}</a></h3>'
            f'<p class="sum">{E(p.get("summary",""))}</p>'
            f'<p class="meta"><time datetime="{E(p.get("date"))}">{sdate(p.get("date"))}</time>'
            f'<a class="more" href="{rel}p/{E(p["id"])}/">자세히</a></p></article>')


# ───────────────────────── CSS ─────────────────────────
CSS = r"""
:root{--paper:#FAFBFC;--ink:#0F1B2D;--ink2:#3B4658;--mute:#5B6475;--line:#E3E7EE;--cobalt:#2457C5;--sky:#57D0FF;--skyl:#EAF7FE;--red:#E5261F;--card:#fff;
--mono:"JetBrains Mono",ui-monospace,monospace;--sans:"Pretendard Variable",Pretendard,"Apple SD Gothic Neo","Noto Sans KR",system-ui,sans-serif;--wm:"Space Grotesk",var(--sans)}
*{box-sizing:border-box}html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);line-height:1.6;-webkit-font-smoothing:antialiased;word-break:keep-all;overflow-wrap:anywhere}
a{color:var(--cobalt);text-decoration:none}a:hover{text-decoration:underline}
.in{max-width:1120px;margin:0 auto;padding:0 20px}
.top{position:sticky;top:0;z-index:9;background:rgba(250,251,252,.9);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.top .in{display:flex;align-items:center;justify-content:space-between;gap:12px;height:58px}
.mark{font-family:var(--wm);font-weight:700;font-size:19px;letter-spacing:-.02em;color:var(--ink);white-space:nowrap}.mark:hover{text-decoration:none}
.mark i{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--red);margin-left:3px}
nav{display:flex;gap:18px;align-items:center;font-size:14px;overflow-x:auto;scrollbar-width:none}nav::-webkit-scrollbar{display:none}
nav a{color:var(--ink2);white-space:nowrap}nav .cta{background:var(--cobalt);color:#fff;padding:7px 14px;border-radius:999px;font-weight:600}nav .cta:hover{text-decoration:none;background:#1c47a6}
.hero{padding:72px 0 44px}
.kick{font-family:var(--mono);font-size:12px;letter-spacing:.12em;color:var(--mute);text-transform:uppercase;margin:0 0 18px}
.hero h1{font-size:clamp(34px,6vw,60px);line-height:1.12;letter-spacing:-.03em;margin:0 0 20px;font-weight:800}
.hero h1 span{position:relative;white-space:nowrap}.hero h1 span:after{content:"";position:absolute;left:0;right:0;bottom:-6px;height:5px;border-radius:3px;background:var(--sky)}
.hero .lead{font-size:18px;color:var(--ink2);max-width:720px;margin:0 0 30px}
.stats{display:flex;flex-wrap:wrap;gap:12px 36px;padding-top:22px;border-top:1px solid var(--line)}
.stats div{font-size:14px;color:var(--mute)}.stats b{display:block;font-family:var(--wm);font-size:30px;color:var(--ink);letter-spacing:-.02em;line-height:1.1}
section.blk{padding:44px 0}
.h2row{display:flex;align-items:baseline;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:6px}
h2{font-size:26px;letter-spacing:-.02em;margin:0}h2 small{font-family:var(--mono);font-size:13px;color:var(--mute);font-weight:500;margin-left:8px}
.desc{color:var(--mute);margin:0 0 22px;max-width:760px;font-size:15px}
.grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px 20px 16px;display:flex;flex-direction:column;transition:border-color .15s,box-shadow .15s}
.card:hover{border-color:#c9d3e3;box-shadow:0 10px 30px -18px rgba(15,27,45,.35)}
.org{font-family:var(--mono);font-size:12px;color:var(--mute);margin:0 0 8px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.badge{font-family:var(--sans);font-size:11px;font-weight:600;color:var(--ink2);background:var(--skyl);border-radius:6px;padding:1px 7px}.badge.new{background:#FFF1D6;color:#8a5a00}.badge.tool{background:#EEF1F6;color:var(--mute);font-family:var(--mono);font-weight:500}
.card h3{font-size:17px;line-height:1.4;margin:0 0 8px;letter-spacing:-.01em}.card h3 a{color:var(--ink)}
.sum{font-size:14px;color:var(--ink2);margin:0 0 14px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.meta{margin:auto 0 0;display:flex;justify-content:space-between;align-items:center;font-family:var(--mono);font-size:12px;color:var(--mute)}
.more{font-family:var(--sans);font-size:13px;font-weight:600}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 22px}
.chip{font:inherit;font-size:13px;font-weight:600;border:1px solid var(--line);background:#fff;color:var(--ink2);padding:7px 14px;border-radius:999px;cursor:pointer}
.chip[aria-pressed=true]{background:var(--ink);border-color:var(--ink);color:#fff}
.sub{font-size:15px;font-weight:700;color:var(--ink2);margin:30px 0 12px;display:flex;align-items:center;gap:10px}.sub:before{content:"";width:18px;height:3px;border-radius:2px;background:var(--sky)}
.orgs{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:18px 28px;margin:0;padding:0}
.orgs div{margin:0}.orgs dt{font-family:var(--mono);font-size:12px;color:var(--mute);margin-bottom:6px}.orgs dd{margin:0;font-size:15px;line-height:1.75;color:var(--ink)}
.band{background:var(--ink);color:#DCE4F0;border-radius:20px;padding:40px 32px;margin:24px 0}
.band h2{color:#fff}.band p{max-width:720px}.band a.btn{display:inline-block;margin-top:10px;background:var(--sky);color:var(--ink);font-weight:700;padding:11px 20px;border-radius:999px}.band a.btn:hover{text-decoration:none;filter:brightness(1.05)}
.band a{color:var(--sky)}a[href^="tel:"],a[href^="mailto:"]{white-space:nowrap}.band .who{font-size:15px;color:#fff;margin:14px 0 6px}
.foot{border-top:1px solid var(--line);padding:30px 0 50px;font-size:13px;color:var(--mute)}.foot p{margin:4px 0}
/* detail */
.crumb{font-size:13px;color:var(--mute);padding:28px 0 0}.crumb a{color:var(--mute)}
.dhead{padding:18px 0 8px}.dhead h1{font-size:clamp(28px,4.6vw,44px);line-height:1.2;letter-spacing:-.025em;margin:8px 0 18px}
.claim{font-size:18px;color:var(--ink);background:var(--skyl);border-radius:12px;padding:16px 18px;margin:0 0 16px}
.dsum{font-size:16px;color:var(--ink2);max-width:760px}
.facts{display:grid;grid-template-columns:120px 1fr;gap:8px 16px;margin:26px 0;padding:20px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);font-size:15px}
.facts dt{color:var(--mute);font-family:var(--mono);font-size:12px;padding-top:3px}.facts dd{margin:0}
.go{display:inline-block;background:var(--cobalt);color:#fff;font-weight:700;padding:13px 22px;border-radius:999px;margin:4px 8px 4px 0}.go:hover{text-decoration:none;background:#1c47a6}
.go.ghost{background:#fff;color:var(--cobalt);border:1px solid var(--line)}
.rel{margin:40px 0 20px}.rel h2{font-size:20px}.rel ul{padding-left:18px}.rel li{margin:6px 0}
/* about */
.prose{max-width:760px;font-size:16px;color:var(--ink2)}.prose h2{margin:44px 0 14px;color:var(--ink)}
.prose ul{padding-left:20px}.prose li{margin:5px 0}
.meth{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px;margin-top:14px}
.meth div{background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px}.meth h3{margin:0 0 6px;font-size:16px;color:var(--ink)}.meth p{margin:0;font-size:14px}
details{border-bottom:1px solid var(--line);padding:14px 0}summary{cursor:pointer;font-weight:700;color:var(--ink)}details p{margin:10px 0 0}
@media (max-width:640px){.hero{padding:44px 0 30px}.hero .lead{font-size:16px}nav{gap:14px;font-size:13px}nav a:not(.cta):nth-child(3){display:none}
.band{padding:28px 20px;border-radius:16px}.facts{grid-template-columns:88px 1fr}.grid{grid-template-columns:1fr}}
"""

FILTER_JS = """<script>
(function(){var cs=document.querySelectorAll('.chip');cs.forEach(function(c){c.addEventListener('click',function(){
var f=c.dataset.f;cs.forEach(function(x){x.setAttribute('aria-pressed',x===c)});
document.querySelectorAll('#lecture [data-group]').forEach(function(g){g.hidden=!(f==='all'||g.dataset.group===f)})})})})();
</script>"""


def person_ld():
    return {
        "@type": "Person", "@id": SITE + "/about/#person", "name": NAME, "alternateName": [profile.get("name_en"), profile.get("handle")],
        "jobTitle": profile.get("title"), "description": profile.get("intro"), "url": SITE + "/about/", "email": "mailto:" + profile.get("email", ""),
        "worksFor": {"@type": "Organization", "name": "IT커뮤니케이션연구소 (ITCL)", "url": "http://itcl.kr/", "email": profile.get("email"),
                     "contactPoint": {"@type": "ContactPoint", "contactType": "강의·자문 문의", "email": profile.get("email"), "telephone": "+82-" + C.get("office", "")[1:], "areaServed": "KR", "availableLanguage": "Korean"}},
        "affiliation": [{"@type": "CollegeOrUniversity", "name": "세종사이버대학교"}, {"@type": "CollegeOrUniversity", "name": "서울시립대학교"}],
        "knowsAbout": profile.get("knows_about", []),
        "sameAs": [l["u"] for l in profile.get("links", []) if l["u"].startswith("http")],
    }


# ───────────────────────── index ─────────────────────────
def build_index():
    n_lec = len(lectures)
    recent = ALL[:6]
    parts = []
    parts.append(f"""<main>
<section class="hero"><div class="in">
<p class="kick">AI Lecture &amp; Project Archive · {E(NAME)} · {E(profile.get('name_en'))}</p>
<h1>강의가 끝나도 남는<br><span>AI 실습</span>을 만듭니다</h1>
<p class="lead">IT커뮤니케이션연구소 {E(NAME)} 소장이 기업·공공기관·대학에서 강의하며 만든 실습 페이지와 직접 만든 서비스를 한곳에 모았습니다. 기술과 사람 사이를 번역하는 AI 내비게이터의 작업 기록입니다.</p>
<div class="stats">
<div><b>{n_lec}</b>강의 실습 페이지</div>
<div><b>{n_orgs}</b>기관</div>
<div><b>{len([p for p in projects if p['section']!='lecture'])}</b>서비스·실험 프로젝트</div>
<div><b>1,000+</b>강연·방송</div>
</div>
</div></section>

<section class="blk" id="recent"><div class="in">
<div class="h2row"><h2>새로 올라온 자료</h2></div>
<p class="desc">가장 최근에 공개한 순서입니다. 새 레포는 매일 아침 자동으로 이곳에 올라옵니다.</p>
<div class="grid">{''.join(card(p) for p in recent)}</div>
</div></section>

<section class="blk" id="orgs"><div class="in">
<div class="h2row"><h2>강의한 기관<small>{n_orgs}곳</small></h2></div>
<p class="desc">실습 페이지가 공개된 기관만 적었습니다. 최근 순입니다.</p>
<dl class="orgs">""")
    for s, label in SECTORS.items():
        if orgs[s]:
            parts.append(f"<div><dt>{E(label)}</dt><dd>{' · '.join(E(o) for o in orgs[s])}</dd></div>")
    parts.append("</dl></div></section>")

    # lecture
    t, d = SECTIONS["lecture"]
    chips = '<button class="chip" data-f="all" aria-pressed="true">전체</button>' + "".join(
        f'<button class="chip" data-f="{s}" aria-pressed="false">{E(l)} {sum(1 for p in lectures if p["sector"]==s)}</button>' for s, l in SECTORS.items())
    parts.append(f'<section class="blk" id="lecture"><div class="in"><div class="h2row"><h2>{t}<small>{len(lectures)}</small></h2></div><p class="desc">{E(d)}</p><div class="chips" role="group" aria-label="분야 필터">{chips}</div>')
    for s, l in SECTORS.items():
        items = sorted([p for p in lectures if p["sector"] == s], key=lambda x: x.get("date") or "", reverse=True)
        if items:
            parts.append(f'<div data-group="{s}"><h3 class="sub">{E(l)}</h3><div class="grid">{"".join(card(p) for p in items)}</div></div>')
    parts.append("</div></section>")

    for sec in ("build", "lab", "family"):
        t, d = SECTIONS[sec]
        items = sorted([p for p in projects if p["section"] == sec], key=lambda x: x.get("date") or "", reverse=True)
        parts.append(f'<section class="blk" id="{sec}"><div class="in"><div class="h2row"><h2>{t}<small>{len(items)}</small></h2></div><p class="desc">{E(d)}</p><div class="grid">{"".join(card(p) for p in items)}</div></div></section>')

    if inbox:
        parts.append(f'<section class="blk" id="new"><div class="in"><div class="h2row"><h2>정리 전 자료<small>{len(inbox)}</small></h2></div><p class="desc">자동으로 발견해 먼저 올려 둔 자료입니다. 곧 분류와 설명을 정리합니다.</p><div class="grid">{"".join(card(p) for p in inbox)}</div></div></section>')

    parts.append(f"""<section class="blk"><div class="in"><div class="band">
<h2>우리 조직에 맞는 AI 강의가 필요하다면</h2>
<p>위 실습 페이지들은 모두 그 기관의 업무 언어로 새로 설계한 것입니다. 경영진 세미나, 직무별 실습, 교직원 연수, 주민 특강까지 대상에 맞춰 준비합니다.</p>
<p class="who">문의 담당 {CONTACT_HTML}</p>
<a class="btn" href="mailto:{E(profile.get('email'))}">강의·자문 문의 메일 보내기</a> &nbsp; <a href="about/">김덕진 소개 보기</a>
</div></div></section>
</main>
{FILTER_JS}""")

    ld = {"@context": "https://schema.org", "@graph": [
        person_ld(),
        {"@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/", "name": "김덕진 · AI 강의와 프로젝트", "inLanguage": "ko", "author": {"@id": SITE + "/about/#person"}},
        {"@type": "ItemList", "name": "김덕진 소장 AI 강의 실습 페이지와 프로젝트", "numberOfItems": len(ALL),
         "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/p/{p['id']}/", "name": (p.get("org") + " · " if p.get("org") else "") + p["title"]} for i, p in enumerate(ALL)]},
    ]}
    desc = f"IT커뮤니케이션연구소 김덕진 소장의 AI 강의 실습 페이지 {n_lec}개와 직접 만든 서비스·실험을 모은 아카이브. {n_orgs}개 기업·공공기관·대학의 강의 기록."
    write("index.html", page("", f"김덕진 AI 강의·프로젝트 아카이브 | IT커뮤니케이션연구소", desc, "".join(parts), ld))


# ───────────────────────── detail ─────────────────────────
def build_detail(p):
    sec = p.get("section")
    sec_name = SECTIONS[sec][0] if sec in SECTIONS else "새로 올라온 자료"
    claim = sentence(p)
    facts = []
    if p.get("org"): facts.append(("기관", p["org"]))
    if p.get("audience"): facts.append(("대상", p["audience"]))
    if sec == "lecture": facts.append(("분야", SECTORS.get(p["sector"], "")))
    else: facts.append(("구분", sec_name + (f" · {p['label']}" if p.get("label") else "")))
    if p.get("date"): facts.append(("날짜", kdate(p["date"])))
    if p.get("made_with"): facts.append(("만든 AI", p["made_with"]))
    if p.get("tools"): facts.append(("도구", ", ".join(p["tools"])))
    if p.get("topics"): facts.append(("주제", ", ".join(p["topics"])))
    facts.append(("만든 사람", "김덕진 (IT커뮤니케이션연구소 소장)"))
    if p.get("repo"): facts.append(("소스", f'<a href="https://github.com/{E(p["repo"])}">github.com/{E(p["repo"])}</a>'))
    fhtml = "".join(f"<dt>{E(k)}</dt><dd>{v if k=='소스' else E(v)}</dd>" for k, v in facts)
    extra = "".join(f'<a class="go ghost" href="{E(x["u"])}" target="_blank" rel="noopener">{E(x["t"])}</a>' for x in p.get("extra", []))
    same = [q for q in ALL if q["id"] != p["id"] and q.get("section") == sec and (sec != "lecture" or q.get("sector") == p.get("sector"))][:5]
    rel = ""
    if same:
        rel = '<div class="rel"><h2>같은 분야의 다른 자료</h2><ul>' + "".join(
            f'<li><a href="../{E(q["id"])}/">{E((q.get("org") + " · ") if q.get("org") else "")}{E(q["title"])}</a> <span class="meta">{sdate(q.get("date"))}</span></li>' for q in same) + "</ul></div>"
    head = (p.get("org") + " · ") if p.get("org") else ""
    body = f"""<main class="in">
<p class="crumb"><a href="../../">홈</a> / <a href="../../#{E(sec if sec in SECTIONS else 'new')}">{E(sec_name)}</a></p>
<div class="dhead"><p class="kick">{E(head)}{E(p.get('audience') or sec_name)}</p>
<h1>{E(p['title'])}</h1>
<p class="claim">{E(claim)}</p>
<p class="dsum">{E(p.get('summary',''))}</p></div>
<a class="go" href="{E(p['url'])}" target="_blank" rel="noopener">페이지 열기</a>{extra}
<dl class="facts">{fhtml}</dl>
{rel}
<p><a href="../../about/">김덕진 소장 소개</a> · <a href="../../">전체 자료 보기</a></p>
</main>"""
    typ = {"lecture": "LearningResource", "build": "SoftwareApplication", "lab": "CreativeWork", "family": "CreativeWork"}.get(sec, "CreativeWork")
    if sec == "lab" and "game" in p.get("sector", ""): typ = "VideoGame"
    ld = {"@context": "https://schema.org", "@type": typ, "name": p["title"], "description": claim + " " + p.get("summary", ""),
          "url": p["url"], "mainEntityOfPage": f"{SITE}/p/{p['id']}/", "inLanguage": "ko", "dateCreated": p.get("date") or None,
          "author": {"@type": "Person", "name": NAME, "url": SITE + "/about/", "jobTitle": profile.get("title")},
          "keywords": ", ".join(p.get("topics", []) + p.get("tools", []))}
    if sec == "lecture":
        ld["provider"] = {"@type": "Organization", "name": "IT커뮤니케이션연구소 (ITCL)"}
        ld["audience"] = {"@type": "Audience", "audienceType": f"{p.get('org')} {p.get('audience')}"}
        ld["learningResourceType"] = "실습 가이드"
    if typ == "SoftwareApplication":
        ld["applicationCategory"] = "WebApplication"; ld["operatingSystem"] = "Web"
    title = f"{head}{p['title']} | 김덕진 AI 강의·프로젝트"
    write(f"p/{p['id']}/index.html", page(f"p/{p['id']}/", title, claim + " " + p.get("summary", ""), body, ld, depth=2))


# ───────────────────────── about ─────────────────────────
def build_about():
    pr = profile
    n_lec = len(lectures)
    org_lines = "".join(f"<li><b>{E(l)}</b>: {' · '.join(E(o) for o in orgs[s])}</li>" for s, l in SECTORS.items() if orgs[s])
    faqs = [
        ("김덕진은 누구인가요?", f"{pr.get('intro')} 현재 {', '.join(pr.get('roles', [])[:4])} 등으로 활동합니다."),
        ("어떤 기관에서 AI 강의를 했나요?", f"이 사이트에 실습 페이지가 공개된 곳만 {n_orgs}곳입니다. " + " / ".join(f"{l}: {', '.join(orgs[s])}" for s, l in SECTORS.items() if orgs[s]) + ". 비공개로 진행한 강의는 여기에 적지 않았습니다."),
        ("강의는 어떤 방식인가요?", "강의마다 그 조직의 업무 언어로 된 실습 페이지를 새로 만들어 공개합니다. 참가자는 프롬프트를 눌러 복사하고 가상 연습 파일로 따라 하며, 강의가 끝난 뒤에도 같은 페이지로 복습할 수 있습니다. ChatGPT, Gemini, Claude, NotebookLM, MCP 연결, AI 에이전트 만들기, 바이브코딩까지 대상 수준에 맞춰 다룹니다."),
        ("강의나 자문은 어떻게 요청하나요?", f"IT커뮤니케이션연구소 {C.get('name','')} {C.get('title','')}에게 문의하시면 됩니다. 휴대전화 {C.get('mobile','')}, 사무실 {C.get('office','')}, 이메일 {pr.get('email')}."),
    ]
    body = f"""<main class="in">
<section class="hero" style="padding-bottom:10px">
<p class="kick">About · {E(pr.get('name_en'))} · {E(pr.get('handle'))}</p>
<h1>{E(NAME)}</h1>
<p class="lead"><b>{E(pr.get('tagline'))}</b><br>{E(pr.get('intro'))}</p>
</section>
<div class="prose">
<h2>하는 일</h2><ul>{''.join(f'<li>{E(r)}</li>' for r in pr.get('roles', []))}</ul>
<h2>방송</h2><ul>{''.join(f'<li>{E(b)}</li>' for b in pr.get('broadcasts', []))}<li>{E(pr.get('stats_note'))}</li></ul>
<h2>저서</h2><ul>{''.join(f'<li>『{E(b["t"])}』{(" · " + E(b["note"])) if b.get("note") else ""}</li>' for b in pr.get('books', []))}<li>{E(pr.get('writing_now'))}</li></ul>
<h2>강의하는 방식</h2></div>
<div class="meth">{''.join(f'<div><h3>{E(m["h"])}</h3><p>{E(m["p"])}</p></div>' for m in pr.get('method', []))}</div>
<div class="prose">
<h2>실습 페이지가 공개된 기관 ({n_orgs}곳)</h2><ul>{org_lines}</ul>
<p>전체 목록은 <a href="../#lecture">강의·실습</a>에서, 기관별 상세는 각 카드의 '자세히'에서 볼 수 있습니다.</p>
<h2>자주 묻는 질문</h2>
{''.join(f'<details><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q, a in faqs)}
<h2>강의·자문 문의</h2><ul><li>{CONTACT_HTML}</li><li>IT커뮤니케이션연구소 (ITCL)</li></ul>
<h2>채널</h2><ul>{''.join(f'<li><a href="{E(l["u"])}" rel="me noopener" target="_blank">{E(l["t"])}</a></li>' for l in pr.get('links', []))}</ul>
</div>
</main>"""
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "ProfilePage", "url": SITE + "/about/", "mainEntity": {"@id": SITE + "/about/#person"}},
        person_ld() | {"hasOccupation": [{"@type": "Occupation", "name": r} for r in pr.get("roles", [])],
                       "workExample": [{"@type": "Book", "name": b["t"]} for b in pr.get("books", [])]},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]},
    ]}
    write("about/index.html", page("about/", f"{NAME} 소개 · IT커뮤니케이션연구소 소장, AI 강사", pr.get("intro", ""), body, ld, depth=1))


# ───────────────────────── machine files ─────────────────────────
def build_machine():
    pr = profile
    L = [f"# {NAME} ({pr.get('name_en')}) · AI 강의와 프로젝트 아카이브", "",
         f"> {pr.get('intro')}", "",
         "## 인물", *[f"- {r}" for r in pr.get("roles", [])], *[f"- {b}" for b in pr.get("broadcasts", [])],
         "- 저서: " + ", ".join(f"『{b['t']}』" for b in pr.get("books", [])), f"- 강의·자문 문의: {CONTACT_TXT} · http://itcl.kr/", f"- 소개 페이지: {SITE}/about/", ""]
    for s, l in SECTORS.items():
        items = [p for p in lectures if p["sector"] == s]
        if not items: continue
        L.append(f"## 강의·실습 · {l}")
        L += [f"- [{p['org']} · {p['title']}]({SITE}/p/{p['id']}/): {p.get('date') or '날짜 미상'}, {p['audience']} 대상. {p['summary']}" for p in sorted(items, key=lambda x: x.get('date') or '', reverse=True)]
        L.append("")
    for sec in ("build", "lab", "family"):
        L.append(f"## {SECTIONS[sec][0]}")
        L += [f"- [{p['title']}]({SITE}/p/{p['id']}/): {p['summary']}" + (f" ({p['label']})" if p.get('label') else "") for p in projects if p["section"] == sec]
        L.append("")
    if inbox:
        L.append("## 정리 전 자료")
        L += [f"- [{p['title']}]({p['url']}): {p.get('date','')}" for p in inbox]
        L.append("")
    write("llms.txt", "\n".join(L))

    F = [f"# {NAME} · 전체 자료 상세", ""]
    for p in ALL:
        F += [f"## {(p.get('org') + ' · ') if p.get('org') else ''}{p['title']}", f"- 상세: {SITE}/p/{p['id']}/", f"- 원본: {p['url']}", f"- {sentence(p)}", f"- {p.get('summary','')}"]
        if p.get("tools"): F.append(f"- 도구: {', '.join(p['tools'])}")
        if p.get("topics"): F.append(f"- 주제: {', '.join(p['topics'])}")
        F.append("")
    write("llms-full.txt", "\n".join(F))

    urls = [(f"{SITE}/", LAST), (f"{SITE}/about/", LAST)] + [(f"{SITE}/p/{p['id']}/", p.get("date") or LAST) for p in ALL]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          "".join(f"<url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n")

    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot", "anthropic-ai", "PerplexityBot", "Perplexity-User", "Google-Extended", "Googlebot", "Bingbot", "Applebot", "Applebot-Extended", "Yeti", "Daum", "CCBot", "Meta-ExternalAgent"]
    write("robots.txt", "# 김덕진 AI 강의·프로젝트 아카이브: 검색엔진과 AI 크롤러 모두 환영합니다.\n" +
          "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + "User-agent: *\nAllow: /\n\n" + f"Sitemap: {SITE}/sitemap.xml\n")

    entries = "".join(
        f"<entry><title>{E((p.get('org') + ' · ') if p.get('org') else '')}{E(p['title'])}</title><link href=\"{SITE}/p/{p['id']}/\"/>"
        f"<id>{SITE}/p/{p['id']}/</id><updated>{fulld(p.get('date') or LAST)}T00:00:00+09:00</updated><summary>{E(p.get('summary',''))}</summary></entry>\n"
        for p in ALL[:30])
    write("feed.xml", f'<?xml version="1.0" encoding="utf-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom"><title>김덕진 · 새로 공개된 AI 강의 자료</title>'
          f'<link href="{SITE}/"/><id>{SITE}/</id><updated>{LAST}T00:00:00+09:00</updated><author><name>{NAME}</name></author>\n{entries}</feed>\n')


def main():
    write("assets/hub.css", CSS.strip() + "\n")
    # 상세 페이지는 매번 새로 만든다(삭제된 항목 정리)
    shutil.rmtree(os.path.join(ROOT, "p"), ignore_errors=True)
    build_index()
    for p in ALL:
        build_detail(p)
    build_about()
    build_machine()
    print(f"built: {len(projects)} curated + {len(inbox)} inbox → index, about, {len(ALL)} detail pages, llms.txt, sitemap.xml, robots.txt, feed.xml")


if __name__ == "__main__":
    main()
