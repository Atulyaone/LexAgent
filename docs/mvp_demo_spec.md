# LexAgent: MVP Demo Specification

**Purpose**: Define exactly what a Kaggle judge should see during a 3-minute capstone demonstration. Every screen, every agent interaction, every output is specified here to maximize judging impact while remaining buildable by a solo developer before July 4.

---

## Section 1: MVP Screens

### 1.1 Dashboard

* **Purpose**: Entry point. Provides an overview of the student's workspace, recent activity, and quick-launch actions.
* **Components**:
  * Hero welcome banner with the LexAgent logo and tagline ("Your AI Legal Research Co-Pilot").
  * "Upload Judgment" primary action button (golden accent, prominent placement).
  * Recent Activity feed — last 5 analyzed cases, saved briefs, and quiz attempts displayed as cards.
  * Workspace Stats bar — total briefs saved, quizzes taken, average confidence score.
  * Sidebar navigation — links to Dashboard, Case Analyzer, Study Zone, Review Inbox, and Workspace.
* **User Actions**: Click "Upload Judgment" to navigate to Case Analyzer. Click any recent case card to reopen its brief. Navigate to other sections via sidebar.
* **Data Displayed**: Case titles, timestamps, confidence scores (color-coded), domain tags (e.g., "Constitutional Law").

---

### 1.2 Case Analyzer

* **Purpose**: The core workflow screen. The user uploads a PDF, watches agents work in real-time via the Trace Console, and receives the structured FIRAC brief.
* **Components**:
  * **Upload Zone**: Drag-and-drop area with file type indicator (accepts `.pdf`, `.txt`). Displays filename and page count after upload.
  * **Agent Trace Console** (right sidebar): A live, scrolling vertical timeline showing each agent's activity, skill loaded, MCP calls made, and status (active / complete / error). This is the centerpiece of the demo.
  * **FIRAC Brief Panel** (main content area): Renders the structured brief after analysis completes. Sections: Facts, Issues, Rules, Analysis, Conclusion. Each section is an editable text block.
  * **Verification Badge Strip**: Inline badges below each FIRAC section showing grounding status. Green checkmark for grounded statements, yellow warning triangle for low-confidence statements.
  * **Confidence Score Indicator**: A circular gauge (0–100%) displayed prominently at the top-right of the brief panel.
* **User Actions**: Upload a PDF. Watch the Trace Console animate through agent steps. Read the generated FIRAC brief. Click "Send to Review Inbox" to stage the brief for approval.
* **Data Displayed**: Raw filename, page count, FIRAC sections, inline citations, verification warnings, confidence score, agent trace log.

---

### 1.3 Review Inbox (HITL Screen)

* **Purpose**: The Human-in-the-Loop approval interface. Briefs land here as drafts and cannot be saved to permanent workspace until the student explicitly reviews and approves them.
* **Components**:
  * **Draft List Sidebar**: A list of pending briefs awaiting review. Each item shows case name, domain, timestamp, and confidence score badge.
  * **Editable Brief View** (main area): The full FIRAC brief rendered in editable text fields. Low-confidence sentences are highlighted with a soft yellow background and a tooltip: "This claim could not be verified against the source document."
  * **Citation Panel**: A collapsible section listing every extracted citation, its regex-validated format status (✓ Valid / ⚠ Unverified), and its precedent status (Active / Overruled) from the local landmark database.
  * **Action Buttons**: "Approve & Save to Workspace" (primary gold button) and "Request Re-Analysis" (secondary outline button).
* **User Actions**: Select a draft from the sidebar. Read highlighted warnings. Edit text inline. Approve and save, or send back for re-analysis.
* **Data Displayed**: Editable FIRAC text, highlighted ungrounded sentences, citation validation table, confidence score.

---

### 1.4 Workspace

* **Purpose**: The student's long-term knowledge base. Stores all approved briefs, saved notes, and quiz history.
* **Components**:
  * **Saved Briefs Grid**: Card layout of approved case briefs. Each card shows case name, domain tag, date saved, and confidence score.
  * **Search Bar**: Full-text search across saved briefs and notes.
  * **Bookmark Folders**: User-created folders for organizing research by topic (e.g., "Article 21 Research", "Contract Exam Prep").
  * **Quick Actions**: "Generate Study Notes" and "Generate Quiz" buttons on each saved brief card.
