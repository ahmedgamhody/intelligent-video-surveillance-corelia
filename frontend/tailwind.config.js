const flowbite = require("flowbite-react/tailwind");

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}", flowbite.content()],
  plugins: [flowbite.plugin()],
  theme: {
    extend: {
      colors: {
        primary: "#553D8E",
        secondary: "#00A099",
        background: "#f8f9fa",
        section: "#E9E9E9",
        text: "#767676",
      },
    },
  },
};
