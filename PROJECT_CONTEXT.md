# PROJECT_CONTEXT · socialkim.github.io 강의·프로젝트 허브

> **이 문서는 다른 AI·CLI·클로드 서비스가 이 작업을 이어받을 때 가장 먼저 읽는 파일이다.**
> 히스토리, 구조, 운영 규칙, 결정, 현재 상태를 한 곳에 모았다. 세부 명세는 `_system/` 문서가 원본이다.
> 마지막 갱신: 2026-10-02 · 작성: Claude(Cowork) · 소유자: 김덕진(kimdukjin)

---

## 0. 30초 요약 (AI용)

- **무엇:** 김덕진 소장(IT커뮤니케이션연구소 ITCL)이 강의·방송·가족 프로젝트 때 만든 웹페이지들을 한곳에 모아 보여 주는 정적 사이트. 주소 https://socialkim.github.io
- **왜:** 사람(섭외 담당자·수강생)과 AI 검색엔진(ChatGPT·Claude·Perplexity 등)이 "누가, 어디서, 무엇을 가르쳤나"를 텍스트로 읽고 인용하게 하려고. 목표는 "AI 강사 추천"을 물으면 계속 추천되는 것.
- **어떻게:** `data/*.json`(원본) → `scripts/build.py`(파이썬 표준 라이브러리만) → 정적 HTML·llms.txt·sitemap 생성. GitHub Actions가 매일 09:00 KST에 새 레포를 자동 발견한다. 정리(분류·설명 작성)는 클로드가 요청 시 한다.
- **가장 중요한 규칙 3개:**
  1. 생성물(`index.html`, `about/`, `p/`, `llms*.txt`, `sitemap.xml`, `robots.txt`, `feed.xml`, `assets/hub.css`)은 **절대 직접 고치지 않는다.** 항상 `data/*.json`을 고치고 build를 돌린다.
  2. 작업 전 반드시 `git pull` (Actions가 매일 커밋한다).
  3. 아들은 "초등학생 아들"로만 쓴다. 이름·나이·학년·학교 금지.

---

## 1. 문제와 진짜 필요 (디깅 결과)

| 항목 | 내용 |
|---|---|
| 원래 문제 (2026-09-24 시점) | 허브가 4월의 10개 카드에서 멈춤. 실제 레포 73개, 웹으로 열리는 페이지 58개. 카드가 JS로만 그려져 AI 크롤러에겐 "자료 없음"으로 읽힘. robots·sitemap·llms.txt·JSON-LD 없음. 404·중복·의미 불명 레포 혼재 |
| 사람의 특수성 | 소장님은 강의 직전·직후에 클로드 코드로 레포를 급히 만들어 올린다. **이름 규칙·설명 입력·허브 수정을 요구할 수 없다.** |
| 독자 셋 | 섭외 담당자(어떤 기관·주제를 해 봤나) / 수강생(내 강의 자료가 어디 있나) / AI 검색엔진(텍스트로 읽히는 사실) |
| 진짜 필요 (한 문장) | **레포를 만들기만 하면, 사람과 AI가 읽을 수 있는 이력 한 줄이 저절로 쌓인다.** |
| 개입 지점 | 레포가 생기는 순간(이미 하는 행동) → 매일 자동 발견 / 정리는 몰아서 "허브 정리해줘" 한마디 |
| 성공 기준 | ① JS 없이 HTML만 읽어도 모든 프로젝트·기관명·날짜가 보인다 ② 새 레포가 24시간 안에 허브에 뜬다 ③ 페이지마다 AI가 인용할 근거 문장(누가·어디서·무엇을)이 있다 |

이 작업은 소장님의 **디깅 방법론**(문제 디깅 → 브리프 → 계획서 → 가이드라인 → 제작, 명세 우선)으로 진행했다. 새 기능도 같은 순서로 간다.

---

## 2. 위치 지도 (어디에 무엇이 있나)

