import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Amazon-inspired palette
        "amazon-orange": "#FF9900",
        "amazon-dark": "#131A22",
        "amazon-light": "#232F3E",
        "surface": "#FAFAFA",
        "surface-dark": "#1A1A2E",
        "accent": "#FF9900",
        "accent-hover": "#FFB347",
        "text-primary": "#0F1111",
        "text-secondary": "#565959",
        "text-muted": "#767676",
        "border-light": "#E8E8E8",
        "success": "#067D62",
        "warning": "#C7511F",
        "info": "#007185",
      },
      fontFamily: {
        sans: ["-apple-system", "BlinkMacSystemFont", "Segoe UI", "Inter", "system-ui", "sans-serif"],
      },
      borderRadius: {
        "card": "12px",
        "button": "8px",
      },
      boxShadow: {
        "card": "0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)",
        "card-hover": "0 4px 12px rgba(0,0,0,0.12)",
        "sidebar": "2px 0 8px rgba(0,0,0,0.06)",
      },
    },
  },
  plugins: [],
};
export default config;
