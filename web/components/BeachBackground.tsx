'use client';

import { useMemo } from 'react';

/**
 * Pure-SVG/CSS animated tropical beach backdrop.
 * - No external assets (copyright-free).
 * - Vector-based, so it stays crisp at 1080p, 4K, and beyond.
 * - Continuously animated: sky gradient drifts, sun pulses, four wave layers
 *   flow at different speeds, sun reflection ripples on the water, glints
 *   scatter across, clouds and seabirds drift past, palm fronds sway in the
 *   bottom corners.
 * - Respects prefers-reduced-motion.
 */
export default function BeachBackground() {
  const glints = useMemo(
    () =>
      Array.from({ length: 28 }, (_, i) => ({
        id: i,
        left: `${(i * 37) % 100}%`,
        top: `${42 + ((i * 11) % 38)}%`,
        delay: `${(i * 0.6) % 7}s`,
        duration: `${3 + ((i * 1.1) % 5)}s`
      })),
    []
  );

  return (
    <div className="beach" aria-hidden>
      <div className="sun" />
      <div className="sun-glare" />

      {/* Drifting clouds */}
      <div className="cloud c1" style={{ animationDelay: '-10s' }} />
      <div className="cloud c2" style={{ animationDelay: '-60s' }} />
      <div className="cloud c3" style={{ animationDelay: '-25s' }} />

      {/* Seabirds */}
      <div className="bird b1">
        <svg viewBox="0 0 22 12" xmlns="http://www.w3.org/2000/svg">
          <path
            d="M1 8 Q 4 1 7 6 Q 9 9 11 6 Q 13 1 16 6 Q 18 9 21 8"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
          />
        </svg>
      </div>
      <div className="bird b2">
        <svg viewBox="0 0 22 12" xmlns="http://www.w3.org/2000/svg">
          <path
            d="M1 8 Q 4 1 7 6 Q 9 9 11 6 Q 13 1 16 6 Q 18 9 21 8"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
          />
        </svg>
      </div>

      {/* Animated ocean — four layered waves */}
      <svg
        className="waves"
        viewBox="0 0 1600 600"
        preserveAspectRatio="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <g className="wave w4">
          <path
            d="M-800 340 Q -600 300 -400 340 T 0 340 T 400 340 T 800 340 T 1200 340 T 1600 340 T 2000 340 T 2400 340 V600 H-800Z"
            fill="#0d6a8a"
            opacity="0.92"
          />
        </g>
        <g className="wave w3">
          <path
            d="M-800 400 Q -600 360 -400 400 T 0 400 T 400 400 T 800 400 T 1200 400 T 1600 400 T 2000 400 T 2400 400 V600 H-800Z"
            fill="#2bb5c4"
            opacity="0.95"
          />
        </g>
        <g className="wave w2">
          <path
            d="M-800 460 Q -600 430 -400 460 T 0 460 T 400 460 T 800 460 T 1200 460 T 1600 460 T 2000 460 T 2400 460 V600 H-800Z"
            fill="#6ee2d0"
            opacity="0.95"
          />
        </g>
        <g className="wave w1">
          <path
            d="M-800 510 Q -600 490 -400 510 T 0 510 T 400 510 T 800 510 T 1200 510 T 1600 510 T 2000 510 T 2400 510 V600 H-800Z"
            fill="#e8f8f7"
            opacity="0.95"
          />
        </g>
      </svg>

      {/* Sparkles on the water */}
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

      {/* Palm fronds swaying in the corners */}
      <div className="palm left">
        <svg viewBox="0 0 200 240" xmlns="http://www.w3.org/2000/svg">
          <path d="M100 240 Q 95 160 110 80 Q 112 60 108 30" stroke="#5b3a1c" strokeWidth="6" fill="none" strokeLinecap="round" />
          <path d="M108 30 Q 30 20 0 60 Q 30 35 100 50" fill="#1d8a5d" opacity="0.9" />
          <path d="M108 30 Q 170 10 200 50 Q 170 30 110 55" fill="#1d8a5d" opacity="0.95" />
          <path d="M108 30 Q 60 -10 30 0 Q 70 20 108 38" fill="#27a06b" opacity="0.9" />
          <path d="M108 30 Q 160 -5 195 10 Q 160 25 112 40" fill="#27a06b" opacity="0.95" />
          <path d="M108 30 Q 95 -20 70 -10 Q 95 10 110 35" fill="#34b87b" opacity="0.9" />
          <path d="M108 30 Q 125 -25 145 -10 Q 122 12 112 38" fill="#34b87b" opacity="0.95" />
        </svg>
      </div>
      <div className="palm right">
        <svg viewBox="0 0 200 240" xmlns="http://www.w3.org/2000/svg">
          <path d="M100 240 Q 95 160 110 80 Q 112 60 108 30" stroke="#5b3a1c" strokeWidth="6" fill="none" strokeLinecap="round" />
          <path d="M108 30 Q 30 20 0 60 Q 30 35 100 50" fill="#1d8a5d" opacity="0.9" />
          <path d="M108 30 Q 170 10 200 50 Q 170 30 110 55" fill="#1d8a5d" opacity="0.95" />
          <path d="M108 30 Q 60 -10 30 0 Q 70 20 108 38" fill="#27a06b" opacity="0.9" />
          <path d="M108 30 Q 160 -5 195 10 Q 160 25 112 40" fill="#27a06b" opacity="0.95" />
          <path d="M108 30 Q 95 -20 70 -10 Q 95 10 110 35" fill="#34b87b" opacity="0.9" />
          <path d="M108 30 Q 125 -25 145 -10 Q 122 12 112 38" fill="#34b87b" opacity="0.95" />
        </svg>
      </div>

      <div className="sand-fg" />
    </div>
  );
}
