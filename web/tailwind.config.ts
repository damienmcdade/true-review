import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        sand: '#fffaf0',
        sandDeep: '#ffe9b8',
        foam: '#e8f8f7',
        seafoam: '#6ee2d0',
        ocean: '#2bb5c4',
        oceanDeep: '#0d6a8a',
        coral: '#ff7a5a',
        sunset: '#ffd166',
        dusk: '#7b4b8a',
        ink: '#0d3b4a',
        verified: '#2ea66f',
        warn: '#e08a3c',
        danger: '#d04545',
        scam: '#c0392b'
      },
      fontFamily: {
        sans: ['ui-sans-serif', 'system-ui', '-apple-system', 'Inter', 'sans-serif'],
        display: ['ui-serif', 'Georgia', 'Cambria', 'serif']
      }
    }
  },
  plugins: []
};

export default config;
