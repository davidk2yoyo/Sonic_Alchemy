"use client";

import React, { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { analyzeVoiceIntent, AudioIntent } from "@/lib/gemini";
import { audioEngine } from "@/lib/audio-engine";
import { Mic, Square, Play, Loader2, Music4, Info, Volume2 } from "lucide-react";
import { toast } from "sonner";

export default function VoiceAlchemy() {
  const [isRecording, setIsRecording] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [intent, setIntent] = useState<AudioIntent | null>(null);
  
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];

      mediaRecorder.current.ondataavailable = (event) => {
        audioChunks.current.push(event.data);
      };

      mediaRecorder.current.onstop = () => {
        const audioBlob = new Blob(audioChunks.current, { type: "audio/wav" });
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        handleAnalyze(audioBlob);
      };

      mediaRecorder.current.start();
      setIsRecording(true);
      toast.info("Recording started... Hum or sing your melody!");
    } catch (err) {
      console.error(err);
      toast.error("Could not access microphone");
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      setIsRecording(false);
    }
  };

  const handleAnalyze = async (blob: Blob) => {
    setIsAnalyzing(true);
    try {
      // Convert blob to base64 for Gemini
      const reader = new FileReader();
      reader.readAsDataURL(blob);
      reader.onloadend = async () => {
        const base64data = (reader.result as string).split(",")[1];
        const result = await analyzeVoiceIntent(base64data);
        setIntent(result);
        toast.success("Gemini understood your intent!");
      };
    } catch (error) {
      console.error(error);
      toast.error("Failed to analyze voice intent");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <Card className="p-6 glass border-primary/20 neon-glow">
      <div className="flex flex-col gap-6">
        <div className="flex items-center gap-2">
          <Mic className="w-6 h-6 text-primary" />
          <h2 className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Voice Alchemy
          </h2>
        </div>

        <div className="flex flex-col items-center justify-center p-12 border-2 border-dashed border-white/10 rounded-xl bg-black/20 gap-6">
          <div className={`relative ${isRecording ? "animate-pulse" : ""}`}>
            <div className={`absolute inset-0 bg-primary/20 rounded-full blur-xl transition-opacity ${isRecording ? "opacity-100" : "opacity-0"}`} />
            <Button
              size="lg"
              variant={isRecording ? "destructive" : "default"}
              className="w-24 h-24 rounded-full relative z-10"
              onClick={isRecording ? stopRecording : startRecording}
            >
              {isRecording ? <Square className="w-8 h-8" /> : <Mic className="w-8 h-8" />}
            </Button>
          </div>
          
          <div className="text-center">
            <h3 className="font-semibold text-lg">
              {isRecording ? "Listening..." : audioUrl ? "Recording Captured" : "Start Recording"}
            </h3>
            <p className="text-sm text-muted-foreground">
              {isRecording ? "Hum your melody clearly" : "Transform your 'bad' singing into music"}
            </p>
          </div>

          {audioUrl && !isRecording && (
            <div className="flex flex-wrap items-center justify-center gap-4">
              <Button variant="outline" size="sm" onClick={() => new Audio(audioUrl).play()} className="gap-2">
                <Play className="w-4 h-4" /> Listen Back
              </Button>
              <Button variant="outline" size="sm" onClick={() => { setAudioUrl(null); setIntent(null); }} className="gap-2">
                Discard
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                className="gap-2 border-primary/20 hover:bg-primary/10 glass"
                onClick={() => {
                  audioEngine.init();
                  toast.success("Audio Engine Ready!");
                }}
              >
                <Volume2 className="w-4 h-4" /> Initialize Audio Path
              </Button>
            </div>
          )}
        </div>

        {isAnalyzing && (
          <div className="flex items-center justify-center gap-2 py-4 italic text-primary animate-pulse">
            <Loader2 className="w-4 h-4 animate-spin" />
            Gemini is deciphering your musical intent...
          </div>
        )}

        {intent && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-primary/5 border border-primary/10">
                <div className="flex items-center gap-2 mb-1 text-primary">
                  <Music4 className="w-4 h-4" />
                  <span className="text-xs font-bold uppercase">Intended Melody</span>
                </div>
                <p className="text-sm">{intent.intendedMelody}</p>
              </div>
              <div className="p-4 rounded-lg bg-accent/5 border border-accent/10">
                <div className="flex items-center gap-2 mb-1 text-accent">
                  <Info className="w-4 h-4" />
                  <span className="text-xs font-bold uppercase">Emotional Intent</span>
                </div>
                <p className="text-sm">{intent.emotionalIntent}</p>
              </div>
            </div>
            
            <div className="p-4 rounded-lg bg-white/5 border border-white/10 space-y-2">
              <span className="text-xs font-bold uppercase text-muted-foreground tracking-wider">Alchemy Guidance</span>
              <p className="text-md italic text-white/80">{intent.correctionGuidance}</p>
              <Button 
                className="w-full mt-2" 
                variant="secondary"
                onClick={() => intent && audioEngine.applyCorrection(intent)}
              >
                Apply Musical Correction & Play
              </Button>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
