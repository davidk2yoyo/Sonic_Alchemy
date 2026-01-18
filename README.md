# Sonic Alchemy

**Multimodal AI Music Creation Studio** built for the Gemini 3 Global Hackathon.

Sonic Alchemy transforms visual and vocal intent into musical gold. Using Gemini 3 as the reasoning engine and Tone.js for real-time synthesis, it bridges the gap between raw emotion and musical production.

## 🚀 Features

- **Emotion Canvas**: Draw or upload an image. Gemini analyzes the visual "mood" and generates structured musical parameters (tempo, key, scale, instruments) to drive a live synth.
- **Voice Alchemy**: Record a hum or a "bad" vocal take. Gemini infers the intended melody and rhythmic structure, providing guidance for pitch correction and timing.
- **Lyric Composer**: Enter a theme or emotion. Gemini generates rhyming lyrics with syllable-to-melody alignment for synchronized display.

## 🛠 Tech Stack

- **Frontend**: Next.js 14 (App Router)
- **UI**: Tailwind CSS, GSAP (animations), Framer Motion (transitions), shadcn/ui
- **Canvas**: P5.js
- **Audio Engine**: Tone.js + Web Audio API
- **AI Engine**: Gemini 1.5 Flash (via Google Generative AI SDK)

## 📦 Getting Started

1. **Clone & Install**:

   ```bash
   npm install
   ```

2. **Environment Variables**:
   Create a `.env.local` file based on `.env.local.example` and add your Gemini API Key:

   ```env
   NEXT_PUBLIC_GEMINI_API_KEY=your_key_here
   ```

3. **Run Locally**:
   ```bash
   npm run dev
   ```

## 🎭 Gemini 3 Integration

Gemini serves as the **Multimodal Reasoning Core**:

- **Vision**: Interprets drawing strokes and image colors into emotional musicality.
- **Audio reasoning**: Decipher "intent" from human voice recordings, ignoring technical singing flaws to find the underlying melody.
- **Creative Writing**: Generates rhythm-aligned lyrics that match the inferred musical parameters.

---

Built with ❤️ for the Gemini 3 Global Hackathon.