| 무엇 | 위치 | 비고 |
|---|---|---|
| **작업 레포 (메인 폴더)** | 소장님 PC `C:\Users\kimdu\claude\socialkim\socialkim.github.io` | Cowork device_bash에서는 `$HOME/mnt/socialkim/socialkim.github.io` |
| GitHub | https://github.com/socialkim/socialkim.github.io (branch `main`) | 공개 레포. GitHub Pages로 배포 |
| 공개 사이트 | https://socialkim.github.io | 홈 / `/about/` / `/p/<id>/` / `/llms.txt` / `/llms-full.txt` / `/card/` |
| 올리기 배치 파일 | `C:\Users\kimdu\claude\socialkim\허브_올리기.bat` | 더블클릭 → `pull --rebase -X theirs` → `push`. 레포 밖(부모 폴더)에 있음 |
| 명세 원본 | 레포 `_system/01_브리프.md`, `02_계획서.md`, `03_가이드라인.md`, `README.md`(운영 설명서) | `_`로 시작해 Pages에 공개되지 않음(GitHub 레포에서는 보임) |
| 명세 사본 | claude.ai 프로젝트 "덕진 강의내용 홍보+아카이빙 페이지작업" → 문서 `socialkim-hub/` | 클로드 채팅·Cowork에서 읽힘 |
| 정리 스킬 | 클로드 스킬 `socialkim-hub-update` | "허브 업데이트해줘", "또 작업했어" 등에서 발동 |
| **헷갈리기 쉬운 것** | `C:\Users\kimdu\claude\socialkim.github.io` (빈 폴더) | 실제 레포 아님. 위의 `socialkim\socialkim.github.io`가 진짜 |

같은 `socialkim` 폴더의 형제 프로젝트(이 허브와 별개):
- `kdj-global-suite/` — 김덕진 답변 연대기(유튜브 방송 91편 분석) + Global 김덕진 크롬 확장. 별도 레포 `socialkim/kdj-global-suite`, 허브에는 `build` 항목으로 실려 있음.
- `lecture-hub/` — 2026-03에 시도한 Next.js+Prisma 강의자료 배포·수강생 관리 서비스. git 레포가 아니며 현재 허브와 연결되지 않음.

---

## 3. 히스토리

| 날짜 | 일 |
|---|---|
| 2026-03-26 | (전신) `lecture-hub` Next.js 서비스 설계. 수강생 정보를 받고 자료 링크를 주는 방식. 배포·운영으로 이어지지 않음 |
| 2026-04-24 | `socialkim.github.io` 첫 배포: "AI 강의 자료실 포털" (JS로 그리는 카드 10개) |
| 2026-04-26 | 숭실대 박사과정 AI 연구 가이드, NotebookLM HR 실습 가이드 추가 |
| 2026-05-18 | 디지털 명함 `/card/` (vCard QR, ITCL 연락처·교수 직함) |
| 2026-07-13 | 레포 안에 직접 올린 콘텐츠: `park-jungho-voyage/`(게임, 소스는 `_game-src/`), `stock-concepts-lab/` |
| 2026-07-21 | `understanding-ocean-game/` (게임 스크립트 분할 업로드 + 개발비 시뮬레이션 문서) |
| **2026-09-24** | **허브 전면 개편** (디깅 → 브리프·계획서·가이드라인 작성 → 제작). 정적 아카이브 + 매일 자동 발견 체계 도입. 59개로 시작 → 같은 날 문의처 변경(info@itcl.kr·심성은 팀장), 검색엔진 인증 메타 자리, ChatGPT로 만든 작업 17개 추가 + `made_with` 배지, 날짜 보강, '가족과 함께' 항목 추가, 저서·교보문고·litt.ly·오픈채팅 홍보 블록 |
| 2026-09-29 | Actions 자동 갱신 (코윈테크 등) |
| 2026-10-02 | 자동 갱신 + 클로드 정리 2건(서울시립대 수업 포털, AI 협업 용어 200선). 운영 설명서에 `허브_올리기.bat` 안내 추가. 이 문서 작성 |

