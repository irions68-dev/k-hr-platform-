# 배포 가이드

프론트엔드는 Cloudflare Pages(정적 호스팅), 백엔드는 FastAPI를 지원하는
Python 호스팅(Render 권장)에 배포합니다. Cloudflare Workers는 ChromaDB·
fastembed 같은 네이티브 의존성을 지원하지 않아 백엔드를 그대로 올릴 수
없습니다.

## 1. 백엔드 배포 (Render) — 계정 생성이 필요해 직접 진행해주세요

1. https://dashboard.render.com 가입/로그인 (GitHub 계정으로 가능)
2. 이 저장소를 GitHub에 push (아직 안 했다면 `git remote add origin <repo-url>` 후 push)
3. Render 대시보드에서 **New +** → **Blueprint** → 이 저장소 선택
   (`backend/render.yaml`을 자동으로 인식합니다)
4. 배포 전 환경변수 3개를 입력하세요:
   - `GEMINI_API_KEY` — 기존에 쓰던 값
   - `APP_PASSWORD` — **반드시 설정**. 비워두면 인터넷에 인증 없이 노출됩니다.
   - `ALLOWED_ORIGINS` — 일단 비워두고 2단계에서 Cloudflare Pages 주소가 나오면 채웁니다
5. 배포 완료 후 나오는 URL(`https://k-hr-backend-xxxx.onrender.com` 형태)을 기록해두세요

**무료 플랜 주의사항**: Render 무료 웹서비스는 15분 미사용 시 슬립되고,
다음 요청 시 재기동에 20~30초 정도 걸립니다(전화 중 첫 질문만 느릴 수 있음).
또한 무료 플랜은 영구 디스크가 없어 재배포할 때마다 사례노트·수험학습
데이터가 초기화됩니다 — 이 데이터가 중요해지면 유료 플랜(디스크 추가)으로
전환하거나 알려주시면 구조를 조정하겠습니다.

## 2. 프론트엔드 배포 (Cloudflare Pages) — 여기부터는 제가 대신 실행 가능

1단계에서 받은 백엔드 URL을 알려주시면:
```bash
# frontend/.env.production 생성
echo "NEXT_PUBLIC_API_BASE_URL=https://<받은 URL>" > frontend/.env.production

cd frontend
npm run build          # out/ 디렉토리 생성 (정적 export)
npx wrangler pages deploy out --project-name=k-hr-guard
```

**⚠️ `.env.local`을 절대 만들지 마세요** — Next.js는 `.env.local`을
`.env.production`보다 우선시켜서, 로컬 개발 편의로 `.env.local`을 만들어두면
`npm run build`(프로덕션 빌드)도 그 값을 그대로 써버립니다(2026-08-20 실제로
이 문제로 로그인이 안 되는 사고 발생 — `.env.local`에 남아있던
`localhost:8010`이 프로덕션 빌드에 그대로 박혀서 배포됨). 로컬 개발용
URL은 반드시 `.env.development`에 넣으세요(`next dev`에서만 로드되고
`next build`에는 영향 없음) — `.env.development.example` 참고.
이 PC엔 Cloudflare Wrangler CLI가 이미 로그인되어 있어(irions68@gmail.com)
제가 바로 실행할 수 있습니다. 배포되면 `https://k-hr-guard.pages.dev` 같은
URL이 나옵니다.

## 3. 마무리 — CORS 연결

Cloudflare Pages 주소가 나오면 Render 대시보드에서 `ALLOWED_ORIGINS`를
`https://k-hr-guard.pages.dev`로 설정하고 재배포(자동 재시작)합니다.
그래야 프론트가 백엔드를 CORS 없이 호출할 수 있습니다.

## 재배포할 때마다 할 일

- 법령 코퍼스가 바뀌면: 백엔드 배포 후 `POST /legal-qa/ingest-sample-corpus` 한 번 호출
  (무료 플랜은 디스크가 초기화되므로 배포마다 필요)
- 프론트만 바뀌면: `cd frontend && npm run build && npx wrangler pages deploy out --project-name=k-hr-guard`
