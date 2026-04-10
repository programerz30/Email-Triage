# tasks.py - Defines the 3 tasks and how they are graded
# Task 1 (Easy): Categorize the email
# Task 2 (Medium): Categorize + set priority
# Task 3 (Hard): Categorize + priority + write a reply

from data import SAMPLE_EMAILS, VALID_CATEGORIES

# ─────────────────────────────────────────────
# TASK DEFINITIONS
# ─────────────────────────────────────────────

TASKS = {
    "task1_categorize": {
        "name": "task1_categorize",
        "description": (
            "EASY TASK: Read the email and classify it into one of these categories: "
            "critical, billing, technical_support, feature_request, business, spam. "
            "Respond with ONLY the category name, nothing else."
        ),
        "difficulty": "easy",
        "max_steps": 3,
        "email_ids": ["email_001", "email_002", "email_003", "email_004"],
    },
    "task2_prioritize": {
        "name": "task2_prioritize",
        "description": (
            "MEDIUM TASK: Read the email and respond with BOTH the category AND priority. "
            "Category must be one of: critical, billing, technical_support, feature_request, business, spam. "
            "Priority must be a number from 1 (most urgent) to 5 (least urgent). "
            "Respond in this exact format: category=<category> priority=<number>"
        ),
        "difficulty": "medium",
        "max_steps": 5,
        "email_ids": ["email_001", "email_002", "email_005", "email_006", "email_008"],
    },
    "task3_full_triage": {
        "name": "task3_full_triage",
        "description": (
            "HARD TASK: Perform complete email triage. You must: "
            "1) Classify the email category, "
            "2) Assign a priority (1-5), "
            "3) Write a professional reply. "
            "Respond in this exact format:\n"
            "category=<category>\npriority=<number>\nreply=<your reply text>"
        ),
        "difficulty": "hard",
        "max_steps": 8,
        "email_ids": ["email_001", "email_002", "email_004", "email_006", "email_007", "email_008"],
    },
}


# ─────────────────────────────────────────────
# GRADER FUNCTIONS
# ─────────────────────────────────────────────

def grade_task1(action_text: str, email_id: str) -> float:
    """
    Easy grader: Did the agent correctly categorize the email?
    Returns 0.99 for correct, 0.01 for wrong, 0.3 for valid but wrong category.
    """
    email_data = next((e for e in SAMPLE_EMAILS if e["id"] == email_id), None)
    if not email_data:
        return 0.01  # FIX: was 0.0, must be strictly > 0

    action_lower = action_text.strip().lower()
    correct = email_data["correct_category"]

    # Exact match = full score
    if correct in action_lower:
        return 0.99

    # Agent gave a valid category but wrong one = partial credit
    for cat in VALID_CATEGORIES:
        if cat in action_lower:
            return 0.3

    # No valid category found
    return 0.01


def grade_task2(action_text: str, email_id: str) -> float:
    """
    Medium grader: Did the agent correctly categorize AND prioritize?
    Returns score from 0.0 to 1.0 based on partial credit.
    """
    email_data = next((e for e in SAMPLE_EMAILS if e["id"] == email_id), None)
    if not email_data:
        return 0.01

    score = 0.0  # FIX: was missing
    action_lower = action_text.strip().lower()  # FIX: was missing
    correct_cat = email_data["correct_category"]

    if correct_cat in action_lower:
        score += 0.5
    else:
        # Valid but wrong category = small credit
        for cat in VALID_CATEGORIES:
            if cat in action_lower:
                score += 0.1
                break

    # Check priority (worth 0.5)
    correct_priority = email_data["correct_priority"]
    try:
        import re
        priority_match = re.search(r'priority[=:\s]+(\d)', action_lower)
        if priority_match:
            given_priority = int(priority_match.group(1))
            if given_priority == correct_priority:
                score += 0.5  # Exact match
            elif abs(given_priority - correct_priority) == 1:
                score += 0.3  # Off by one
            elif abs(given_priority - correct_priority) == 2:
                score += 0.1  # Off by two
    except Exception:
        pass

    return round(max(0.01, min(score, 0.99)), 2)


def grade_task3(action_text: str, email_id: str) -> float:
    """
    Hard grader: Category + Priority + Quality Reply.
    Returns score from 0.0 to 1.0.
    """
    email_data = next((e for e in SAMPLE_EMAILS if e["id"] == email_id), None)
    if not email_data:
        return 0.01

    score = 0.0  # FIX: was missing
    action_lower = action_text.strip().lower()  # FIX: was missing
    correct_cat = email_data["correct_category"]

    if correct_cat in action_lower:
        score += 0.3
    else:
        for cat in VALID_CATEGORIES:
            if cat in action_lower:
                score += 0.1
                break

    # Priority check (worth 0.3)
    import re
    correct_priority = email_data["correct_priority"]
    priority_match = re.search(r'priority[=:\s]+(\d)', action_lower)
    if priority_match:
        given_priority = int(priority_match.group(1))
        if given_priority == correct_priority:
            score += 0.3
        elif abs(given_priority - correct_priority) == 1:
            score += 0.2
        elif abs(given_priority - correct_priority) == 2:
            score += 0.1

    # Reply quality check (worth 0.4)
    reply_match = re.search(r'reply[=:\s]+(.+)', action_lower, re.DOTALL)
    if reply_match:
        reply_text = reply_match.group(1)
        if len(reply_text.split()) >= 10:  # Reply has at least 10 words
            score += 0.1

            # Check for correct keywords
            keywords = email_data.get("correct_reply_keywords", [])
            matched_keywords = sum(1 for kw in keywords if kw in reply_text)
            keyword_score = (matched_keywords / max(len(keywords), 1)) * 0.3
            score += keyword_score

    return round(max(0.01, min(score, 0.99)), 2)


def get_grader(task_name: str):
    """Returns the correct grader function for a task."""
    graders = {
        "task1_categorize": grade_task1,
        "task2_prioritize": grade_task2,
        "task3_full_triage": grade_task3,
    }
    return graders.get(task_name)