커밋 기록은 `git log --date=short --pretty='%ad %h %s'`로 확인. 정리 커밋 메시지 형식은 `hub: +N 추가, M 정리 (YYYY-MM-DD)`, 자동 커밋은 `hub: auto update YYYY-MM-DD`.

---

## 4. 시스템 구조

```
[소장님이 새 레포 생성 + Pages 켬]
        │  (매일 00:00 UTC = 09:00 KST, 또는 data/·scripts/ push 시)
        ▼
.github/workflows/update-hub.yml
  1) scripts/discover.py   GitHub API로 socialkim 계정 레포 중 has_pages인 것 조회
                           → projects.json·exclude.json에 없는 것을 data/inbox.json에 추가
                             (페이지 <title>·설명·첫 문단 자동 추출)
  2) scripts/build.py      data/*.json → 정적 HTML·기계용 파일 생성
  3) scripts/check.py      필수 필드·중복·금지 표현·아들 이름 노출 검사
  4) 변경 있으면 커밋(socialkim-hub-bot) → Pages 빌드 요청
        ▼
[클로드 정리 (요청 시)]  inbox 항목을 실제로 열어 읽고 → projects.json으로 옮겨 분류·요약 작성
```

### 파일 지도

| 경로 | 역할 | 누가 고치나 |
|---|---|---|
| `data/projects.json` | 정리된 원본 목록 (배열) | 클로드 |
| `data/inbox.json` | 자동 발견된 정리 전 레포 | Actions (자동) |
| `data/exclude.json` | 허브에서 뺄 레포 (`repos` 배열) | 클로드 |
| `data/profile.json` | 인물 소개·직함·저서·방송·문의처·링크·검색엔진 인증(`verify`) | 클로드 (소장님 요청 시) |
| `scripts/discover.py` · `build.py` · `check.py` | 발견 · 생성 · 점검 (`check.py --links`로 링크 HTTP 검사) | 개발 시에만 |
| `.github/workflows/update-hub.yml` | 매일 자동 실행 | 개발 시에만 |
| `_system/` | 명세 문서(비공개 폴더) | 결정이 바뀔 때 |
| 생성물: `index.html`, `about/`, `p/<id>/`, `llms.txt`, `llms-full.txt`, `sitemap.xml`, `robots.txt`, `feed.xml`, `assets/hub.css` | **직접 수정 금지** | build.py |
| 레포 직접 콘텐츠: `card/`, `park-jungho-voyage/`, `_game-src/`, `stock-concepts-lab/`, `understanding-ocean-game/` | 허브 이전부터 이 레포에 직접 올린 페이지 | 해당 작업 시 |

### 정보 구조

| 페이지 | 역할 | 주 독자 |
|---|---|---|
| `/` | 한 줄 정체성, 숫자 요약, 최근 공개, 전체 목록(분야 필터), 기관 색인 | 섭외 담당자·수강생 |
| `/about/` | 약력·저서·방송·일하는 방식·FAQ (`ProfilePage`+`Person`+`FAQPage` JSON-LD) | AI 검색엔진·섭외 담당자 |
| `/p/<id>/` | 첫 문단 = 근거 문장 ("IT커뮤니케이션연구소 김덕진 소장이 ○년 ○월 ○일 △△ 대상 □□에서 사용한 실습 가이드입니다"), `LearningResource` JSON-LD | AI 검색엔진 |
| `llms.txt` / `llms-full.txt` | AI용 요약과 전체 목록 | LLM 크롤러 |
| `robots.txt` | GPTBot·ClaudeBot·PerplexityBot·Google-Extended 등 명시 허용 | 크롤러 |

### 분류 체계 (section → sector)

- `lecture` 강의·실습: `corp` 기업·금융·투자사 / `public` 정부·공기업·지자체·협회·재단·교회·도서관 / `univ` 대학 수업·교직원·대학원·교재 / `media` 언론사 / `job` 특정 조직 없는 직무 대상
- `build` 만든 것: `service`(서비스·MCP·도구·컨설팅 페이지) / `brand`(브랜드 캠페인)
- `lab` 실험실: `game` / `edu` / `record` — 방송용 제작물은 `label: "방송 연계"`, 비공식 패러디는 `label: "팬메이드"`, 가상 시안은 `"가상 프로그램"`·`"실습 예시"`
- `family` 가족과 함께: 초등학생 아들과 만든 것, 가족 북토크

