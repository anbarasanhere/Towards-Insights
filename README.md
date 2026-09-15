# Towards Insights

Towards Insights is a local browser app that turns dataset columns and optional sample rows into a leadership-focused business analysis. It first presents a data overview and starter business questions, then supports interactive follow-up questions before you commit. Each case is stored as one canonical Markdown file under `cases/` and can be committed and pushed to GitHub.

See [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md) for the full product workflow, architecture, data contract, case format, configuration, privacy expectations, and future extensions.

<img width="1920" height="1080" alt="Screenshot 2026-09-15 at 1 33 54 PM" src="https://github.com/user-attachments/assets/6bf409a3-fc40-4ac9-84bb-aa0df496dded" />

<img width="1428" height="667" alt="Screenshot 2026-09-15 at 1 35 54 PM" src="https://github.com/user-attachments/assets/f11055c8-0911-4eb9-bc97-85890428a581" />


## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
cp .env.example .env
PYTHONPATH=src python -m towards_insights.app
```

Open http://127.0.0.1:8765.

Without `OPENAI_API_KEY`, the app uses a deterministic schema-based starter analysis and directional follow-up answers so the workflow can be tested locally. To use an OpenAI-compatible provider, set `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL` in the environment. Sample data and follow-up context are sent to that provider; remove confidential values before submitting.

## Git publishing

The app expects the current checkout to be the target repository. Configure a remote and authentication before publishing:

```bash
git remote add origin https://github.com/anbarasanhere/Towards-Insights.git
git branch -M main
```

Set `REPOSITORY_PATH` if the target checkout differs from the app directory. After reviewing the Overview tab and using Ask questions, use the Commit tab. Publishing creates or updates exactly one file for a case, such as `cases/customer-churn.md`, including the overview, starter questions, and discussion transcript, then commits and pushes that file to `GIT_REMOTE` and `GIT_BRANCH`.

The first local commit should include the application itself before using the publish action, so Git has a valid `HEAD`.
