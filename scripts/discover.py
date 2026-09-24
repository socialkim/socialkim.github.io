#!/usr/bin/env python3
"""새 레포 자동 발견 → data/inbox.json

GitHub 공개 API로 socialkim 계정의 레포를 읽어, GitHub Pages가 켜져 있거나(has_pages)
외부 홈페이지가 있는 레포 중 projects.json·exclude.json·inbox.json에 없는 것을 inbox에 추가한다.
페이지의 <title>, description, 첫 문단을 자동으로 뽑아 임시 제목·요지로 쓴다.

실행:  python3 scripts/discover.py      (환경변수 GITHUB_TOKEN이 있으면 사용)
"""
import json, os, re, html, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER = os.environ.get("HUB_GITHUB_USER", "socialkim")
PAGES = f"https://{USER}.github.io/"


def get(url, accept="application/json"):
    req = urllib.request.Request(url, headers={"User-Agent": "socialkim-hub", "Accept": accept})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "ignore")


def load(name, default):
    p = os.path.join(ROOT, "data", name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default


def clean(s):
    s = re.sub(r"<(script|style|svg|noscript|nav)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def sniff(url):
    try:
        s = get(url, "text/html")
    except Exception as e:
        return None
    t = re.search(r"<title[^>]*>(.*?)</title>", s, re.S | re.I)
    d = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)', s, re.I)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S | re.I)
    body = clean(s)
    return {
        "title": clean(t.group(1)) if t else "",
        "desc": html.unescape(d.group(1)).strip() if d else "",
        "h1": clean(h1.group(1)) if h1 else "",
        "text": body[:400],
    }


def main():
    projects = load("projects.json", [])
    exclude = set(load("exclude.json", {}).get("repos", []))
    inbox = load("inbox.json", [])
    known = {p["id"] for p in projects} | exclude
    inbox = [i for i in inbox if i["id"] not in known]  # 정리된 항목은 inbox에서 뺀다
    have = {i["id"] for i in inbox}

    repos, page = [], 1
    while True:
        batch = json.loads(get(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}"))
        if not batch:
            break
        repos += batch
        page += 1
        if page > 10:
            break

    added = []
    for r in sorted(repos, key=lambda r: r["created_at"]):
        n = r["name"]
        if n in known or n in have or r.get("fork") or r.get("archived"):
            continue
        home = (r.get("homepage") or "").strip()
        if r.get("has_pages"):
            url = f"{PAGES}{n}/"
        elif home.startswith("http") and "github.com" not in home:
            url = home
        else:
            continue  # 공개 페이지가 없는 레포는 건너뜀
        info = sniff(url)
        if not info:
            continue  # 404 등: 다음 실행에서 다시 시도
        title = info["h1"] or info["title"] or r.get("description") or n
        cands = [r.get("description") or "", info["desc"], info["title"]]
        summary = next((c for c in cands if len(c) >= 15), "") or info["text"][:160]
        item = {
            "id": n, "url": url, "repo": f"{USER}/{n}", "section": "new", "sector": "",
            "org": "", "audience": "", "title": title[:80], "summary": summary[:200],
            "date": r["created_at"][:10], "tools": [], "topics": [], "status": "auto",
            "page_title": info["title"][:120],
        }
        inbox.append(item)
        added.append(n)

    inbox.sort(key=lambda i: i["date"], reverse=True)
    with open(os.path.join(ROOT, "data", "inbox.json"), "w", encoding="utf-8") as f:
        json.dump(inbox, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"repos={len(repos)} inbox={len(inbox)} added={added}")


if __name__ == "__main__":
    main()
