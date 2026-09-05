# Stewart Acid Base Sid Analyzer

> **Domain:** Clinical Decision Support & Biomedical Computing
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Stewart Physicochemical Acid-Base & Strong Ion Difference (SID)
Calculates apparent SID (SIDa), effective SID (SIDe), and Strong Ion Gap (SIG) for complex ICU dysnatremias.

Zero-dependency Python implementation with single and batch evaluation.
Author: Dr. Abu Suraih Sakhri
License: MIT

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`calculate_metrics()`**: Core domain algorithm for stewart-acid-base-sid-analyzer.
- **`process_single()`** — calculates and validates process_single parameters.
- **`process_batch()`** — calculates and validates process_batch parameters with input validation and error handling.
- **`main()`** — CLI entry point with graceful error handling.

---

## 📐 Mathematical Formulation & Logic

```text
  score = primary_val
  rounded_score = round(score, 2)
  res = calculate_metrics(**kwargs)
  calc_res = calculate_metrics(**r)
```

---

## 💻 Installation

```bash
pip install -r requirements.txt
```

---

## 💻 CLI Quickstart & Usage

### 1. Single Evaluation
```bash
python stewart_sid.py single --v1 15.0 --v2 5.0 --v3 2.0
```

### 2. Batch CSV Processing
```bash
python stewart_sid.py batch -i sample.csv -o results.csv
```

### 3. Enterprise CLI (requires FastAPI/uvicorn)
```bash
python cli.py audit --task-id TASK-001 --primary 28.5 --secondary 14.2
python cli.py batch -i sample.csv -o results.csv
python cli.py chat "Explain Stewart parameters"
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--v1`: Primary parameter (float, default: 10.0)
- `--v2`: Secondary parameter (float, default: 5.0)
- `--v3`: Tertiary parameter (float, default: 2.0)
- `-i, --input`: Input CSV file path (required for batch)
- `-o, --output`: Output CSV file path (default: results.csv)

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `Patient_ID` | Parameter / observation metric | Required |
| `v1` | Parameter / observation metric | Required |
| `v2` | Parameter / observation metric | Required |
| `v3` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Security Configuration

Set the `AUDIT_SECRET_KEY` environment variable for production deployments:

```bash
# Linux/macOS
export AUDIT_SECRET_KEY="your-secure-random-key"

# Windows
set AUDIT_SECRET_KEY=your-secure-random-key
```

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t stewart-acid-base-sid-analyzer .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secure-key stewart-acid-base-sid-analyzer
```

Or using Docker Compose:

```bash
docker-compose up -d
```

---

## 📁 Project Structure

```
stewart-acid-base-sid-analyzer/
├── agents/                 # Enterprise agent framework
│   ├── api.py             # FastAPI REST server
│   ├── base.py            # Security, PHI guard, HMAC audit
│   ├── models.py          # Pydantic data models
│   ├── supervisor.py      # Multi-agent orchestrator
│   ├── workers.py         # Specialized domain workers
│   ├── llm_factory.py     # LLM provider factory
│   ├── learning.py        # Bayesian calibration engine
│   ├── metrics.py         # Prometheus metrics exporter
│   └── streamer.py        # WebSocket telemetry broadcaster
├── tests/                 # Pytest test suite
├── web/index.html         # Operations console UI
├── cli.py                 # Enterprise CLI entry point
├── stewart_sid.py         # Core SID analysis engine
├── enrichment.py          # Clinical enrichment modules
├── simulator.py           # High-throughput stress tester
├── sample.csv             # Sample input data
├── benchmark_dataset.json # Golden benchmark test cases
├── openapi_spec.json      # OpenAPI 3.1 specification
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container build config
└── docker-compose.yml     # Multi-service orchestration
```
