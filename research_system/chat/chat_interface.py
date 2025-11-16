"""
Chat Integration Interface
Provides conversational interface to the research system
"""

from typing import Dict, Any, Optional, List
import logging
import re

from ..core.research_gatekeeper import ResearchGatekeeper
from ..core.config_manager import get_config_manager

logger = logging.getLogger(__name__)


class ChatInterface:
    """
    Chat-based interface for the Research System
    Allows users to interact conversationally with the research gatekeeper
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize chat interface

        Args:
            config_file: Optional configuration file path
        """
        self.gatekeeper = ResearchGatekeeper(config_file)
        self.conversation_history: List[Dict[str, str]] = []
        self.current_context: Dict[str, Any] = {}

        logger.info("Chat Interface initialized")

    def process_message(self, user_message: str) -> str:
        """
        Process user message and return response

        Args:
            user_message: User's message

        Returns:
            System response
        """
        # Add to history
        self.conversation_history.append({
            'role': 'user',
            'content': user_message
        })

        # Parse intent
        intent = self._parse_intent(user_message)

        # Route to appropriate handler
        response = self._handle_intent(intent, user_message)

        # Add response to history
        self.conversation_history.append({
            'role': 'assistant',
            'content': response
        })

        return response

    def _parse_intent(self, message: str) -> str:
        """
        Parse user intent from message

        Args:
            message: User message

        Returns:
            Intent category
        """
        message_lower = message.lower()

        # Research request
        if any(word in message_lower for word in ['research', 'find', 'search', 'papers', 'study', 'investigate']):
            return 'research'

        # Fact checking
        elif any(word in message_lower for word in ['fact check', 'verify', 'is it true', 'validate']):
            return 'fact_check'

        # Add source
        elif any(word in message_lower for word in ['add source', 'new source', 'add database']):
            return 'add_source'

        # Statistics
        elif any(word in message_lower for word in ['statistics', 'stats', 'how many', 'show me']):
            return 'statistics'

        # Help
        elif any(word in message_lower for word in ['help', 'how', 'what can you do']):
            return 'help'

        # Default
        else:
            return 'research'

    def _handle_intent(self, intent: str, message: str) -> str:
        """
        Handle user intent

        Args:
            intent: Parsed intent
            message: Original message

        Returns:
            Response string
        """
        try:
            if intent == 'research':
                return self._handle_research(message)

            elif intent == 'fact_check':
                return self._handle_fact_check(message)

            elif intent == 'add_source':
                return self._handle_add_source(message)

            elif intent == 'statistics':
                return self._handle_statistics()

            elif intent == 'help':
                return self._handle_help()

            else:
                return self._handle_research(message)

        except Exception as e:
            logger.error(f"Error handling intent '{intent}': {e}")
            return f"I encountered an error: {str(e)}. Please try rephrasing your request."

    def _handle_research(self, message: str) -> str:
        """Handle research requests"""
        # Extract topic from message
        topic = self._extract_topic(message)

        if not topic:
            return "I'd be happy to help with research! What topic would you like me to investigate?"

        logger.info(f"Conducting research on: {topic}")

        # Conduct research
        try:
            report = self.gatekeeper.conduct_research(
                topic=topic,
                query=topic
            )

            # Format response
            response = f"""I've completed research on "{topic}". Here's what I found:

**Research Summary:**
- Analyzed {len(report.papers)} academic papers
- Sources: {', '.join(set(p.source for p in report.papers[:10]))}
- Quality Score: {report.validation_result.overall_score:.1f}/10
- Status: {'✓ Meets academic standards' if report.validation_result.passed else '⚠ Needs improvement'}

**Key Insights:**
{self._format_list(report.insights[:5])}

**Knowledge Gaps Identified:**
{self._format_list(report.knowledge_gaps[:3])}

**Research Synthesis:**
{report.synthesis[:500]}...

Full report saved to: {report.metadata.get('filename', 'outputs/')}

Would you like me to:
1. Dive deeper into a specific aspect?
2. Fact-check specific claims?
3. Find more recent papers?
"""
            self.current_context['last_report'] = report

            return response

        except Exception as e:
            logger.error(f"Research error: {e}")
            return f"I encountered an error during research: {str(e)}"

    def _handle_fact_check(self, message: str) -> str:
        """Handle fact-checking requests"""
        # Extract claim
        claim = self._extract_claim(message)

        if not claim:
            return "What claim would you like me to fact-check? Please provide the specific statement."

        # Extract topic (or use last research context)
        topic = self._extract_topic(message) or self.current_context.get('last_topic', '')

        if not topic:
            return "Please provide the topic area for this claim so I can find relevant research."

        logger.info(f"Fact-checking: {claim}")

        try:
            result = self.gatekeeper.fact_check_claim(claim, topic)

            verdict_emoji = {
                'SUPPORTED': '✓',
                'PARTIALLY_SUPPORTED': '⚠',
                'CONTRADICTED': '✗',
                'INSUFFICIENT_EVIDENCE': '?'
            }

            response = f"""Fact-Check Result for: "{claim}"

**Verdict:** {verdict_emoji.get(result['verdict'], '?')} {result['verdict']}
**Confidence:** {result['confidence']:.1f}/10

**Supporting Evidence:**
{self._format_list(result.get('supporting_evidence', [])[:3])}

**Contradicting Evidence:**
{self._format_list(result.get('contradicting_evidence', [])[:3])}

**Reasoning:**
{result.get('reasoning', 'Analysis unavailable')}

**Caveats:**
{self._format_list(result.get('caveats', []))}
"""
            return response

        except Exception as e:
            return f"Error fact-checking: {str(e)}"

    def _handle_add_source(self, message: str) -> str:
        """Handle adding custom sources"""
        return """To add a custom research source, you need to:

1. Implement a class that extends `BaseResearchSource`
2. Register it with the system using:
   ```python
   gatekeeper.aggregator.add_custom_source(your_source, priority=7)
   ```

This modular design allows you to add any academic database or repository.

Would you like help with implementing a specific source?"""

    def _handle_statistics(self) -> str:
        """Handle statistics requests"""
        stats = self.gatekeeper.get_statistics()

        response = f"""**Research System Statistics:**

📊 **Overall:**
- Total research reports: {stats['total_research_reports']}
- Citations tracked: {stats['citations_tracked']}
- Sources available: {stats['sources_available']}

📚 **Source Performance:**
"""
        for source, source_stats in stats.get('source_statistics', {}).items():
            response += f"\n  - {source}: {source_stats['requests_made']} requests ({source_stats['success_rate']*100:.0f}% success)"

        return response

    def _handle_help(self) -> str:
        """Handle help requests"""
        return """**Research System Help**

I'm an advanced research assistant powered by Claude AI. I can help you with:

🔬 **Research Tasks:**
- "Research quantum computing breakthroughs"
- "Find papers on climate change from 2020-2024"
- "Investigate AI safety research"

✓ **Fact Checking:**
- "Fact check: renewable energy is cost-effective"
- "Verify if machine learning improves diagnosis"

📊 **System Info:**
- "Show statistics"
- "What sources do you use?"

**Features:**
- Multi-database search (JSTOR, PubMed, arXiv, Semantic Scholar, CrossRef, OpenAlex)
- AI-powered synthesis using Claude
- Credibility analysis and quality validation
- Citation tracking
- Knowledge gap identification

**Quality Standards:**
- Academic rigor: 8.0+/10
- Source credibility: 9.0+/10
- Multi-source validation

Just ask your question naturally!"""

    def _extract_topic(self, message: str) -> Optional[str]:
        """Extract research topic from message"""
        # Remove common prefixes
        message = re.sub(r'^(research|find|search|investigate|study|analyze)\s+(about|on)?\s*', '', message, flags=re.IGNORECASE)
        message = re.sub(r'^(papers|studies|articles)\s+(about|on)\s*', '', message, flags=re.IGNORECASE)

        # Clean up
        topic = message.strip()

        # Minimum length check
        if len(topic) < 3:
            return None

        self.current_context['last_topic'] = topic
        return topic

    def _extract_claim(self, message: str) -> Optional[str]:
        """Extract claim from message"""
        # Remove fact-check prefixes
        message = re.sub(r'^(fact check|verify|is it true|validate):?\s*', '', message, flags=re.IGNORECASE)

        claim = message.strip()

        if len(claim) < 5:
            return None

        return claim

    def _format_list(self, items: List[str], max_items: int = 5) -> str:
        """Format list items for display"""
        if not items:
            return "  - None"

        formatted = []
        for i, item in enumerate(items[:max_items], 1):
            formatted.append(f"  {i}. {item}")

        return "\n".join(formatted)

    def interactive_mode(self) -> None:
        """Run in interactive mode"""
        print("="*80)
        print("Research System - Interactive Mode")
        print("="*80)
        print("Type 'help' for assistance, 'exit' to quit")
        print()

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\nGoodbye!")
                    break

                response = self.process_message(user_input)
                print(f"\nAssistant: {response}")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                logger.error(f"Interactive mode error: {e}")

    def __repr__(self) -> str:
        """String representation"""
        return f"ChatInterface(messages={len(self.conversation_history)})"


def main():
    """Main entry point for chat interface"""
    import sys

    # Check for config file argument
    config_file = sys.argv[1] if len(sys.argv) > 1 else None

    # Initialize and run
    interface = ChatInterface(config_file)
    interface.interactive_mode()


if __name__ == "__main__":
    main()
