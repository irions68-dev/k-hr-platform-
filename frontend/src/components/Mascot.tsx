/**
 * 오리지널 마스코트 - 짱구 특유의 장난기·짙은 눈썹 "느낌"만 가져오되,
 * 실제 캐릭터 디자인(스파이크 머리, 빨강/노랑 배색 등)은 쓰지 않는다.
 * 대신 이 앱이 전화응대 헬프데스크라는 점에 맞춰 헤드셋을 씌워 완전히
 * 새로운 오리지널 캐릭터로 만들었다.
 */
export function Mascot({ size = 40, className }: { size?: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 120 120"
      className={className}
      role="img"
      aria-label="마스코트"
    >
      {/* 볼록 단발머리 */}
      <path
        d="M60 14c-24 0-38 16-38 36 0 6 1 11 3 16 2-3 5-5 8-5 2-8 3-16 3-16s7 6 24 6 24-6 24-6 1 8 3 16c3 0 6 2 8 5 2-5 3-10 3-16 0-20-14-36-38-36Z"
        fill="oklch(0.86 0.05 300)"
      />

      {/* 얼굴 */}
      <circle cx="60" cy="62" r="34" fill="oklch(0.93 0.03 60)" />

      {/* 볼터치 */}
      <circle cx="34" cy="70" r="7" fill="oklch(0.82 0.09 20)" opacity="0.55" />
      <circle cx="86" cy="70" r="7" fill="oklch(0.82 0.09 20)" opacity="0.55" />

      {/* 짙은 일자눈썹 - 장난기 포인트 */}
      <rect x="34" y="52" width="18" height="6" rx="3" fill="oklch(0.3 0.02 300)" />
      <rect x="68" y="52" width="18" height="6" rx="3" fill="oklch(0.3 0.02 300)" />

      {/* 눈 (한쪽은 웃는 눈) */}
      <circle cx="43" cy="64" r="4" fill="oklch(0.3 0.02 300)" />
      <path
        d="M69 64c2-3 5-3 7 0"
        stroke="oklch(0.3 0.02 300)"
        strokeWidth="3"
        strokeLinecap="round"
        fill="none"
      />

      {/* 코 */}
      <circle cx="60" cy="72" r="2" fill="oklch(0.55 0.03 40)" />

      {/* 장난스러운 미소 */}
      <path
        d="M48 80c4 6 20 6 24 0"
        stroke="oklch(0.3 0.02 300)"
        strokeWidth="3"
        strokeLinecap="round"
        fill="none"
      />

      {/* 헤드셋 - 전화응대 헬프데스크 컨셉 */}
      <path
        d="M24 58c0-22 16-38 36-38s36 16 36 38"
        stroke="var(--primary)"
        strokeWidth="5"
        strokeLinecap="round"
        fill="none"
      />
      <rect x="17" y="54" width="11" height="20" rx="5.5" fill="var(--primary)" />
      <rect x="92" y="54" width="11" height="20" rx="5.5" fill="var(--primary)" />
      <path
        d="M97 74v6c0 5-4 8-9 8h-4"
        stroke="var(--primary)"
        strokeWidth="4"
        strokeLinecap="round"
        fill="none"
      />
      <circle cx="82" cy="88" r="3.5" fill="var(--primary)" />
    </svg>
  );
}
