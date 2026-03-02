from langchain_groq import ChatGroq
from config import GROQ_API_KEY


class AISuggester:
    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found. Check your .env file.")

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
                        "You are an experienced coding mentor. "
                        "Provide a concise technical review including "
                        "time complexity, space complexity, PEP8 naming issues, "
                        "logical errors, and structural improvements."
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