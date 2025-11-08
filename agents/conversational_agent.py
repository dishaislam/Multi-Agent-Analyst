from mistralai import Mistral
import os
import re
from typing import Dict, Any
from .agent_base import BaseAgent, AgentType

class ConversationalAgent(BaseAgent):
    """Adaptive conversational agent — handles casual and business analytics chat."""

    def __init__(self):
        super().__init__("ConversationalAgent", AgentType.CONVERSATIONAL)
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.client = Mistral(api_key=self.api_key)
        self.conversation_history = []
        self.capabilities = [
            "chat",
            "explain_results",
            "answer_questions",
            "provide_recommendations"
        ]

        self.sales_keywords = {
            "sales", "revenue", "profit", "margin", "income", "customer",
            "marketing", "lead", "conversion", "growth", "forecast"
        }

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route tasks to appropriate conversational sub-function"""
        action = task.get("action")
        params = task.get("parameters", {})

        try:
            if action == "chat":
                return self.chat(params.get("message"), params.get("context"))
            elif action == "explain_results":
                return self.explain_results(params.get("results"))
            elif action == "generate_insights":
                return self.generate_insights(params.get("data"))
            else:
                return {"error": f"Unknown action: {action}", "success": False}
        except Exception as e:
            self.log(f"Error in conversation: {str(e)}", "ERROR")
            return {"error": str(e), "success": False}

    def chat(self, user_message: str, context: str = "") -> Dict[str, Any]:
        """Decide conversational style: casual or sales-analytic"""
        self.log(f"Processing chat: {user_message[:50]}...")

        # Detect sales intent
        if self._is_sales_related(user_message):
            return self._business_chat(user_message, context)
        else:
            return self._casual_chat(user_message)

    def _casual_chat(self, user_message: str) -> Dict[str, Any]:
        """Handle general or unrelated questions"""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a friendly assistant for general conversation. "
                    "Be polite, concise, and natural. Avoid giving business data "
                    "or analysis unless the user specifically asks about sales or data."
                )
            }
        ]

        for msg in self.conversation_history[-5:]:
            messages.append(msg)
        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.complete(
                model="mistral-small-latest",
                messages=messages
            )
            assistant_message = response.choices[0].message.content

            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})

            return {"success": True, "response": assistant_message, "mode": "casual"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _business_chat(self, user_message: str, context: str = "") -> Dict[str, Any]:
        """Use business-analytics persona for sales/revenue questions"""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a smart business analytics assistant. You analyze company sales, "
                    "customer, and revenue data, explain patterns, and give actionable insights. "
                    "Be concise and data-driven. Always format numbers clearly (e.g. $1,200.50, 12.4%)."
                )
            }
        ]

        if context:
            messages.append({"role": "system", "content": f"Context: {context}"})

        for msg in self.conversation_history[-5:]:
            messages.append(msg)
        messages.append({"role": "user", "content": user_message})

        models = ["open-mistral-7b", "mistral-tiny", "mistral-small-latest"]

        for model in models:
            try:
                response = self.client.chat.complete(model=model, messages=messages)
                assistant_message = response.choices[0].message.content

                self.conversation_history.append({"role": "user", "content": user_message})
                self.conversation_history.append({"role": "assistant", "content": assistant_message})

                return {
                    "success": True,
                    "response": assistant_message,
                    "model_used": model,
                    "mode": "sales"
                }

            except Exception as e:
                if "429" in str(e) or "capacity" in str(e).lower():
                    self.log(f"Model {model} at capacity, trying next...", "WARN")
                    continue
                else:
                    return {"success": False, "error": str(e)}

        return {
            "success": False,
            "error": "All models are at capacity. Please try again later.",
            "mode": "sales"
        }

    def explain_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Explain analytical results in natural language"""
        self.log("Explaining results...")
        context = f"Analysis Results:\n{self._format_results(results)}"
        prompt = (
            "Explain the following business analysis results in simple terms. "
            "Focus on key insights, trends, and actionable recommendations."
        )
        return self._business_chat(prompt, context)

    def generate_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from data"""
        self.log("Generating insights...")
        context = f"Business Data:\n{self._format_results(data)}"
        prompt = (
            "Based on this data, provide 3-5 insights and recommendations "
            "for improving sales or business performance."
        )
        return self._business_chat(prompt, context)

    def _format_results(self, results: Dict[str, Any]) -> str:
        formatted = []
        for key, value in results.items():
            if isinstance(value, (int, float)):
                formatted.append(f"{key}: {value:,.2f}")
            elif isinstance(value, dict):
                formatted.append(f"{key}:")
                for k, v in value.items():
                    formatted.append(f"  - {k}: {v}")
            else:
                formatted.append(f"{key}: {value}")
        return "\n".join(formatted)

    def _is_sales_related(self, text: str) -> bool:
        """Check if user input relates to sales, profit, or marketing"""
        words = set(re.findall(r"\b\w+\b", text.lower()))
        return any(w in self.sales_keywords for w in words)

    def clear_history(self):
        self.conversation_history = []
        self.log("Conversation history cleared")
