# data.py - Sample emails for the environment
# These are fake emails used to train/test the AI agent

SAMPLE_EMAILS = [
    {
        "id": "email_001",
        "subject": "URGENT: Server is down in production!",
        "sender": "alerts@company.com",
        "body": "Our main production server has been down for 10 minutes. Customers cannot access the website. We are losing $5000 per minute. Please fix immediately.",
        "correct_category": "critical",
        "correct_priority": 1,
        "correct_reply_keywords": ["acknowledge", "investigating", "team", "fix", "urgent"]
    },
    {
        "id": "email_002",
        "subject": "Question about my invoice",
        "sender": "customer123@gmail.com",
        "body": "Hi, I received my invoice for last month but I think there is a mistake. I was charged $200 but my plan is only $150 per month. Can you please check this?",
        "correct_category": "billing",
        "correct_priority": 3,
        "correct_reply_keywords": ["apologize", "check", "invoice", "resolve", "refund"]
    },
    {
        "id": "email_003",
        "subject": "New feature request: Dark mode",
        "sender": "user456@gmail.com",
        "body": "Hello, I love your product! I would really like to see a dark mode option added. Many users have been requesting this. It would make using the app at night much easier.",
        "correct_category": "feature_request",
        "correct_priority": 5,
        "correct_reply_keywords": ["thank", "feedback", "consider", "future", "team"]
    },
    {
        "id": "email_004",
        "subject": "Cannot login to my account",
        "sender": "blocked_user@yahoo.com",
        "body": "I have been trying to login for the past hour but keep getting an error message saying my password is incorrect. I tried resetting my password but the reset email never arrived.",
        "correct_category": "technical_support",
        "correct_priority": 2,
        "correct_reply_keywords": ["help", "reset", "password", "account", "support"]
    },
    {
        "id": "email_005",
        "subject": "Partnership opportunity",
        "sender": "business@partner.com",
        "body": "Dear team, we are a marketing company with 500k followers. We would like to explore a partnership or sponsorship opportunity with your brand. Please let us know if you are interested.",
        "correct_category": "business",
        "correct_priority": 4,
        "correct_reply_keywords": ["interest", "team", "discuss", "opportunity", "contact"]
    },
    {
        "id": "email_006",
        "subject": "SECURITY BREACH - Immediate action required",
        "sender": "security@company.com",
        "body": "We have detected unauthorized access to our database. Customer data may have been compromised. We need to notify affected users immediately and shut down affected systems.",
        "correct_category": "critical",
        "correct_priority": 1,
        "correct_reply_keywords": ["security", "team", "immediate", "action", "breach"]
    },
    {
        "id": "email_007",
        "subject": "How do I export my data?",
        "sender": "regular_user@gmail.com",
        "body": "Hi support team, I would like to export all my data from your platform. I checked the documentation but could not find clear instructions. Can you help me with step by step instructions?",
        "correct_category": "technical_support",
        "correct_priority": 4,
        "correct_reply_keywords": ["export", "steps", "help", "data", "instructions"]
    },
    {
        "id": "email_008",
        "subject": "Refund request for unused subscription",
        "sender": "unhappy@customer.com",
        "body": "I accidentally subscribed to the annual plan instead of monthly. I have only used the service for 2 days and would like a full refund. I did not mean to commit to the annual plan.",
        "correct_category": "billing",
        "correct_priority": 2,
        "correct_reply_keywords": ["refund", "process", "apologize", "policy", "annual"]
    }
]

# Valid categories the agent can assign
VALID_CATEGORIES = ["critical", "billing", "technical_support", "feature_request", "business", "spam"]

# Priority levels: 1 = most urgent, 5 = least urgent
PRIORITY_LEVELS = [1, 2, 3, 4, 5]