* **User Actions**: Browse saved briefs. Search by keyword. Open a brief to read. Click "Generate Study Notes" or "Generate Quiz" to send the brief to the Study Assistant Agent.
* **Data Displayed**: Case names, domain tags, confidence scores, timestamps, folder structures.

---

### 1.5 Study Zone

* **Purpose**: Exam preparation hub. Displays generated revision notes, interactive MCQ quizzes, and flashcards.
* **Components**:
  * **Tab Navigation**: Tabs for "Revision Notes", "Practice Quiz", and "Flashcards".
  * **Revision Notes Panel**: Markdown-rendered study summary derived from the case brief. Includes key doctrines, landmark rulings cited, and statutory sections.
  * **Quiz Interface**: One question displayed at a time. Four radio-button options. "Submit Answer" button. After submission: correct answer highlighted in green, wrong answer in red, and a detailed rationale paragraph explaining why each option is correct or incorrect.
  * **Score Summary**: After completing a quiz, a results card shows total score, time taken, and a breakdown of correct/incorrect answers.
* **User Actions**: Read revision notes. Take a quiz question by question. Review explanations. Save difficult questions as flashcards.
* **Data Displayed**: Study notes (markdown), MCQ questions, option text, rationale explanations, quiz score.

---

## Section 2: Agent Trace Experience

The **Agent Trace Console** is the single most important UI element for impressing Kaggle judges. It makes the invisible multi-agent architecture visible and understandable in real-time.

### 2.1 Visual Design
The Trace Console is a vertical timeline rendered in a right-hand sidebar panel with a dark, translucent glassmorphic background (`rgba(10, 15, 30, 0.85)` with `backdrop-filter: blur(12px)`). Each entry in the timeline is a "trace card" that appears with a subtle slide-in animation.

### 2.2 Trace Card Anatomy
Each trace card contains:
* **Agent Avatar & Name**: A small colored icon and label (e.g., 🔍 Research Agent, 📄 Case Analysis Agent, ✅ Verification Agent, 📚 Study Assistant).
* **Status Indicator**: A pulsing dot — blue (active), green (complete), red (error).
* **Action Description**: A one-line summary of what the agent is doing (e.g., "Loading Constitutional Law Skill…", "Querying Indian Statutes MCP for Article 21…").
* **Duration Badge**: Time elapsed for the step (e.g., "1.2s").
* **Expandable Detail**: Clicking a completed card reveals the raw tool call or MCP request/response JSON payload.

### 2.3 Example Trace Sequence (for Maneka Gandhi PDF upload)
The console animates through the following cards, one after another:

```
┌─────────────────────────────────────────────────────┐
│  🎯 Orchestrator Agent                    ● Active  │
│  Analyzing input... Detected domain:                │
│  Constitutional Law                                 │
│                                            0.4s     │
├─────────────────────────────────────────────────────┤
│  🎯 Orchestrator Agent                   ✓ Done    │
│  Loading Constitutional Law Skill                   │
│  ├─ Prompt: "Identify disputes under Part III..."   │
│  └─ Tools: fetch_bench_composition                  │
│                                            0.2s     │
├─────────────────────────────────────────────────────┤
│  🔍 Research Agent                        ● Active  │
│  Querying Indian Statutes MCP Server                │
│  └─ get_section_text("constitution", "21")          │
│                                            1.1s     │
├─────────────────────────────────────────────────────┤
│  🔍 Research Agent                       ✓ Done    │
│  Found: Article 21, Maneka Gandhi (1978)            │
│  Matched 2 statutory references                     │
│                                            0.3s     │
├─────────────────────────────────────────────────────┤
│  📄 Case Analysis Agent                  ● Active  │
│  Reading document via Legal Documents MCP           │
│  └─ parse_pdf_document("maneka_gandhi.pdf")         │
│                                            2.8s     │
├─────────────────────────────────────────────────────┤
│  📄 Case Analysis Agent                 ✓ Done    │
│  FIRAC Brief generated (5 sections)                 │
│  Extracted 4 citations                              │
│                                            0.5s     │
├─────────────────────────────────────────────────────┤
│  ✅ Verification Agent                   ● Active  │
│  Checking grounding against source PDF              │
│  └─ 12 assertions to verify...                      │
│                                            1.6s     │
├─────────────────────────────────────────────────────┤
│  ✅ Verification Agent                  ✓ Done    │
│  Grounding: 92% | Citations: 100%                  │
│  Confidence Score: 95%                              │
│  ⚠ 1 low-confidence statement flagged               │
│                                            0.2s     │
├─────────────────────────────────────────────────────┤
│  📚 Study Assistant Agent                ● Active  │
│  Generating revision notes & 5 MCQs                 │
│                                            2.1s     │
├─────────────────────────────────────────────────────┤
│  📚 Study Assistant Agent               ✓ Done    │
│  Created 1 study guide, 5 quiz questions            │
│                                            0.3s     │
├─────────────────────────────────────────────────────┤
│  🎯 Orchestrator Agent                  ✓ Done    │
│  All agents complete. Staging in Review Inbox.      │
│  Total pipeline time: 9.5s                          │
└─────────────────────────────────────────────────────┘
```

