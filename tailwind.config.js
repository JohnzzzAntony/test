/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
    "./static/**/*.js",
    "./core/design_models.py",
  ],
  theme: {
    extend: {
      colors: {
        primary: "var(--primary)",
        secondary: "var(--secondary)",
        accent: "var(--accent)",
        surface: "var(--surface)",
        card: "var(--card)",
        "border-custom": "var(--border-custom)",
        "txt-main": "var(--txt-main)",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "Inter", "sans-serif"],
        heading: ["var(--font-heading)", "Outfit", "sans-serif"],
      },
      borderRadius: {
        container: "var(--radius-container)",
        "card-custom": "var(--radius-card)",
        "btn-custom": "var(--radius-btn)",
        "img-custom": "var(--radius-img)",
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite alternate',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px var(--accent)' },
          '100%': { boxShadow: '0 0 20px var(--accent)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-20px)' },
        }
      }
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["light", "dark", "cupcake"],
  },
};
