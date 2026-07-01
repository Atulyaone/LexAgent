export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface DocumentUploadResponse {
  doc_id: string;
  filename: string;
  page_count: number;
  status: string;
  text_preview: string;
}

export interface FiracBrief {
  facts: string;
  issues: string;
  rule: string;
  analysis: string;
  conclusion: string;
}

export interface AnalysisMetadata {
  page_count: number;
  model: string;
  processing_time_ms: number;
}

export interface AnalyzeResponse {
  doc_id: string;
  filename: string;
  status: string;
  firac_brief: FiracBrief;
  metadata: AnalysisMetadata;
  error: string | null;
  trace: string[] | null;
  confidence_score: number | null;
  hallucination_detected: boolean | null;
}

export async function uploadDocument(file: File): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    let errMsg = "Failed to upload document";
    try {
      const data = await response.json();
      errMsg = data.detail || errMsg;
    } catch {
      // Ignore JSON parse error
    }
    throw new Error(errMsg);
  }

  return response.json();
}

export async function analyzeDocument(docId: string): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE_URL}/api/agents/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ doc_id: docId }),
  });

  if (!response.ok) {
    let errMsg = "Failed to analyze document";
    try {
      const data = await response.json();
      errMsg = data.detail || errMsg;
    } catch {
      // Ignore JSON parse error
    }
    throw new Error(errMsg);
  }

  return response.json();
}
