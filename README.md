# 📧 Email Triage OpenEnv

An OpenEnv-compliant environment where AI agents learn to triage customer support emails — a real-world task performed by thousands of support teams every day.

---

## 🌍 Environment Overview

Customer support teams receive hundreds of emails daily. They must quickly:
1. **Categorize** the email (billing issue? technical problem? feature request?)
2. **Prioritize** it (is this a 5-alarm fire or a casual question?)
3. **Reply** professionally and helpfully

This environment simulates exactly that workflow, allowing AI agents to be trained and evaluated on real email triage skills.

---

## 📋 Tasks

| Task | Difficulty | Description | Max Steps |
|------|-----------|-------------|-----------|
| `task1_categorize` | 🟢 Easy | Classify email into correct category | 3 |
| `task2_prioritize` | 🟡 Medium | Classify + assign priority (1-5) | 5 |
| `task3_full_triage` | 🔴 Hard | Classify + prioritize + write reply | 8 |

### Task 1: Categorize (Easy)
The agent reads an email and responds with ONE category:
- `critical` — server down, security breach, urgent issues
- `billing` — invoice questions, refunds, subscription issues
- `technical_support` — login problems, how-to questions
- `feature_request` — suggestions for new features
- `business` — partnership/sponsorship inquiries
- `spam` — irrelevant or junk email

**Expected response:** Just the category name, e.g. `billing`

### Task 2: Prioritize (Medium)
The agent must give both category AND priority.

**Expected response format:**
```
category=billing priority=2
```

Priority scale: 1 (most urgent) → 5 (least urgent)

### Task 3: Full Triage (Hard)
The agent must do everything: categorize, prioritize, AND write a professional reply.

**Expected response format:**
```
category=billing
priority=2
reply=Dear customer, thank you for reaching out. I have reviewed your invoice...
```

---

## 🔍 Action & Observation Spaces

### Observation (what the agent sees)
```json
{
  "email_id": "email_002",
  "subject": "Question about my invoice",
  "sender": "customer123@gmail.com",
  "body": "Hi, I received my invoice...",
  "task_description": "EASY TASK: Read the email and classify it...",
  "step_number": 1,
  "last_reward": 0.0,
  "message": "Read the email carefully and respond as instructed."
}
```

### Action (what the agent does)
```json
{
  "text": "billing"
}
```

### Reward
- Range: 0.0 to 1.0
- Partial credit given at every step
- Penalizes empty responses
- Penalizes wasting steps

---

## 🚀 Setup & Usage

### Run locally

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd email-triage-env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
cd server
python app.py
```

Server starts at `http://localhost:7860`

### Run with Docker

```bash
docker build -t email-triage-env .
docker run -p 7860:7860 email-triage-env
```

### Run inference script

```bash
export HF_TOKEN=your_token_here
export API_BASE_URL=https://api.openai.com/v1
export MODEL_NAME=gpt-4.1-mini
export ENV_BASE_URL=http://localhost:7860

python inference.py
```

---

## 📊 Baseline Scores

| Task | Baseline Model | Score |
|------|---------------|-------|
| task1_categorize | gpt-4.1-mini | ~0.85 |
| task2_prioritize | gpt-4.1-mini | ~0.65 |
| task3_full_triage | gpt-4.1-mini | ~0.55 |

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/` | Health check + info |
| GET | `/health` | Simple health check |
| POST | `/reset` | Start new episode |
| POST | `/step` | Agent takes action |
| GET | `/state` | Current env state |
| GET | `/tasks` | List all tasks |

---

## 📁 Project Structure

```
email-triage-env/
├── inference.py        ← Baseline inference script (root)
├── openenv.yaml        ← OpenEnv metadata
├── Dockerfile          ← Container config
├── requirements.txt
├── README.md
└── server/
    ├── app.py          ← FastAPI server
    ├── env.py          ← Environment logic
    ├── tasks.py        ← Task definitions + graders
    └── data.py         ← Sample email dataset
```
