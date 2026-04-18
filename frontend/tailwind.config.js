/** @type {import('tailwindcss').Config} */
export default {
  // Tailwind scanne ces fichiers pour ne générer que les classes utilisées
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
};
