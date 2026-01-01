"use client";

import { cn } from "@/lib/utils";
import { Progress } from "@/components/ui/progress";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { OptimizeResponse } from "@/lib/api";

interface ScoreCardProps {
  result: OptimizeResponse;
  className?: string;
}

function getScoreColor(score: number): string {
  if (score >= 80) return "text-green-500";
  if (score >= 60) return "text-yellow-500";
  if (score >= 40) return "text-orange-500";
  return "text-red-500";
}

function getScoreLabel(score: number): string {
  if (score >= 90) return "Excellent";
  if (score >= 80) return "Great";
  if (score >= 70) return "Good";
  if (score >= 60) return "Fair";
  if (score >= 40) return "Needs Work";
  return "Poor";
}

function getProgressColor(score: number): string {
  if (score >= 80) return "bg-green-500";
  if (score >= 60) return "bg-yellow-500";
  if (score >= 40) return "bg-orange-500";
  return "bg-red-500";
}

export function ScoreCard({ result, className }: ScoreCardProps) {
  const agentLabels: Record<string, { label: string; color: string }> = {
    coding: { label: "Coding Expert", color: "bg-blue-500" },
    creative: { label: "Creative Writer", color: "bg-purple-500" },
    analyst: { label: "Data Analyst", color: "bg-emerald-500" },
    general: { label: "General Assistant", color: "bg-gray-500" },
  };

  const agent = agentLabels[result.agent] || agentLabels.general;

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="text-lg">Prompt Score</CardTitle>
            <CardDescription>Evaluated by {agent.label}</CardDescription>
          </div>
          <div className="text-right">
            <div
              className={cn("text-4xl font-bold", getScoreColor(result.score))}
            >
              {result.score}
            </div>
            <div className="text-sm text-muted-foreground">
              {getScoreLabel(result.score)}
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Score Progress Bar */}
        <div className="space-y-2">
          <Progress
            value={result.score}
            className={cn("h-2", getProgressColor(result.score))}
          />
        </div>

        {/* Agent & Confidence */}
        <div className="flex items-center gap-2 flex-wrap">
          <Badge className={agent.color}>{result.agent}</Badge>
          <Badge variant="outline">
            {Math.round(result.routing.confidence * 100)}% confident
          </Badge>
        </div>

        {/* Routing Reasoning */}
        <div className="text-sm text-muted-foreground bg-muted/50 p-3 rounded-md">
          <span className="font-medium">Routing: </span>
          {result.routing.reasoning}
        </div>

        {/* Feedback */}
        <div className="space-y-2">
          <h4 className="font-medium text-sm">Feedback</h4>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {result.feedback}
          </p>
        </div>

        {/* Error Display */}
        {result.error && (
          <div className="bg-destructive/10 text-destructive p-3 rounded-md text-sm">
            <span className="font-medium">Error: </span>
            {result.error}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
