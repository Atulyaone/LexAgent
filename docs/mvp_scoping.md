# MVP Scope Refinement and Course Alignment Corrections

---

## Part 1: Correct Course Concept Mapping

To ensure LexAgent perfectly aligns with the curriculum of the **Google + Kaggle AI Agents Intensive Course**, the following matrix maps all major LexAgent features to their correct, respective course days.

| Course Day | Core Course Theme | LexAgent Feature Implementation | Technical Proof & Mechanism |
| :--- | :--- | :--- | :--- |
| **Day 1** | **Vibe Coding & Agentic Engineering** | • Case Analysis Agent<br>• Structured output parsing (FIRAC) | Uses structured LLM prompt templates and output schemas to parse raw judgment text into a structured JSON dictionary. |
| **Day 2** | **MCP, Agent Interoperability & Tool Use** | • `Indian Statutes` & `Legal Documents` MCP Servers<br>• LangGraph State Orchestrator | Implements JSON-RPC over stdio to fetch laws. Coordinates agents via a shared typed state dict where agents read/write data sequentially. |
| **Day 3** | **Agent Skills, Memory & Context Management** | • Lightweight Domain Skills (Contract, Constitutional, etc.)<br>• RAG Vector Store & Local Session Memory | Employs **progressive disclosure** by storing prompt guidelines and specialized tool schemas in distinct skill folders, loading them dynamically based on active state routes. |
| **Day 4** | **Security, Evaluation & Human-in-the-Loop** | • Grounding verification checks<br>• Interactive Draft Staging UI (Review Inbox) | The Verification Agent scores generated summaries for factual grounding. The UI blocks automatic workspace saves until the student edits and approves. |
| **Day 5** | **Production, Deployment & Observability** | • Next.js + FastAPI Local Deployment<br>• LangSmith trace logging | Runs as a production-grade FastAPI service. Includes a toggleable UI trace console displaying the agent execution history and LLM token usage. |

---

## Part 2: Ruthless MVP Scoping

To guarantee a working, highly competitive project by the **July 4 deadline**, features are classified below with strict prioritization.

### 2.1 Must Have (Required for MVP)
* **Orchestrator Agent (LangGraph)**: Manages the sequential workflow (Research -> Analysis -> Verification -> Study Generator). Without this, the system is a chatbot, not an agent.
* **Case Analysis Agent (FIRAC Brief Parser)**: Extracts Facts, Issues, Rules, Analysis, and Conclusions from uploaded PDFs. Essential for core value proposition.
* **Indian Statutes MCP Server**: Local stdio-based server providing section text for Contract, Constitution, Consumer, and Succession. Proves Day 2 capabilities.
* **Legal Documents MCP Server**: Handles file reads, ingestion, and vector chunking of uploaded PDFs.
* **Grounding-Based Verification Agent**: Checks the generated brief against the raw uploaded text for hallucinations. Core trust mechanism.
* **Review Inbox (HITL Dashboard)**: A simple editing window showing the generated brief, confidence score, and verified citations. Allows the user to edit and save.
* **Study Notes & Quiz Generator**: Generates 5 high-fidelity MCQs with rationales and basic markdown study summaries from the verified briefs.
* **Local Workspace Memory (SQLite)**: Persists user-approved briefs, quiz history, and bookmark folders.

### 2.2 Nice To Have (Build only if ahead of schedule)
* **Active-Recall Flashcards**: Card deck generator mapping to the brief ratios.
* **Simple Spaced Repetition (SRS)**: Adds a next review timestamp (+1, +3, +7 days) to cards in the local SQLite database.
* **Static Overruled Case Lookup Map**: Local JSON map alerting if one of 30 predefined landmark cases is cited (e.g., flagging that *Indra Sawhney* is modified by later amendments).

### 2.3 Future Version (Do NOT build for Capstone)
* **Legal Mentor Mode (Socratic Dialogue)**: Multi-turn reasoning assessment is too complex to implement and evaluate cleanly in 10 days.
* **Live Court Registry Scrapers**: Government registries lack official public APIs; custom scrapers are slow, fragile, and prone to IP blocks.
* **Coparcenary Share Calculator / Inheritance Decision Trees**: Writing partition logic trees for Hindu Succession Law takes weeks of legal logic debugging.
* **Mock Courtroom Simulation**: Running dynamic roleplay between an AI Judge and opposing Counsel is expensive, slow, and prone to context drift.
* **Multi-user Collaboration & Cloud Syncing**: Adds unnecessary overhead (auth, multi-tenancy databases) for a capstone presentation.

