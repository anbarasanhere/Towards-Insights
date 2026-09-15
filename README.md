# Towards Insights

Towards Insights is a local browser app that turns dataset columns and optional sample rows into a leadership-focused business analysis. Each case is stored as one canonical Markdown file under `cases/` and can be committed and pushed to GitHub.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
cp .env.example .env
PYTHONPATH=src python -m towards_insights.app
```

Open http://127.0.0.1:8765.

Without `OPENAI_API_KEY`, the app uses a deterministic schema-based starter analysis so the workflow can be tested locally. To use an OpenAI-compatible provider, set `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL` in the environment. Sample data is sent to that provider; remove confidential values before submitting.

## Git publishing

The app expects the current checkout to be the target repository. Configure a remote and authentication before publishing:

```bash
git remote add origin https://github.com/anbarasanhere/Towards-Insights.git
git branch -M main
```

Set `REPOSITORY_PATH` if the target checkout differs from the app directory. Publishing creates or updates exactly one file for a case, such as `cases/customer-churn.md`, then commits and pushes that file to `GIT_REMOTE` and `GIT_BRANCH`.

The first local commit should include the application itself before using the publish action, so Git has a valid `HEAD`.
