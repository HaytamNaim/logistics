/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Biophilic "Logistics in Harmony" palette
        sage: {
          DEFAULT: '#5B7B6B',
          light: '#8FA99A',
        },
        slate: '#4A6572',
        stone: {
          paper: '#F6F4F0',
          DEFAULT: '#E8E4DD',
        },
        sand: '#E8E4DD',
        driftwood: '#C4BDB4',
        charcoal: '#3D3630',
        pebble: '#6B645C',
        terracotta: '#C17F59',
        amber: '#D4A04A',
        moss: '#6B8E6B',
        mist: '#7B9AAF',
        clay: '#B8957A',
        frost: '#FFFFFF',
      },
      fontFamily: {
        display: ['Fraunces', 'Georgia', 'serif'],
        body: ['DM Sans', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'IBM Plex Mono', 'monospace'],
      },
      borderRadius: {
        'sm': '8px',
        'md': '12px',
        'lg': '20px',
      },
      boxShadow: {
        'rest': '0 1px 3px rgba(61, 54, 48, 0.06)',
        'elevated': '0 4px 12px rgba(61, 54, 48, 0.08)',
        'overlay': '0 8px 24px rgba(61, 54, 48, 0.12)',
      },
      transitionDuration: {
        'fast': '200ms',
        'normal': '280ms',
        'moment': '420ms',
      },
      transitionTimingFunction: {
        'out': 'cubic-bezier(0.33, 1, 0.68, 1)',
        'in-out': 'cubic-bezier(0.65, 0, 0.35, 1)',
      },
    },
  },
  plugins: [],
}