---

## Part 3: Simplify Over-Engineered Features

| Feature | Complexity | User Value | MVP Recommendation |
| :--- | :--- | :--- | :--- |
| **Bench Composition Analysis** | **Medium**: Requires parsing varied judge lists and division bench layouts. | **Low**: Students only need the size of the bench to know precedent weight. | **Simplify**: Extract only the bench count (e.g., "5-judge bench") and name of the judge authoring the opinion. |
| **Dissenting Opinion Extraction** | **High**: Dissenting opinions require extracting an entirely parallel reasoning path. | **Medium**: Focuses on academic nuance. | **Simplify**: Capture a simple boolean flag `has_dissent` (Yes/No) and a single-sentence summary of the dissenting judge's conclusion. |
| **Constituent Assembly Debate Tracing** | **Extremely High**: Indexes massive historical archive transcripts from the 1940s. | **Low**: Highly specialized historical research. | **Future**: Cut entirely. |
| **Overruled Precedent Detection** | **High**: Requires scanning recent appellate court registries. | **High**: Prevents citing dead law. | **Simplify**: Use a static local JSON lookup map containing 30 well-known overruled/modified landmark cases. |
| **Citation Registry Verification** | **High**: Requires integrating with paid databases (SCC, Manupatra) or writing scrapers. | **High**: Establishes trust. | **Simplify**: Verify citation string structure via Regex patterns (e.g., matching standard AIR/SCC layout) rather than live API pinging. |
| **Coparcenary Share Calculation** | **High**: Extremely complex lineage rules (Hindu Succession Act Sec 6). | **Low**: Highly niche. | **Future**: Cut entirely. |
| **Succession Inheritance Calculators** | **High**: Same as above. | **Low**: Niche. | **Future**: Cut entirely. |
| **Mock Courtroom Simulations** | **Extremely High**: Requires state synchronization across 3 chat agents and a user. | **Medium**: Fun but prone to drift. | **Future**: Cut entirely. |
| **Collaboration Workspaces** | **High**: Requires authorization systems and real-time database locks. | **Low**: Solo study is the primary case. | **Future**: Cut entirely. |
| **Spaced Repetition System (SRS) Sync** | **Medium**: Requires writing card exporter formats and syncing schedules. | **Medium**: Useful for exams. | **Simplify**: Local SQL database table with date flags rather than full Anki/third-party API syncing. |
| **Timeline Generation** | **Medium**: Requires a visual canvas and chronological layout logic. | **Medium**: Visual aid. | **Simplify**: Output a plain Markdown table mapping cases to years (chronological sorting of search results). |
| **Multi-format Ingestion** | **Medium**: Requires OCR for scans, DOCX parser libraries, and video transcript readers. | **Low**: Text-searchable PDFs are standard. | **Simplify**: Restrict file upload strictly to text-searchable PDFs and raw TXT inputs. |

---

## Part 4: MVP Skills Design

To demonstrate **Day 3 (Skills & Progressive Disclosure)** concepts without bloating the codebase, we simplify the four Agent Skills into lightweight prompt folders containing target rules, statutory excerpts, and landmark lists.

### 4.1 Constitutional Law Skill
* **Minimal Scope**: Focus exclusively on Article 14 (Equality), Article 19 (Freedoms), and Article 21 (Life & Liberty).
* **Trigger Conditions**: Input text contains "Article 14", "Article 19", "Article 21", "fundamental rights", or "basic structure".
* **Knowledge Included**:
  * Text of Articles 14, 19, and 21.
  * Landmark rulings: *Kesavananda Bharati* (Basic Structure), *Maneka Gandhi* (Procedural Due Process), and *K.S. Puttaswamy* (Privacy).
* **Example Tasks**: Verify if a scenario involving surveillance violates the principles of *K.S. Puttaswamy* under Article 21.

