import { Scale } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-border bg-zinc-50 dark:bg-zinc-950/20">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <Scale className="h-4.5 w-4.5" />
            </div>
            <span className="font-semibold text-sm text-foreground">
              LexAgent
            </span>
            <span className="text-xs text-muted-foreground">
              — AI Multi-Agent Legal Platform
            </span>
          </div>
          <p className="text-xs text-muted-foreground">
            &copy; {new Date().getFullYear()} LexAgent. Built for premium legal research.
          </p>
        </div>
      </div>
    </footer>
  );
}
