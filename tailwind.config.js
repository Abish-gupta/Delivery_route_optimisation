/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'sans': ['Inter', 'ui-sans-serif', 'system-ui'],
      },
    },
  },
  plugins: [],
  safelist: [
    'text-blue-600',
    'text-green-600',
    'text-purple-600',
    'text-indigo-600',
    'text-yellow-600',
    'text-red-600',
    'bg-blue-600',
    'bg-green-600',
    'bg-purple-600',
    'bg-indigo-600',
    'bg-yellow-600',
    'bg-red-600',
  ]
}
