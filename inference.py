"""
inference.py - Baseline Inference Script for Email Triage OpenEnv
"""
import os
import requests
from openai import OpenAI

# ── Environment variables ────────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME",   "meta-llama/Llama-3.3-70B-Instruct")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "https://proz1-email-triage.hf.space")
HF_TOKEN     = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

TASKS = ["task1_categorize", "task2_prioritize", "task3_full_triage"]

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


def clamp(value: float) -> float:
    """Ensure reward is strictly between 0 and 1 (exclusive)."""
    return round(max(0.01, min(float(value), 0.99)), 2)


def build_user_prompt(obs: dict) -> str:
    return (
        f"Task: {obs.get('task_description', '')}\n\n"
        f"Email ID: {obs.get('email_id', '')}\n"
        f"Subject: {obs.get('subject', '')}\n"
        f"From: {obs.get('sender', '')}\n"
        f"Body:\n{obs.get('body', '')}\n\n"
        f"Step {obs.get('step_number', 1)}"
    )


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
    except Exception:
        return "billing"  # fallback to a valid category


def run_task(task_name: str):
    try:
        reset_resp = requests.post(
            f"{ENV_BASE_URL}/reset",
            json={"task": task_name},
            timeout=30,
        )
        reset_resp.raise_for_status()
        obs = reset_resp.json()
        if "observation" in obs:
            obs = obs["observation"]
    except Exception as e:
        print(f"[START] task={task_name} env=EmailTriageEnv model={MODEL_NAME}")
        print(f"[STEP] step=1 action='billing' reward=0.01 done=true error={str(e)}")
        print(f"[END] success=false steps=1 rewards=0.01")
        return [0.01]

    print(f"[START] task={task_name} env=EmailTriageEnv model={MODEL_NAME}")

    rewards  = []
    step_num = 0
    done     = False

    while not done:
        step_num  += 1
        last_error = None

        try:
            action_text = get_action(obs)
        except Exception as e:
            last_error  = str(e)
            action_text = "billing"

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
            reward = 0.01
            rewards.append(reward)
            print(
                f"[STEP] step={step_num} action={repr(action_text)} "
                f"reward={reward:.2f} done=true error={last_error}"
            )
            break

        # ── Clamp reward strictly between 0 and 1 ───────────────────────────
        reward     = clamp(result.get("reward", 0.01))
        done       = bool(result.get("done", False))

        # Handle both flat and nested observation formats
        new_obs = result.get("observation", obs)
        if isinstance(new_obs, dict) and "observation" in new_obs:
            new_obs = new_obs["observation"]
        obs = new_obs

        step_error = result.get("error") or (result.get("info") or {}).get("error")
        last_error = step_error if step_error else last_error

        rewards.append(reward)
        action_oneline = action_text.replace("\n", "\\n")

        print(
            f"[STEP] step={step_num} action={repr(action_oneline)} "
            f"reward={reward:.2f} done={str(done).lower()} "
            f"error={last_error if last_error else 'null'}"
        )

        # Safety cap — never loop more than max_steps
        if step_num >= 10:
            done = True

    success     = any(r > 0.01 for r in rewards)
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)

    print(
        f"[END] success={str(success).lower()} steps={step_num} "
        f"rewards={rewards_str}"
    )
    return rewards


if __name__ == "__main__":
    all_rewards = {}
    for task in TASKS:
        try:
            task_rewards = run_task(task)
            all_rewards[task] = task_rewards
        except Exception as e:
            print(f"[END] success=false steps=0 rewards=0.01")

    print("\n=== SUMMARY ===")
    for task, rewards in all_rewards.items():
        avg = sum(rewards) / len(rewards) if rewards else 0
        print(f"{task}: avg_reward={avg:.2f} over {len(rewards)} steps")
