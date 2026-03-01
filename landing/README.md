# FakePhoto.ai Landing Page

The official landing page for FakePhoto.ai - Multi-Model AI Detection Engine

## 🚀 Quick Start

```bash
cd landing
npm install
npm run dev
```

## 🏗️ Build

```bash
npm run build
```

Output will be in the `dist` folder, ready for Vercel deployment.

## 📁 Structure

```
landing/
├── public/           # Static assets
│   ├── images/       # Images and logos
│   └── favicon.ico
├── src/
│   ├── components/   # React components
│   ├── pages/        # Page components
│   ├── styles/       # CSS/Tailwind styles
│   ├── App.tsx       # Main app component
│   └── main.tsx      # Entry point
├── index.html
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts
```

## 🎨 Customization

Edit the following files to customize the landing page:

- `src/pages/Home.tsx` - Main landing page content
- `tailwind.config.js` - Colors, fonts, and theme settings
- `public/` - Replace logo and images

## 🌐 Deployment

The landing page is automatically deployed to Vercel via GitHub Actions on push to main.

### Manual Deployment

```bash
vercel --prod
```