### 4.2 Contract Law Skill
* **Minimal Scope**: Focus exclusively on Section 10 (Valid agreements), Section 56 (Frustration), and Section 73 (Damages for breach).
* **Trigger Conditions**: Input text contains "agreement", "contract", "breach", "damages", "frustration", "Section 56", or "Section 73".
* **Knowledge Included**:
  * Indian Contract Act sections: 10, 56, 73.
  * Landmark rulings: *Satyabrata Ghose v. Mugneeram Bangur* (Contractual frustration parameters).
* **Example Tasks**: Evaluate whether a contract became frustrated due to a government land acquisition order.

### 4.3 Consumer Protection Skill
* **Minimal Scope**: Focus exclusively on Section 2(9) (Consumer Rights) and Section 2(11) (Deficiency of Service) under the 2019 Act.
* **Trigger Conditions**: Input text contains "consumer commission", "deficiency of service", "pecuniary jurisdiction", or "product liability".
* **Knowledge Included**:
  * Pecuniary jurisdictional limits (District: up to ₹50 Lakhs; State: up to ₹2 Crores; National: above ₹2 Crores).
  * Definition of "consumer" vs "commercial user".
* **Example Tasks**: Determine the correct Consumer Commission to file a complaint for a defective car worth ₹45 Lakhs.

