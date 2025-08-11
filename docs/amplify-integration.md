## Amplify Gen2 연동 가이드

### API 호출 (Next.js Server Component)

```ts
// app/actions/ocr.ts
export async function runOCR(file: File) {
  const token = await getIdToken(); // Cognito 가정
  const form = new FormData();
  form.append("file", file);
  form.append("lang", "en");
  const res = await fetch(process.env.OCR_API + "/ocr", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: form,
    cache: "no-store",
  });
  if (!res.ok) throw new Error("OCR failed");
  return res.json();
}
```

### CORS

- ALB/백엔드에서 Amplify 도메인 허용(`ALLOWED_ORIGINS`)
- 프리플라이트: `OPTIONS` 허용, 헤더 노출 설정

### 인증

- 권장: Amplify Auth(Cognito) → JWT 검증 (FastAPI 미들웨어)
- 대안: API Gateway + API Key

### AppSync(GraphQL) 대안

- Lambda Resolver에서 ECS 엔드포인트 호출(프록시)
- 서버 컴포넌트/액션과 비교하여 캐싱/권한 요구에 따라 선택
