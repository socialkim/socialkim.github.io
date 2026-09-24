#!/usr/bin/env python3
"""데이터 점검: 필수 필드·중복·금지 표현 검사. --links 를 붙이면 모든 링크의 HTTP 상태도 확인.

실행:  python3 scripts/check.py [--links]
"""
import json, os, sys, urllib.request, concurrent.futures as cf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(os.path.join(ROOT, "data", "projects.json"), encoding="utf-8"))
SECT = {"lecture": {"corp", "public", "univ", "media", "job"}, "build": None, "lab": None, "family": None}
REQ = ["id", "url", "section", "sector", "title", "summary", "date"]
BANNED = ["—", "**", "혁신적인", "획기적인"]
errs, ids = [], set()
for p in P:
    for k in REQ:
        if not p.get(k):
            errs.append(f"{p.get('id')}: '{k}' 비어 있음")
    if p["id"] in ids:
        errs.append(f"{p['id']}: id 중복")
    ids.add(p["id"])
    if p.get("section") not in SECT:
        errs.append(f"{p['id']}: section 값 오류 {p.get('section')}")
    elif SECT[p["section"]] and p.get("sector") not in SECT[p["section"]]:
        errs.append(f"{p['id']}: sector 값 오류 {p.get('sector')}")
    if p.get("section") == "lecture" and not (p.get("org") and p.get("audience")):
        errs.append(f"{p['id']}: 강의는 org·audience 필수")
    for b in BANNED:
        if b in p.get("summary", ""):
            errs.append(f"{p['id']}: summary에 '{b}' 사용")
    if p.get("section") == "family" and "수찬" in (p.get("title", "") + p.get("summary", "")):
        errs.append(f"{p['id']}: 아들 이름 노출")

if "--links" in sys.argv:
    def st(p):
        try:
            req = urllib.request.Request(p["url"], headers={"User-Agent": "socialkim-hub"})
            return p["id"], urllib.request.urlopen(req, timeout=20).status
        except Exception as e:
            return p["id"], str(e)[:40]
    with cf.ThreadPoolExecutor(12) as ex:
        for i, s in ex.map(st, [p for p in P if not p.get("hidden")]):
            if s != 200:
                errs.append(f"{i}: 링크 상태 {s}")

print("\n".join(errs) if errs else f"OK · {len(P)}개 항목 이상 없음")
sys.exit(1 if errs else 0)
