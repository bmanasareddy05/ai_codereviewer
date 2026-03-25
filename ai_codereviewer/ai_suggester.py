from langchain_groq import ChatGroq
from config import GROQ_API_KEY


class AISuggester:
    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found.")

        self.model = ChatGroq(
            model_name="llama-3.1-8b-instant",
            groq_api_key=GROQ_API_KEY
        )

    def generate_review(self, code: str):
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a strict code reviewer. "
                        "Give:\n"
                        "1. Bugs\n"
                        "2. Complexity\n"
                        "3. Code quality issues\n"
                        "4. Improvements\n"
                        "Be concise and accurate."
                    )
                },
                {
                    "role": "user",
                    "content": code
                }
            ]

            response = self.model.invoke(messages)
            return response.content

        except Exception as e:
            return f"AI Review Failed: {str(e)}"