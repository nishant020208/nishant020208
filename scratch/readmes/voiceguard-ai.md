# 🛡️ VoxGuard — Deepfake Audio Detector

> **"Every fake voice leaves a trace."**

VoxGuard is an AI-powered deepfake audio detection system that analyzes voice clips to determine whether they are human-generated or synthetically created. It doesn't just give you a verdict — it shows you **exactly where** in the audio the anomalies are.

Built for cybersecurity researchers, journalists, banks, and everyday users who need forensic-grade audio verification.

![VoxGuard Banner](https://voxguard-sound.vercel.app/)

---

## 🔴 Live Demo

**[https://voxguard-sound.vercel.app/](https://voxguard-sound.vercel.app/)**

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎙️ Audio Upload & Live Mic | Drag-drop files or record directly from browser mic |
| 🤖 Gemini AI Analysis | Forensic spectral + prosody analysis via Gemini 1.5 Pro |
| 📊 Confidence Score Meter | Animated arc meter with Real / Suspicious / Fake zones |
| 🔴 Spectral Anomaly Highlights | Waveform + spectrogram with red overlays at flagged timestamps |
| 📁 Scan History & Compare | Last 50 scans in localStorage with side-by-side compare mode |
| 📄 Report Export | Download forensic report as PDF or JSON |

---

## 🛠️ Tech Stack

- **Frontend** — Vite + React + TypeScript
- **AI** — Google Gemini 1.5 Pro API
- **Audio** — Web Audio API + WaveSurfer.js
- **Export** — jsPDF + html2canvas
- **Storage** — localStorage (no backend needed)
- **Deployment** — Vercel

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/nishant020208/voiceguard-ai.git
cd voiceguard-ai
```

### 2. Install dependencies

```bash
npm install
```

### 3. Set up environment variables

Create a `.env` file in the root:

```env
VITE_GEMINI_API_KEY=your_gemini_api_key_here
```

Get your free Gemini API key at [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### 4. Run locally

```bash
npm run dev
```

### 5. Build for production

```bash
npm run build
```

---

## 📁 Project Structure

```
voiceguard-ai/
├── public/
├── src/
│   ├── components/
│   │   ├── AudioInput.tsx         # Upload + mic recording
│   │   ├── ConfidenceMeter.tsx    # Animated arc score display
│   │   ├── SpectrogramView.tsx    # Waveform + anomaly highlights
│   │   ├── ScanHistory.tsx        # localStorage history panel
│   │   └── ReportExport.tsx       # PDF + JSON export
│   ├── lib/
│   │   └── gemini.ts              # Gemini API call + prompt
│   ├── App.tsx
│   └── main.tsx
├── .env.example
├── vercel.json
└── vite.config.ts
```

---

## 🔑 How the AI Detection Works

1. Audio is converted to **base64** in the browser
2. Sent to **Gemini 1.5 Pro** with a forensic system prompt
3. Gemini checks for:
   - Unnatural prosody and pitch quantization
   - TTS (Text-to-Speech) artifacts
   - Missing breath sounds
   - Spectral inconsistencies
   - Clipping patterns from voice synthesis
4. Returns structured JSON: `verdict`, `confidence`, `summary`, `anomaly_timestamps`
5. Anomaly timestamps are overlaid as **red highlights** on the spectrogram

---

## 📦 Environment Variables

| Variable | Description |
|---|---|
| `VITE_GEMINI_API_KEY` | Your Google Gemini API key |

---

## 🌐 Deploying to Vercel

The repo includes a `vercel.json` for SPA routing:

```json
{
  "buildCommand": "vite build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

1. Push to GitHub
2. Import repo on [vercel.com](https://vercel.com)
3. Add `VITE_GEMINI_API_KEY` in Vercel → Settings → Environment Variables
4. Deploy ✅

---

## 🎯 Use Cases

- **Journalists** — Verify leaked audio before publishing
- **Banks / Fintech** — Detect voice phishing in call recordings
- **Cybersecurity teams** — Analyze suspicious voice messages
- **General users** — Check if a viral audio clip is real

---

## 🧑‍💻 Author

**Nishant** — IT Student at SVIT Vasad, GTU
Building in public 🚀

- GitHub: [@nishant020208](https://github.com/nishant020208)
- Live App: [voxguard-sound.vercel.app](https://voxguard-sound.vercel.app/)

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

> Built as part of a hackathon project. If this helped you learn something, drop a ⭐ on the repo!
