# socialkim.github.io 허브 운영 설명서

이 폴더(`_system/`)는 사이트에 공개되지 않습니다(밑줄로 시작하는 폴더는 GitHub Pages가 건너뜀).

## 파일 지도
| 경로 | 역할 | 누가 고치나 |
|---|---|---|
| `data/projects.json` | 정리된 원본 목록 (59개로 시작) | 클로드 |
| `data/inbox.json` | 자동 발견된 정리 전 레포 | 자동 (Actions) |
| `data/exclude.json` | 허브에서 뺄 레포 | 클로드 |
| `data/profile.json` | 인물 소개·저서·방송·링크 | 클로드 (소장님 요청 시) |
| `scripts/discover.py` | 새 레포 찾기 | |
| `scripts/build.py` | HTML·llms.txt·sitemap 생성 | |
| `scripts/check.py` | 데이터 점검 (`--links`로 링크 검사) | |
| `.github/workflows/update-hub.yml` | 매일 09:00 자동 실행 | |
| `index.html`, `about/`, `p/`, `llms*.txt`, `sitemap.xml`, `robots.txt`, `feed.xml`, `assets/hub.css` | **생성물. 직접 고치지 않음** | build.py |

## 자주 하는 일
- 새 레포 반영: 아무것도 안 해도 다음 날 아침 '새로 올라온 자료'에 '정리 전'으로 뜬다.
- 정리: 클로드에게 "socialkim 허브 정리해줘" → inbox를 읽고 projects.json으로 옮겨 분류·설명 작성 → build → check.
- 특정 자료 숨기기: projects.json에서 해당 항목에 `"hidden": true`.
- 소개 문구 바꾸기: profile.json 수정 후 build.
- 수동으로 돌리기: GitHub > Actions > update-hub > Run workflow.

## 주의
- Actions가 매일 커밋하므로, PC에서 작업하기 전에 `git pull`을 먼저 한다.
- 기준 문서: `01_브리프.md` → `02_계획서.md` → `03_가이드라인.md`.
