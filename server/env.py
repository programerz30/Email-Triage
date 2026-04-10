# env.py - The main Email Triage Environment
# This implements the OpenEnv spec: reset(), step(), state()

from pydantic import BaseModel
from typing import Optional, Any
import random
from data import SAMPLE_EMAILS
from tasks import TASKS, get_grader


# ─────────────────────────────────────────────
# PYDANTIC MODELS (typed inputs/outputs)
# ─────────────────────────────────────────────

class EmailObservation(BaseModel):
    """What the agent SEES at each step."""
    email_id: str
    subject: str
    sender: str
    body: str
    task_description: str
    step_number: int
    last_reward: float
    message: str  # Extra guidance message


class EmailAction(BaseModel):
    """What the agent DOES (sends back as text)."""
    text: str  # The agent's response text


class EmailReward(BaseModel):
    """Reward signal given to the agent."""
    value: float      # Between 0.0 and 1.0
    reason: str       # Human-readable explanation


class StepResult(BaseModel):
    """What step() returns."""
    observation: EmailObservation
    reward: float
    done: bool
    info: dict


class ResetResult(BaseModel):
    """What reset() returns."""
    observation: EmailObservation


# ─────────────────────────────────────────────
# MAIN ENVIRONMENT CLASS
# ─────────────────────────────────────────────

class EmailTriageEnv:
    """
    Email Triage Environment for AI agents.
    
    The agent receives emails and must triage them correctly:
    - Task 1 (Easy): Categorize the email
    - Task 2 (Medium): Categorize + set priority
    - Task 3 (Hard): Categorize + priority + write a reply
    """

    def __init__(self, task_name: str = "task1_categorize"):
        # Validate task name
        if task_name not in TASKS:
            raise ValueError(f"Unknown task: {task_name}. Choose from: {list(TASKS.keys())}")

        self.task_name = task_name
        self.task_config = TASKS[task_name]
        self.grader = get_grader(task_name)

        # State variables
        self.current_step = 0
        self.current_email = None
        self.done = False
        self.cumulative_reward = 0.01
        self.rewards_history = []
        self.attempts = []

    def _pick_email(self):
        """Pick a random email from the task's email list."""
        email_ids = self.task_config["email_ids"]
        email_id = random.choice(email_ids)
        email = next(e for e in SAMPLE_EMAILS if e["id"] == email_id)
        return email

    def _make_observation(self, message: str = "") -> EmailObservation:
        """Build an observation object from current state."""
        return EmailObservation(
            email_id=self.current_email["id"],
            subject=self.current_email["subject"],
            sender=self.current_email["sender"],
            body=self.current_email["body"],
            task_description=self.task_config["description"],
            step_number=self.current_step,
            last_reward=self.rewards_history[-1] if self.rewards_history else 0.01,
            message=message or "Read the email carefully and respond as instructed."
        )

    def reset(self) -> ResetResult:
        """
        Start a fresh episode.
        Called at the beginning of every new task attempt.
        """
        self.current_step = 0
        self.done = False
        self.cumulative_reward = 0.01
        self.rewards_history = []
        self.attempts = []
        self.current_email = self._pick_email()

        obs = self._make_observation(
            message=f"New episode started. Task: {self.task_config['difficulty'].upper()}. "
                    f"You have {self.task_config['max_steps']} steps."
        )
        return ResetResult(observation=obs)

    def step(self, action: EmailAction) -> StepResult:
        """
        Agent takes an action (submits a response).
        Returns new observation, reward, done flag, and info.
        """
        if self.done:
            obs = self._make_observation(message="Episode is already done. Call reset() to start again.")
            return StepResult(observation=obs, reward=0.01, done=True, info={"error": "episode_done"})

        self.current_step += 1
        agent_text = action.text.strip()
        self.attempts.append(agent_text)

        # Grade the action
        try:
            reward = self.grader(agent_text, self.current_email["id"])
            if reward is None or not isinstance(reward, (int, float)):
                reward = 0.01
        except Exception:
            reward = 0.01

        # Apply small penalty for very short/empty responses (penalize lazy behavior)
        if len(agent_text) < 3:
            reward = max(0.01, reward - 0.2)

        # Apply small penalty for taking too many steps without success
        max_steps = self.task_config["max_steps"]
        step_penalty = 0.0
        if self.current_step > max_steps // 2:
            step_penalty = 0.05 * (self.current_step - max_steps // 2)
            reward = max(0.01, reward - step_penalty)

        reward = round(max(0.01, min(reward, 0.99)), 2)
        self.rewards_history.append(reward)
        self.cumulative_reward += reward

        # Decide if episode is done
        # Done if: got perfect score, or ran out of steps
        is_success = reward >= 0.9
        out_of_steps = self.current_step >= max_steps
        self.done = is_success or out_of_steps

        # Build feedback message
        if is_success:
            message = f"Excellent! Score: {reward}. Task completed successfully!"
        elif out_of_steps:
            message = f"Out of steps. Final score: {reward}. Better luck next time."
        elif reward > 0.5:
            message = f"Good attempt! Score: {reward}. Try to improve further."
        elif reward > 0.01:
            message = f"Partial credit: {reward}. Review the task instructions and try again."
        else:
            message = f"Score: 0. Your response was not in the correct format. Please re-read the instructions."

        obs = self._make_observation(message=message)

        return StepResult(
            observation=obs,
            reward=reward,
            done=self.done,
            info={
                "step": self.current_step,
                "cumulative_reward": round(self.cumulative_reward, 2),
                "success": is_success,
                "agent_response": agent_text,
            }
        )

    def state(self) -> dict:
        """Return the current internal state of the environment."""
        return {
            "task_name": self.task_name,
            "difficulty": self.task_config["difficulty"],
            "current_step": self.current_step,
            "max_steps": self.task_config["max_steps"],
            "done": self.done,
            "cumulative_reward": round(self.cumulative_reward, 2),
            "rewards_history": self.rewards_history,
            "current_email_id": self.current_email["id"] if self.current_email else None,
        }