### projects.json 한 항목

```json
{
  "id": "cowin",                                  // 레포 이름 또는 서브도메인 (고유)
  "url": "https://socialkim.github.io/cowin/",
  "repo": "socialkim/cowin",                      // GitHub 밖 작업이면 null
  "section": "lecture", "sector": "corp",
  "org": "코윈테크", "audience": "임직원",          // lecture는 둘 다 필수
  "title": "AI, 내 업무에 이렇게 써봅니다",
  "summary": "두 문장 이내. 누구를 위해 무엇을 / 무엇을 따라 할 수 있는지.",
  "date": "2026-09-29",                           // YYYY-MM-DD 또는 YYYY-MM, 모르면 빈 값
  "tools": ["ChatGPT"], "topics": ["업무 자동화"],
  "status": "curated"                             // 자동 발견 상태는 "auto"
}
```
선택 필드: `label`, `extra:[{"t":..,"u":..}]`(짝 작업 서로 잇기), `hidden:true`, `org_generic:true`(일반 명칭 기관, 기관 색인에서 제외), `made_with`("ChatGPT"/"Claude"), `claim`(상세 페이지 첫 문장을 직접 쓸 때). 미래 날짜면 근거 문장이 자동으로 "진행할 예정인"이 된다.

---

## 5. 운영 루틴

### 소장님이 하는 일
평소처럼 레포를 만들고 GitHub Pages를 켠다. 끝. 가끔 "socialkim 허브 정리해줘"라고 말한다. 클로드가 커밋해 두면 `허브_올리기.bat`을 더블클릭해 올린다.

### AI가 하는 정리 루틴 (스킬 `socialkim-hub-update`와 동일)
```bash
cd <레포>
git pull --ff-only                 # 0) .git/index.lock 때문에 실패하면 잠금 파일부터 정리
python3 scripts/discover.py        # 1) inbox 갱신 (GITHUB_TOKEN 있으면 사용)
# 2) inbox 항목·받은 링크를 실제로 열어 읽고 projects.json으로 옮긴다.
#    JS로 그리는 페이지는 데이터 파일(courses.json 등)까지 확인.
#    중복·테스트·404는 exclude.json에 추가.
python3 scripts/build.py           # 3) 생성
python3 scripts/check.py --links   # 4) OK가 나와야 함
git add -A && git commit -m "hub: +N 추가, M 정리 (YYYY-MM-DD)"
# 5) push는 소장님 PC에서 (허브_올리기.bat 또는 git push). 클라우드 세션은 push 권한이 없을 수 있음
```
- GitHub 밖 작업(ChatGPT 사이트 `*.socialkim.chatgpt.site`, Vercel 등)은 자동 발견되지 않는다. 링크를 받아 수동으로 넣고 `made_with`를 적는다. 링크 없이 "ChatGPT로도 했어"라고 하면 링크를 한 번만 묻는다.
- 날짜를 모르면 구글 캘린더(kimdukjin@itcl.kr의 '김덕진 - 강의/코칭/멘토링', '김덕진-방송', '김덕진-프로젝트/업무미팅', '개인일정-김덕진')에서 찾는다. 그래도 없으면 비워 두고 묻는다. **추측한 날짜는 쓰지 않는다.**
- 마치면 추가·정리한 항목(분류·날짜), 숨긴 것, 확인이 필요한 것, push 필요 여부를 짧게 보고한다.

### 자주 오는 요청
| 요청 | 처리 |
|---|---|
| "이 자료 빼줘" | 해당 항목 `hidden: true` → build |
| 소개·저서·방송·문의처 변경 | `data/profile.json`(`books`, `contact`, `cta`, `links`, `roles`) → build |
| 검색엔진 인증 코드 | `profile.json`의 `verify.google/naver/bing`에 content 값만 → build |
| 새 실습 페이지 제작 | 페이지 하단에 `_system/03_가이드라인.md` E절의 허브 링크 + JSON-LD 조각을 넣도록 권한다 |

