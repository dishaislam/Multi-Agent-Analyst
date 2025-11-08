from typing import Dict, Any, List
from .agent_base import BaseAgent, AgentType
from .data_agent import DataAgent
from .analytics_agent import AnalyticsAgent
from .conversational_agent import ConversationalAgent
import re

class CoordinatorAgent(BaseAgent):
    """Coordinator that orchestrates between all agents"""
    
    def __init__(self, data_path: str = None):
        super().__init__("Coordinator", AgentType.COORDINATOR)
        
        # Initialize all agents
        self.data_agent = DataAgent(data_path)
        self.analytics_agent = AnalyticsAgent()
        self.conversational_agent = ConversationalAgent()
        
        self.agents = {
            "data": self.data_agent,
            "analytics": self.analytics_agent,
            "conversational": self.conversational_agent
        }
        
        self.data_loaded = False
        self.capabilities = [
            "route_request",
            "coordinate_analysis",
            "handle_conversation"
        ]
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process and route tasks to appropriate agents"""
        user_input = task.get("user_input", "")
        
        self.log(f"Processing request: {user_input[:50]}...")
        
        # Parse user intent
        intent = self._parse_intent(user_input)
        
        # Route to appropriate workflow
        if intent["type"] == "data_query":
            return self._handle_data_query(intent, user_input)
        elif intent["type"] == "analytics":
            return self._handle_analytics_request(intent, user_input)
        elif intent["type"] == "conversation":
            return self._handle_conversation(user_input)
        elif intent["type"] == "initialization":
            return self._handle_initialization(intent)
        else:
            return self._handle_conversation(user_input)
    
    def _parse_intent(self, user_input: str) -> Dict[str, Any]:
        """Parse user intent from input"""
        user_lower = user_input.lower()
        
        # Data loading
        if any(keyword in user_lower for keyword in ["load data", "prepare data", "initialize"]):
            return {"type": "initialization"}
        
        # Profit margin queries
        if "profit margin" in user_lower:
            year_match = re.search(r'\b(20\d{2}|201\d|202\d)\b', user_input)
            year = int(year_match.group()) if year_match else None
            return {
                "type": "data_query",
                "query_type": "profit_margin_by_year",
                "parameters": {"year": year}
            }
        
        # Revenue trends
        if any(keyword in user_lower for keyword in ["revenue trend", "sales trend", "growth"]):
            return {
                "type": "data_query",
                "query_type": "revenue_trends"
            }
        
        # Top products
        if any(keyword in user_lower for keyword in ["top product", "best seller", "highest revenue"]):
            year_match = re.search(r'\b(20\d{2})\b', user_input)
            year = int(year_match.group()) if year_match else None
            return {
                "type": "data_query",
                "query_type": "top_products",
                "parameters": {"year": year}
            }
        
        # Analytics requests
        if any(keyword in user_lower for keyword in ["analyze", "analysis", "report", "visualize", "chart"]):
            return {"type": "analytics"}
        
        # General conversation
        return {"type": "conversation"}
    
    def _handle_data_query(self, intent: Dict, user_input: str) -> Dict[str, Any]:
        """Handle data queries"""
        if not self.data_loaded:
            return {
                "success": False,
                "response": "⚠️ Data not loaded. Please load data first by saying 'load data' or 'initialize'."
            }
        
        # Query data agent
        query_result = self.data_agent.query_data({
            "query_type": intent["query_type"],
            **intent.get("parameters", {})
        })
        
        if not query_result.get("success"):
            # Handle error with conversational agent
            error_context = f"Query failed: {query_result.get('error', 'Unknown error')}"
            return self.conversational_agent.chat(user_input, error_context)
        
        # Explain results with conversational agent
        explanation = self.conversational_agent.explain_results(query_result)
        
        return {
            "success": True,
            "data": query_result,
            "response": explanation.get("response"),
            "workflow": ["data_agent", "conversational_agent"]
        }
    
    def _handle_analytics_request(self, intent: Dict, user_input: str) -> Dict[str, Any]:
        """Handle analytics requests"""
        if not self.data_loaded:
            return {
                "success": False,
                "response": "⚠️ Data not loaded. Please load data first."
            }
        
        # Run full analysis
        analysis_result = self.analytics_agent.process({
            "action": "full_analysis",
            "parameters": {"dataframe": self.data_agent.df}
        })
        
        if not analysis_result.get("success"):
            return {
                "success": False,
                "response": f"Analysis failed: {analysis_result.get('error')}"
            }
        
        # Generate insights
        insights = self.conversational_agent.generate_insights(
            analysis_result.get("results", {})
        )
        
        return {
            "success": True,
            "analysis": analysis_result,
            "response": insights.get("response"),
            "workflow": ["data_agent", "analytics_agent", "conversational_agent"]
        }
    
    def _handle_conversation(self, user_input: str) -> Dict[str, Any]:
        """Handle general conversation"""
        # Provide context about loaded data if available
        context = ""
        if self.data_loaded:
            summary = self.data_agent.get_data_summary({})
            context = f"Available data: {summary.get('years_available')} | Total revenue: ${summary.get('total_revenue', 0):,.2f}"
        
        chat_result = self.conversational_agent.chat(user_input, context)
        
        return {
            "success": chat_result.get("success"),
            "response": chat_result.get("response"),
            "workflow": ["conversational_agent"]
        }
    
    def _handle_initialization(self, intent: Dict) -> Dict[str, Any]:
        """Handle data initialization"""
        self.log("Initializing data...")
        
        # Load and prepare data
        load_result = self.data_agent.process({
            "action": "load_and_prepare",
            "parameters": {"file_path": self.data_agent.data_path}
        })
        
        if load_result.get("success"):
            self.data_loaded = True
            response = (
                f"✅ Data loaded successfully!\n"
                f"📊 {load_result['rows']:,} records from "
                f"{load_result['date_range']['start']} to {load_result['date_range']['end']}\n"
                f"You can now ask questions like:\n"
                f"- 'What was the profit margin in 2015?'\n"
                f"- 'Show me revenue trends'\n"
                f"- 'Analyze top products for 2016'"
            )
        else:
            response = f"❌ Failed to load data: {load_result.get('error')}"
        
        return {
            "success": load_result.get("success"),
            "response": response,
            "data_info": load_result
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "data_loaded": self.data_loaded,
            "agents": {
                name: {
                    "status": agent.status,
                    "capabilities": agent.get_capabilities()
                }
                for name, agent in self.agents.items()
            }
        }