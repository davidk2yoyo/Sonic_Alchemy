"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { generateLyrics, LyricResult } from "@/lib/gemini";
import { audioEngine } from "@/lib/audio-engine";
import { FileText, Sparkles, Loader2, Music, Type } from "lucide-react";
import { toast } from "sonner";
import { ScrollArea } from "@/components/ui/scroll-area";

export default function LyricComposer() {
  const [theme, setTheme] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<LyricResult | null>(null);

  const handleGenerate = async () => {
    if (!theme.trim()) {
      toast.error("Please enter a theme or emotion");
      return;
    }

    setIsGenerating(true);
    try {
      const lyrics = await generateLyrics(theme);
      setResult(lyrics);
      toast.success("Lyrics composed with alchemy!");
    } catch (error) {
      console.error(error);
      toast.error("Failed to generate lyrics");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Card className="p-6 glass border-primary/20 neon-glow">
      <div className="flex flex-col gap-6">
        <div className="flex items-center gap-2">
          <FileText className="w-6 h-6 text-primary" />
          <h2 className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Lyric Composer
          </h2>
        </div>

        <div className="flex gap-2">
          <Input
            placeholder="Describe the theme, emotion or story (e.g., 'A rainy night in New York')"
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            className="bg-white/5 border-white/10"
            onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
          />
          <Button onClick={handleGenerate} disabled={isGenerating} className="gap-2">
            {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            Compose
          </Button>
        </div>

        {result && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in slide-in-from-bottom-4">
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Type className="w-4 h-4" />
                <span className="text-xs font-bold uppercase tracking-widest">Generated Lyrics</span>
              </div>
              <ScrollArea className="h-[300px] w-full rounded-md border border-white/10 p-4 bg-black/20">
                <pre className="font-sans text-lg leading-relaxed whitespace-pre-wrap italic text-white/90">
                  {result.lyrics}
                </pre>
              </ScrollArea>
            </div>

            <div className="space-y-6">
              <div className="p-4 rounded-lg bg-primary/5 border border-primary/10">
                <span className="text-xs font-bold uppercase text-primary/70 block mb-2">Rhyme Scheme</span>
                <p className="text-sm font-mono">{result.rhymeScheme}</p>
              </div>

              <div className="p-4 rounded-lg bg-accent/5 border border-accent/10">
                <span className="text-xs font-bold uppercase text-accent/70 block mb-2">Syllable Alignment</span>
                <div className="flex flex-wrap gap-2 uppercase">
                  {result.syllableAlignment.slice(0, 12).map((syllable, i) => (
                    <span key={i} className="text-[10px] bg-white/5 px-2 py-1 rounded border border-white/5">
                      {syllable.text} <span className="text-white/30 ml-1">{syllable.time}s</span>
                    </span>
                  ))}
                  {result.syllableAlignment.length > 12 && (
                    <span className="text-[10px] text-white/30 italic">...and more</span>
                  )}
                </div>
              </div>

              <Button 
                className="w-full gap-2" 
                variant="outline"
                onClick={() => {
                  audioEngine.playParametricMusic({
                    tempo: 120,
                    key: "C",
                    scale: "major",
                    mood: "poetic",
                    dynamics: "moderate",
                    instrument: "piano"
                  });
                }}
              >
                <Music className="w-4 h-4" />
                Sync with Melody & Listen
              </Button>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
