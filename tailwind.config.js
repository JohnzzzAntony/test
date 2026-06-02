module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
    "./static/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#114084',
          50: '#f1f6fc',
          100: '#e1ecf8',
          200: '#c8def2',
          300: '#a1c7e9',
          400: '#72a8dc',
          500: '#5189ce',
          600: '#3d6dbf',
          700: '#3459ad',
          800: '#2f4a8c',
          900: '#2a3f70',
          950: '#1c2845',
        },
        secondary: '#1E293B',
        accent: '#0081ff',
        surface: '#f8fafc',
        card: '#ffffff',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        heading: ['Outfit', 'sans-serif'],
      },
      borderRadius: {
        'container': '40px',
        'card-custom': '24px',
        'btn-custom': '9999px',
        'img-custom': '20px',
      },
      boxShadow: {
        'premium': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'premium-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'premium-xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
      },
    },
  },
  plugins: [],
}