### 2.4 Why This Matters for Judges
* Makes multi-agent orchestration **tangible** rather than theoretical.
* Shows MCP tool calls happening in real-time with actual request payloads.
* Demonstrates progressive skill loading as a visible event.
* Displays the verification confidence score prominently, proving the security pipeline is live.

---

## Section 3: Demo Scenario — 3-Minute Walkthrough

**Demo Case**: *Maneka Gandhi v. Union of India*, AIR 1978 SC 597 — a landmark 7-judge bench decision under Article 21 of the Constitution of India establishing that the right to travel abroad is part of "personal liberty" and that any procedure depriving a person of liberty must be "fair, just, and reasonable."

### Minute 0:00 – 0:45 | Introduction & Upload

| Timestamp | User Action | What the Judge Sees |
| :--- | :--- | :--- |
| 0:00 | Narrator introduces LexAgent | Dashboard screen. Clean, dark navy UI with gold accents. |
| 0:10 | — | Narrator explains: "LexAgent uses 5 specialized AI agents..." |
| 0:25 | Clicks "Upload Judgment" | Navigates to Case Analyzer. Drag-and-drop zone appears. |
| 0:30 | Drops `maneka_gandhi.pdf` | File accepted. "maneka_gandhi.pdf — 24 pages" displayed. |
| 0:35 | Clicks "Analyze" | Agent Trace Console activates. First card appears: Orchestrator Active. |
| 0:40 | Watches | Trace card: "Detected domain: Constitutional Law" |
| 0:45 | Watches | Trace card: "Loading Constitutional Law Skill" — shows the skill's prompt excerpt and `fetch_bench_composition` tool registration. |

### Minute 0:45 – 1:30 | Agent Execution (Visible in Trace Console)

| Timestamp | Agent Activity | What the Judge Sees |
| :--- | :--- | :--- |
| 0:45 | Research Agent activates | Trace card: "Querying Indian Statutes MCP — `get_section_text('constitution', '21')`" |
| 0:55 | Research Agent completes | Trace card: "Found Article 21 text. Matched *Maneka Gandhi v. UOI*." |
| 1:00 | Case Analysis Agent activates | Trace card: "Reading document via Legal Documents MCP — `parse_pdf_document`" |
| 1:15 | Case Analysis Agent completes | Trace card: "FIRAC Brief generated. 4 citations extracted." FIRAC panel starts rendering on the left. |
| 1:20 | Verification Agent activates | Trace card: "Verifying 12 assertions against source PDF…" |
| 1:30 | Verification Agent completes | Trace card: "Grounding: 92% · Citations: 100% · Confidence: 95%". Confidence gauge animates to 95%. One sentence highlighted yellow. |

### Minute 1:30 – 2:15 | FIRAC Brief Review & Human Approval

| Timestamp | User Action | What the Judge Sees |
| :--- | :--- | :--- |
| 1:30 | Reads the generated FIRAC brief | Facts, Issues, Rules, Analysis, Conclusion sections are displayed with clean typography. |
| 1:40 | Scrolls to the flagged sentence | Yellow-highlighted text: *"The passport was impounded without any hearing."* Tooltip: "Low confidence — verify against source." |
| 1:50 | Edits the sentence inline | Types a correction. The text field updates in real-time. |
| 1:55 | Clicks "Send to Review Inbox" | Navigates to Review Inbox. The draft appears in the sidebar. |
| 2:00 | Reviews the Citation Panel | Table shows: `AIR 1978 SC 597 ✓ Valid · Active`, `(1978) 1 SCC 248 ✓ Valid · Active`. |
| 2:10 | Clicks "Approve & Save to Workspace" | Brief saved. Success toast notification: "Saved to Constitutional Law folder." |

