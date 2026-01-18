"use client";

import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Bug, CheckCircle2, XCircle } from "lucide-react";

export default function DebugOverlay() {
  const [models, setModels] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const fetchModels = async () => {
      const apiKey = process.env.NEXT_PUBLIC_GEMINI_API_KEY;
      const apiVersion = process.env.NEXT_PUBLIC_GEMINI_API_VERSION || "v1beta";
      
      if (!apiKey) {
        setError("API Key missing in .env.local");
        return;
      }

      try {
        const response = await fetch(`https://generativelanguage.googleapis.com/${apiVersion}/models?key=${apiKey}`);
        const data = await response.json();
        if (data.models) {
          setModels(data.models.map((m: any) => m.name.replace("models/", "")));
        } else {
          setError(data.error?.message || "Could not list models");
        }
      } catch (err) {
        setError("Network error fetching models");
      }
    };

    fetchModels();
  }, []);

  if (process.env.NODE_ENV !== "development") return null;

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="bg-black/80 p-2 rounded-full border border-white/20 hover:border-primary transition-colors text-white"
        title="Debug Panel"
      >
        <Bug className="w-5 h-5" />
      </button>

      {isOpen && (
        <Card className="absolute bottom-12 right-0 w-80 p-4 glass border-white/10 shadow-2xl animate-in slide-in-from-bottom-5">
          <h3 className="text-sm font-bold uppercase mb-4 text-primary tracking-widest flex items-center gap-2">
            <Bug className="w-4 h-4" /> Gemini Debugger
          </h3>
          
          <div className="space-y-4">
            <div>
              <p className="text-[10px] text-muted-foreground uppercase mb-2">Active Config</p>
              <div className="flex flex-col gap-1">
                <Badge variant="outline" className="text-[10px] py-0">Model: {process.env.NEXT_PUBLIC_GEMINI_MODEL || "flash"}</Badge>
                <Badge variant="outline" className="text-[10px] py-0">Ver: {process.env.NEXT_PUBLIC_GEMINI_API_VERSION || "v1beta"}</Badge>
              </div>
            </div>

            <div>
              <p className="text-[10px] text-muted-foreground uppercase mb-2">Available Models</p>
              {error ? (
                <div className="flex items-center gap-2 text-red-400 text-xs">
                  <XCircle className="w-3 h-3" /> {error}
                </div>
              ) : models.length > 0 ? (
                <div className="flex flex-wrap gap-1 max-h-32 overflow-y-auto pr-2">
                  {models.map(m => (
                    <Badge key={m} variant="secondary" className="text-[9px] px-1 h-4">
                      {m}
                    </Badge>
                  ))}
                </div>
              ) : (
                <p className="text-xs italic text-muted-foreground">Fetching models...</p>
              )}
            </div>

            <div className="pt-2 border-t border-white/5">
              <p className="text-[9px] leading-tight text-muted-foreground">
                Tip: Copy one of these model names exactly into your .env.local if you get a 404.
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
