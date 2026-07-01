"use client";

import * as React from "react";
import { Navbar } from "@/components/navbar";
import { Footer } from "@/components/footer";
import { UploadPanel } from "@/components/upload-panel";
import { FiracResults } from "@/components/firac-results";
import { WorkflowTrace } from "@/components/workflow-trace";
import { DocumentUploadResponse, AnalyzeResponse, analyzeDocument } from "@/lib/api";
import { toast } from "sonner";

export default function AnalyzerPage() {
  const [docInfo, setDocInfo] = React.useState<DocumentUploadResponse | null>(null);
  const [uploading, setUploading] = React.useState(false);
  const [analyzing, setAnalyzing] = React.useState(false);
  const [analysisResult, setAnalysisResult] = React.useState<AnalyzeResponse | null>(null);
  
  // Observability simulator states while blocking HTTP call runs
  const [currentAgent, setCurrentAgent] = React.useState<string | null>(null);
  const [simulatedProgress, setSimulatedProgress] = React.useState(0);

  const handleUploadSuccess = (info: DocumentUploadResponse) => {
    setDocInfo(info);
    setAnalysisResult(null);
    setCurrentAgent(null);
    setSimulatedProgress(0);
  };

  const handleReset = () => {
    setDocInfo(null);
    setAnalysisResult(null);
    setUploading(false);
    setAnalyzing(false);
    setCurrentAgent(null);
    setSimulatedProgress(0);
  };

  const handleStartAnalysis = async () => {
    if (!docInfo) return;

    setAnalyzing(true);
    setAnalysisResult(null);
    setSimulatedProgress(10);
    setCurrentAgent("Research Agent Starting...");

    // Timers to simulate progress updates for the user during the blocking API request
    let timerStep = 0;
    const progressInterval = setInterval(() => {
      timerStep += 1;
      if (timerStep === 1) {
        setCurrentAgent("Research Agent: Extracting statutes & precedents...");
        setSimulatedProgress(25);
      } else if (timerStep === 4) {
        setCurrentAgent("Case Analysis Agent: Identifying facts & defining legal issues...");
        setSimulatedProgress(50);
      } else if (timerStep === 8) {
        setCurrentAgent("Verification Agent: Reviewing references & checks...");
        setSimulatedProgress(75);
      } else if (timerStep === 12) {
        setCurrentAgent("Verification Agent: Detecting potential model hallucinations...");
        setSimulatedProgress(90);
      } else if (timerStep >= 18) {
        setSimulatedProgress((prev) => (prev >= 98 ? 98 : prev + 1));
      }
    }, 500);

    try {
      const response = await analyzeDocument(docInfo.doc_id);
      
      clearInterval(progressInterval);
      setSimulatedProgress(100);
      setCurrentAgent("Workflow Complete");
      
      setTimeout(() => {
        setAnalysisResult(response);
        setAnalyzing(false);
        toast.success("Orchestration pipeline finished! FIRAC brief generated.");
      }, 300);
    } catch (error) {
      clearInterval(progressInterval);
      setAnalyzing(false);
      setCurrentAgent("Workflow Failed");
      setSimulatedProgress(0);
      const errorMessage = error instanceof Error ? error.message : "Multi-agent analysis failed. Please try again.";
      toast.error(errorMessage);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-zinc-50/50 dark:bg-zinc-950/20">
      <Navbar />

      {/* Workspace Grid Container */}
      <main className="flex-1 flex flex-col p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full">
        <div className="flex flex-col lg:grid lg:grid-cols-12 gap-6 items-stretch flex-1 min-h-0">
          
          {/* Upload Panel (25% equivalent: 3 cols in 12-col grid) */}
          <div className="lg:col-span-3 flex flex-col h-[650px] lg:h-auto">
            <UploadPanel
              onUploadSuccess={handleUploadSuccess}
              onReset={handleReset}
              docInfo={docInfo}
              uploading={uploading}
              setUploading={setUploading}
              analyzing={analyzing}
              onStartAnalysis={handleStartAnalysis}
            />
          </div>

          {/* FIRAC Results Panel (50% equivalent: 6 cols in 12-col grid) */}
          <div className="lg:col-span-6 flex flex-col h-[650px] lg:h-auto">
            <FiracResults
              result={analysisResult}
              analyzing={analyzing}
            />
          </div>

          {/* Workflow Trace + Confidence Panel (25% equivalent: 3 cols in 12-col grid) */}
          <div className="lg:col-span-3 flex flex-col h-[650px] lg:h-auto">
            <WorkflowTrace
              result={analysisResult}
              analyzing={analyzing}
              currentAgent={currentAgent}
              progress={simulatedProgress}
            />
          </div>

        </div>
      </main>

      <Footer />
    </div>
  );
}
