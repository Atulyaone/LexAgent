"use client";

import * as React from "react";
import { ListFilter, Cpu, Clock, Layers, AlertTriangle, CircleDot } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { AnalyzeResponse } from "@/lib/api";

interface WorkflowTraceProps {
  result: AnalyzeResponse | null;
  analyzing: boolean;
  currentAgent: string | null;
  progress: number;
}

export function WorkflowTrace({ result, analyzing, currentAgent, progress }: WorkflowTraceProps) {
  // Determine color theme based on confidence score
  const getConfidenceStyles = (score: number, hallucination: boolean) => {
    if (hallucination) {
      return {
        bg: "bg-destructive/10 text-destructive border-destructive/20",
        ring: "ring-destructive/30",
        label: "Hallucination Warning",
        text: "text-destructive",
      };
    }
    if (score >= 90) {
      return {
        bg: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
        ring: "ring-emerald-500/30",
        label: "High Confidence",
        text: "text-emerald-600 dark:text-emerald-400",
      };
    }
    if (score >= 70) {
      return {
        bg: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
        ring: "ring-amber-500/30",
        label: "Moderate Confidence",
        text: "text-amber-600 dark:text-amber-400",
      };
    }
    return {
      bg: "bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20",
      ring: "ring-red-500/30",
      label: "Low Confidence",
      text: "text-red-600 dark:text-red-400",
    };
  };

  const confidence = result?.confidence_score ?? 100;
  const hallucinationDetected = result?.hallucination_detected ?? false;
  const confidenceStyles = getConfidenceStyles(confidence, hallucinationDetected);

  return (
    <Card className="rounded-2xl border border-border shadow-sm flex flex-col h-full bg-card overflow-hidden">
      {/* Panel Header */}
      <CardHeader className="pb-3 border-b border-border bg-zinc-50/50 dark:bg-zinc-950/20">
        <CardTitle className="text-base font-bold flex items-center gap-2 text-foreground">
          <ListFilter className="h-4.5 w-4.5 text-primary" />
          Workflow & Observability
        </CardTitle>
        <CardDescription className="text-xs text-muted-foreground">
          Real-time pipeline monitoring.
        </CardDescription>
      </CardHeader>

      {/* Main Panel Content */}
      <CardContent className="flex-1 flex flex-col p-4 gap-4 min-h-0">
        {analyzing ? (
          // Active Analysis State
          <div className="flex-1 flex flex-col justify-between py-2">
            <div className="space-y-4">
              <div className="rounded-xl border border-border bg-accent/20 p-4 space-y-3">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-semibold text-foreground">Pipeline Execution</span>
                  <span className="text-primary font-bold text-xs">{progress}%</span>
                </div>
                <Progress value={progress} className="h-2 bg-muted" />
                <p className="text-[10px] text-muted-foreground animate-pulse leading-normal italic">
                  {currentAgent || "Orchestrating agent workflow..."}
                </p>
              </div>

              {/* Progress Stepper Visualizer */}
              <div className="space-y-2.5 pl-2 mt-4">
                <div className="flex items-center gap-2 text-xs">
                  <CircleDot className={`h-4.5 w-4.5 shrink-0 text-primary ${progress >= 10 ? "animate-ping" : ""}`} />
                  <span className={progress >= 10 ? "font-semibold text-foreground" : "text-muted-foreground"}>
                    Research Agent
                  </span>
                </div>
                <div className="h-3 border-l border-border ml-2" />
                <div className="flex items-center gap-2 text-xs">
                  <CircleDot className={`h-4.5 w-4.5 shrink-0 ${progress >= 40 ? "text-primary animate-ping" : "text-muted-foreground/30"}`} />
                  <span className={progress >= 40 ? "font-semibold text-foreground" : "text-muted-foreground"}>
                    Case Analysis Agent
                  </span>
                </div>
                <div className="h-3 border-l border-border ml-2" />
                <div className="flex items-center gap-2 text-xs">
                  <CircleDot className={`h-4.5 w-4.5 shrink-0 ${progress >= 70 ? "text-primary animate-ping" : "text-muted-foreground/30"}`} />
                  <span className={progress >= 70 ? "font-semibold text-foreground" : "text-muted-foreground"}>
                    Verification Agent
                  </span>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-dashed border-border p-4 text-center text-[10px] text-muted-foreground">
              Please wait while the orchestrator synthesizes the legal document.
            </div>
          </div>
        ) : result ? (
          // Completed State: Show metrics, confidence score and timeline trace
          <div className="flex-1 flex flex-col gap-4 min-h-0">
            
            {/* Confidence Score Card */}
            <div className={`rounded-xl border p-4 flex items-center justify-between shadow-sm transition-all ${confidenceStyles.bg}`}>
              <div className="space-y-1">
                <span className="text-[10px] font-bold uppercase tracking-wider block opacity-75">
                  Brief Verification
                </span>
                <span className="text-xs font-semibold block">
                  {confidenceStyles.label}
                </span>
                {hallucinationDetected && (
                  <span className="text-[9px] font-medium leading-none block text-destructive flex items-center gap-0.5">
                    <AlertTriangle className="h-2.5 w-2.5 shrink-0" />
                    Hallucinated references flagged
                  </span>
                )}
              </div>
              <div className="text-right flex flex-col items-end">
                <span className="text-3xl font-extrabold tracking-tight leading-none">
                  {confidence}%
                </span>
                <span className="text-[9px] font-bold block opacity-75 mt-0.5">
                  Confidence Score
                </span>
              </div>
            </div>

            {/* Performance Statistics Grid */}
            <div className="grid grid-cols-3 gap-2">
              <div className="rounded-xl border border-border bg-zinc-50/50 dark:bg-zinc-950/20 p-2 text-center">
                <Clock className="h-4 w-4 text-muted-foreground mx-auto mb-1.5" />
                <span className="text-[9px] text-muted-foreground block font-medium">Latency</span>
                <span className="text-[11px] font-bold text-foreground">
                  {(result.metadata.processing_time_ms / 1000).toFixed(2)}s
                </span>
              </div>
              <div className="rounded-xl border border-border bg-zinc-50/50 dark:bg-zinc-950/20 p-2 text-center">
                <Layers className="h-4 w-4 text-muted-foreground mx-auto mb-1.5" />
                <span className="text-[9px] text-muted-foreground block font-medium">Pages</span>
                <span className="text-[11px] font-bold text-foreground">
                  {result.metadata.page_count}
                </span>
              </div>
              <div className="rounded-xl border border-border bg-zinc-50/50 dark:bg-zinc-950/20 p-2 text-center">
                <Cpu className="h-4 w-4 text-muted-foreground mx-auto mb-1.5" />
                <span className="text-[9px] text-muted-foreground block font-medium">Model</span>
                <span className="text-[10px] font-bold text-foreground truncate block max-w-full" title={result.metadata.model}>
                  {result.metadata.model.replace("gemini-", "")}
                </span>
              </div>
            </div>

            {/* Trace log Timeline */}
            <div className="flex-1 flex flex-col min-h-0">
              <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block mb-2">
                Execution Log
              </span>
              
              <ScrollArea className="flex-1 border border-border bg-zinc-50/20 dark:bg-zinc-950/5 rounded-xl p-3">
                {result.trace && result.trace.length > 0 ? (
                  <div className="relative border-l border-border pl-4 space-y-4 py-1">
                    {result.trace.map((event, index) => {
                      const isLast = index === result.trace!.length - 1;
                      return (
                        <div key={index} className="relative text-xs">
                          {/* Dot Indicator */}
                          <div className={`absolute -left-[21.5px] top-1.5 h-2 w-2 rounded-full border bg-background ${
                            isLast ? "border-primary bg-primary scale-125 shadow-sm shadow-primary/20" : "border-muted-foreground/30"
                          }`} />
                          
                          <span className={`block font-medium ${isLast ? "text-foreground font-semibold" : "text-muted-foreground"}`}>
                            {event}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="text-center py-6 text-[10px] text-muted-foreground italic">
                    No execution events in trace log.
                  </div>
                )}
              </ScrollArea>
            </div>

          </div>
        ) : (
          // Idle State
          <div className="flex flex-col items-center justify-center p-8 text-center h-full space-y-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/5 text-primary shadow-inner">
              <ListFilter className="h-6 w-6" />
            </div>
            <p className="text-xs font-semibold text-foreground">Observability idle</p>
            <p className="text-[10px] text-muted-foreground max-w-[200px] leading-relaxed">
              Real-time monitoring logs, LLM latency stats, and verification metrics will appear here during execution.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
