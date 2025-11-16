"""
Chat Interface for Master Orchestrator

Provides intelligent chat-based interaction with the Master Orchestrator.
Supports natural language understanding, context management, and
conversational workflows.

Author: AI Research Team
Date: November 2025
Version: 1.0.0
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import get_logger
from utils.anthropic_client import AnthropicIntelligence


@dataclass
class ChatMessage:
    """Represents a chat message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatSession:
    """Represents a chat session with conversation history."""
    session_id: str
    messages: List[ChatMessage] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_activity: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ChatInterface:
    """
    Intelligent Chat Interface for Master Orchestrator.

    Features:
    - Natural language understanding
    - Context-aware conversations
    - Multi-turn dialogue support
    - Intent recognition and routing
    - Helpful suggestions and guidance
    """

    def __init__(self, ai: AnthropicIntelligence):
        """
        Initialize chat interface.

        Args:
            ai: Anthropic intelligence client
        """
        self.ai = ai
        self.logger = get_logger(__name__)
        self.sessions: Dict[str, ChatSession] = {}
        self.current_session: Optional[ChatSession] = None

    def start_session(self, session_id: Optional[str] = None) -> ChatSession:
        """
        Start a new chat session.

        Args:
            session_id: Optional session ID (generated if not provided)

        Returns:
            ChatSession instance
        """
        if session_id is None:
            session_id = f"session_{datetime.utcnow().timestamp()}"

        session = ChatSession(session_id=session_id)
        self.sessions[session_id] = session
        self.current_session = session

        self.logger.info("Started chat session", session_id=session_id)

        # Add welcome message
        welcome = self._generate_welcome_message()
        session.messages.append(ChatMessage(role="assistant", content=welcome))

        return session

    def process_message(
        self,
        user_message: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate response.

        Args:
            user_message: User's message
            session_id: Session ID (uses current if not specified)

        Returns:
            Response dict with action, message, and data
        """
        # Get or create session
        if session_id:
            session = self.sessions.get(session_id)
            if not session:
                session = self.start_session(session_id)
        else:
            if not self.current_session:
                self.start_session()
            session = self.current_session

        # Add user message to history
        session.messages.append(ChatMessage(role="user", content=user_message))
        session.last_activity = datetime.utcnow().isoformat()

        self.logger.info(
            "Processing chat message",
            session_id=session.session_id,
            message_preview=user_message[:100]
        )

        # Understand intent
        intent = self._extract_intent(user_message, session)

        # Generate response
        response = self._generate_response(intent, session)

        # Add assistant message to history
        session.messages.append(
            ChatMessage(
                role="assistant",
                content=response.get("message", ""),
                metadata={"intent": intent}
            )
        )

        return response

    def _extract_intent(
        self,
        message: str,
        session: ChatSession
    ) -> Dict[str, Any]:
        """
        Extract user intent from message using AI.

        Args:
            message: User message
            session: Chat session for context

        Returns:
            Intent dict with action and parameters
        """
        system_prompt = """You are an intent classifier for a viral YouTube content generation system.

Available actions:
- generate_video: User wants to generate a complete viral video
- research_topic: User wants research only
- analyze_video: User wants to analyze a YouTube video
- viral_strategy: User wants viral strategy for existing research
- generate_script: User wants script generation
- help: User needs help or guidance
- status: User wants system status
- explain: User wants explanation of system/features
- modify_request: User wants to modify previous request

Extract from the message:
- action: one of the above
- topic: content topic (if mentioned)
- video_url: YouTube URL (if mentioned)
- target_audience: target audience (if mentioned)
- duration: video duration in minutes (if mentioned)
- style: video style (if mentioned)
- additional_params: any other parameters

Consider conversation context when available.

Return JSON only with: action, confidence (0-1), and extracted parameters."""

        # Include recent context
        context_messages = session.messages[-5:] if len(session.messages) > 0 else []
        context_text = "\n".join([
            f"{msg.role}: {msg.content}" for msg in context_messages
        ])

        prompt = f"""
Recent conversation context:
{context_text}

Current user message: {message}

Extract intent and parameters:
"""

        try:
            response = self.ai.generate(prompt, system_prompt=system_prompt, temperature=0.3)
            intent = json.loads(response.content)

            # Ensure required fields
            if "action" not in intent:
                intent["action"] = "help"
            if "confidence" not in intent:
                intent["confidence"] = 0.5

            self.logger.info(
                "Extracted intent",
                action=intent["action"],
                confidence=intent["confidence"]
            )

            return intent

        except Exception as e:
            self.logger.error(f"Intent extraction failed: {str(e)}")
            return {
                "action": "help",
                "confidence": 0.3,
                "error": str(e)
            }

    def _generate_response(
        self,
        intent: Dict[str, Any],
        session: ChatSession
    ) -> Dict[str, Any]:
        """
        Generate response based on intent.

        Args:
            intent: Extracted intent
            session: Chat session

        Returns:
            Response dict
        """
        action = intent.get("action", "help")

        # Route to appropriate handler
        if action == "generate_video":
            return self._handle_generate_video(intent, session)
        elif action == "research_topic":
            return self._handle_research(intent, session)
        elif action == "analyze_video":
            return self._handle_analyze_video(intent, session)
        elif action == "viral_strategy":
            return self._handle_viral_strategy(intent, session)
        elif action == "generate_script":
            return self._handle_generate_script(intent, session)
        elif action == "status":
            return self._handle_status(intent, session)
        elif action == "explain":
            return self._handle_explain(intent, session)
        elif action == "help":
            return self._handle_help(intent, session)
        else:
            return self._handle_unknown(intent, session)

    def _handle_generate_video(
        self,
        intent: Dict[str, Any],
        session: ChatSession
    ) -> Dict[str, Any]:
        """Handle video generation request."""
        topic = intent.get("topic")

        if not topic:
            return {
                "action": "request_info",
                "message": "I'd love to help you create a viral video! What topic would you like the video to be about?",
                "required": ["topic"],
                "optional": ["target_audience", "duration", "style"]
            }

        return {
            "action": "execute_workflow",
            "workflow_type": "full_pipeline",
            "message": f"Great! I'll create a complete viral video package about '{topic}'. This includes:\n\n"
                      f"1. 🔬 World-class research from top academic sources\n"
                      f"2. 🎯 Viral strategy with psychology triggers and hooks\n"
                      f"3. ✍️ Production-ready script with visual scenes\n\n"
                      f"This will take about 10-15 minutes. Starting now...",
            "parameters": {
                "topic": topic,
                "target_audience": intent.get("target_audience", "general audience"),
                "duration_minutes": intent.get("duration", 15),
                "style": intent.get("style", "documentary")
            }
        }

    def _handle_research(
        self,
        intent: Dict[str, Any],
        session: ChatSession
    ) -> Dict[str, Any]:
        """Handle research-only request."""
        topic = intent.get("topic")

        if not topic:
            return {
                "action": "request_info",
                "message": "What topic would you like me to research?",
                "required": ["topic"]
            }

        return {
            "action": "execute_workflow",
            "workflow_type": "research_only",
            "message": f"I'll conduct comprehensive research on '{topic}' using multiple academic databases including JSTOR, Semantic Scholar, and arXiv. Starting now...",
            "parameters": {
                "topic": topic
            }
        }

    def _handle_analyze_video(
        self,
        intent: Dict[str, Any],
        session: ChatSession
    ) -> Dict[str, Any]:
        """Handle YouTube video analysis request."""
        video_url = intent.get("video_url")

        if not video_url:
            return {
                "action": "request_info",
                "message": "Please provide the YouTube video URL you'd like me to analyze.",
                "required": ["video_url"]
            }

        return {
            "action": "execute_workflow",
            "workflow_type": "youtube_analysis",
            "message": f"I'll analyze this YouTube video to identify viral patterns, psychology triggers, and successful strategies. Starting analysis...",
            "parameters": {
                "video_url": video_url,
                "store_in_library": intent.get("store_in_library", True)
            }
        }

    def _handle_viral_strategy(
        self,
        intent: Dict[str, Any],
        session: ChatSession
    ) -> Dict[str, Any]:
        """Handle viral strategy request."""
        return {
            "action": "execute_workflow",
            "workflow_type": "viral_analysis",
            "message": "I'll create a viral strategy with hooks, psychology triggers, and engagement optimization.",
            "parameters": intent.get("additional_params", {})
        }

    def _handle_generate_script(
        self,
        intent: Dict[str, Any],
        session: ChatSession
    ) -> Dict[str, Any]:
        """Handle script generation request."""
        return {
            "action": "execute_workflow",
            "workflow_type": "content_generation",
            "message": "I'll generate a complete production-ready script with visual scenes and production notes.",
            "parameters": intent.get("additional_params", {})
        }

    def _handle_status(
        self,
        intent: Dict[str, Any],
        session: ChatSession
    ) -> Dict[str, Any]:
        """Handle status request."""
        return {
            "action": "get_status",
            "message": "Let me get the current system status for you..."
        }

    def _handle_explain(
        self,
        intent: Dict[str, Any],
        session: ChatSession
    ) -> Dict[str, Any]:
        """Handle explanation request."""
        explanation = """
This is a world-class viral YouTube content generation system. Here's how it works:

**🏗️ System Architecture:**
- **Master Orchestrator**: Coordinates all components (that's me!)
- **Research Gatekeeper**: Conducts academic research using multiple databases
- **Viral Analyser Gatekeeper**: Analyzes successful videos and creates viral strategies
- **Content Synthesis Gatekeeper**: Generates production-ready scripts
- **Vector Database**: Stores and learns from successful patterns

**🎯 What I Can Do:**
1. Generate complete viral video packages (research + strategy + script)
2. Conduct world-class academic research
3. Analyze YouTube videos for viral patterns
4. Create viral strategies with psychology triggers
5. Generate production-ready scripts with visual scenes

**📊 Quality Standards:**
- Research: PhD-level academic rigor (8.0+/10)
- Viral Potential: 9.0+/10 predicted performance
- Script Quality: 9.0+/10 production readiness

All outputs go through multiple validation iterations to ensure excellence!
"""
        return {
            "action": "explain",
            "message": explanation
        }

    def _handle_help(
        self,
        intent: Dict[str, Any],
        session: ChatSession
    ) -> Dict[str, Any]:
        """Handle help request."""
        help_message = """
**Master Orchestrator - How to Use:**

**Generate Complete Video:**
- "Create a viral video about quantum computing"
- "Generate a 20-minute documentary on AI history"

**Research Only:**
- "Research the latest breakthroughs in biotechnology"
- "Give me academic insights on climate change"

**Analyze YouTube Video:**
- "Analyze https://youtube.com/watch?v=..."
- "What makes this video viral: [URL]"

**Get Help:**
- "How does this work?"
- "What can you do?"
- "Show system status"

**💡 Tips:**
- Be specific about your topic
- Mention target audience if you have one in mind
- Specify video duration (default is 15 minutes)
- I'll ask for clarification if I need more info!

What would you like to do?
"""
        return {
            "action": "help",
            "message": help_message
        }

    def _handle_unknown(
        self,
        intent: Dict[str, Any],
        session: ChatSession
    ) -> Dict[str, Any]:
        """Handle unknown intent."""
        return {
            "action": "clarify",
            "message": "I'm not quite sure what you'd like me to do. Here are some things I can help with:\n\n"
                      "• Generate viral YouTube videos\n"
                      "• Research topics using academic sources\n"
                      "• Analyze successful YouTube videos\n"
                      "• Create viral strategies\n\n"
                      "What would you like to do?",
            "confidence": intent.get("confidence", 0)
        }

    def _generate_welcome_message(self) -> str:
        """Generate welcome message for new session."""
        return """
👋 Welcome to the Master Orchestrator!

I'm your AI assistant for creating world-class, viral-optimized YouTube content.

**I can help you:**
✅ Generate complete viral video packages (research + strategy + script)
✅ Conduct PhD-level academic research
✅ Analyze successful YouTube videos
✅ Create viral hooks and psychology triggers
✅ Generate production-ready scripts

**Try saying:**
- "Create a viral video about [topic]"
- "Research [topic]"
- "Analyze https://youtube.com/watch?v=..."

What would you like to create today?
"""

    def get_conversation_history(
        self,
        session_id: Optional[str] = None,
        limit: int = 10
    ) -> List[ChatMessage]:
        """
        Get conversation history.

        Args:
            session_id: Session ID (uses current if not specified)
            limit: Maximum messages to return

        Returns:
            List of chat messages
        """
        if session_id:
            session = self.sessions.get(session_id)
        else:
            session = self.current_session

        if not session:
            return []

        return session.messages[-limit:]

    def clear_session(self, session_id: Optional[str] = None):
        """Clear a chat session."""
        if session_id:
            if session_id in self.sessions:
                del self.sessions[session_id]
                self.logger.info("Cleared session", session_id=session_id)
        else:
            if self.current_session:
                session_id = self.current_session.session_id
                if session_id in self.sessions:
                    del self.sessions[session_id]
                self.current_session = None
                self.logger.info("Cleared current session")


if __name__ == "__main__":
    # Example usage
    import os
    from utils.anthropic_client import AnthropicIntelligence

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("Set ANTHROPIC_API_KEY environment variable")
        exit(1)

    ai = AnthropicIntelligence(api_key=api_key)
    chat = ChatInterface(ai)

    # Start session
    session = chat.start_session()
    print(session.messages[0].content)

    # Example interactions
    examples = [
        "Create a viral video about artificial consciousness",
        "What can you do?",
        "Analyze https://youtube.com/watch?v=dQw4w9WgXcQ"
    ]

    for example in examples:
        print(f"\n{'='*60}")
        print(f"User: {example}")
        response = chat.process_message(example)
        print(f"\nAssistant: {response['message']}")
        print(f"Action: {response['action']}")
