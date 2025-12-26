"use client";

import { motion } from "framer-motion";
import { Code2, PenTool, BarChart3, Wrench, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

type AgentType = "auto" | "coding" | "creative" | "analyst" | "general";

interface AgentOption {
  value: AgentType;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  description: string;
}

const agents: AgentOption[] = [
  {
    value: "auto",
    label: "Auto-detect",
    icon: Sparkles,
    color: "from-purple-500 to-pink-500",
    description: "AI routes to best expert",
  },
  {
    value: "coding",
    label: "Coding",
    icon: Code2,
    color: "from-blue-500 to-cyan-500",
    description: "Code & development",
  },
  {
    value: "creative",
    label: "Creative",
    icon: PenTool,
    color: "from-pink-500 to-rose-500",
    description: "Writing & content",
  },
  {
    value: "analyst",
    label: "Analyst",
    icon: BarChart3,
    color: "from-green-500 to-emerald-500",
    description: "Data & research",
  },
  {
    value: "general",
    label: "General",
    icon: Wrench,
    color: "from-gray-500 to-slate-500",
    description: "General tasks",
  },
];

interface AgentSelectorProps {
  value: AgentType;
  onChange: (value: AgentType) => void;
  disabled?: boolean;
}

export function AgentSelector({
  value,
  onChange,
  disabled,
}: AgentSelectorProps) {
  return (
    <div className="space-y-3">
      <label className="text-sm font-medium text-foreground/90">
        Select Expert Agent
      </label>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
        {agents.map((agent) => {
          const Icon = agent.icon;
          const isSelected = value === agent.value;

          return (
            <motion.button
              key={agent.value}
              type="button"
              onClick={() => !disabled && onChange(agent.value)}
              disabled={disabled}
              whileHover={!disabled ? { scale: 1.05 } : {}}
              whileTap={!disabled ? { scale: 0.95 } : {}}
              className={cn(
                "relative p-3 rounded-lg border-2 transition-all duration-200",
                "flex flex-col items-center gap-2 text-center",
                "disabled:opacity-50 disabled:cursor-not-allowed",
                isSelected
                  ? "border-primary bg-primary/10 shadow-lg shadow-primary/20"
                  : "border-border hover:border-primary/50 bg-card/50"
              )}
            >
              {isSelected && (
                <motion.div
                  layoutId="agent-selector"
                  className="absolute inset-0 bg-gradient-to-br from-primary/20 to-transparent rounded-lg"
                  transition={{ type: "spring", duration: 0.6 }}
                />
              )}

              <div
                className={cn(
                  "relative w-8 h-8 rounded-full flex items-center justify-center",
                  isSelected ? `bg-gradient-to-br ${agent.color}` : "bg-muted"
                )}
              >
                <Icon
                  className={cn(
                    "w-4 h-4",
                    isSelected ? "text-white" : "text-muted-foreground"
                  )}
                />
              </div>

              <div className="relative">
                <div
                  className={cn(
                    "text-xs font-medium",
                    isSelected ? "text-foreground" : "text-muted-foreground"
                  )}
                >
                  {agent.label}
                </div>
                <div className="text-[10px] text-muted-foreground hidden md:block">
                  {agent.description}
                </div>
              </div>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}
