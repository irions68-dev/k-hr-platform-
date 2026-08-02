import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Cloudflare Pages는 정적 파일 호스팅이라 SSR 없이 클라이언트에서 백엔드
  // API를 직접 호출하는 이 앱 구조엔 정적 export가 가장 간단하고 저렴하다.
  output: "export",
};

export default nextConfig;
