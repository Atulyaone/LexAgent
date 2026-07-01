"use client";

import * as React from "react";
import { FileText, Copy, Check, Download } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { toast } from "sonner";
import { AnalyzeResponse } from "@/lib/api";

interface FiracResultsProps {
  result: AnalyzeResponse | null;
  analyzing: boolean;
}

type TabType = "all" | "facts" | "issues" | "rule" | "analysis" | "conclusion";

export function FiracResults({ result, analyzing }: FiracResultsProps) {
  const [activeTab, setActiveTab] = React.useState<TabType>("all");
  const [copied, setCopied] = React.useState(false);

  const brief = result?.firac_brief;

  const tabs: { id: TabType; label: string }[] = [
    { id: "all", label: "Full Brief" },
    { id: "facts", label: "Facts" },
    { id: "issues", label: "Issues" },
    { id: "rule", label: "Rule" },
    { id: "analysis", label: "Analysis" },
    { id: "conclusion", label: "Conclusion" },
  ];

  const getBriefMarkdown = (): string => {
    if (!brief) return "";
    return `# FIRAC Brief: ${result.filename}
    
## Facts
${brief.facts}

## Issues
${brief.issues}

## Rule
${brief.rule}

## Analysis
${brief.analysis}

## Conclusion
${brief.conclusion}
`;
  };

  const getActiveContent = (): string => {
    if (!brief) return "";
    if (activeTab === "all") return getBriefMarkdown();
    return brief[activeTab] || "";
  };

  const handleCopy = async () => {
    const content = getActiveContent();
    if (!content) return;

    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      toast.success("Content copied to clipboard!");
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error("Failed to copy content.");
    }
  };

  const handleDownload = () => {
    if (!result) return;
    const mdContent = getBriefMarkdown();
    if (!mdContent) return;

    const blob = new Blob([mdContent], { type: "text/markdown;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `FIRAC_Brief_${result.filename.replace(/\.[^/.]+$/, "")}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    toast.success("Markdown brief downloaded successfully!");
  };

  return (
    <Card className="rounded-2xl border border-border shadow-sm flex flex-col h-full bg-card overflow-hidden">
      {/* Panel Header */}
      <CardHeader className="pb-3 border-b border-border bg-zinc-50/50 dark:bg-zinc-950/20 flex flex-row items-center justify-between space-y-0">
        <div>
          <CardTitle className="text-base font-bold flex items-center gap-2 text-foreground">
            <FileText className="h-4.5 w-4.5 text-primary" />
            FIRAC Case Brief
          </CardTitle>
          <CardDescription className="text-xs text-muted-foreground">
            Structured analysis output of the judgment.
          </CardDescription>
        </div>

        {/* Action Buttons (Copy, Download) */}
        {result && !analyzing && (
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-lg"
              onClick={handleCopy}
              title="Copy active section"
            >
              {copied ? <Check className="h-4 w-4 text-emerald-500" /> : <Copy className="h-4 w-4" />}
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-lg"
              onClick={handleDownload}
              title="Download Markdown brief"
            >
              <Download className="h-4 w-4" />
            </Button>
          </div>
        )}
      </CardHeader>

      {/* Tab Switcher Bar */}
      {result && !analyzing && (
        <div className="flex border-b border-border bg-zinc-50/20 dark:bg-zinc-950/5 p-1 overflow-x-auto gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg shrink-0 transition-colors ${
                activeTab === tab.id
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:bg-accent/50 hover:text-foreground"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      )}

      {/* Content Area */}
      <CardContent className="flex-1 min-h-0 p-0 relative">
        {analyzing ? (
          // Skeleton Loader during analysis state
          <div className="p-6 space-y-6 h-full overflow-y-auto">
            <div className="space-y-2">
              <Skeleton className="h-4 w-32 bg-muted/60" />
              <Skeleton className="h-24 w-full bg-muted/60" />
            </div>
            <div className="space-y-2">
              <Skeleton className="h-4 w-24 bg-muted/60" />
              <Skeleton className="h-16 w-full bg-muted/60" />
            </div>
            <div className="space-y-2">
              <Skeleton className="h-4 w-40 bg-muted/60" />
              <Skeleton className="h-32 w-full bg-muted/60" />
            </div>
          </div>
        ) : brief ? (
          // Brief Render Area
          <ScrollArea className="h-full">
            <div className="p-6">
              {activeTab === "all" ? (
                // Full Document Render
                <div className="space-y-8">
                  <section className="space-y-2">
                    <h3 className="text-xs font-extrabold uppercase tracking-wider text-primary border-l-2 border-primary pl-2 flex items-center gap-1.5">
                      Facts
                    </h3>
                    <p className="text-sm leading-relaxed text-foreground/90 whitespace-pre-wrap pl-2.5">
                      {brief.facts}
                    </p>
                  </section>

                  <section className="space-y-2">
                    <h3 className="text-xs font-extrabold uppercase tracking-wider text-primary border-l-2 border-primary pl-2 flex items-center gap-1.5">
                      Issues
                    </h3>
                    <p className="text-sm leading-relaxed text-foreground/90 whitespace-pre-wrap pl-2.5">
                      {brief.issues}
                    </p>
                  </section>

                  <section className="space-y-2">
                    <h3 className="text-xs font-extrabold uppercase tracking-wider text-primary border-l-2 border-primary pl-2 flex items-center gap-1.5">
                      Rule
                    </h3>
                    <p className="text-sm leading-relaxed text-foreground/90 whitespace-pre-wrap pl-2.5">
                      {brief.rule}
                    </p>
                  </section>

                  <section className="space-y-2">
                    <h3 className="text-xs font-extrabold uppercase tracking-wider text-primary border-l-2 border-primary pl-2 flex items-center gap-1.5">
                      Analysis
                    </h3>
                    <p className="text-sm leading-relaxed text-foreground/90 whitespace-pre-wrap pl-2.5">
                      {brief.analysis}
                    </p>
                  </section>

                  <section className="space-y-2">
                    <h3 className="text-xs font-extrabold uppercase tracking-wider text-primary border-l-2 border-primary pl-2 flex items-center gap-1.5">
                      Conclusion
                    </h3>
                    <p className="text-sm leading-relaxed text-foreground/90 whitespace-pre-wrap pl-2.5">
                      {brief.conclusion}
                    </p>
                  </section>
                </div>
              ) : (
                // Individual Section Render
                <div className="space-y-3">
                  <h3 className="text-xs font-extrabold uppercase tracking-wider text-primary border-l-2 border-primary pl-2">
                    {activeTab}
                  </h3>
                  <p className="text-sm leading-relaxed text-foreground/90 whitespace-pre-wrap pl-2.5">
                    {brief[activeTab]}
                  </p>
                </div>
              )}
            </div>
          </ScrollArea>
        ) : (
          // Default empty/idle state
          <div className="flex flex-col items-center justify-center p-8 text-center h-full space-y-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/5 text-primary shadow-inner">
              <FileText className="h-6 w-6" />
            </div>
            <p className="text-xs font-semibold text-foreground">No case brief generated yet</p>
            <p className="text-[10px] text-muted-foreground max-w-[280px] leading-relaxed">
              Synthesizing legal documents takes precision. Once you upload your document, click &ldquo;Analyze Judgment&rdquo; to start the multi-agent legal synthesis.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
