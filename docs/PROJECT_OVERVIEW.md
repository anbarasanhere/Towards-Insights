# Towards Insights: Project Overview

## Purpose

Towards Insights is a local browser-based data intelligence assistant. It helps a user move from a pasted dataset structure to practical business decisions by combining:

- Dataset overview and inferred business context
- Core entities and relationships
- Leadership-oriented business questions
- Interactive follow-up questions
- A final Markdown case committed to GitHub

The application is designed for early-stage exploration when the user has column names and a small number of representative records, but does not yet have a complete data dictionary or dashboard plan.

## User Workflow

1. **Create a case**
   - Enter a case title.
   - Paste column names and a few reference records into the data area.
   - The first pasted row is treated as the header row.

2. **Generate the initial analysis**
   - The system infers a possible business domain.
   - It identifies likely entities and relationships.
   - It describes the likely row grain, field roles, and data-quality questions.
   - It proposes questions in three categories:
     - Key Metrics & KPIs
     - Customer & Behavioral Segmentation
     - Operational Efficiency
   - Each question includes why it matters, how to compute it, and which visualization fits best.

3. **Explore interactively**
   - Use the Ask questions tab to ask about metrics, segments, assumptions, data quality, or next steps.
   - The assistant receives the original dataset context, generated analysis, and conversation history.

4. **Commit the case**
   - After reviewing the overview and follow-up discussion, use the Commit tab.
   - The application creates or updates one canonical Markdown file under `cases/`.
   - The file includes the overview, business questions, assumptions, and follow-up discussion.
   - Git commits and pushes that case file to the configured repository.

## Architecture

```text
Browser UI
  -> Local HTTP server
      -> Analysis request validation
      -> Analysis provider
          -> OpenAI-compatible API, or deterministic local fallback
      -> Structured analysis models
      -> Markdown case renderer
      -> Local Git publisher
          -> Configured GitHub remote
```

### Browser UI

The interface is served from `web/` and contains:

- `index.html`: case form and result container
- `app.js`: paste parsing, API calls, tabs, conversation state, and rendering
- `style.css`: workspace layout and visual styling

The input is intentionally paste-first. It accepts tab-separated spreadsheet data, comma-separated rows, and simple one-column-per-line input.

### Local application server

`src/towards_insights/app.py` provides a small standard-library HTTP server with these routes:

- `GET /`: serve the application page
- `GET /style.css`: serve styles
- `GET /app.js`: serve browser behavior
- `POST /api/analyze`: generate the initial overview and business questions
- `POST /api/question`: answer a follow-up question
- `POST /api/publish`: render, commit, and push the case Markdown file

### Structured models

`src/towards_insights/models.py` defines the application contract:

- `AnalysisRequest`: case title, column names, and sample data
- `DataOverview`: summary, likely grain, field roles, and quality notes
- `BusinessQuestion`: question, leadership rationale, computation logic, and visualization recommendation
- `AnalysisResult`: overview, domain, entities, relationships, questions, and assumptions

### Analysis provider

`src/towards_insights/providers.py` isolates analysis generation from the server:

- With `OPENAI_API_KEY`, it calls an OpenAI-compatible `/chat/completions` endpoint.
- Without an API key, it returns a deterministic local fallback so the complete UI workflow can be tested without a provider.
- Follow-up questions use the same provider configuration and receive the current analysis plus conversation history.

The provider is intentionally replaceable so a local model or another compatible service can be added later.

### Markdown and Git publishing

`src/towards_insights/markdown.py` renders a stable case document. The filename is derived from the case title, for example:

```text
cases/customer-churn.md
```

A repeated analysis for the same case updates that file rather than creating a second case file. `src/towards_insights/git_publisher.py` stages only the case file, creates a focused commit, and pushes it to the configured branch.

## Case Document Structure

Each case contains:

- YAML-style frontmatter with case identity, timestamps, domain, status, and columns
- Business domain
- Data overview
- Field roles and quality checks
- Core entities and relationships
- Assumptions
- Key Metrics & KPIs questions
- Customer & Behavioral Segmentation questions
- Operational Efficiency questions
- Follow-up discussion transcript

The case is intended to be readable in GitHub, easy to review in a pull request or commit history, and useful as a durable decision-research record.

## Configuration

Copy `.env.example` to `.env` and configure as needed:

- `OPENAI_API_KEY`: optional provider key
- `OPENAI_BASE_URL`: OpenAI-compatible API base URL
- `OPENAI_MODEL`: provider model name
- `REPOSITORY_PATH`: local checkout used for case publishing
- `GIT_REMOTE`: Git remote name, normally `origin`
- `GIT_BRANCH`: target branch, normally `main`
- `PORT`: local server port, normally `8765`

The `.env` file is ignored by Git. Git authentication is handled by the local Git installation rather than stored by the application.

## Privacy Expectations

The application may send pasted sample data and follow-up context to the configured AI provider. Users should:

- Remove names, emails, phone numbers, account numbers, and other direct identifiers.
- Use representative examples rather than full exports.
- Avoid pasting secrets, credentials, or regulated personal data.
- Confirm the configured provider and endpoint before submitting sensitive schemas.

The fallback mode does not send data to an external provider.

## Development and Verification

Run the tests with:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Validate the browser script with:

```bash
node --check web/app.js
```

The current tests cover request normalization, required input, analysis category validation, stable case slugs, and Markdown rendering. A full browser automation suite and provider integration test are future improvements.

## Current Scope and Future Extensions

Current scope:

- Local browser application
- Paste-based schema and sample-data input
- Initial structured analysis
- Interactive follow-up questions
- One Markdown file per case
- Local Git commit and push

Natural next extensions:

- CSV file upload and local profiling
- Existing-case browsing and loading
- Richer data-quality statistics
- Provider selection and local-model support
- Draft mode before committing
- Pull-request publishing instead of direct branch pushes
- Browser automation tests
