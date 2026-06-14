/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0f172a',
        surface: '#1e293b',
        'surface-light': '#334155',
        foreground: '#e2e8f0',
        accent: {
          emerald: '#10b981',
          rose: '#f43f5e',
          indigo: '#6366f1',
        },
      },
    },
  },
  plugins: [],
};
