import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        sand: '#fff4e3',
        sandDeep: '#f4d9b0',
        seafoam: '#9bd9d2',
        ocean: '#3a8fa3',
        oceanDeep: '#1f5d6e',
        coral: '#ff8a65',
        sunset: '#ffb38a',
        dusk: '#7b4b8a',
        ink: '#1f2a2e',
        verified: '#3aa676',
        warn: '#e08a3c',
        danger: '#d05050'
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
