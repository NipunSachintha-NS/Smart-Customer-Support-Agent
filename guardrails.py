import re
from typing import Tuple

# 1. Regex Patterns for PII (Personal Identifiable Information)
CREDIT_CARD_PATTERN = r"\b(?:\d[ -]*?){13,16}\b"
EMAIL_PATTERN = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PASSWORD_PATTERN = r"(?i)(?:password\s*[:=]\s*\S+)"

# 2. Known Jailbreak / Prompt Injection Signatures
PROMPT_INJECTION_KEYWORDS = [
    "ignore previous instructions",
    "ignore all previous commands",
    "system prompt",
    "developer mode",
    "bypass safety",
    "act as dan",
    "reveal your prompt",
    "forget your instructions"
]

# 3. Restricted Competitor Keywords (Example Policy)
RESTRICTED_COMPETITORS = ["amazon", "bestbuy", "walmart", "ebay", "aliexpress"]

class SafetyGuardrail:
    @staticmethod
    def sanitize_input(user_text: str) -> Tuple[bool, str, str]:
        """
        Validates and sanitizes user input before sending to LLM.
        Returns: (is_safe: bool, sanitized_text: str, message: str)
        """
        lowered_text = user_text.lower()

        # Check for Prompt Injection / Jailbreaks
        for pattern in PROMPT_INJECTION_KEYWORDS:
            if pattern in lowered_text:
                return (
                    False,
                    "",
                    "⚠️ Security Alert: Input violates our AI safety policy (Potential Prompt Injection / Jailbreak detected)."
                )

        # Sanitize PII (Mask Credit Cards, Passwords, Emails)
        sanitized = re.sub(CREDIT_CARD_PATTERN, "[REDACTED_CARD_NUMBER]", user_text)
        sanitized = re.sub(PASSWORD_PATTERN, "password: [REDACTED_PASSWORD]", sanitized)
        sanitized = re.sub(EMAIL_PATTERN, "[REDACTED_EMAIL]", sanitized)

        return True, sanitized, ""

    @staticmethod
    def sanitize_output(agent_response: str) -> str:
        """
        Inspects LLM output before delivering to client.
        """
        lowered = agent_response.lower()
        
        # Prevent mentioning competitors favorably
        for comp in RESTRICTED_COMPETITORS:
            if comp in lowered:
                return "TechGear Support is dedicated exclusively to TechGear products and services. For competitor inquiries, please contact them directly."

        # Extra safety check against leaking sensitive system keys
        if "sk-" in agent_response or "api_key" in lowered:
            return "TechGear Support: Action blocked due to sensitive data leak protection."

        return agent_response