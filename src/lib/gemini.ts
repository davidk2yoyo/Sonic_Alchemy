import { GoogleGenerativeAI } from "@google/generative-ai";

const apiKey = process.env.NEXT_PUBLIC_GEMINI_API_KEY || "";
const modelName = process.env.NEXT_PUBLIC_GEMINI_MODEL || "gemini-1.5-flash";
const apiVersion = process.env.NEXT_PUBLIC_GEMINI_API_VERSION || "v1beta";

console.log(`[Sonic Alchemy] Initializing Gemini with model: ${modelName}, version: ${apiVersion}`);

const genAI = new GoogleGenerativeAI(apiKey);

// Helper to debug available models for the user's API Key
async function listAvailableModels() {
  try {
    const url = `https://generativelanguage.googleapis.com/${apiVersion}/models?key=${apiKey}`;
    console.log(`[Sonic Alchemy] Fetching models from: ${url.replace(apiKey, "REDACTED")}`);
    const response = await fetch(url);
    if (!response.ok) {
      console.error(`[Sonic Alchemy] Model list fetch failed with status: ${response.status}`);
      const errorData = await response.json();
      console.error("[Sonic Alchemy] Error details:", errorData);
      return;
    }
    const data = await response.json();
    console.log("[Sonic Alchemy] Available models for this key:", data.models?.map((m: any) => m.name));
  } catch (e) {
    console.warn("[Sonic Alchemy] Could not list models", e);
  }
}

if (typeof window !== "undefined") {
  listAvailableModels();
}

export interface MusicalParameters {
  tempo: number;
  key: string;
  mood: string;
  instrument: string;
  dynamics: string;
  scale?: string;
}

export interface AudioIntent {
  intendedMelody: string;
  rhythm: string;
  emotionalIntent: string;
  correctionGuidance: string;
  mood: string;
  key: string;
  scale?: string;
}

export interface LyricResult {
  lyrics: string;
  rhymeScheme: string;
  syllableAlignment: { text: string; time: number }[];
}

export async function analyzeImage(imageBuffer: string): Promise<MusicalParameters> {
  console.log(`[Sonic Alchemy] analyzeImage: using model=${modelName}, version=${apiVersion}`);
  const model = genAI.getGenerativeModel({ model: modelName }, { apiVersion: apiVersion as any });

  const prompt = `Analyze this image and translate its visual emotions and elements into unique musical parameters. 
  BE DRAMATIC and provide high-contrast results:
  - If the image is chaotic/busy, use dissonant scales (Locrian), high tempo (160+), and sharp instruments.
  - If the image is minimal/empty, use ambient scales (Lydian), low tempo (60-), and soft instruments.
  Return ONLY a JSON object with the following structure:
  {
    "tempo": number (40-180),
    "key": "string (e.g., C, Eb, F#)",
    "mood": "string (e.g., crystalline, industrial, vast, frantic)",
    "instrument": "string (piano, synth, strings, brass, flute)",
    "dynamics": "string (soft, moderate, loud)",
    "scale": "string (major, minor, pentatonic, blues, locrian, lydian)"
  }`;

  try {
    const result = await model.generateContent([
      prompt,
      {
        inlineData: {
          data: imageBuffer.split(",")[1],
          mimeType: "image/png",
        },
      },
    ]);
    const response = await result.response;
    const text = response.text();
    console.log("[Sonic Alchemy] Gemini Image Raw Response:", text);
    const parsed = JSON.parse(text.replace(/```json|```/g, "").trim());
    console.log("[Sonic Alchemy] Gemini Image Parsed:", parsed);
    return parsed;
  } catch (e: any) {
    if (e.message?.includes("404")) {
      console.error("[Sonic Alchemy] Critical: Model not found. Please check your NEXT_PUBLIC_GEMINI_MODEL variable.");
    }
    if (e.message?.includes("403") || e.message?.includes("API_KEY_INVALID")) {
      console.error("[Sonic Alchemy] Critical: Invalid API Key.");
    }
    console.error("Failed to parse Gemini response or fetch data", e);
    throw e;
  }
}

export async function analyzeVoiceIntent(audioBase64: string): Promise<AudioIntent> {
  console.log(`[Sonic Alchemy] analyzeVoiceIntent: using model=${modelName}, version=${apiVersion}`);
  const model = genAI.getGenerativeModel({ model: modelName }, { apiVersion: apiVersion as any });

  const prompt = `Analyze this vocal recording (humming or singing). Decipher the user's musical intent and emotional state.
  Provide structured musical guidance for a "perfected" version of this motif.
  
  Return ONLY a JSON object:
  {
    "intendedMelody": "string description",
    "rhythm": "string description",
    "emotionalIntent": "string description",
    "correctionGuidance": "string description",
    "mood": "string (e.g. heroic, melancholic, ethereal)",
    "key": "string (e.g. Bb, C#)",
    "scale": "string (major, minor, pentatonic, lydian)"
  }`;

  try {
    const result = await model.generateContent([
      prompt,
      {
        inlineData: {
          data: audioBase64,
          mimeType: "audio/wav",
        },
      },
    ]);

    const response = await result.response;
    const text = response.text();
    console.log("[Sonic Alchemy] Gemini Voice Raw Response:", text);
    const parsed = JSON.parse(text.replace(/```json|```/g, "").trim());
    console.log("[Sonic Alchemy] Gemini Voice Parsed:", parsed);
    return parsed;
  } catch (e: any) {
    if (e.message?.includes("404")) {
      console.error("[Sonic Alchemy] Critical: Voice Intent model not found. Check NEXT_PUBLIC_GEMINI_MODEL.");
    }
    console.error("Failed to parse Voice Intent response", e);
    throw e;
  }
}

export async function generateLyrics(theme: string): Promise<LyricResult> {
  console.log(`[Sonic Alchemy] generateLyrics: using model=${modelName}, version=${apiVersion}`);
  const model = genAI.getGenerativeModel({ model: modelName }, { apiVersion: apiVersion as any });

  const prompt = `Generate lyrics for a short song based on the theme/emotion: "${theme}".
  Provide a rhyme scheme and syllable alignment to a simple 4/4 melody.
  Return ONLY a JSON object:
  {
    "lyrics": "string",
    "rhymeScheme": "string",
    "syllableAlignment": [
      { "text": "word/syllable", "time": 0.5 }
    ]
  }`;

  try {
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();
    return JSON.parse(text.replace(/```json|```/g, "").trim());
  } catch (e: any) {
    if (e.message?.includes("404")) {
      console.error("[Sonic Alchemy] Critical: Lyric model not found. Check NEXT_PUBLIC_GEMINI_MODEL.");
    }
    console.error("Failed to generate lyrics", e);
    throw e;
  }
}
