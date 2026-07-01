"use client";

import * as React from "react";
import { UploadCloud, FileText, Trash2 } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { uploadDocument, DocumentUploadResponse } from "@/lib/api";

interface UploadPanelProps {
  onUploadSuccess: (docInfo: DocumentUploadResponse) => void;
  onReset: () => void;
  docInfo: DocumentUploadResponse | null;
  uploading: boolean;
  setUploading: (uploading: boolean) => void;
  analyzing: boolean;
  onStartAnalysis: () => void;
}

export function UploadPanel({
  onUploadSuccess,
  onReset,
  docInfo,
  uploading,
  setUploading,
  analyzing,
  onStartAnalysis,
}: UploadPanelProps) {
  const [dragActive, setDragActive] = React.useState(false);
  const [uploadProgress, setUploadProgress] = React.useState(0);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const processFile = async (file: File) => {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      toast.error("Invalid file format. Only PDF files are supported.");
      return;
    }

    const maxMb = 50;
    if (file.size > maxMb * 1024 * 1024) {
      toast.error(`File size exceeds the ${maxMb}MB limit.`);
      return;
    }

    setUploading(true);
    setUploadProgress(10);
    
    // Simulate initial upload progress steps
    const timer = setInterval(() => {
      setUploadProgress((prev) => (prev >= 80 ? prev : prev + 15));
    }, 150);

    try {
      const response = await uploadDocument(file);
      clearInterval(timer);
      setUploadProgress(100);
      
      // Delay to show 100% completion before finishing
      setTimeout(() => {
        onUploadSuccess(response);
        setUploading(false);
        setUploadProgress(0);
        toast.success("Document uploaded and text extracted successfully!");
      }, 300);
    } catch (error) {
      clearInterval(timer);
      setUploading(false);
      setUploadProgress(0);
      const errorMessage = error instanceof Error ? error.message : "Upload failed. Please try again.";
      toast.error(errorMessage);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await processFile(e.target.files[0]);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  return (
    <Card className="rounded-2xl border border-border shadow-sm flex flex-col h-full bg-card">
      <CardHeader className="pb-4">
        <CardTitle className="text-base font-bold flex items-center gap-2 text-foreground">
          <UploadCloud className="h-4.5 w-4.5 text-primary" />
          Document Upload
        </CardTitle>
        <CardDescription className="text-xs text-muted-foreground">
          Upload a PDF legal judgment to begin multi-agent analysis.
        </CardDescription>
      </CardHeader>
      
      <CardContent className="flex-1 flex flex-col gap-4">
        {!docInfo ? (
          // Drag and Drop Area
          <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            onClick={uploading ? undefined : triggerFileInput}
            className={`flex-1 border-2 border-dashed rounded-xl flex flex-col items-center justify-center p-6 text-center transition-all cursor-pointer ${
              dragActive
                ? "border-primary bg-primary/5 scale-[0.99]"
                : "border-muted-foreground/20 hover:border-primary/50 hover:bg-zinc-50/50 dark:hover:bg-zinc-950/20"
            } ${uploading ? "pointer-events-none opacity-60" : ""}`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={handleFileInput}
              disabled={uploading}
            />
            
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/5 text-primary mb-4 shadow-sm">
              <UploadCloud className="h-6 w-6" />
            </div>

            <p className="text-xs font-semibold text-foreground">
              {dragActive ? "Drop PDF file here" : "Drag & drop PDF judgment here"}
            </p>
            <p className="text-[10px] text-muted-foreground mt-1 max-w-[180px] mx-auto">
              Only PDF format supported (max 50MB)
            </p>
            
            {!uploading && (
              <Button size="sm" variant="outline" className="mt-4 rounded-xl text-xs font-medium">
                Choose File
              </Button>
            )}
          </div>
        ) : (
          // File Selected/Uploaded View
          <div className="flex-1 flex flex-col justify-between border border-border bg-zinc-50/50 dark:bg-zinc-950/10 rounded-xl p-4">
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <FileText className="h-5 w-5" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-semibold text-foreground truncate" title={docInfo.filename}>
                    {docInfo.filename}
                  </p>
                  <p className="text-[10px] text-muted-foreground mt-0.5">
                    {docInfo.page_count} {docInfo.page_count === 1 ? "page" : "pages"}
                  </p>
                </div>
              </div>

              {/* Status Badge */}
              <div className="rounded-lg border border-border bg-background p-3">
                <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block mb-1">
                  Extraction Status
                </span>
                <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-medium text-emerald-600 dark:text-emerald-400">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                  Text Extracted
                </span>
              </div>

              {/* Preview Box */}
              {docInfo.text_preview && (
                <div className="rounded-lg border border-border bg-background p-3">
                  <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block mb-1">
                    Text Preview
                  </span>
                  <p className="text-[10px] text-muted-foreground leading-normal line-clamp-4 italic">
                    &ldquo;{docInfo.text_preview}&rdquo;
                  </p>
                </div>
              )}
            </div>

            <div className="flex items-center gap-2 mt-4 pt-4 border-t border-border">
              <Button
                variant="outline"
                size="icon"
                onClick={onReset}
                disabled={analyzing}
                className="rounded-xl shrink-0 text-destructive hover:bg-destructive/10"
                aria-label="Remove document"
              >
                <Trash2 className="h-4.5 w-4.5" />
              </Button>
              
              <Button
                onClick={onStartAnalysis}
                disabled={analyzing}
                className="flex-1 rounded-xl text-xs font-semibold shadow-sm hover:shadow"
              >
                {analyzing ? "Analyzing..." : "Analyze Judgment"}
              </Button>
            </div>
          </div>
        )}

        {/* Uploading progress indicator */}
        {uploading && (
          <div className="space-y-2 py-2">
            <div className="flex justify-between items-center text-xs">
              <span className="text-muted-foreground font-medium">Uploading & indexing...</span>
              <span className="font-semibold text-primary">{uploadProgress}%</span>
            </div>
            <Progress value={uploadProgress} className="h-1.5 bg-muted" />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
