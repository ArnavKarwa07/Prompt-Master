"use client";

import { motion } from "framer-motion";
import { Copy, Check, ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { OptimizeResponse } from "@/lib/api";

interface ResultPanelProps {
  result: OptimizeResponse;
  className?: string;
}

export function ResultPanel({ result, className }: ResultPanelProps) {
  const [copiedOriginal, setCopiedOriginal] = useState(false);
  const [copiedOptimized, setCopiedOptimized] = useState(false);
  const [showFeedback, setShowFeedback] = useState(true);

  const copyToClipboard = async (
    text: string,
    type: "original" | "optimized"
  ) => {
    await navigator.clipboard.writeText(text);
    if (type === "original") {
      setCopiedOriginal(true);
      setTimeout(() => setCopiedOriginal(false), 2000);
    } else {
      setCopiedOptimized(true);
      setTimeout(() => setCopiedOptimized(false), 2000);
    }
  };

  const agentLabels: Record<
    string,
    { label: string; color: string; gradient: string }
  > = {
    coding: {
      label: "Coding Expert",
      color: "bg-blue-500",
      gradient: "from-blue-500 to-cyan-500",
    },
    creative: {
      label: "Creative Writer",
      color: "bg-pink-500",
      gradient: "from-pink-500 to-rose-500",
    },
    analyst: {
      label: "Data Analyst",
      color: "bg-green-500",
      gradient: "from-green-500 to-emerald-500",
    },
    general: {
      label: "General Assistant",
      color: "bg-gray-500",
      gradient: "from-gray-500 to-slate-500",
    },
  };

  const agent = agentLabels[result.agent] || agentLabels.general;

  return (
    <div className={cn("space-y-3 sm:space-y-4", className)}>
      {/* Agent & Confidence */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-2 sm:gap-3 flex-wrap"
      >
        <div className="flex items-center gap-1.5 sm:gap-2">
          <span className="text-xs sm:text-sm text-muted-foreground">
            Analyzed by:
          </span>
          <Badge
            className={cn(
              "bg-linear-to-r text-white border-0 text-xs",
              agent.gradient
            )}
          >
            {agent.label}
          </Badge>
        </div>
        <Badge variant="outline" className="border-primary/30 text-xs">
          {Math.round(result.routing.confidence * 100)}% confident
        </Badge>
      </motion.div>

      {/* Optimized Prompt */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-strong rounded-lg p-3 sm:p-4 space-y-2 sm:space-y-3"
      >
        <div className="flex items-center justify-between">
          <div className="text-[10px] sm:text-xs text-muted-foreground uppercase tracking-wider">
            Optimized Prompt
          </div>
          <Button
            size="sm"
            variant="ghost"
            onClick={() =>
              copyToClipboard(result.optimized_prompt, "optimized")
            }
            className="h-6 sm:h-7 gap-1.5 sm:gap-2 px-2"
          >
            {copiedOptimized ? (
              <>
                <Check className="w-3 h-3" />
                <span className="text-[10px] sm:text-xs">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-3 h-3" />
                <span className="text-[10px] sm:text-xs">Copy</span>
              </>
            )}
          </Button>
        </div>
        <div className="bg-background/50 rounded-md p-3 sm:p-4 border border-border/50">
          <p className="text-xs sm:text-sm leading-relaxed whitespace-pre-wrap">
            {result.optimized_prompt}
          </p>
        </div>
      </motion.div>

      {/* Routing Reasoning */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass-strong rounded-lg p-3 sm:p-4"
      >
        <div className="text-[10px] sm:text-xs text-muted-foreground uppercase tracking-wider mb-1.5 sm:mb-2">
          Routing Decision
        </div>
        <p className="text-xs sm:text-sm leading-relaxed">
          {result.routing.reasoning}
        </p>
      </motion.div>

      {/* Feedback Section */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="glass-strong rounded-lg overflow-hidden"
      >
        <button
          onClick={() => setShowFeedback(!showFeedback)}
          className="w-full p-3 sm:p-4 flex items-center justify-between hover:bg-white/5 transition-colors"
        >
          <div className="flex items-center gap-2">
            <span className="text-xs sm:text-sm font-medium">
              Expert Feedback
            </span>
          </div>
          {showFeedback ? (
            <ChevronUp className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          )}
        </button>
        {showFeedback && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="px-3 sm:px-4 pb-3 sm:pb-4"
          >
            <p className="text-xs sm:text-sm leading-relaxed text-muted-foreground">
              {result.feedback}
            </p>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
