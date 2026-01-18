"use client";

import React from "react";
import EmotionCanvas from "@/components/EmotionCanvas";
import VoiceAlchemy from "@/components/VoiceAlchemy";
import LyricComposer from "@/components/LyricComposer";
import DebugOverlay from "@/components/DebugOverlay";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Toaster } from "@/components/ui/sonner";
import { Sparkles, Mic2, FileText } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen p-4 md:p-8 flex flex-col items-center bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-background to-background">
      <div className="max-w-4xl w-full flex flex-col gap-12 pt-12">
        {/* Header */}
        <div className="flex flex-col items-center text-center gap-4 animate-in fade-in slide-in-from-top-4 duration-1000">
          <h1 className="text-6xl md:text-8xl font-black tracking-tight bg-gradient-to-b from-white to-white/40 bg-clip-text text-transparent italic px-2">
            SONIC ALCHEMY
          </h1>
          <p className="text-muted-foreground text-lg md:text-xl max-w-lg font-medium">
            The multimodal AI music studio. Transform images, hums, and themes into gold.
          </p>
        </div>

        {/* Core Sections */}
        <div className="w-full">
          <Tabs defaultValue="canvas" className="w-full">
            <TabsList className="grid w-full grid-cols-3 glass mb-8 p-1">
              <TabsTrigger value="canvas" className="gap-2 text-md py-3">
                <Sparkles className="w-4 h-4" />
                Emotion Canvas
              </TabsTrigger>
              <TabsTrigger value="voice" className="gap-2 text-md py-3">
                <Mic2 className="w-4 h-4" />
                Voice Alchemy
              </TabsTrigger>
              <TabsTrigger value="lyrics" className="gap-2 text-md py-3">
                <FileText className="w-4 h-4" />
                Lyric Composer
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="canvas" className="focus-visible:outline-none">
              <EmotionCanvas />
            </TabsContent>
            
            <TabsContent value="voice">
              <VoiceAlchemy />
            </TabsContent>
            
            <TabsContent value="lyrics">
              <LyricComposer />
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Background Micro-animations Backdrop */}
      <div className="fixed inset-0 pointer-events-none -z-10 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 contrast-150 brightness-150" />
      
      <Toaster position="bottom-right" theme="dark" richColors />
      <DebugOverlay />
    </main>
  );
}
