/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  // tailwind.config.js
    theme: {
      extend: {
        colors: {
          calendarRed: "#FCA5A5",
          calendarBlue: "#93C5FD",
          calendarYellow: "#FDE68A",
          calendarGreen: "#A7F3D0",
          calendarPurple: "#E9D5FF",
          calendarPink: "#F9A8D4",
          brand: {
            blue: '#3b82f6',
            pink: '#ec4899',
            neon: '#00f0ff',
            dark: '#0f172a'
          }
        }
      }
    }
,
  plugins: [],
}
