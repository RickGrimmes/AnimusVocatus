/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        'insta-black': '#000000',
        'insta-dark': '#121212',
        'insta-card': '#1c1c1e',
        'insta-border': 'rgba(255, 255, 255, 0.15)',
        'insta-border-light': '#dbdbdb',
        'insta-red': '#ff3040',
        'insta-blue': '#0095f6',
        'insta-gray': '#737373',
        'insta-light-gray': '#f2f2f2',
        'editorial-bg': '#fcfbf9',
        'editorial-card': '#ffffff',
        'editorial-dark': '#18181b',
        'editorial-accent': '#27272a',
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          'Helvetica',
          'Arial',
          'sans-serif',
        ],
        serif: ['"Playfair Display"', 'Georgia', 'serif'],
      },
      keyframes: {
        'heart-bounce': {
          '0%': { transform: 'scale(0.8)', opacity: '0' },
          '50%': { transform: 'scale(1.2)', opacity: '1' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'heart-bounce': 'heart-bounce 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
        'fade-in': 'fade-in 0.3s ease-out forwards',
      },
    },
  },
  plugins: [],
};
