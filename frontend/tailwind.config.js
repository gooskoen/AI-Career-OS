/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1f2937",
        surface: "#f8fafc",
        line: "#dbe3ef",
        brand: "#2563eb",
        accent: "#0f766e"
      }
    }
  },
  plugins: []
};
