/** @type {import('tailwindcss').Config} */

export default {
  content: [
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    spacing: {
      '8': '0.5rem',
      '16': '1rem',
      '24': '1.5rem',
      '32': '2rem',
    },
    colors: {
      'green': {
        '200': 'hsl(141, 75%, 76%)',
        '300': 'hsl(147, 71%, 63%)',
        DEFAULT: 'hsl(152, 59%, 48%)',
        '500': 'hsl(157, 77%, 45%)',
        '600': 'hsl(162, 86%, 36%)',
        '700': 'hsl(166, 86%, 30%)',
        '800': 'hsl(169, 80%, 26%)',
        '900': 'hsl(175, 79%, 22%)',
      },
      'grey': {
        '50': 'hsl(0, 0%, 96%)',
        '100': 'hsl(0, 0%, 91%)',
        '200': 'hsl(0, 0%, 82%)',
        '300': 'hsl(0, 0%, 69%)',
        '400': 'hsl(0, 0%, 58%)',
        '500': 'hsl(0, 0%, 43%)',
        DEFAULT: 'hsl(0, 0%, 85%)',
        '700': 'hsl(0, 0%, 53%)',
        '800': 'hsl(0, 0%, 27%)',
        '900': 'hsl(0, 0%, 24%)',
        '950': 'hsl(0, 0%, 15%)',
      },
      'yellow': 'hsl(36, 100%, 50%)',
      'red': {
        '300': 'hsl(351, 100%, 81%)',
        DEFAULT: 'hsl(351, 85%, 44%)',
      },
      'white': 'hsl(0, 0%, 100%)',
    },
    fontFamily: {
      'sans': ['Open Sans', 'Arial', 'sans-serif'],
    },
    extend: {
      boxShadow: ({ theme }) => ({
        'solid-shadow-green': `0px 0.25rem 0px 0px  ${theme('colors.green.700')}`,
        'solid-shadow-grey': `0px 0.25rem 0px 0px  ${theme('colors.grey.300')}`,

      })
    },
  },
  plugins: [
    // eslint-disable-next-line no-undef
    require('@tailwindcss/container-queries'),
  ],
}