---

## 6. 가드레일 (절대 규칙)

- 생성물 직접 수정 금지. 원본은 `data/*.json`.
- 아들: "초등학생 아들"로만. 이름·나이·학년·학교 금지 (`check.py`가 검사).
- summary 금지 표현: 대시(—), 별표 강조(`**`), "혁신적인·획기적인" (`check.py`가 검사).
- 금액, 수강생 개인정보, 비공개 자료 내용은 싣지 않는다.
- 연락처는 문의 담당만: info@itcl.kr, 심성은 팀장(번호는 `profile.json`의 `contact`), litt.ly/kimdukjin, 카카오 오픈채팅. **김덕진 개인 번호·개인 메일은 쓰지 않는다.**
- 기관명은 실명 공개가 원칙. 숨길 곳만 `hidden: true`.
- 이름 표기 통일: 김덕진 / Kim Dukjin / kimdukjin (kimdeokjin 아님), 소속 IT커뮤니케이션연구소(ITCL).
- 확인하지 않은 책·서비스 소개 문구를 지어내지 않는다.
- 디자인 (개인 브랜드 방향 J "네이비와 하늘"): 종이 #FAFBFC, 네이비 #0F1B2D, 코발트 #2457C5(링크·버튼), 하늘 #57D0FF(배지), 하늘 옅음 #EAF7FE, 빨강 #E5261F는 로고 점에만. Pretendard / Space Grotesk / JetBrains Mono. 이모지 아이콘 금지. 카드 = 기관 · 제목 · 요지 한 줄 · 날짜.

---

## 7. 결정 로그

| 날짜 | 결정 |
|---|---|
| 2026-09-24 | 기관명 모두 실명 공개(뺄 곳만 숨김) |
| 2026-09-24 | 아들 프로젝트는 "초등학생 아들"로만 표기 |
| 2026-09-24 | 방송 소재 게임은 '실험실'에 팬메이드 표기로 공개 |
| 2026-09-24 | 자동화 수준: 자동 발견(매일) + 클로드 정리(요청 시). 완전 자동 분류는 하지 않음 |
| 2026-09-24 | 문의 연락처를 info@itcl.kr · 심성은 팀장으로 통일 (개인 메일 kimdukjin@itcl.kr 대신) |
| 2026-09-24 | GitHub 밖 작업도 허브에 싣고 만든 AI(`made_with`)를 배지로 표시 |
| 2026-09-24 | 섹션 이름 '아들과 함께' → '가족과 함께' (가족 북토크 포함) |
| 2026-10-02 | push는 `허브_올리기.bat`로 (pull --rebase -X theirs 후 push) |

허브에서 뺀 레포(`exclude.json`): aving, china-ai(404) · hankookilbo-media-tf1, jangjang, janreu-yeouido-soccer, business-card-, lunchch, unch-weather-app, weather-lunch-finder(중복) · itcl-hp2, toss-test, sobang, sch_faculty, pharma-care(테스트/빈 레포) · socialkim.github.io(허브 자신).

---

## 8. 현재 상태 (2026-10-02 스냅샷)

- 항목 **80개**, 숨김 0, inbox 비어 있음.
  - 강의·실습 45 (기업 15 · 대학 12 · 공공 11 · 직무 4 · 언론 3)
  - 만든 것 18 (서비스 16 · 브랜드 2)
  - 실험실 12 (게임 9 · 교육 2 · 기록 1)
  - 가족과 함께 5
  - `made_with`: ChatGPT 19, Claude 2 (나머지는 미표기)
- 최근 항목: 코윈테크(9/29), 서울시립대 수업 포털·AI 협업 용어 200선(10/2).
- 로컬 `main`은 `origin/main`과 같은 상태(마지막 fetch 기준).
- 숫자는 바뀐다. 최신 값은 아래로 확인:
  ```bash
  python3 -c "import json,collections;p=json.load(open('data/projects.json'));print(len(p),collections.Counter((i['section'],i['sector']) for i in p))"
  ```

