<!-- Header banner -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,20,24&height=200&section=header&text=Kapture%20Collections%20VoiceBot&fontSize=40&fontColor=ffffff&desc=AI%20voice%20agent%20for%20automated%20loan-collection%20calls&descSize=18&descAlignY=68" alt="Kapture Collections VoiceBot" width="100%">
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white">
  <img alt="Vapi" src="https://img.shields.io/badge/Voice%20AI-Vapi-7C3AED">
  <img alt="Alembic" src="https://img.shields.io/badge/Migrations-Alembic-6B7280">
  <img alt="pytest" src="https://img.shields.io/badge/Tests-pytest-0A9EDC?logo=pytest&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green">
</p>

<p align="center">
  <b>An AI voice agent that calls borrowers, verifies their identity, looks up dues, negotiates a payment commitment, and logs every outcome.</b>
</p>

---

## 📑 Table of Contents

[Overview](#-overview) · [Features](#-features) · [Demo](#-demo) · [Architecture](#-architecture) · [Call Workflow](#-call-workflow) · [Data Model](#-data-model) · [Tech Stack](#-tech-stack) · [Project Structure](#-project-structure) · [Getting Started](#-getting-started) · [Configuration](#-configuration) · [Testing](#-testing) · [Design Decisions](#-design-decisions) · [Security](#-security-and-responsible-collections) · [Roadmap](#-roadmap) · [Author](#-author)

---

## 📌 Overview

Loan collection is repetitive, high-volume, and sensitive. Human agents spend most of their day on routine reminder calls, while borrowers who genuinely need a conversation wait in the queue.

**Kapture Collections VoiceBot** automates the routine part. A voice agent built on [Vapi](https://vapi.ai) calls the borrower, verifies who they are, fetches outstanding dues from a **Python backend backed by PostgreSQL**, discusses payment options, and records a structured outcome. Anything that needs human judgment is escalated.

| Without automation | With VoiceBot |
|---|---|
| Agents make repetitive reminder calls | The bot handles routine calls end to end |
| Call notes are inconsistent or missing | Every call produces a structured outcome record |
| Coverage is limited by headcount | Calls scale with infrastructure |
| Disputes get buried in the queue | Disputes are flagged for a human immediately |

---

## ✨ Features

- 🎙️ **Natural voice conversations** with speech-to-text, LLM reasoning, and text-to-speech orchestrated by Vapi
- 🔐 **Identity verification first.** Account details are shared only after the borrower is verified
- 🗄️ **Live account lookup.** The assistant calls backend tools to fetch dues from PostgreSQL in real time
- 📋 **Structured call outcomes.** Promise to pay, callback, dispute, or failed verification are stored as queryable records
- 🙋 **Human escalation** for disputes and sensitive situations
- 🐳 **One-command database setup** with Docker Compose and Alembic migrations
- 🧾 **Configuration as code.** The Vapi assistant definition is versioned in [`vapi-config/`](vapi-config)
- ✅ **Tested backend** using `pytest`

---

## 🎬 Demo

<!-- Add a screenshot or GIF here, e.g.  ![Demo](docs/demo.gif)  -->

**Sample conversation** (synthetic data)

| Speaker | Utterance |
|---|---|
| 🤖 Bot | "Hello, this is an automated assistant calling on behalf of Kapture Finance. Am I speaking with Mr. Rahul?" |
| 👤 Borrower | "Yes, speaking." |
| 🤖 Bot | "For security, could you confirm your date of birth?" |
| 👤 Borrower | "12th March 1990." |
| 🤖 Bot | "Thank you, you're verified. Your EMI of ₹8,500 was due on the 5th and is still pending." |
| 👤 Borrower | "I can pay this Friday." |
| 🤖 Bot | "Noted. I've recorded a payment of ₹8,500 for Friday. Thank you for your time." |

---

## 🏗️ Architecture

```mermaid
flowchart LR
    B([📞 Borrower]) <-->|voice call| LLM

    subgraph V[Vapi Voice AI Platform]
        STT[Speech-to-Text] --> LLM[LLM Assistant<br/>prompt + tools] --> TTS[Text-to-Speech]
    end

    LLM -->|tool calls - HTTPS| API
    API -->|JSON result| LLM

    subgraph BE[Backend Service - Python]
        API[API Layer<br/>webhook + tool endpoints] --> SVC[Service Layer<br/>verification, dues, outcomes] --> DAL[Data Layer<br/>models + queries]
    end

    DAL <-->|SQL| DB[(PostgreSQL 16<br/>Docker)]
    MIG[Alembic migrations] -.-> DB

    style V fill:#f5f3ff,stroke:#7c3aed
    style BE fill:#fff7ed,stroke:#ea580c
    style DB fill:#dbeafe,stroke:#2563eb
```

| Component | Responsibility |
|---|---|
| **Vapi** | Telephony, speech-to-text, LLM conversation, text-to-speech. Configured in `vapi-config/` |
| **Backend (Python)** | Webhook and tool-call endpoints, verification, dues lookup, outcome recording |
| **PostgreSQL 16** | System of record for customers, accounts, calls, and outcomes |
| **Alembic** | Versioned schema migrations |

### Request lifecycle

```mermaid
sequenceDiagram
    autonumber
    participant B as Borrower
    participant V as Vapi
    participant A as Backend API
    participant D as PostgreSQL

    V->>B: Places call and greets
    B->>V: Speaks
    V->>A: Tool call: verify identity
    A->>D: Query customer record
    D-->>A: Customer data
    A-->>V: Verified
    V->>A: Tool call: fetch dues
    A->>D: Query account dues
    D-->>A: Amount and due date
    A-->>V: Dues payload
    V->>B: Explains dues, asks for commitment
    B->>V: Agrees to pay on a date
    V->>A: Tool call: record outcome
    A->>D: Insert call outcome
    A-->>V: Saved
    V->>B: Confirms and ends call
```

---

## 🔄 Call Workflow

```mermaid
flowchart TD
    A([Call starts]) --> B[Greeting and AI disclosure]
    B --> C[Verify identity]
    C -->|fails| X[Cannot verify<br/>end politely, share no details]
    C -->|passes| D[Fetch dues from backend]
    D --> E[Discuss payment options]
    E --> F{Call outcome?}
    F -->|Agrees to pay| G[Promise to pay<br/>record amount and date]
    F -->|Needs time| H[Callback requested<br/>schedule follow-up]
    F -->|Disputes| I[Escalate to human agent]
    G --> L[(Log outcome and summary<br/>to PostgreSQL)]
    H --> L
    I --> L
    X --> L

    style C fill:#fff7ed,stroke:#ea580c
    style D fill:#fff7ed,stroke:#ea580c
    style L fill:#fff7ed,stroke:#ea580c
    style G fill:#f0fdf4,stroke:#16a34a
    style H fill:#f0fdf4,stroke:#16a34a
    style I fill:#fef2f2,stroke:#dc2626
    style X fill:#f1f5f9,stroke:#64748b
```

🟧 Orange steps involve the backend and database.

---

## 🗃️ Data Model

```mermaid
erDiagram
    CUSTOMER ||--o{ LOAN_ACCOUNT : holds
    LOAN_ACCOUNT ||--o{ CALL_LOG : receives
    CALL_LOG ||--o| PROMISE_TO_PAY : may_produce

    CUSTOMER {
        int id PK
        string name
        string phone
    }
    LOAN_ACCOUNT {
        int id PK
        int customer_id FK
        decimal amount_due
        date due_date
        string status
    }
    CALL_LOG {
        int id PK
        int account_id FK
        string outcome
        text summary
        timestamp called_at
    }
    PROMISE_TO_PAY {
        int id PK
        int call_id FK
        decimal amount
        date promised_date
    }
```

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Voice AI | [Vapi](https://vapi.ai) (telephony, STT, LLM, TTS) |
| Backend | Python |
| Database | PostgreSQL 16 |
| Migrations | Alembic |
| Containers | Docker, Docker Compose |
| Testing | pytest |

---

## 📁 Project Structure

```text
kapture-collections-voicebot/
├── backend/            # Python service: endpoints, business logic, DB access, migrations
├── docs/               # Documentation
├── vapi-config/        # Vapi assistant definition (prompt, tools, voice settings)
├── docker-compose.yml  # Local PostgreSQL 16 with health check and persistent volume
└── .gitignore
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- A [Vapi](https://vapi.ai) account and API key
- [ngrok](https://ngrok.com) (or any tunnel) so Vapi can reach your local backend

### Setup

```bash
# 1. Clone
git clone https://github.com/SidharthA7204/kapture-collections-voicebot.git
cd kapture-collections-voicebot

# 2. Start PostgreSQL (host port 5433)
docker compose up -d

# 3. Backend environment
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then fill in your values

# 4. Create the schema
alembic upgrade head

# 5. Run the backend
uvicorn app.main:app --reload --port 8000

# 6. Expose it to Vapi (in a new terminal)
ngrok http 8000
```

### Connect Vapi

1. Create an assistant in the Vapi dashboard from the definition in [`vapi-config/`](vapi-config).
2. Set the tool/server URL to your ngrok HTTPS address.
3. Attach a phone number, or use the dashboard's web call to test.
4. Place a test call and watch the backend logs and database update.

---

## ⚙️ Configuration

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://kapture_user:kapture_password@localhost:5433/kapture` |
| `VAPI_API_KEY` | Vapi private API key | `your-vapi-key` |
| `VAPI_WEBHOOK_SECRET` | Authenticates incoming Vapi requests | `a-long-random-string` |
| `LOG_LEVEL` | Log verbosity | `INFO` |

> ⚠️ The database credentials shown match `docker-compose.yml` and are **for local development only**. Use strong credentials and a secrets manager in any shared or production environment. `.env` files are git-ignored.

---

## 🧪 Testing

```bash
cd backend
pytest -v
```

---

## 🧠 Design Decisions

| Decision | Why |
|---|---|
| **Vapi for voice orchestration** | Handles telephony and the STT/LLM/TTS pipeline, so effort goes into collections logic instead of audio plumbing |
| **Backend tools instead of giving the LLM the data** | The model requests only what it needs, after verification. This limits data exposure and hallucination risk |
| **Structured outcomes over free-text notes** | Enables reporting, follow-up automation, and audit trails |
| **PostgreSQL with Alembic** | Relational integrity plus reviewable, reversible schema changes |
| **Assistant config in Git** | Prompt and tool changes get code review and history |
| **Docker Compose for the DB** | New contributors get a working data layer in one command |

---

## 🔒 Security and Responsible Collections

- **Verify before disclosing.** Debt details are shared only after identity verification
- **Secrets stay out of Git.** `.env` files are git-ignored
- **Least-privilege data access** through narrow, purpose-built backend tools
- **Transparency.** The agent identifies itself as automated
- **Human in the loop** for disputes and sensitive situations
- **Auditability.** Each outcome is stored with a timestamp and summary

Production use would also require compliance review (permitted calling hours, consent and do-not-call rules, data retention, call-recording disclosures) and authenticated webhooks.

---

## 🗺️ Roadmap

- [ ] Multilingual conversations (Hindi, Malayalam, and other regional languages)
- [ ] Payment link delivery via SMS or WhatsApp after a promise to pay
- [ ] Automated follow-up calls when a promised date is missed
- [ ] Analytics dashboard (contact rate, promise-to-pay rate, escalation rate)
- [ ] Sentiment detection to trigger early human handoff
- [ ] CI pipeline with GitHub Actions (lint, tests, migration check)
- [ ] Backend container image and one-command deployment

---

## 💡 What This Project Demonstrates

- **Conversational AI engineering:** prompt design, tool calling, voice pipeline orchestration
- **Backend development:** real-time API design, business logic, and data access in Python
- **Database engineering:** relational modeling, Alembic migrations, containerized PostgreSQL
- **DevOps fundamentals:** Docker Compose, health checks, environment-based config, secret hygiene
- **Product thinking:** a real business workflow with compliance, escalation, and audit needs

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a pull request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.

---

## 👤 Author

**Sidharth A**

[![GitHub](https://img.shields.io/badge/GitHub-SidharthA7204-181717?logo=github)](https://github.com/SidharthA7204)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/YOUR-USERNAME)

⭐ If you found this project useful, consider giving it a star!
