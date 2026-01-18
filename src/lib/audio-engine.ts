import * as Tone from "tone";
import { MusicalParameters, AudioIntent } from "./gemini";

class AudioEngine {
  private synth: Tone.PolySynth | null = null;
  private membraneSynth: Tone.MembraneSynth | null = null;
  private fmSynth: Tone.PolySynth | null = null;
  private reverb: Tone.Reverb | null = null;
  private delay: Tone.FeedbackDelay | null = null;
  private isInitialized = false;

  async init() {
    if (this.isInitialized) return;
    await Tone.start();
    
    this.reverb = new Tone.Reverb({ decay: 5, wet: 0.4 }).toDestination();
    this.delay = new Tone.FeedbackDelay("8n.", 0.4).connect(this.reverb);
    
    // Create multiple synth types for variety
    this.synth = new Tone.PolySynth(Tone.Synth).connect(this.delay);
    this.fmSynth = new Tone.PolySynth(Tone.FMSynth).connect(this.delay);
    this.membraneSynth = new Tone.MembraneSynth().connect(this.delay);
    
    this.isInitialized = true;
    console.log("Audio Engine Initialized with multi-instrument support");
  }

  private mapMood(mood: string) {
    const m = mood.toLowerCase();
    
    // Default values
    let type: any = "sine";
    let rhythm = [0, 0.5, 1, 1.5];
    let duration: any = "8n";

    // 1. Harsh/Fast Moods
    if (m.includes("industrial") || m.includes("harsh") || m.includes("energetic") || m.includes("chaotic") || m.includes("frantic")) {
      type = "sawtooth";
      rhythm = [0, 0.125, 0.25, 0.5, 0.625, 0.75, 1, 1.25];
      duration = "16n";
    } 
    // 2. Bright/Sharp Moods
    else if (m.includes("crystal") || m.includes("sharp") || m.includes("bright") || m.includes("bell") || m.includes("mystical")) {
      type = "square";
      rhythm = [0, 0.5, 0.75, 1.5, 1.75]; // Syncopated
      duration = "8n";
    }
    // 3. Ethereal/Soft Moods
    else if (m.includes("vast") || m.includes("ethereal") || m.includes("ambient") || m.includes("calm") || m.includes("poetic") || m.includes("warm")) {
      type = "triangle";
      rhythm = [0, 4, 8];
      duration = "2n";
    }

    return { type, rhythm, duration };
  }

  setParameters(params: MusicalParameters) {
    if (!this.synth || !this.fmSynth) return;

    Tone.Transport.bpm.value = params.tempo || 120;
    
    const isSoft = params.dynamics.toLowerCase() === "soft" || params.mood.toLowerCase().includes("calm");
    const envelope = {
      attack: isSoft ? 0.3 : 0.01,
      decay: 0.1,
      sustain: 0.3,
      release: isSoft ? 3 : 0.8,
    };

    // Change Oscillator based on mood for extreme contrast
    const mood = params.mood.toLowerCase();
    let type: any = "sine";
    if (mood.includes("industrial") || mood.includes("harsh") || mood.includes("intense")) type = "sawtooth";
    else if (mood.includes("crystal") || mood.includes("sharp") || mood.includes("digital")) type = "square";
    else if (mood.includes("warm") || mood.includes("ethereal")) type = "triangle";

    this.synth.set({ envelope, oscillator: { type } });
    this.fmSynth.set({ envelope, oscillator: { type: "fmsquare" } });

    console.log(`[AudioEngine] 🧬 DNA Set: BPM=${params.tempo}, Key=${params.key}, Oscillator=${type}`);
  }

  playParametricMusic(params: MusicalParameters) {
    if (!this.synth || !this.fmSynth || !this.membraneSynth) return;

    const inst = params.instrument.toLowerCase();
    let octave = 4;
    if (inst.includes("bass") || inst.includes("cello") || inst.includes("drum")) octave = 2;
    if (inst.includes("flute") || inst.includes("violin") || inst.includes("high")) octave = 5;

    const rootNote = params.key.split(" ")[0] + octave;
    const scaleType = (params.scale || params.key).toLowerCase();
    
    let activeSynth: any = this.synth;
    if (inst.includes("synth") || inst.includes("bell") || inst.includes("metallic")) activeSynth = this.fmSynth;
    if (inst.includes("drum") || inst.includes("perc") || inst.includes("kick")) activeSynth = this.membraneSynth;

    // Scale Intervals
    let intervals = [0, 4, 7, 12];
    const s = scaleType;
    if (s.includes("minor")) intervals = [0, 3, 7, 10];
    else if (s.includes("locrian") || s.includes("dissonant") || s.includes("chaos")) intervals = [0, 1, 6, 8, 13];
    else if (s.includes("lydian") || s.includes("ethereal") || s.includes("mystic")) intervals = [0, 4, 6, 7, 11];
    else if (s.includes("pentatonic")) intervals = [0, 2, 4, 7, 9];
    else if (s.includes("blues")) intervals = [0, 3, 5, 6, 7, 10, 12];

    const mood = params.mood.toLowerCase();
    const { rhythm, duration } = this.mapMood(mood);
    const now = Tone.now();
    const beatUnit = 60 / Tone.Transport.bpm.value;

    console.log(`[AudioEngine] 🪄 Rendering ${inst} (${activeSynth.constructor.name}) in ${params.key} ${scaleType}`);
    console.log(`[AudioEngine] 🧬 Intervals:`, intervals);
    console.log(`[AudioEngine] 🥁 Rhythm offsets:`, rhythm);

    rhythm.forEach((timeOffset, i) => {
      // Use sequential selection for more melodic structure, or random for chaos
      const interval = (mood.includes("chaos") || mood.includes("frantic")) 
        ? intervals[Math.floor(Math.random() * intervals.length)]
        : intervals[i % intervals.length];
        
      const note = Tone.Frequency(rootNote).transpose(interval).toNote();
      const velocity = params.dynamics.toLowerCase() === "loud" ? 0.9 : 0.4;
      
      if (i === 0) {
        const bassNote = Tone.Frequency(rootNote).transpose(-12).toNote();
        activeSynth.triggerAttackRelease(bassNote, "1n", now, velocity * 0.5);
      }

      activeSynth.triggerAttackRelease(note, duration, now + (timeOffset * beatUnit), velocity);
    });
  }

  async applyCorrection(intent: AudioIntent) {
    if (!this.synth) await this.init();
    
    console.log("[Sonic Alchemy] Applying correction based on intent:", intent.emotionalIntent);
    
    const params: MusicalParameters = {
      tempo: 120,
      key: intent.key || "C",
      scale: intent.scale || "major",
      mood: intent.mood || "ethereal",
      dynamics: "moderate",
      instrument: "synth"
    };

    this.setParameters(params);
    this.playParametricMusic(params);
  }

  stop() {
    Tone.Transport.stop();
    this.synth?.releaseAll();
  }
}

export const audioEngine = new AudioEngine();
