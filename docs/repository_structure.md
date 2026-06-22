# LexAgent: MVP Repository Structure

This document outlines the complete directory layout, file descriptions, and development dependencies for the LexAgent MVP. It is designed to be implemented by a solo developer before the **July 4 deadline** using Google's **Agent Development Kit (ADK)**, Gemini, local stdio MCP servers, FastAPI, and Next.js.

---

## 1. Root Directory Structure

```
lexagent-mvp/
├── backend/                   # FastAPI and Google ADK Backend Service
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI Entry Point
│   │   ├── config.py          # Environment & API Configurations
│   │   ├── agents/            # ADK Agent Specifications
│   │   ├── skills/            # ADK Domain Skills
│   │   ├── mcp/               # Model Context Protocol Servers
│   │   ├── memory/            # SQLite Workspace Database & State Memory
│   │   └── eval/              # Evaluation Frameworks & Judge Scripts
│   ├── requirements.txt       # Python Backend Dependencies
│   └── Dockerfile.backend
├── frontend/                  # Next.js Frontend Web Client
│   ├── public/
│   ├── src/
│   │   ├── components/        # Glassmorphic React Components & Trace Console
│   │   ├── pages/             # Pages (Dashboard, Analyzer, Quiz, Inbox)
│   │   ├── styles/            # Vanilla CSS (Rich Navy/Gold Palette)
│   │   └── utils/             # API Fetchers & Websocket Helpers
│   ├── package.json           # Frontend Node.js Dependencies
│   └── Dockerfile.frontend
├── deploy/                    # Deployment Scripts & Local Orchestration
│   ├── docker-compose.yml
│   └── nginx.conf
├── tests/                     # Test Suites
│   ├── test_agents.py
│   ├── test_mcp.py
│   ├── test_skills.py
│   └── test_evaluation.py
└── README.md
```

---

## 2. Agents Directory (`backend/app/agents/`)

* **Purpose**: Houses the declaration and initialization of the five ADK Agents. These files define system instructions, output schemas, delegation logic, and target task parameters.
* **Files**:
  * `__init__.py`: Registers and exports the agents.
  * `orchestrator.py`: Implements the top-level ADK agent that parses requests, selects domains, and coordinates delegation transitions.
  * `research.py`: Declares the search-oriented agent that targets acts, sections, and precedents.
  * `case_analysis.py`: Contains the document parsing agent that segments court judgments.
  * `study_assistant.py`: Declares the educational content agent that generates summaries and MCQs.
  * `verification.py`: Houses the grounding checker and regex citation evaluator.
* **Dependencies**: `google-genai` (ADK Library), `fastapi`, `pydantic` (for structural output schemas).

---

## 3. Skills Directory (`backend/app/skills/`)

* **Purpose**: Implements domain-specific expertise as modular components. Each sub-folder acts as a progressive disclosure container containing prompt overrides, local data references, and specific tool schemas.
* **Files**:
  * `constitutional_law/`: Holds Article 14, 19, 21 resources and tools like `fetch_bench_composition`.
    * `constitutional_skill.py`: Exports the ADK Skill class wrapper.
    * `SKILL.md`: Prompts and instructions.
  * `contract_law/`: Houses Indian Contract Act (Sec 10, 56, 73) rules and element check tools.
    * `contract_skill.py`: Exports the ADK Skill class wrapper.
    * `SKILL.md`: Prompts and instructions.
  * `consumer_protection/`: Contains the 2019 Act rules and pecuniary calculator tools.
    * `consumer_skill.py`: Exports the ADK Skill class wrapper.
    * `SKILL.md`: Prompts and instructions.
  * `succession_law/`: Contains Section 6 Hindu Succession Act context and wills execution rules.
    * `succession_skill.py`: Exports the ADK Skill class wrapper.
    * `SKILL.md`: Prompts and instructions.
* **Dependencies**: `google-genai` (ADK Registry classes).

---

## 4. MCP Directory (`backend/app/mcp/`)

* **Purpose**: Houses the two stdio JSON-RPC MCP servers that decouple statutory databases and uploaded files from the reasoning models.
* **Files**:
  * `documents_server.py`: Executable python script running the Legal Documents MCP Server over stdio. Handles PDF metadata and chunk lookups.
  * `statutes_server.py`: Executable python script running the Indian Statutes MCP Server over stdio. Serves statutory texts from local static datasets.
  * `client_manager.py`: Manages the backend's stdio subprocess connections to the MCP servers, translating agent requests into standard MCP JSON-RPC payloads.
  * `data/`: Local database storage directories.
    * `statutes_db.json`: Static, validated JSON file containing statutory texts for target sections.
* **Dependencies**: `mcp` (Python Model Context Protocol SDK), `pypdf` (PDF parser), `numpy`/`scikit-learn` (for lightweight local vector calculations if needed).

---

## 5. Memory Directory (`backend/app/memory/`)

* **Purpose**: Manages long-term data persistence (bookmarks, study guides, profiles) and short-term runtime state (`AgentContext` serialization).
* **Files**:
  * `sqlite_db.py`: Establishes the database connection, handles thread pools, and sets up tables.
  * `crud.py`: Implements SQL queries to read/write briefs, notes, quiz scores, and settings.
  * `session_context.py`: Handles saving and loading the short-term `AgentContext` JSON payload during agent handoffs.
* **Dependencies**: `sqlite3` (built-in Python library), `sqlalchemy` (or raw SQL queries to minimize framework overhead).

---

## 6. Evaluation Directory (`backend/app/eval/`)