### Minute 2:15 – 3:00 | Study Materials & Wrap-Up

| Timestamp | User Action | What the Judge Sees |
| :--- | :--- | :--- |
| 2:15 | Opens Workspace | Saved brief card visible with "Constitutional Law" tag and "95% Confidence" badge. |
| 2:20 | Clicks "Generate Quiz" on the card | Study Assistant Agent trace card animates briefly. |
| 2:30 | Navigates to Study Zone → Practice Quiz | First MCQ displayed. |
| 2:35 | Selects an answer and clicks "Submit" | Correct answer highlighted green. Rationale paragraph appears explaining the legal reasoning. |
| 2:45 | Switches to "Revision Notes" tab | Markdown study guide rendered. Key doctrines, Article 21 analysis, landmark case comparison. |
| 2:55 | Narrator summarizes | "LexAgent demonstrates multi-agent orchestration, MCP, skills, memory, HITL, and grounding verification — all concepts from the Google AI Agents Intensive course." |

---

## Section 4: Screen-by-Screen Agent Outputs

### 4.1 Research Agent Output

```json
{
  "agent": "research",
  "status": "complete",
  "active_domain": "constitutional_law",
  "skill_loaded": "Constitutional Law Skill",
  "statutory_references": [
    {
      "act": "Constitution of India",
      "article": "21",
      "text": "No person shall be deprived of his life or personal liberty except according to procedure established by law."
    },
    {
      "act": "Constitution of India",
      "article": "14",
      "text": "The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India."
    }
  ],
  "matched_cases": [
    {
      "case_name": "Maneka Gandhi v. Union of India",
      "citation": "AIR 1978 SC 597",
      "bench_size": 7,
      "year": 1978
    }
  ],
  "mcp_calls": [
    {
      "server": "Indian Statutes MCP",
      "tool": "get_section_text",
      "args": { "act_name": "constitution", "section_number": "21" }
    }
  ]
}
```

---

### 4.2 Case Analysis Agent Output

```json
{
  "agent": "case_analysis",
  "status": "complete",
  "firac_brief": {
    "facts": "Maneka Gandhi's passport was impounded by the Regional Passport Officer, Delhi, on July 2, 1977, under Section 10(3)(c) of the Passports Act, 1967. The Government of India declined to furnish reasons for the impounding, citing that it was 'in the interest of the general public.' Maneka Gandhi challenged the impounding order as violative of her fundamental rights under Articles 14, 19(1)(a), and 21 of the Constitution.",

    "issues": "1. Whether the right to travel abroad is part of 'personal liberty' under Article 21.\n2. Whether the procedure established by law must satisfy the test of reasonableness under Article 14.\n3. Whether the right under Article 21 can be read in isolation or must be read with Articles 14 and 19.",

    "rule": "Article 21 of the Constitution of India: 'No person shall be deprived of his life or personal liberty except according to procedure established by law.' Section 10(3)(c) of the Passports Act, 1967: empowers the passport authority to impound a passport 'in the interest of the general public.'",

    "analysis": "The Supreme Court overruled the narrow interpretation of Article 21 established in A.K. Gopalan v. State of Madras (1950), where the Court had held that 'procedure established by law' merely requires the existence of a validly enacted statute. In Maneka Gandhi, the 7-judge bench held that the procedure contemplated by Article 21 must be 'right and just and fair' and not 'arbitrary, fanciful, or oppressive.' The Court established the doctrine of inter-relationship of fundamental rights — Article 21 cannot be read in a silo; any law depriving personal liberty must also satisfy the reasonableness test of Article 14 and the fair restriction test of Article 19.",

    "conclusion": "The impounding of the passport without providing reasons or an opportunity of hearing was held to be violative of Article 21. The Supreme Court established that 'personal liberty' includes the right to travel abroad, and any deprivation must follow a procedure that is fair, just, and reasonable — not merely a procedure that technically exists in a statute."
  },
  "extracted_citations": [
    "AIR 1978 SC 597",
    "(1978) 1 SCC 248",
    "AIR 1950 SC 27"
  ],
  "bench_size": 7,
  "has_dissent": false,
  "mcp_calls": [
    {
      "server": "Legal Documents MCP",
      "tool": "parse_pdf_document",
      "args": { "file_path": "uploads/maneka_gandhi.pdf" }
    }
  ]
}
```

