"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { TrendingUp, Award, AlertCircle } from "lucide-react";

interface ScoreIndicatorProps {
  score: number;
  className?: string;
  size?: "sm" | "md" | "lg";
}

function getScoreColor(score: number): string {
  if (score >= 80) return "text-green-500";
  if (score >= 60) return "text-yellow-500";
  if (score >= 40) return "text-orange-500";
  return "text-red-500";
}

function getScoreGradient(score: number): string {
  if (score >= 80) return "from-green-500 to-emerald-500";
  if (score >= 60) return "from-yellow-500 to-orange-500";
  if (score >= 40) return "from-orange-500 to-red-500";
  return "from-red-500 to-rose-500";
}

function getScoreLabel(score: number): string {
  if (score >= 90) return "Excellent";
  if (score >= 80) return "Great";
  if (score >= 70) return "Good";
  if (score >= 60) return "Fair";
  if (score >= 40) return "Needs Work";
  return "Poor";
}

function getScoreIcon(score: number) {
  if (score >= 80) return Award;
  if (score >= 60) return TrendingUp;
  return AlertCircle;
}

export function ScoreIndicator({
  score,
  className,
  size = "md",
}: ScoreIndicatorProps) {
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    const duration = 1000;
    const steps = 60;
    const increment = score / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= score) {
        setDisplayScore(score);
        clearInterval(timer);
      } else {
        setDisplayScore(Math.floor(current));
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [score]);

  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (displayScore / 100) * circumference;

  const sizes = {
    sm: { container: "w-24 h-24", text: "text-xl", label: "text-xs" },
    md: { container: "w-32 h-32", text: "text-3xl", label: "text-sm" },
    lg: { container: "w-40 h-40", text: "text-4xl", label: "text-base" },
  };

  const Icon = getScoreIcon(score);

  return (
    <div className={cn("flex flex-col items-center gap-3", className)}>
      <div className={cn("relative", sizes[size].container)}>
        {/* Background circle */}
        <svg className="absolute inset-0 -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            className="text-muted/20"
          />
        </svg>

        {/* Animated progress circle */}
        <svg className="absolute inset-0 -rotate-90" viewBox="0 0 100 100">
          <motion.circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            strokeWidth="8"
            strokeLinecap="round"
            className={cn("stroke-current", getScoreColor(score))}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1, ease: "easeOut" }}
            style={{
              strokeDasharray: circumference,
            }}
          />
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3, type: "spring" }}
            className={cn(
              "font-bold tabular-nums",
              sizes[size].text,
              getScoreColor(score)
            )}
          >
            {displayScore}
          </motion.div>
          <div className="text-xs text-muted-foreground">/ 100</div>
        </div>

        {/* Glow effect */}
        <div
          className={cn(
            "absolute inset-0 rounded-full blur-xl opacity-30",
            `bg-gradient-to-br ${getScoreGradient(score)}`
          )}
        />
      </div>

      <div className="flex items-center gap-2">
        <Icon className={cn("w-4 h-4", getScoreColor(score))} />
        <span className={cn("font-medium", sizes[size].label)}>
          {getScoreLabel(score)}
        </span>
      </div>
    </div>
  );
}
