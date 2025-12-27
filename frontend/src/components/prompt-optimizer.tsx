"use client";

import { useState } from "react";
import { useUser } from "@clerk/nextjs";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2, Send, Sparkles, Upload as UploadIcon } from "lucide-react";
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
  const { isSignedIn, isLoaded } = useUser();

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

  // Header file upload (visible action in the circled area)
  const triggerHeaderUpload = () => {
    const input = document.getElementById(
      "prompt-header-upload"
    ) as HTMLInputElement | null;
    input?.click();
  };

  const handleHeaderFileChange = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      if (!projectId) {
        toast.error("Select a project to attach files");
        return;
      }
      const result = await api.uploadContextFile(projectId, file);
      toast.success(`${result.filename} uploaded`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Upload failed");
    } finally {
      e.target.value = "";
    }
  };

  return (
    <div className="w-full">
      {/* Desktop: Split panel layout, Mobile: Stacked */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        {/* Left Panel - Input Form */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-4 sm:space-y-6"
        >
          <div className="glass-strong rounded-xl p-4 sm:p-6 space-y-4 sm:space-y-6">
            <div className="flex items-center justify-between gap-2 sm:gap-3">
              <div className="p-1.5 sm:p-2 rounded-lg bg-linear-to-br from-purple-500 to-pink-500">
                <Sparkles className="h-4 w-4 sm:h-5 sm:w-5 text-white" />
              </div>
              <div className="flex-1">
                <h2 className="text-lg sm:text-xl font-bold">
                  Optimize Your Prompt
                </h2>
                <p className="text-xs sm:text-sm text-muted-foreground">
                  Get AI-powered improvements
                </p>
              </div>
              <div className="flex items-center gap-2">
                <input
                  id="prompt-header-upload"
                  type="file"
                  className="hidden"
                  accept="image/*,.pdf,.txt,.md,.doc,.docx"
                  onChange={handleHeaderFileChange}
                />
                <Button
                  variant="outline"
                  size="sm"
                  className="gap-2 border-white/10 hover:bg-white/5"
                  onClick={triggerHeaderUpload}
                  disabled={isLoaded && !isSignedIn}
                >
                  <UploadIcon className="h-4 w-4" />
                  <span className="hidden sm:inline">
                    {isSignedIn ? "Add Context" : "Sign in to add context"}
                  </span>
                  <span className="sm:hidden">
                    {isSignedIn ? "Upload" : "Sign in"}
                  </span>
                </Button>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5">
              {/* Goal Input */}
              <div className="space-y-1.5 sm:space-y-2">
                <Label
                  htmlFor="goal"
                  className="text-xs sm:text-sm font-medium"
                >
                  What do you want to achieve?
                </Label>
                <Input
                  id="goal"
                  placeholder="e.g., Generate a Python function to parse JSON"
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                  disabled={isLoading}
                  className="bg-background/50 border-white/10 focus:border-primary/50 transition-colors text-sm"
                />
              </div>

              {/* Prompt Input */}
              <div className="space-y-1.5 sm:space-y-2">
                <Label
                  htmlFor="prompt"
                  className="text-xs sm:text-sm font-medium"
                >
                  Your Prompt
                </Label>
                <Textarea
                  id="prompt"
                  placeholder="Enter the prompt you want to optimize..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  disabled={isLoading}
                  className="min-h-40 sm:min-h-48 resize-y bg-background/50 border-white/10 focus:border-primary/50 transition-colors text-sm"
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
              <div className="flex gap-2 sm:gap-3 pt-2">
                <Button
                  type="submit"
                  disabled={isLoading || !prompt.trim() || !goal.trim()}
                  className="flex-1 gap-2 gradient-primary text-white border-0 shadow-lg shadow-primary/25 hover:shadow-primary/40 transition-shadow text-sm sm:text-base"
                  size="lg"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span className="hidden xs:inline">Optimizing...</span>
                      <span className="xs:hidden">...</span>
                    </>
                  ) : (
                    <>
                      <Send className="h-4 w-4" />
                      <span className="hidden xs:inline">Optimize Prompt</span>
                      <span className="xs:hidden">Optimize</span>
                    </>
                  )}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleClear}
                  disabled={isLoading}
                  className="border-white/10 hover:bg-white/5 text-sm"
                  size="lg"
                >
                  Clear
                </Button>
              </div>
            </form>
          </div>

          {/* Score Card - appears below form after optimization */}
          <AnimatePresence>
            {result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="glass-strong rounded-xl p-4 sm:p-6 flex flex-col items-center"
              >
                <ScoreIndicator score={result.score} size="lg" />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Right Panel - Results */}
        <div className="min-h-72 sm:min-h-96">
          <AnimatePresence mode="wait">
            {isLoading ? (
              <motion.div
                key="loading"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="glass-strong rounded-xl p-6 sm:p-8 h-full flex flex-col items-center justify-center gap-4 sm:gap-6"
              >
                <div className="relative">
                  <div className="absolute inset-0 bg-linear-to-r from-purple-500 to-pink-500 blur-2xl opacity-50 animate-pulse" />
                  <Loader2 className="h-12 w-12 sm:h-16 sm:w-16 animate-spin text-primary relative" />
                </div>
                <div className="text-center space-y-1 sm:space-y-2">
                  <h3 className="text-base sm:text-lg font-semibold">
                    Analyzing your prompt...
                  </h3>
                  <p className="text-xs sm:text-sm text-muted-foreground">
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
              >
                {/* Result Details */}
                <ResultPanel result={result} />
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="glass rounded-xl p-6 sm:p-8 h-full flex flex-col items-center justify-center text-center gap-3 sm:gap-4"
              >
                <div className="mesh-gradient absolute inset-0 rounded-xl opacity-30" />
                <div className="relative space-y-3 sm:space-y-4">
                  <div className="w-16 h-16 sm:w-20 sm:h-20 mx-auto rounded-full bg-linear-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center">
                    <Sparkles className="w-8 h-8 sm:w-10 sm:h-10 text-primary" />
                  </div>
                  <div className="space-y-1 sm:space-y-2">
                    <h3 className="text-lg sm:text-xl font-semibold">
                      Ready to optimize?
                    </h3>
                    <p className="text-xs sm:text-sm text-muted-foreground max-w-md">
                      Enter your prompt and let our AI experts analyze and
                      improve it for you.
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