---

### 4.3 Verification Agent Output

```json
{
  "agent": "verification",
  "status": "complete",
  "grounding_report": {
    "total_assertions": 12,
    "grounded": 11,
    "ungrounded": 1,
    "grounding_score": 91.7,
    "flagged_statements": [
      {
        "text": "The passport was impounded without any hearing.",
        "reason": "Source document states impounding occurred under Section 10(3)(c) but does not explicitly state that no hearing was held prior to impounding. The absence of hearing is inferred from the petitioner's arguments, not from a direct factual statement.",
        "severity": "low"
      }
    ]
  },
  "citation_report": {
    "total_citations": 3,
    "valid_format": 3,
    "matched_in_database": 2,
    "unmatched": 1,
    "citation_score": 100.0,
    "details": [
      { "citation": "AIR 1978 SC 597", "format": "valid", "status": "Active" },
      { "citation": "(1978) 1 SCC 248", "format": "valid", "status": "Active" },
      { "citation": "AIR 1950 SC 27", "format": "valid", "status": "Distinguished (Maneka Gandhi overruled the narrow A.K. Gopalan ratio on Article 21)" }
    ]
  },
  "confidence_score": 95.0
}
```

---

### 4.4 Study Assistant Agent Output

**Revision Notes** (Markdown):
```markdown
# Maneka Gandhi v. Union of India (1978) — Study Guide

## Core Doctrine
The **procedural due process** doctrine in Indian Constitutional Law.
Before this case, Article 21 was interpreted narrowly (A.K. Gopalan, 1950) — any
validly enacted law was sufficient. After Maneka Gandhi, the procedure must be
**fair, just, and reasonable**.

## Key Legal Principles
1. **Right to Travel Abroad**: Part of "personal liberty" under Article 21.
2. **Inter-relationship of Fundamental Rights**: Articles 14, 19, and 21 form a
   golden triangle — they cannot be read in isolation.
3. **Overruling of A.K. Gopalan**: The narrow "procedure established by law"
   test was replaced with a substantive due process standard.

## Statutory Provisions
- **Article 21**: Life and personal liberty.
- **Article 14**: Equality before law.
- **Section 10(3)(c), Passports Act 1967**: Power to impound passports.

## Bench
7-Judge Bench. No dissent. Unanimous on the core ratio.
```

**Quiz Questions** (JSON):
```json
[
  {
    "question": "In Maneka Gandhi v. Union of India (1978), the Supreme Court held that the procedure under Article 21 must be:",
    "options": [
      "Any procedure validly enacted by Parliament",
      "Fair, just, and reasonable",
      "Approved by the President of India",
      "Consistent with British common law traditions"
    ],
    "correct_option_index": 1,
    "explanation": "The 7-judge bench overruled the A.K. Gopalan (1950) interpretation and held that 'procedure established by law' under Article 21 must satisfy the test of being 'right and just and fair' — not merely a validly enacted statute. This established procedural due process in Indian law."
  },
  {
    "question": "Which earlier Supreme Court decision was effectively overruled by Maneka Gandhi on the interpretation of Article 21?",
    "options": [
      "Kesavananda Bharati v. State of Kerala (1973)",
      "A.K. Gopalan v. State of Madras (1950)",
      "Golak Nath v. State of Punjab (1967)",
      "Minerva Mills v. Union of India (1980)"
    ],
    "correct_option_index": 1,
    "explanation": "In A.K. Gopalan (1950), the Court had adopted a narrow, literal interpretation — that Article 21 only requires a valid law to exist. Maneka Gandhi's 7-judge bench rejected this view and mandated substantive fairness, marking a foundational shift in Indian Constitutional jurisprudence."
  },
  {
    "question": "The 'Golden Triangle' of fundamental rights established in Maneka Gandhi refers to the inter-relationship between which Articles?",
    "options": [
      "Articles 14, 19, and 21",
      "Articles 19, 20, and 21",
      "Articles 12, 14, and 21",
      "Articles 21, 25, and 32"
    ],
    "correct_option_index": 0,
    "explanation": "The Court held that Articles 14 (Equality), 19 (Freedoms), and 21 (Life and Liberty) are interconnected. Any law that deprives personal liberty under Article 21 must also withstand scrutiny under Article 14 (non-arbitrariness) and Article 19 (reasonable restrictions)."
  },
  {
    "question": "Under which statutory provision was Maneka Gandhi's passport impounded?",
    "options": [
      "Section 144, Code of Criminal Procedure",
      "Section 10(3)(c), Passports Act 1967",
      "Section 56, Indian Contract Act 1872",
      "Article 352, Constitution of India"
    ],
    "correct_option_index": 1,
    "explanation": "The Regional Passport Officer impounded Maneka Gandhi's passport under Section 10(3)(c) of the Passports Act, 1967, citing 'interest of the general public' without furnishing specific reasons."
  },
  {
    "question": "What was the bench strength in Maneka Gandhi v. Union of India?",
    "options": [
      "3-Judge Bench",
      "5-Judge Bench",
      "7-Judge Bench",
      "13-Judge Bench"
    ],
    "correct_option_index": 2,
    "explanation": "Maneka Gandhi was decided by a 7-Judge Bench of the Supreme Court. The larger bench was constituted specifically to reconsider the narrow interpretation of Article 21 established by the 6-Judge Bench in A.K. Gopalan (1950)."
  }
]
```

