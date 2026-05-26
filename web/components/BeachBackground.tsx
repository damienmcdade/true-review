'use client';

import { useMemo } from 'react';

/**
 * Pure-SVG/CSS animated beach backdrop.
 * - No external assets (copyright-free).
 * - Vector-based, so it renders crisp at 1080p, 4K, and beyond.
 * - Continuously animated: sky gradient drifts, sun pulses, four wave layers
 *   flow at different speeds, and glints scatter across the water.
 * - Respects prefers-reduced-motion.
 */
export default function BeachBackground() {
  // Pre-compute glint positions so they're stable per render.
  const glints = useMemo(
    () =>
      Array.from({ length: 18 }, (_, i) => ({
        id: i,
        left: `${(i * 53) % 100}%`,
        top: `${30 + ((i * 17) % 35)}%`,
        delay: `${(i * 0.8) % 8}s`,
        duration: `${4 + ((i * 1.3) % 5)}s`
      })),
    []
  );

  return (
    <div className="beach" aria-hidden>
      <div className="sun" />

      <svg
        className="waves"
        viewBox="0 0 1600 600"
        preserveAspectRatio="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Furthest wave — deepest ocean */}
        <g className="wave w4">
          <path
            d="M-800 360 Q -600 320 -400 360 T 0 360 T 400 360 T 800 360 T 1200 360 T 1600 360 T 2000 360 T 2400 360 V600 H-800Z"
            fill="#1f5d6e"
            opacity="0.85"
          />
        </g>
        {/* Mid-distance wave */}
        <g className="wave w3">
          <path
            d="M-800 420 Q -600 380 -400 420 T 0 420 T 400 420 T 800 420 T 1200 420 T 1600 420 T 2000 420 T 2400 420 V600 H-800Z"
            fill="#3a8fa3"
            opacity="0.9"
          />
        </g>
        {/* Near wave */}
        <g className="wave w2">
          <path
            d="M-800 470 Q -600 440 -400 470 T 0 470 T 400 470 T 800 470 T 1200 470 T 1600 470 T 2000 470 T 2400 470 V600 H-800Z"
            fill="#6cb6b8"
            opacity="0.9"
          />
        </g>
        {/* Foamy shore */}
        <g className="wave w1">
          <path
            d="M-800 510 Q -600 490 -400 510 T 0 510 T 400 510 T 800 510 T 1200 510 T 1600 510 T 2000 510 T 2400 510 V600 H-800Z"
            fill="#bfe6e2"
            opacity="0.95"
          />
        </g>
      </svg>

      {glints.map((g) => (
        <span
          key={g.id}
          className="glint"
          style={{
            left: g.left,
            top: g.top,
            animationDelay: g.delay,
            animationDuration: g.duration
          }}
        />
      ))}

      <div className="sand-fg" />
    </div>
  );
}
