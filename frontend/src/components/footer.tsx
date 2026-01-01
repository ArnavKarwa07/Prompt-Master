import Link from "next/link";
import { Sparkles, Github } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t py-6 md:py-0">
      <div className="container flex flex-col items-center justify-between gap-4 md:h-16 md:flex-row">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Sparkles className="h-4 w-4" />
          <span>Prompt Master</span>
          <span className="hidden md:inline">•</span>
          <span className="hidden md:inline">Multi-Agent Prompt Optimizer</span>
        </div>

        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <Link
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-foreground transition-colors"
          >
            <Github className="h-4 w-4" />
          </Link>
          <span>Built with LangGraph + Groq</span>
        </div>
      </div>
    </footer>
  );
}