---

### 4.5 Human Approval Output
After the student edits the flagged sentence and clicks "Approve & Save":

```json
{
  "action": "approved_and_saved",
  "case_name": "Maneka Gandhi v. Union of India",
  "domain": "constitutional_law",
  "confidence_score": 95.0,
  "user_edits": [
    {
      "section": "facts",
      "original": "The passport was impounded without any hearing.",
      "edited": "The passport was impounded under Section 10(3)(c) without providing reasons or an opportunity of hearing to the petitioner."
    }
  ],
  "saved_to_workspace": true,
  "workspace_folder": "Constitutional Law",
  "timestamp": "2026-06-28T14:32:00+05:30"
}
```

---

### 4.6 Workspace Output
After saving, the Workspace screen displays a new card:

```
┌──────────────────────────────────────────────┐
│  📄 Maneka Gandhi v. Union of India          │
│                                              │
│  Domain: Constitutional Law                  │
│  Confidence: 95%  ●●●●●●●●●○                │
│  Bench: 7-Judge · No Dissent                 │
│  Saved: June 28, 2026                        │
│                                              │
│  [ Generate Study Notes ]  [ Generate Quiz ] │
└──────────────────────────────────────────────┘
```

---

## Section 5: Judge Visibility Matrix

This matrix maps every core course concept to a specific, visible UI element. A judge should be able to verify each concept within 30 seconds.

| Course Concept | Where the Judge Sees It | Specific UI Element | Why It Matters |
| :--- | :--- | :--- | :--- |
| **Multi-Agent Systems** | Case Analyzer → Trace Console | Sequential trace cards showing 5 distinct agents activating, completing, and handing off state. Each agent has a unique icon and name. | Proves the system is not a single-prompt chatbot. Each trace card represents a different agent with a distinct responsibility. |
| **MCP (Day 2)** | Trace Console → Expandable detail panels | Trace cards display actual MCP tool calls: `get_section_text("constitution", "21")` for Statutes MCP, `parse_pdf_document(...)` for Documents MCP. Expanding a card reveals the JSON-RPC request and response. | Proves real stdio MCP server communication is occurring, not hardcoded outputs. The judge can see the tool name, arguments, and response payload. |
| **Agent Skills (Day 3)** | Trace Console → Skill loading card | A dedicated trace card reads: "Loading Constitutional Law Skill" and shows the injected prompt instructions and registered tools. | Proves progressive disclosure — the skill was loaded dynamically based on detected domain, not pre-baked into a monolithic system prompt. |
| **Memory (Day 3)** | Workspace screen | Saved briefs persist across sessions. Reopening a brief shows the previously approved content with its original confidence score and domain tags. | Proves long-term workspace memory. The student's approved work survives page refreshes and new sessions. |
| **Human-in-the-Loop (Day 4)** | Review Inbox screen | The draft brief is staged with yellow highlights on ungrounded sentences. The student edits text inline and clicks "Approve & Save." Nothing is saved until the human acts. | Proves the system does not auto-commit AI outputs. The human is the final gatekeeper. |
| **Security & Grounding (Day 4)** | Confidence Score gauge + Verification badge strip | The circular 95% confidence gauge on the brief panel. Green ✓ badges on grounded statements. Yellow ⚠ badges on flagged statements with hover tooltips explaining why. | Proves the Verification Agent actively checks assertions against source text and computes a quantitative trust score. |
| **Evaluation (Day 4)** | Citation Panel in Review Inbox | Table listing each extracted citation with its format validation status (✓ Valid / ⚠ Unverified) and precedent status (Active / Overruled / Distinguished). | Proves the system evaluates citation quality programmatically, not just generates text. |

