"""
Chat Interface for Viral Analysis System
Provides interactive user experience with natural language processing
"""

import sys
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

sys.path.append('/home/user/fullagentyoutubedriffther/src')

from viral_analysis.viral_analyser_gatekeeper import ViralAnalyserGatekeeper
from integrations.anthropic_integration import AnthropicIntegration
from config.config_manager import get_config_manager


class ChatInterface:
    """
    Interactive chat interface for viral analysis system
    Uses natural language to interact with the gatekeeper
    """

    def __init__(self):
        self.config = get_config_manager()
        self.gatekeeper = ViralAnalyserGatekeeper(self.config)
        self.ai = AnthropicIntegration(self.config.get_api_key('anthropic'))
        self.conversation_history = []

    def start(self):
        """Start interactive chat session"""
        print("\n" + "="*80)
        print("🎯 VIRAL ANALYSIS SYSTEM - Chat Interface")
        print("="*80)
        print("\nWelcome to the Viral Analysis System!")
        print("I can help you analyze and optimize content for viral potential.\n")
        print("What I can do:")
        print("  • Analyze topics for viral potential")
        print("  • Generate viral hooks and strategies")
        print("  • Analyze YouTube videos")
        print("  • Provide optimization recommendations")
        print("  • Score content for virality\n")
        print("Commands:")
        print("  'help' - Show available commands")
        print("  'stats' - Show system statistics")
        print("  'exit' - Exit the system\n")
        print("="*80 + "\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\n👋 Thanks for using Viral Analysis System! Goodbye!\n")
                    break

                if user_input.lower() == 'help':
                    self._show_help()
                    continue

                if user_input.lower() == 'stats':
                    self._show_stats()
                    continue

                # Process user request
                response = self.process_message(user_input)
                print(f"\nAssistant: {response}\n")

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")

    def process_message(self, message: str) -> str:
        """
        Process user message and generate response

        Args:
            message: User's message

        Returns:
            System response
        """
        # Add to conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })

        # Determine intent
        intent = self._classify_intent(message)

        response = ""

        if intent == 'analyze_topic':
            response = self._handle_topic_analysis(message)

        elif intent == 'analyze_video':
            response = self._handle_video_analysis(message)

        elif intent == 'generate_hooks':
            response = self._handle_hook_generation(message)

        elif intent == 'score_content':
            response = self._handle_content_scoring(message)

        elif intent == 'get_recommendations':
            response = self._handle_recommendations(message)

        else:
            response = self._handle_general_query(message)

        # Add response to history
        self.conversation_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat()
        })

        return response

    def _classify_intent(self, message: str) -> str:
        """Classify user intent from message"""
        message_lower = message.lower()

        if any(word in message_lower for word in ['analyze topic', 'analyze', 'viral analysis', 'check topic']):
            return 'analyze_topic'

        if any(word in message_lower for word in ['youtube', 'video url', 'analyze video', 'check video']):
            return 'analyze_video'

        if any(word in message_lower for word in ['generate hook', 'create hook', 'hooks for', 'hook ideas']):
            return 'generate_hooks'

        if any(word in message_lower for word in ['score', 'rate', 'how viral', 'viral potential']):
            return 'score_content'

        if any(word in message_lower for word in ['recommend', 'suggestion', 'improve', 'optimize']):
            return 'get_recommendations'

        return 'general'

    def _handle_topic_analysis(self, message: str) -> str:
        """Handle topic analysis request"""
        # Extract topic from message
        topic = self._extract_topic(message)

        if not topic:
            return "I'd love to analyze a topic for viral potential! Please specify the topic. For example: 'Analyze topic: The Future of AI'"

        print(f"\n🔍 Analyzing topic: {topic}\n")

        # Run analysis
        result = self.gatekeeper.analyze_content(
            topic=topic,
            target_audience="general",
            video_duration_minutes=15,
            content_type="documentary"
        )

        # Format response
        viral_score = result['viral_score']['overall_viral_score']
        rating = result['viral_score']['rating']

        response = f"""✅ Analysis Complete for: {topic}

📊 Viral Score: {viral_score}/10 - {rating}
🎯 Quality Gate: {result['quality_gate']['status']}

🎬 Top Hook Generated:
   "{result['hooks']['top_hooks'][0]['hook_text']}"
   (Virality Score: {result['hooks']['top_hooks'][0].get('virality_score', 'N/A')}/10)

📈 Key Recommendations:
"""

        # Add top 3 recommendations
        for i, rec in enumerate(result['recommendations'][:3], 1):
            response += f"   {i}. [{rec['priority']}] {rec['recommendation']}\n"

        response += f"\n⏱️  Processing Time: {result['metadata']['processing_time_seconds']}s"

        return response

    def _handle_video_analysis(self, message: str) -> str:
        """Handle YouTube video analysis"""
        # Extract URL from message
        url = self._extract_url(message)

        if not url:
            return "Please provide a YouTube video URL. For example: 'Analyze video: https://youtube.com/watch?v=...'"

        print(f"\n📹 Analyzing video: {url}\n")

        result = self.gatekeeper.analyze_youtube_video(url, store_in_library=True)

        tier = result.get('tier', 'none')
        viral_score = result.get('viral_score', 0)

        response = f"""✅ Video Analysis Complete

🏆 Tier Classification: {tier.upper()}
📊 Viral Score: {viral_score}/10

📈 Performance Metrics:
   • Views: {result['performance_metrics']['views']:,}
   • Engagement Rate: {result['performance_metrics']['engagement_rate']:.2f}%
   • Like Rate: {result['performance_metrics']['like_rate']:.2f}%
   • Comment Rate: {result['performance_metrics']['comment_rate']:.2f}%

"""

        if 'stored_in_library' in result:
            response += f"💾 Strategy stored in {tier.upper()} tier library\n"

        return response

    def _handle_hook_generation(self, message: str) -> str:
        """Handle hook generation request"""
        topic = self._extract_topic(message)

        if not topic:
            return "Please specify a topic for hook generation. For example: 'Generate hooks for quantum computing'"

        print(f"\n🎯 Generating hooks for: {topic}\n")

        hooks = self.gatekeeper.hook_specialist.generate_hooks(
            topic=topic,
            count=5,
            target_audience="general"
        )

        response = f"✅ Generated {len(hooks)} Viral Hooks for: {topic}\n\n"

        for i, hook in enumerate(hooks[:5], 1):
            response += f"{i}. \"{hook['hook_text']}\"\n"
            response += f"   Score: {hook.get('virality_score', 'N/A')}/10 | Type: {hook.get('hook_type', 'N/A')}\n\n"

        return response

    def _handle_content_scoring(self, message: str) -> str:
        """Handle content scoring request"""
        return """To score content, I need details about your content:

Please provide:
1. Topic
2. Your hook (first 15 seconds)
3. Main content structure
4. Target audience
5. Video duration

Or use the full analysis command: 'Analyze topic: [your topic]'
"""

    def _handle_recommendations(self, message: str) -> str:
        """Handle recommendations request"""
        return """I can provide recommendations in several ways:

1. **Topic Analysis** - Analyze a topic and get comprehensive recommendations
   Example: "Analyze topic: Climate Change Solutions"

2. **Video Optimization** - Analyze an existing YouTube video for improvements
   Example: "Analyze video: [YouTube URL]"

3. **Hook Optimization** - Generate and optimize hooks
   Example: "Generate hooks for [topic]"

What would you like to optimize?
"""

    def _handle_general_query(self, message: str) -> str:
        """Handle general queries with AI"""
        if not self.ai:
            return "AI integration not available. Please set your Anthropic API key."

        system_prompt = """You are a viral content analysis assistant. Help users understand:
- How to create viral content
- Psychology triggers for engagement
- Video optimization strategies
- Brendan Kane's viral methodology

Keep responses concise and actionable."""

        result = self.ai.generate_text(
            message,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=500
        )

        return result['text']

    def _extract_topic(self, message: str) -> Optional[str]:
        """Extract topic from message"""
        # Simple extraction - can be enhanced
        if ':' in message:
            return message.split(':', 1)[1].strip()

        # Remove common phrases
        message_clean = message.lower()
        for phrase in ['analyze', 'generate hooks for', 'hooks for', 'topic', 'about']:
            message_clean = message_clean.replace(phrase, '')

        return message_clean.strip() if message_clean.strip() else None

    def _extract_url(self, message: str) -> Optional[str]:
        """Extract URL from message"""
        words = message.split()
        for word in words:
            if 'youtube.com' in word or 'youtu.be' in word:
                return word.strip()
        return None

    def _show_help(self):
        """Show help information"""
        print("\n" + "="*80)
        print("📚 HELP - Available Commands")
        print("="*80)
        print("""
🎯 Topic Analysis:
   "Analyze topic: [topic name]"
   Example: "Analyze topic: The Future of AI"

📹 Video Analysis:
   "Analyze video: [YouTube URL]"
   Example: "Analyze video: https://youtube.com/watch?v=..."

🎬 Hook Generation:
   "Generate hooks for [topic]"
   Example: "Generate hooks for quantum computing"

📊 Get Recommendations:
   "How can I optimize [topic]?"
   "What makes content go viral?"

💬 General Questions:
   Ask anything about viral content, psychology triggers, or optimization!

📈 System Commands:
   'help' - Show this help message
   'stats' - Show system statistics
   'exit' - Exit the system
""")
        print("="*80 + "\n")

    def _show_stats(self):
        """Show system statistics"""
        stats = self.gatekeeper.get_statistics()

        print("\n" + "="*80)
        print("📊 SYSTEM STATISTICS")
        print("="*80)
        print(f"""
Total Analyses Performed: {stats['total_analyses']}
Total Processing Time: {stats['total_processing_time']:.2f}s
Average Processing Time: {stats['avg_processing_time']:.2f}s
Strategy Library Size: {stats['strategy_library_size']} strategies
Quality Threshold: {stats['quality_threshold']}/10

Conversation Messages: {len(self.conversation_history)}
""")
        print("="*80 + "\n")


def main():
    """Main entry point for chat interface"""
    chat = ChatInterface()
    chat.start()


if __name__ == "__main__":
    main()