## 9. 열린 것 (아직 안 정해졌거나 안 한 것)

- 검색엔진 인증 코드(`profile.json` → `verify`)가 비어 있음. Google Search Console·네이버 서치어드바이저·Bing 등록은 소장님 계정이 필요.
- 성공 기준 ③(AI가 실제로 추천·인용하는가)을 정기적으로 확인하는 방법은 아직 없음.
- 개별 실습 레포에 허브 footer·JSON-LD 조각(가이드라인 E절)을 넣는 작업은 권장만 했고 일괄 적용하지 않음.
- 레포 루트의 미추적 파일 `httpsocialkim.github.io 페이지를 업데이트 해.txt`(4월에 쓴 요청 메모). 지워도 되는지 미확인.
- 소장님 PC에서 `.git/index.lock`이 남아 git 명령이 실패할 때가 있음 → 잠금 파일 삭제 필요(Cowork에서는 삭제 권한 요청 후).

---

## 10. 연관 시스템

| 시스템 | 관계 |
|---|---|
| 클로드 프로젝트 '강의 자료 자판기', '덕진 AI 강의 커리큘럼 자판기' | 강의 실습 페이지가 만들어지는 곳. 결과 레포가 이 허브로 흘러 들어온다 |
| 스킬 `lecture-material-pipeline`, `lecture-digging-design`, `d4u-ui-design`, `itcl-pptx-design` | 강의자료·실습 페이지 제작 스킬 (허브와 별개, 산출물이 허브에 실림) |
| 스킬 `problem-digging`, `spec-first-pipeline` | 이 허브를 설계한 방법론 |
| 디지털 김덕진 (`C:\Users\kimdu\claude\디지털-김덕진\`, 규칙 `AGENTS.md`·맥락 `PROJECT_CONTEXT.md`) | 별도 시스템. 방송대본·카톡메모 지식베이스. 허브와 직접 연동되지 않음 |
| 슬랙 강의·방송 요청 → 원드라이브 폴더("YYYY.MM.DD 기관명 (NNmin)") | 강의 일정·기관명·날짜의 출처 |
| 구글 캘린더 | 날짜 확인용 (위 5절) |

---

## 11. 도구별 시작 방법

- **Claude Code / Codex / 기타 CLI (로컬):** 레포 폴더에서 이 파일 → `_system/01~03` 순으로 읽고 5절 루틴을 따른다. 파이썬 3 표준 라이브러리만 있으면 된다(설치 없음).
- **클라우드 CLI / 다른 PC:** `git clone https://github.com/socialkim/socialkim.github.io.git` 후 동일. push 권한이 없으면 커밋까지만 하고 소장님께 push를 부탁한다.
- **Claude Cowork:** 소장님 PC의 `socialkim` 폴더가 연결돼 있으면 device_bash로 `$HOME/mnt/socialkim/socialkim.github.io`에서 작업. 스킬 `socialkim-hub-update`가 자동으로 붙는다.
- **claude.ai 채팅 / 다른 AI 채팅:** 이 파일을 붙여 넣거나, 프로젝트 "덕진 강의내용 홍보+아카이빙 페이지작업"의 `socialkim-hub/` 문서를 참고. 코드 실행이 없으면 `projects.json`에 넣을 항목(JSON)을 만들어 주는 데까지만 한다.
- **ChatGPT로 만든 새 작업을 넣을 때:** 링크와 강의 날짜·기관을 함께 넘기면 된다.

## 12. 이 문서 갱신 규칙

- 결정이 바뀌면 7절에 한 줄 추가하고, 원본 `_system/` 문서와 claude.ai 프로젝트 `socialkim-hub/` 문서도 같이 고친다.
- 큰 작업(구조 변경, 새 섹션, 새 자동화)을 마치면 3절 히스토리와 8절 스냅샷을 갱신한다.
- 일상적인 항목 추가만으로는 갱신하지 않아도 된다(숫자는 8절 명령으로 확인).