* **Purpose**: Provides automated test suites running LLM-as-a-judge rubrics to verify factual grounding, citation formats, and quiz accuracy.
* **Files**:
  * `eval_runner.py`: Triggers test suites and compares agent output JSONs to benchmark answers.
  * `grounding_scorer.py`: Checks for information alignment between raw PDF fragments and generated briefs.
  * `fixtures/`: Test documents.
    * `contract_ground_truth.json`: Gold-standard FIRAC briefs for validation testing.
* **Dependencies**: `pytest`, `google-genai` (for evaluative scoring).

---

## 7. Frontend Directory (`frontend/`)

* **Purpose**: Implements the user portal, integrating document upload zones, study consoles, and a visual trace console representing the active agent workflow.
* **Files**:
  * `src/pages/index.js`: Dashboard homepage showing files list, bookmarks, and quick stats.
  * `src/pages/analyzer.js`: Document upload area, interactive FIRAC viewer, and the HITL Review Inbox.
  * `src/pages/quiz.js`: Practice test engine displaying MCQs and detailed rationales.
  * `src/components/TraceConsole.js`: Visual glassmorphic console displaying active agent handoffs and tool execution steps.
  * `src/styles/index.css`: Stylesheet implementing Outfit/Inter typography, deep navy backing, gold highlight details, and cards with background blurs.
  * `src/utils/api.js`: Unified client wrapper to communicate with the FastAPI backend.
* **Dependencies**: `next`, `react`, `lucide-react` (for icons). TailwindCSS is excluded in favor of clean, premium Vanilla CSS.

---

## 8. Backend Directory (`backend/`)

* **Purpose**: Serves the application REST API endpoints, handles document upload tasks, and manages agent executions.
* **Files**:
  * `app/main.py`: FastAPI server setup. Exposes endpoints:
    * `/api/documents/upload`
    * `/api/agents/analyze`
    * `/api/workspace/briefs`
    * `/api/study/quiz`
  * `app/config.py`: Loads environment configurations (`GEMINI_API_KEY`, SQLite file paths, server port).
* **Dependencies**: `fastapi`, `uvicorn`, `python-multipart` (for file uploads).

---

## 9. Deployment Directory (`deploy/`)

* **Purpose**: Packages backend and frontend services into local containers for consistent evaluation.
* **Files**:
  * `docker-compose.yml`: Multi-container orchestrator starting the FastAPI backend and Next.js frontend, routing ports locally.
  * `nginx.conf`: Nginx configuration mapping `/api/*` requests to the backend container and other routes to Next.js.
* **Dependencies**: `Docker`, `docker-compose`.

---

## 10. Tests Directory (`tests/`)

* **Purpose**: Contains automated testing scripts to verify agent logic, skill triggers, and MCP tool executions independently from the frontend.
* **Files**:
  * `test_agents.py`: Executes tests checking that the Orchestrator routes requests correctly to child agents.
  * `test_mcp.py`: Validates JSON-RPC communication with the local MCP servers over stdio.
  * `test_skills.py`: Verifies progressive disclosure (triggering Constitutional Law skill loading on relevant inputs).
* **Dependencies**: `pytest`, `httpx` (for API endpoint testing).

---

## 11. Developer Build Order (Timeline Plan)

To minimize integration risk and ensure a fully functional submission by **July 4**, follow this progressive build order:

```
[Phase 1: Setup & DB] ──> [Phase 2: Local MCP] ──> [Phase 3: ADK Skills] ──> [Phase 4: Verification] ──> [Phase 5: UI & Polish]
```

### 11.1 Phase-by-Phase Execution

#### Phase 1: Core Setup & Workspace Storage (Days 1–2)
1. Initialize the git repository and folder structure.
2. Setup the python virtual environment and compile `requirements.txt`.
3. Build the SQLite tables (`sqlite_db.py`, `crud.py`) to manage saved briefs and quiz scores.
4. Establish the base FastAPI service (`main.py`) with test GET/POST endpoints.

#### Phase 2: Local MCP Servers (Days 3–4)
1. Write the static `statutes_db.json` dataset containing target legal sections.
2. Implement the stdio JSON-RPC `Statutes MCP Server` and verify tools via command-line tests.
3. Implement the `Legal Documents MCP Server` (extracting text chunks from local PDFs).
4. Build `client_manager.py` to establish the backend stdio connection wrapper.

#### Phase 3: ADK Agents & Domain Skills (Days 5–6)
1. Write the 4 domain-specific Skill folders with their respective trigger keywords and landmark rules.
2. Implement the declarative `Orchestrator Agent` routing graph logic.
3. Build the worker agents: `Research Agent` and `Case Analysis Agent`.
4. Test the pipeline via CLI to confirm that uploading a Contract PDF retrieves Section 56 text and returns a structured brief.

#### Phase 4: Verification & Study Generation (Days 7–8)
1. Build the `Verification Agent` regex citation parser and factual grounding checking prompts.
2. Implement the `Study Assistant Agent` to generate revision guides and MCQ quiz arrays.
3. Set up the Review Inbox staging table to hold draft briefs prior to SQLite commitment.
4. Run evaluation scripts (`eval_runner.py`) using LLM-as-a-judge patterns to check outputs.

#### Phase 5: Next.js Frontend & Observability Console (Days 9–11)
1. Build the Next.js pages: Dashboard list, Analyzer dropzone, and Quiz interface.
2. Connect the React state hooks to backend API endpoints.
3. Build the visual **Trace Console component** rendering agent state changes (e.g. showing "Case Analysis active... -> Verification complete").
4. Style the entire web portal using high-fidelity Vanilla CSS.

#### Phase 6: Observability, Packaging & Demo (Day 12)
1. Integrate basic logging hooks to monitor token footprints and trace durations.
2. Write the deployment orchestrator (`docker-compose.yml`).
3. Conduct final validation runs.
4. Record the 3-minute capstone video demonstration and package files for submission.