---

## Section 6: Final MVP Definition

### 6.1 Must Build (Non-Negotiable for Demo)

| # | Feature | Rationale |
| :--- | :--- | :--- |
| 1 | **Orchestrator Agent** (ADK routing logic) | Without it, there is no multi-agent system to demonstrate. |
| 2 | **Research Agent** with Indian Statutes MCP connection | Proves Day 2 MCP concepts. The judge must see a real tool call. |
| 3 | **Case Analysis Agent** with Legal Documents MCP connection | Proves the core product value — PDF to structured brief. |
| 4 | **Verification Agent** with grounding checker and citation regex | Proves Day 4 security/trust. The confidence score is a key visual. |
| 5 | **Study Assistant Agent** generating revision notes + 5 MCQs | Proves the system does more than summarize — it teaches. |
| 6 | **Indian Statutes MCP Server** (stdio, local JSON) | Day 2 proof. Must serve real statutory text via JSON-RPC. |
| 7 | **Legal Documents MCP Server** (stdio, PDF parser) | Day 2 proof. Must parse real uploaded PDFs. |
| 8 | **4 Domain Skills** (Constitutional, Contract, Consumer, Succession) | Day 3 proof. Dynamic skill loading must be visible in the Trace Console. |
| 9 | **Agent Trace Console** (real-time sidebar) | This is the demo centerpiece. Without it, judges cannot see the agent architecture. |
| 10 | **FIRAC Brief Panel** with inline verification badges | Core deliverable. Must render Facts, Issues, Rules, Analysis, Conclusion. |
| 11 | **Review Inbox** with editable draft and approval workflow | Day 4 HITL proof. Judges must see the human editing and approving. |
| 12 | **Workspace page** with saved brief cards | Day 3 memory proof. Must persist across sessions. |
| 13 | **Study Zone** with quiz interface and rationale display | Demonstrates the Study Assistant Agent's output in an interactive way. |
| 14 | **SQLite database** for workspace persistence | Required for memory demonstration. |
| 15 | **FastAPI backend** with upload and analysis endpoints | Required server infrastructure. |
| 16 | **Next.js frontend** with dark premium design system | The visual quality directly impacts judge perception. |

---

### 6.2 Nice To Have (Build only if ahead of schedule)

| # | Feature | Rationale |
| :--- | :--- | :--- |
| 1 | Flashcard deck generator with basic SRS timestamps | Extends the Study Zone but is not required for the core demo flow. |
| 2 | Static overruled-case lookup map (30 landmark cases) | Enriches the citation panel but can be faked with a smaller dataset. |
| 3 | Bookmark folders in Workspace | Organizational nicety; a flat list of saved briefs is sufficient. |
| 4 | Expandable JSON payloads in Trace Console | Impressive for technical judges, but the summary-level trace cards are sufficient. |
| 5 | Quiz score history chart | Visualization of past scores; a simple text summary is adequate. |

---

### 6.3 Cut From MVP (Do Not Build)

| # | Feature | Reason for Cutting |
| :--- | :--- | :--- |
| 1 | Legal Mentor Mode (Socratic dialogue) | Multi-turn pedagogical state machine is too complex and too risky for a demo. |
| 2 | Live court registry scrapers | External dependency; will fail during live judging if the site is down. |
| 3 | Coparcenary share calculators | Deterministic math that does not demonstrate AI agent concepts. |
| 4 | Mock courtroom simulation | Requires 3+ chat agents running concurrently; high failure risk. |
| 5 | Multi-user collaboration / sharing | Requires auth, multi-tenancy — unnecessary for a solo demo. |
| 6 | Anki export / third-party SRS sync | External format dependency; adds no judging value. |
| 7 | OCR for scanned PDFs | Adds complexity; text-searchable PDFs are sufficient for demo. |
| 8 | Docker deployment | Nice for production but unnecessary for a local capstone demo. Run `npm run dev` and `uvicorn` directly. |
