# DocForge — Project Brief

**Project:** DocForge
**Owner:** Christian (Theseus Research)
**Date:** March 3, 2026
**Status:** Active Development

---

## What Is DocForge?

DocForge is an open-source, template-driven document generation engine with a web-based interface. Users author document templates in Microsoft Word using red-formatted text as instructions to the system — telling it where to pull data, what to generate with an LLM, and what values to substitute. DocForge parses those templates, auto-resolves data mappings, generates the document, and hands it off to the user in a built-in editor for proofing and final export.

## Why Does This Exist?

Across regulated industries, consulting, finance, and enterprise operations, teams keep rebuilding the same document generation pipeline with minor variations. Template parsing, data ingestion, table population, section assembly, formatting preservation — the logic is 80%+ identical every time, but every project starts from scratch. DocForge makes this a solved problem.

## Who Is It For?

- **AI Engineers** building document generation workflows who want a reusable framework instead of another one-off pipeline
- **Business Users** who author templates in Word and want a visual tool for mapping data, generating documents, and proofing output
- **Technical Program Managers** evaluating tools for their teams who need to see a working end-to-end demo
- **Developers** looking to integrate or extend document generation for their own domains

## How Does It Work?

1. **Author** a template in Word — use red text for LLM instructions and data placeholders
2. **Upload** the template and data files into DocForge
3. **Review** the auto-resolved mappings in the web GUI — the system infers what goes where from the template context
4. **Generate** the document — data populates tables, LLM fulfills instructions, placeholders get substituted
5. **Proof** in the built-in editor — review LLM content, flag low-confidence items, edit text and tables
6. **Export** the final .docx

## Key Design Decisions

- **Red text = LLM instruction by default.** Template authors write natural language instructions in red; the system treats everything as a prompt unless it's clearly a short variable placeholder.
- **Template-primary mapping.** The template drives the generation logic. The GUI verifies, corrects, and refines — it doesn't define the workflow from scratch.
- **Section-scoped LLM context.** Each LLM prompt only sees data from its own section unless the prompt explicitly references broader scope. This keeps outputs focused and costs predictable.
- **Low-confidence items don't block generation.** Everything runs, and anything uncertain gets flagged in the editor for post-generation review.
- **Web-based architecture.** React frontend + FastAPI backend, containerized with Docker. Modern UX, easy to deploy, easy to extend.
- **Database-backed projects.** Project configurations persist in SQLite so users can reuse templates with new data files across sessions.

## Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | React + TypeScript, TipTap/ProseMirror editor |
| Backend | Python 3.10+, FastAPI |
| Document Engine | python-docx, lxml |
| Data Processing | pandas, openpyxl, python-pptx, pymupdf |
| LLM Integration | LiteLLM (LM Studio, Ollama, OpenAI, Anthropic, Google, Bedrock) |
| Storage | SQLite |
| Deployment | Docker / Docker Compose |

## What's Out of Scope (v1)

Image injection, multi-document batch generation, PDF output, real-time collaboration, multi-language templates, and full word processor capabilities.

## Release Milestones

| Phase | Focus | Key Deliverable |
|-------|-------|----------------|
| v0.1 | Foundation | Template parser, basic table population, minimal web UI, Docker setup |
| v0.2 | Data Pipeline | Full mapping GUI, transforms, Office extraction, project DB |
| v0.3 | LLM Integration | Prompt execution, provider config, context assembly |
| v0.4 | Document Editor | WYSIWYG editor, accept/reject, table editing, export |
| v0.5 | Polish | Plugin architecture, docs site, PyPI publication |

## Success Criteria

- End-to-end demo completable in under 10 minutes from launch to exported document
- Document generation (excluding LLM inference) under 10 seconds
- Fully functional without LLM API keys — LLM features degrade gracefully
- A developer can clone, `docker compose up`, and run the demo with zero configuration
