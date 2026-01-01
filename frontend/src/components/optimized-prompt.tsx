"use client";

import { useState } from "react";
import { Copy, Check, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface OptimizedPromptProps {
  originalPrompt: string;
  optimizedPrompt: string;
  className?: string;
}

export function OptimizedPrompt({
  originalPrompt,
  optimizedPrompt,
  className,
}: OptimizedPromptProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(optimizedPrompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            <CardTitle className="text-lg">Optimized Prompt</CardTitle>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleCopy}
            className="gap-2"
          >
            {copied ? (
              <>
                <Check className="h-4 w-4" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="h-4 w-4" />
                Copy
              </>
            )}
          </Button>
        </div>
        <CardDescription>Your improved prompt ready to use</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="optimized" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="optimized">Optimized</TabsTrigger>
            <TabsTrigger value="compare">Compare</TabsTrigger>
          </TabsList>

          <TabsContent value="optimized" className="mt-4">
            <div className="bg-muted/50 p-4 rounded-lg">
              <p className="text-sm whitespace-pre-wrap leading-relaxed">
                {optimizedPrompt}
              </p>
            </div>
          </TabsContent>

          <TabsContent value="compare" className="mt-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-muted-foreground">
                  Original
                </h4>
                <div className="bg-muted/30 p-3 rounded-lg border border-dashed">
                  <p className="text-sm whitespace-pre-wrap leading-relaxed text-muted-foreground">
                    {originalPrompt}
                  </p>
                </div>
              </div>
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-primary">Optimized</h4>
                <div className="bg-primary/5 p-3 rounded-lg border border-primary/20">
                  <p className="text-sm whitespace-pre-wrap leading-relaxed">
                    {optimizedPrompt}
                  </p>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
