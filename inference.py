"""
inference.py - Baseline Inference Script for Email Triage OpenEnv
=====================================================================
This script runs an LLM agent against the Email Triage environment
and logs results in the required [START] / [STEP] / [END] format.

Required environment variables:
  API_BASE_URL  - LLM API endpoint (has default)
  MODEL_NAME    - Model to use (has default)
  HF_TOKEN      - Hugging Face token (REQUIRED, no default)
"""
import os
import requests
from openai import OpenAI

# ── Environment variables (with required defaults) ──────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME",   "meta-llama/Llama-3.3-70B-Instruct")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "https://proz1-email-triage.hf.space")
HF_TOKEN     = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

# ── OpenAI client pointed at HF free inference API ──────────────────────────


TASKS = ["task1_categorize", "task2_prioritize", "task3_full_triage"]

# ── System prompt ────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert customer support email triage agent.

For task1_categorize: Reply with ONLY the category name. Nothing else.
Categories: critical, billing, technical_support, feature_request, business, spam

For task2_prioritize: Reply in this exact format (one line, nothing else):
category=<category> priority=<1-5>
Priority: 1=most urgent, 5=least urgent

For task3_full_triage: Reply in this exact format (nothing else):
category=<category>
priority=<1-5>
reply=<professional reply to the customer>

Follow the format exactly. No extra text. No explanations."""


def build_user_prompt(obs: dict) -> str:
    return f"""Task: {obs.get('task_description', '')}

Email ID: {obs.get('email_id', '')}
Subject: {obs.get('subject', '')}
From: {obs.get('sender', '')}
Body:
{obs.get('body', '')}

Step {obs.get('step_number', 1)} | Last reward: {obs.get('last_reward', 0.0)}"""


def get_action(obs: dict) -> str:
    try:
        client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": build_user_prompt(obs)},
            ],
            max_tokens=512,
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return ""


def run_task(task_name: str):
    # ── Reset environment ────────────────────────────────────────────────────
    try:
        reset_resp = requests.post(
            f"{ENV_BASE_URL}/reset",
            json={"task": task_name},
            timeout=30,
        )
        reset_resp.raise_for_status()
        obs = reset_resp.json()
    except Exception as e:
        print(f"[START] task={task_name} env=EmailTriageEnv model={MODEL_NAME}")
        print(f"[STEP] step=1 action='' reward=0.00 done=true error={str(e)}")
        print(f"[END] success=false steps=1 rewards=0.00")
        return []

    print(f"[START] task={task_name} env=EmailTriageEnv model={MODEL_NAME}")

    rewards  = []
    step_num = 0
    done     = False

    while not done:
        step_num   += 1
        last_error  = None

        # ── Get action from LLM ──────────────────────────────────────────────
        try:
            action_text = get_action(obs)
        except Exception as e:
            last_error  = str(e)
            action_text = ""

        # ── Send action to environment ───────────────────────────────────────
        try:
            step_resp = requests.post(
                f"{ENV_BASE_URL}/step",
                json={"text": action_text},
                timeout=30,
            )
            step_resp.raise_for_status()
            result = step_resp.json()
        except Exception as e:
            last_error = str(e)
            rewards.append(0.0)
            print(
                f"[STEP] step={step_num} action={repr(action_text)} "
                f"reward=0.00 done=true error={last_error}"
            )
            break

        reward     = float(result.get("reward", 0.0))
        done       = bool(result.get("done", False))
        obs        = result.get("observation", obs)
        step_error = result.get("error") or result.get("info", {}).get("error")
        last_error = step_error if step_error else last_error

        rewards.append(reward)

        action_oneline = action_text.replace("\n", "\\n")

        print(
            f"[STEP] step={step_num} action={repr(action_oneline)} "
            f"reward={reward:.2f} done={str(done).lower()} "
            f"error={last_error if last_error else 'null'}"
        )

    # ── Episode end ──────────────────────────────────────────────────────────
    success     = any(r > 0 for r in rewards)
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)

    print(
        f"[END] success={str(success).lower()} steps={step_num} "
        f"rewards={rewards_str}"
    )
    return rewards


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    all_rewards = {}

    for task in TASKS:
        try:
            task_rewards = run_task(task)
            all_rewards[task] = task_rewards
        except Exception as e:
            print(f"[END] success=false steps=0 rewards=0.00")

    print("\n=== SUMMARY ===")
    for task, rewards in all_rewards.items():
        avg = sum(rewards) / len(rewards) if rewards else 0
        print(f"{task}: avg_reward={avg:.2f} over {len(rewards)} steps")