### 4.4 Succession Law Skill
* **Minimal Scope**: Focus exclusively on Section 6 (Daughters' Coparcenary Rights) under the Hindu Succession Act.
* **Trigger Conditions**: Input text contains "Hindu Succession", "Section 6", "coparcenary", or "inheritance partition".
* **Knowledge Included**:
  * Rules of coparcenary devolution pre-2005 vs post-2005.
  * Landmark ruling: *Vineeta Sharma v. Rakesh Sharma* (Establishing retroactive daughter rights).
* **Example Tasks**: Explain if a daughter is entitled to share in ancestral property if her father passed away prior to 2005.

---

## Part 5: MVP Verification Agent

Instead of connecting to official databases, the MVP Verification Agent functions as an **in-context self-evaluator** to eliminate hallucinations and verify grounding.

```
       [ Generated Brief / Note ]
                   │
                   ▼
       [ Verification Agent ]
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
[Citation Checker]    [Grounding Engine]
- Uses local regex    - Chunks raw uploaded PDF
- Validates structure - Prompts LLM: "Is this sentence
  against local map.    supported by raw text?"
        │                     │
        └──────────┬──────────┘
                   ▼
        [ Confidence Score (0-100) ]
        [ Yellow highlight if < 80 ]
```

### 5.1 Architecture & Flow
1. **Citation Extraction & Matcher**: Uses regular expressions to extract citations matching standard formats:
   * `\d{4}\s*(\(\d\))?\s*SCC\s*\d+` (e.g., *(2020) 3 SCC 1*)
   * `AIR\s*\d{4}\s*SC\s*\d+` (e.g., *AIR 1954 SC 44*)
   * The agent cross-references these matches against a static JSON array of 50 common Indian case laws. If matched, it returns the metadata; if not, it marks it as "Unverified Structure".
2. **Factual Grounding Engine**: Passes the generated brief segments and raw text fragments of the uploaded document to the LLM with a target prompt: 
   `"Verify if the following assertion is directly supported by the provided text. Answer only YES or NO: [Assertion]"`
3. **Scoring Logic**:
   * Grounding Score: (Number of YES assertions / Total assertions) * 100
   * Citation Score: (Number of structural valid citations / Total citations) * 100
   * Confidence Score: Average of Grounding and Citation scores.
4. **UI Highlight**: High-confidence statements (>80%) appear normally. Low-confidence statements (<80%) are wrapped in a yellow warning tag in the UI, pointing out to the user that manual verification is needed.

---

## Part 6: MVP MCP Design

To satisfy the **Day 2 (MCP)** requirement while minimizing development complexity, the project runs exactly **two** MCP servers locally over stdio.

```
                  [ FastAPI Application ]
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   (STDIO JSON-RPC)                  (STDIO JSON-RPC)
[Legal Documents MCP]              [Indian Statutes MCP]
- Exposes raw uploaded PDFs.        - Exposes statutory text for
- Tools: parse_pdf, search_chunks   Contract, Constitution,
                                    Consumer, and Succession from
                                    local JSON datasets.
```

### 6.1 Required MCP Servers (Must Have)
1. **Legal Documents MCP Server**: Exposes resources for uploaded PDFs. It allows the Case Analysis agent to access file text chunks via standard MCP tools.
2. **Indian Statutes MCP Server**: Serves statutory provisions from a local JSON database of the 4 supported domains. The Research Agent calls this server to look up acts and sections.

### 6.2 Deferred MCP Servers (Moved to Main App)
* **Research Workspace Storage**: Save note additions, folders, and settings directly to SQLite from the main FastAPI server backend. This removes the need to build and maintain a third workspace-specific MCP server.

---

## Part 7: Kaggle Judge Perspective

### 7.1 What parts of LexAgent are most impressive?
* **Clean MCP Isolation**: Having a local stdio MCP server provide statutory text is a textbook demonstration of Day 2 concepts. It proves you understand how to write tool and resource definitions.
* **Progressive Skills Architecture**: The modular skills folders showing that prompts and tools are loaded on-the-fly depending on query context. This directly demonstrates Day 3 advanced context management.
* **The Grounding Verification UI (HITL)**: Showing the student a draft brief, highlighting ungrounded sentences in yellow, and providing a Trust Confidence Score. This is a very strong demonstration of Day 4 concepts.

### 7.2 What parts are unnecessary complexity (Cut Immediately)?
* **Mock Courtrooms**: Judges will not run interactive roleplays. If it drifts or errors during the evaluation, it ruins the score.
* **Inheritance Fraction Calculators**: Writing hundreds of lines of deterministic math to compute family tree shares does not highlight AI Agent concepts.
* **Real-time Government Scrapers**: This will fail during live judging if the government site changes or blocks the server IP.

### 7.3 What features help the project place in the top submissions?
* **An interactive "Trace Debugger" panel** in the UI: A glassmorphic sidebar showing the Orchestrator routing tasks (e.g., `Orchestrator -> Research -> Case Analysis -> Verification -> HITL Draft`). This makes the multi-agent orchestration visible to judges.
* **High Grounding Precision**: The Verification Agent's ability to catch hallucinated references in uploaded files.

---

## Part 8: Final Build Plan

### 8.1 Build Timeline

```
                     [ LexAgent MVP Build Timeline ]

   Week 1: Core Engine & MCP              Week 2: UI, Verification, & Polish
┌──────────────────────────────┐       ┌────────────────────────────────┐
│ Day 1-2: LangGraph Framework │       │ Day 8-9: Next.js Rich UI      │
│ Day 3-4: Build MCP Servers   │ ──────>│ Day 10-11: Grounding & HITL    │
│ Day 5-7: Implement 4 Skills  │       │ Day 12: Trace Logging & Demo   │
└──────────────────────────────┘       └────────────────────────────────┘
```

#### Week 1: Core Agentic Engine & MCP Gateway
* **Day 1-2: Core Setup**: Initialize FastAPI backend, SQLite local database, and configure the LangGraph state machine.
* **Day 3-4: MCP Implementations**: Write the `Indian Statutes` MCP Server (loading local JSON acts) and the `Legal Documents` MCP Server (handling PDF text extracts).
* **Day 5-7: Skills Configuration**: Build the four minimal Skills folders. Verify that the Orchestrator dynamically loads prompt instructions based on search queries.

#### Week 2: UI, Verification, & Polish
* **Day 8-9: Frontend Development**: Build the Next.js React UI dashboard, incorporating a premium design system (deep navy, gold accents, clear navigation).
* **Day 10-11: Grounding & Human-in-the-Loop**: Implement the self-evaluator Verification Agent and connect it to the draft review editing screen.
* **Day 12: Trace Console & Video**: Build the trace debugger window, write tests, record a 3-minute video presentation, and publish the codebase.

### 8.2 Final Scoping Recommendation
* **MUST Build**: Local Statutes MCP server, FIRAC PDF brief parser, Grounding self-checker, HITL review page, and a visual orchestration trace console.
* **SHOULD Build**: Spaced repetition SQLite table, 5-question MCQ generator, and local bookmark folders.
* **MUST NOT Build**: Scrapers for live court registries, succession calculators, multi-agent courtroom simulators, or real-time group collaboration hubs.
