"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2, Send, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api, type OptimizeRequest, type OptimizeResponse } from "@/lib/api";
import { AgentSelector } from "@/components/agent-selector";
import { ScoreIndicator } from "@/components/score-indicator";
import { ResultPanel } from "@/components/result-panel";
import { toast } from "sonner";

type AgentType = "auto" | "coding" | "creative" | "analyst" | "general";

interface PromptOptimizerProps {
  projectId?: string;
  onResult?: (result: OptimizeResponse) => void;
}

export function PromptOptimizer({ projectId, onResult }: PromptOptimizerProps) {
  const [prompt, setPrompt] = useState("");
  const [goal, setGoal] = useState("");
  const [selectedAgent, setSelectedAgent] = useState<AgentType>("auto");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<OptimizeResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!prompt.trim() || !goal.trim()) {
      toast.error("Please provide both a prompt and a goal.");
      return;
    }

    setIsLoading(true);
    setResult(null);

    try {
      const request: OptimizeRequest = {
        prompt: prompt.trim(),
        goal: goal.trim(),
        force_agent: selectedAgent === "auto" ? null : selectedAgent,
        project_id: projectId || null,
      };

      const response = await api.optimizePrompt(request);
      setResult(response);
      onResult?.(response);
      toast.success("Prompt optimized successfully!");
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Failed to optimize prompt"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setPrompt("");
    setGoal("");
    setSelectedAgent("auto");
    setResult(null);
  };

  return (
    <div className="w-full">
      {/* Desktop: Split panel layout, Mobile: Stacked */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Panel - Input Form */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-6"
        >
          <div className="glass-strong rounded-xl p-6 space-y-6">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold">Optimize Your Prompt</h2>
                <p className="text-sm text-muted-foreground">
                  Get AI-powered improvements
                </p>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Goal Input */}
              <div className="space-y-2">
                <Label htmlFor="goal" className="text-sm font-medium">
                  What do you want to achieve?
                </Label>
                <Input
                  id="goal"
                  placeholder="e.g., Generate a Python function to parse JSON"
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                  disabled={isLoading}
                  className="bg-background/50 border-white/10 focus:border-primary/50 transition-colors"
                />
              </div>

              {/* Prompt Input */}
              <div className="space-y-2">
                <Label htmlFor="prompt" className="text-sm font-medium">
                  Your Prompt
                </Label>
                <Textarea
                  id="prompt"
                  placeholder="Enter the prompt you want to optimize..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  disabled={isLoading}
                  className="min-h-[200px] resize-y bg-background/50 border-white/10 focus:border-primary/50 transition-colors"
                />
                <div className="flex items-center justify-between">
                  <p className="text-xs text-muted-foreground">
                    {prompt.length} characters
                  </p>
                  {prompt.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="text-xs text-primary"
                    >
                      Looking good! ✨
                    </motion.div>
                  )}
                </div>
              </div>

              {/* Agent Selection */}
              <AgentSelector
                value={selectedAgent}
                onChange={setSelectedAgent}
                disabled={isLoading}
              />

              {/* Action Buttons */}
              <div className="flex gap-3 pt-2">
                <Button
                  type="submit"
                  disabled={isLoading || !prompt.trim() || !goal.trim()}
                  className="flex-1 gap-2 gradient-primary text-white border-0 shadow-lg shadow-primary/25 hover:shadow-primary/40 transition-shadow"
                  size="lg"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Optimizing...
                    </>
                  ) : (
                    <>
                      <Send className="h-4 w-4" />
                      Optimize Prompt
                    </>
                  )}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleClear}
                  disabled={isLoading}
                  className="border-white/10 hover:bg-white/5"
                  size="lg"
                >
                  Clear
                </Button>
              </div>
            </form>
          </div>
        </motion.div>

        {/* Right Panel - Results */}
        <div className="min-h-[500px]">
          <AnimatePresence mode="wait">
            {isLoading ? (
              <motion.div
                key="loading"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="glass-strong rounded-xl p-8 h-full flex flex-col items-center justify-center gap-6"
              >
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-500 blur-2xl opacity-50 animate-pulse" />
                  <Loader2 className="h-16 w-16 animate-spin text-primary relative" />
                </div>
                <div className="text-center space-y-2">
                  <h3 className="text-lg font-semibold">
                    Analyzing your prompt...
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Our AI experts are working their magic
                  </p>
                </div>
              </motion.div>
            ) : result ? (
              <motion.div
                key="results"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                {/* Score Card */}
                <div className="glass-strong rounded-xl p-6 flex flex-col items-center">
                  <ScoreIndicator score={result.score} size="lg" />
                </div>

                {/* Result Details */}
                <ResultPanel result={result} />
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="glass rounded-xl p-8 h-full flex flex-col items-center justify-center text-center gap-4"
              >
                <div className="mesh-gradient absolute inset-0 rounded-xl opacity-30" />
                <div className="relative space-y-4">
                  <div className="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center">
                    <Sparkles className="w-10 h-10 text-primary" />
                  </div>
                  <div className="space-y-2">
                    <h3 className="text-xl font-semibold">
                      Ready to optimize?
                    </h3>
                    <p className="text-sm text-muted-foreground max-w-md">
                      Enter your prompt on the left and let our AI experts
                      analyze and improve it for you.
                    </p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
