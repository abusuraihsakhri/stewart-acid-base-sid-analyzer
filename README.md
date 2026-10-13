# Stewart Acid–Base SID Analyzer

A Stewart–Figge physicochemical acid–base calculator for **apparent strong ion difference (SIDa)**, **effective strong ion difference (SIDe)**, and **strong ion gap (SIG)**. The calculation engine is available in Python, as a local FastAPI endpoint, and as a standalone JavaScript browser application suitable for GitHub Pages.

**Scope:** Research and education. This is not a validated medical device or a stand-alone diagnostic or treatment algorithm.

## Main features

- Fully client-side browser calculator with explicit laboratory units, numerical validation, and CSV export. No Python runtime, account, or server is needed to calculate in the browser.
- Zero-dependency Python calculation engine with single-case and batch-CSV modes.
- FastAPI `POST /api/calculate` endpoint and automatically generated interactive API documentation at `/docs`.
- Separate legacy demonstration audit/chat modules for software workflows; **these do not derive clinical severity from Stewart physiology**.
- Numerical regression tests, input-validation tests, audit HMAC verification tests, and GitHub Actions CI for Python 3.10–3.12.

## Calculation and units

All strong-ion inputs, including **ionized Ca²⁺ and Mg²⁺**, are supplied in **mmol/L**. The divalent ions are multiplied by 2 to express their charge contribution in mEq/L. Albumin is **g/L**; inorganic phosphate is **mmol/L**; **PaCO₂ is mmHg**; pH is unitless.

```text
SIDa = [Na+] + [K+] + 2[iCa2+] + 2[iMg2+] - [Cl-] - [lactate-]
HCO3- = 0.0301 * PaCO2 * 10^(pH - 6.1)
Alb- = albumin * (0.123 * pH - 0.631)
Pi- = phosphate * (0.309 * pH - 0.469)
SIDe = HCO3- + Alb- + Pi-
SIG  = SIDa - SIDe
```

SIDa, SIDe and SIG are reported in **mEq/L**; estimated bicarbonate is in **mmol/L**. Precision is retained through calculation and rounded to 3 decimal places for reporting. The result depends on measured species, sampling and analytical uncertainty and should not be interpreted against a universal severity cutoff.

Reference: [The Stewart Approach—One Clinician's Perspective](https://pmc.ncbi.nlm.nih.gov/articles/PMC2702213/). For clinical research comparisons see [Strong ion gap and anion gap corrected for albumin and lactate in ICU sepsis](https://pmc.ncbi.nlm.nih.gov/articles/PMC11101998/).

## Browser use

Open `index.html` directly, enter same-time-point laboratory measurements and select **Calculate SID / SIG**. Select **Export CSV** to save the current values and results. **Restore example** reloads non-patient example measurements. `web/index.html` redirects to the main app.

The browser calculation is implemented in JavaScript because these equations require no Python-specific libraries. **Pyodide/PyScript are not required**. The page needs a modern browser with ES2017 support; the calculations work without a network connection. An external literature link requires a connection only if selected.

## Python CLI

```bash
python -m pip install -r requirements.txt
python stewart_sid.py single \
  --sodium 140 --potassium 4 --ionized-calcium 1.2 --ionized-magnesium 0.8 \
  --chloride 104 --lactate 1.5 --ph 7.4 --pco2 40 --albumin 40 --phosphate 1.2

python stewart_sid.py batch -i sample.csv -o results.csv
pytest -v
```

Batch CSV input must contain the exact input columns present in `sample.csv`. Extra metadata columns are retained, and incomplete or invalid records are rejected. The export protects text fields beginning with spreadsheet formula characters.

## Local API and optional demonstration components

```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` for the locally served calculator or `http://127.0.0.1:8000/docs` for the API. The `POST /api/calculate` JSON request takes the ten measurement fields named in the CLI example (underscores instead of hyphens). FastAPI serves the authoritative OpenAPI schema at `/openapi.json`.

The older `python cli.py audit`, `batch`, `chat`, and `verify-audit` commands remain available for generic workflow demonstrations. Their thresholds and mock chat responses are **not clinically validated**. External LLM providers are not implemented.

### Docker

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
docker compose up --build
```

Compose binds to localhost by default. The signing key is required for Compose; the process otherwise generates an ephemeral key for local development. Audit records are **in memory**, not a durable multi-process ledger.

## Privacy and security

The standalone page processes entered numbers locally, with no analytics, external scripts, uploads or browser storage. The Python CLI also computes locally. **Using the API transmits request data to the configured API server**. The legacy agent modules include a limited identifier-pattern filter, not comprehensive PHI detection, anonymization or HIPAA compliance. Do not submit identifiable patient information.

Never embed server signing keys in static pages or commit them to source control. Set `AUDIT_SECRET_KEY` securely in any server deployment.

## Technology and license

Python 3.10–3.12, FastAPI, Pydantic 2, Pytest; vanilla HTML/CSS/JavaScript for the browser. [MIT License](LICENSE).
