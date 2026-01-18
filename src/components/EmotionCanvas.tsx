"use client";

import React, { useRef, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { analyzeImage, MusicalParameters } from "@/lib/gemini";
import { audioEngine } from "@/lib/audio-engine";
import { Loader2, Palette, Upload, Music, Trash2 } from "lucide-react";
import { toast } from "sonner";

export default function EmotionCanvas() {
  const canvasRef = useRef<HTMLDivElement>(null);
  const p5Instance = useRef<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [params, setParams] = useState<MusicalParameters | null>(null);
  const [currentColor, setCurrentColor] = useState("#ffffff");
  const colorRef = useRef("#ffffff");

  useEffect(() => {
    colorRef.current = currentColor;
  }, [currentColor]);

  const colors = [
    { name: "White", value: "#ffffff" },
    { name: "Neon Pink", value: "#ff2d55" },
    { name: "Neon Cyan", value: "#00f2ff" },
    { name: "Neon Green", value: "#39ff14" },
    { name: "Neon Yellow", value: "#ffff00" },
    { name: "Neon Orange", value: "#ff8800" },
    { name: "Deep Purple", value: "#8a2be2" },
  ];

  useEffect(() => {
    // Dynamic import of p5 to avoid SSR issues
    const initP5 = async () => {
      const p5 = (await import("p5")).default;
      
      const sketch = (p: any) => {
        p.setup = () => {
          const canvas = p.createCanvas(600, 400);
          canvas.parent(canvasRef.current);
          p.background(20);
          p.stroke(colorRef.current);
          p.strokeWeight(4);
        };

        p.draw = () => {
          if (p.mouseIsPressed) {
            p.stroke(colorRef.current);
            p.line(p.pmouseX, p.pmouseY, p.mouseX, p.mouseY);
          }
        };

        p.clearCanvas = () => {
          p.background(20);
        };
      };

      p5Instance.current = new p5(sketch);
    };

    if (typeof window !== "undefined") {
      initP5();
    }

    return () => {
      if (p5Instance.current) {
        p5Instance.current.remove();
      }
    };
  }, []);

  const handleClear = () => {
    if (p5Instance.current) {
      p5Instance.current.clearCanvas();
    }
  };

  const handleAnalyze = async () => {
    if (!p5Instance.current) return;

    setIsAnalyzing(true);
    try {
      const canvas = document.querySelector("canvas");
      if (!canvas) throw new Error("Canvas not found");
      
      const imageData = canvas.toDataURL("image/png");
      console.log(`[Sonic Alchemy] Captured Canvas: ${imageData.length} bytes`);
      const result = await analyzeImage(imageData);
      setParams(result);
      
      toast.success(`Gemini detected: ${result.mood} ${result.instrument} in ${result.key}`);
      
      await audioEngine.init();
      audioEngine.setParameters(result);
      audioEngine.playParametricMusic(result);
      
    } catch (error) {
      console.error(error);
      toast.error("Failed to analyze image");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !p5Instance.current) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const imgUrl = event.target?.result as string;
      p5Instance.current.loadImage(imgUrl, (img: any) => {
        // Adjust image to fit canvas while maintaining aspect ratio
        const canvasWidth = 600;
        const canvasHeight = 400;
        const ratio = Math.min(canvasWidth / img.width, canvasHeight / img.height);
        const newWidth = img.width * ratio;
        const newHeight = img.height * ratio;
        
        p5Instance.current.background(20);
        p5Instance.current.image(img, (canvasWidth - newWidth) / 2, (canvasHeight - newHeight) / 2, newWidth, newHeight);
      });
    };
    reader.readAsDataURL(file);
  };

  return (
    <Card className="p-6 glass border-primary/20 neon-glow animate-float">
      <div className="flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Palette className="w-6 h-6 text-primary" />
            <h2 className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Emotion Canvas
            </h2>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="icon" onClick={handleClear} title="Clear Canvas">
              <Trash2 className="w-4 h-4" />
            </Button>
            <div className="relative">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                className="absolute inset-0 opacity-0 cursor-pointer"
                title="Upload Image"
              />
              <Button variant="outline" size="icon">
                <Upload className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 items-center justify-center p-2 bg-black/40 rounded-full border border-white/5">
          {colors.map((color) => (
            <button
              key={color.value}
              onClick={() => setCurrentColor(color.value)}
              className={`w-8 h-8 rounded-full border-2 transition-all hover:scale-110 active:scale-95 ${
                currentColor === color.value ? "border-white scale-110 shadow-[0_0_10px_rgba(255,255,255,0.5)]" : "border-transparent"
              }`}
              style={{ backgroundColor: color.value }}
              title={color.name}
            />
          ))}
        </div>

        <div 
          ref={canvasRef} 
          className="w-full h-[400px] border border-white/10 rounded-lg overflow-hidden bg-black/20 flex items-center justify-center p5-canvas-container"
        />

        <div className="flex justify-center">
          <Button 
            size="lg" 
            className="w-full max-w-xs gap-2" 
            onClick={handleAnalyze}
            disabled={isAnalyzing}
          >
            {isAnalyzing ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Music className="w-4 h-4" />
            )}
            Alchemy: Image to Music
          </Button>
        </div>

        {params && (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 p-4 border border-primary/20 rounded-lg bg-primary/5 animate-in fade-in slide-in-from-bottom-2">
            <div className="flex flex-col">
              <span className="text-xs text-muted-foreground uppercase">Tempo</span>
              <span className="font-mono text-lg">{params.tempo} BPM</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs text-muted-foreground uppercase">Key</span>
              <span className="font-mono text-lg">{params.key}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs text-muted-foreground uppercase">Mood</span>
              <span className="font-mono text-lg capitalize">{params.mood}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs text-muted-foreground uppercase">Instrument</span>
              <span className="font-mono text-lg capitalize">{params.instrument}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs text-muted-foreground uppercase">Dynamics</span>
              <span className="font-mono text-lg capitalize">{params.dynamics}</span>
            </div>
            {params.scale && (
              <div className="flex flex-col">
                <span className="text-xs text-muted-foreground uppercase">Scale</span>
                <span className="font-mono text-lg capitalize">{params.scale}</span>
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}
