"""
Chat Integration Interface
Interactive chat interface for the Content Synthesis system
"""
import asyncio
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from src.core.config_manager import get_config_manager
from src.core.anthropic_client import AnthropicClient
from src.content_synthesis import ContentSynthesisGatekeeper, ContentPackage

logger = logging.getLogger(__name__)


class ChatInterface:
    """
    Interactive chat interface for content generation
    Allows users to interact with the system through natural language
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize chat interface

        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config_manager = get_config_manager(config_path)

        # Initialize Anthropic client
        anthropic_config = self.config_manager.get_anthropic_config()
        self.anthropic_client = AnthropicClient(
            api_key=anthropic_config.api_key,
            model=anthropic_config.model,
            max_tokens=anthropic_config.max_tokens,
            temperature=anthropic_config.temperature,
            timeout=anthropic_config.timeout
        )

        # Initialize Content Synthesis Gatekeeper
        content_config = self.config_manager.get_content_synthesis_config()
        self.gatekeeper = ContentSynthesisGatekeeper(
            anthropic_client=self.anthropic_client,
            config=content_config
        )

        # Session state
        self.session_history: List[Dict[str, str]] = []
        self.current_project: Optional[Dict[str, Any]] = None

        logger.info("Chat interface initialized")

    def start_interactive_session(self):
        """Start interactive chat session"""
        print("\n" + "="*70)
        print("  CONTENT SYNTHESIS SYSTEM - Interactive Chat Interface")
        print("="*70)
        print("\nWelcome! I can help you create world-class YouTube documentary content.")
        print("\nCommands:")
        print("  /generate - Generate content for a new topic")
        print("  /refine   - Refine the current content")
        print("  /save     - Save the current content package")
        print("  /status   - Show current project status")
        print("  /config   - Adjust system configuration")
        print("  /help     - Show this help message")
        print("  /quit     - Exit the system")
        print("\nJust describe what you want to create, and I'll guide you through the process!")
        print("="*70 + "\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith('/'):
                    self._handle_command(user_input)
                else:
                    # Process natural language input
                    response = self._process_user_message(user_input)
                    print(f"\nAssistant: {response}\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")
                logger.error(f"Error in chat session: {str(e)}")

    def _handle_command(self, command: str):
        """Handle slash commands"""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()

        if cmd == '/quit' or cmd == '/exit':
            print("\nGoodbye! 👋\n")
            exit(0)

        elif cmd == '/help':
            self._show_help()

        elif cmd == '/generate':
            self._interactive_generate()

        elif cmd == '/refine':
            self._interactive_refine()

        elif cmd == '/save':
            self._save_current_project()

        elif cmd == '/status':
            self._show_status()

        elif cmd == '/config':
            self._interactive_config()

        else:
            print(f"\n❌ Unknown command: {cmd}")
            print("Type /help to see available commands.\n")

    def _process_user_message(self, message: str) -> str:
        """
        Process natural language user message

        Args:
            message: User message

        Returns:
            Response string
        """
        # Add to history
        self.session_history.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        })

        # Analyze intent using Claude
        intent = self._analyze_intent(message)

        # Route to appropriate handler
        if intent['action'] == 'generate':
            return self._handle_generate_intent(intent)
        elif intent['action'] == 'refine':
            return self._handle_refine_intent(intent)
        elif intent['action'] == 'question':
            return self._handle_question(message)
        else:
            return self._handle_general_message(message)

    def _analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user intent using Claude"""

        prompt = f"""Analyze this user message and determine their intent.

User message: "{message}"

Classify the intent as one of:
- generate: User wants to create new content
- refine: User wants to improve existing content
- question: User is asking a question
- config: User wants to change settings
- general: General conversation

Extract key parameters if present:
- topic: What topic do they want content about?
- duration: Video duration (in minutes)
- style: Visual style preference
- audience: Target audience

Respond in this format:
Action: [action]
Topic: [topic or "not specified"]
Duration: [number or "not specified"]
Style: [style or "not specified"]
Audience: [audience or "not specified"]"""

        try:
            result = self.anthropic_client.generate(
                prompt=prompt,
                max_tokens=200,
                temperature=0.3
            )

            # Parse response
            lines = result.content.strip().split('\n')
            intent = {}

            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    intent[key.strip().lower()] = value.strip()

            return intent

        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            return {'action': 'general'}

    def _handle_generate_intent(self, intent: Dict[str, Any]) -> str:
        """Handle content generation intent"""

        topic = intent.get('topic', 'not specified')

        if topic == 'not specified' or topic.lower() in ['none', 'n/a']:
            return "I'd be happy to help you generate content! What topic would you like to create a video about?"

        # Extract parameters
        duration = self._parse_duration(intent.get('duration', '15'))
        style = intent.get('style', 'documentary')
        audience = intent.get('audience', 'general audience')

        print(f"\n🚀 Generating content...")
        print(f"   Topic: {topic}")
        print(f"   Duration: {duration} minutes")
        print(f"   Style: {style}")
        print(f"   Audience: {audience}")
        print(f"\nThis may take a few minutes...\n")

        try:
            # Generate content
            package = self.gatekeeper.generate_content_sync(
                topic=topic,
                video_duration=duration,
                style=style,
                target_audience=audience
            )

            # Store in session
            self.current_project = {
                'package': package,
                'topic': topic,
                'created_at': datetime.now().isoformat()
            }

            return self._format_generation_result(package)

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return f"❌ Generation failed: {str(e)}\n\nPlease check your API configuration and try again."

    def _handle_refine_intent(self, intent: Dict[str, Any]) -> str:
        """Handle refinement intent"""

        if not self.current_project:
            return "No content to refine. Please generate content first using /generate or describe what you want to create."

        print("\n🔄 Refining content...\n")

        try:
            # Re-generate with feedback
            old_package = self.current_project['package']

            package = self.gatekeeper.generate_content_sync(
                topic=self.current_project['topic'],
                video_duration=old_package.metadata['target_duration'],
                enable_iteration=True,
                max_iterations=3
            )

            # Update session
            self.current_project['package'] = package

            return self._format_refinement_result(old_package, package)

        except Exception as e:
            logger.error(f"Refinement failed: {e}")
            return f"❌ Refinement failed: {str(e)}"

    def _handle_question(self, message: str) -> str:
        """Handle user questions"""

        context = ""
        if self.current_project:
            package = self.current_project['package']
            context = f"""
Current project:
- Topic: {self.current_project['topic']}
- Quality Score: {package.quality_score}/10
- Word Count: {package.word_count}
- Scenes: {package.scene_count}
"""

        prompt = f"""Answer this user question about the content synthesis system.

{context}

User question: {message}

Provide a helpful, concise answer."""

        try:
            result = self.anthropic_client.generate(
                prompt=prompt,
                max_tokens=500,
                temperature=0.7
            )

            return result.content

        except Exception as e:
            return f"I'm having trouble answering that question. Error: {str(e)}"

    def _handle_general_message(self, message: str) -> str:
        """Handle general conversation"""

        prompt = f"""You are a helpful assistant for a content synthesis system.
The user said: "{message}"

Provide a friendly, helpful response. If they seem interested in generating content,
encourage them to describe what they want to create."""

        try:
            result = self.anthropic_client.generate(
                prompt=prompt,
                max_tokens=300,
                temperature=0.8
            )

            return result.content

        except Exception as e:
            return "I'm here to help you create amazing content! What would you like to make?"

    def _interactive_generate(self):
        """Interactive content generation wizard"""

        print("\n" + "="*70)
        print("  CONTENT GENERATION WIZARD")
        print("="*70 + "\n")

        # Collect parameters
        topic = input("What's your video topic? ").strip()
        if not topic:
            print("❌ Topic is required.\n")
            return

        duration_input = input("Target duration in minutes (default: 15): ").strip()
        duration = self._parse_duration(duration_input) if duration_input else 15

        style = input("Visual style (documentary/educational/cinematic) [default: documentary]: ").strip()
        style = style if style else "documentary"

        audience = input("Target audience (default: general audience): ").strip()
        audience = audience if audience else "general audience"

        tone = input("Tone (engaging/authoritative/casual) [default: engaging]: ").strip()
        tone = tone if tone else "engaging"

        # Confirm
        print(f"\n📋 Summary:")
        print(f"   Topic: {topic}")
        print(f"   Duration: {duration} minutes")
        print(f"   Style: {style}")
        print(f"   Audience: {audience}")
        print(f"   Tone: {tone}")

        confirm = input("\nProceed with generation? (yes/no): ").strip().lower()

        if confirm not in ['yes', 'y']:
            print("❌ Generation cancelled.\n")
            return

        print(f"\n🚀 Generating content... This may take a few minutes.\n")

        try:
            package = self.gatekeeper.generate_content_sync(
                topic=topic,
                video_duration=duration,
                style=style,
                target_audience=audience,
                tone=tone
            )

            self.current_project = {
                'package': package,
                'topic': topic,
                'created_at': datetime.now().isoformat()
            }

            print(self._format_generation_result(package))

        except Exception as e:
            print(f"\n❌ Generation failed: {str(e)}\n")
            logger.error(f"Generation failed: {e}")

    def _interactive_refine(self):
        """Interactive refinement"""

        if not self.current_project:
            print("\n❌ No content to refine. Generate content first.\n")
            return

        print("\n" + "="*70)
        print("  CONTENT REFINEMENT")
        print("="*70 + "\n")

        package = self.current_project['package']

        print(f"Current quality score: {package.quality_score}/10")
        print(f"\nKey issues:")
        for issue in package.validation_report.get('critical_issues', [])[:3]:
            print(f"  - {issue}")

        confirm = input("\nRefine this content? (yes/no): ").strip().lower()

        if confirm not in ['yes', 'y']:
            print("❌ Refinement cancelled.\n")
            return

        print(f"\n🔄 Refining content...\n")

        try:
            old_package = package

            new_package = self.gatekeeper.generate_content_sync(
                topic=self.current_project['topic'],
                video_duration=package.metadata['target_duration'],
                enable_iteration=True,
                max_iterations=3
            )

            self.current_project['package'] = new_package

            print(self._format_refinement_result(old_package, new_package))

        except Exception as e:
            print(f"\n❌ Refinement failed: {str(e)}\n")

    def _save_current_project(self):
        """Save current project to files"""

        if not self.current_project:
            print("\n❌ No content to save. Generate content first.\n")
            return

        try:
            package = self.current_project['package']
            output_path = self.gatekeeper.save_content_package(package)

            print(f"\n✅ Content saved successfully!")
            print(f"   Location: {output_path}\n")

        except Exception as e:
            print(f"\n❌ Save failed: {str(e)}\n")

    def _show_status(self):
        """Show current project status"""

        if not self.current_project:
            print("\n📊 Status: No active project\n")
            print("Start by generating content with /generate or describing what you want to create.\n")
            return

        package = self.current_project['package']

        print("\n" + "="*70)
        print("  PROJECT STATUS")
        print("="*70)
        print(f"\nTopic: {self.current_project['topic']}")
        print(f"Created: {self.current_project['created_at']}")
        print(f"\n📊 Quality Metrics:")
        print(f"   Overall Score: {package.quality_score}/10")
        print(f"   Script: {package.word_count} words ({package.estimated_duration:.1f} min estimated)")
        print(f"   Visual Scenes: {package.scene_count}")
        print(f"   Iterations: {package.iteration_count}")
        print(f"   Processing Time: {package.total_processing_time:.1f}s")

        validation = package.validation_report
        print(f"\n📋 Validation Scores:")
        for category, result in validation['validation_passes'].items():
            print(f"   {category.replace('_', ' ').title()}: {result['score']}/10")

        if validation.get('strengths'):
            print(f"\n✅ Strengths:")
            for strength in validation['strengths'][:3]:
                print(f"   - {strength}")

        if validation.get('recommendations'):
            print(f"\n💡 Recommendations:")
            for rec in validation['recommendations'][:3]:
                print(f"   [{rec['priority']}] {rec['recommendation']}")

        print("="*70 + "\n")

    def _show_help(self):
        """Show help message"""

        print("\n" + "="*70)
        print("  HELP - AVAILABLE COMMANDS")
        print("="*70)
        print("\n📝 Commands:")
        print("   /generate  - Start content generation wizard")
        print("   /refine    - Refine and improve current content")
        print("   /save      - Save current content to files")
        print("   /status    - View detailed project status")
        print("   /config    - Adjust system configuration")
        print("   /help      - Show this help message")
        print("   /quit      - Exit the system")
        print("\n💬 Natural Language:")
        print("   Just type what you want! For example:")
        print("   - 'Create a 10-minute documentary about AI'")
        print("   - 'Make a video about climate change for students'")
        print("   - 'Generate content about space exploration'")
        print("\n🎯 Tips:")
        print("   - Be specific about your topic and target audience")
        print("   - Generation takes 2-10 minutes depending on complexity")
        print("   - Use /refine to improve quality if needed")
        print("   - Always /save your work when satisfied")
        print("="*70 + "\n")

    def _interactive_config(self):
        """Interactive configuration adjustment"""

        print("\n" + "="*70)
        print("  CONFIGURATION")
        print("="*70 + "\n")

        print("What would you like to configure?")
        print("1. Quality threshold")
        print("2. Video duration")
        print("3. Max iterations")
        print("4. Back")

        choice = input("\nChoice (1-4): ").strip()

        if choice == '1':
            threshold = input("Enter quality threshold (0-10) [current: 9.0]: ").strip()
            if threshold:
                try:
                    value = float(threshold)
                    self.config_manager.update_config('content_synthesis', {'quality_threshold': value})
                    print(f"✅ Quality threshold set to {value}\n")
                except ValueError:
                    print("❌ Invalid value\n")

        elif choice == '2':
            duration = input("Enter default video duration in minutes [current: 15]: ").strip()
            if duration:
                try:
                    value = int(duration)
                    self.config_manager.update_config('content_synthesis', {'target_video_duration': value})
                    print(f"✅ Default duration set to {value} minutes\n")
                except ValueError:
                    print("❌ Invalid value\n")

        elif choice == '3':
            iterations = input("Enter max iterations [current: 5]: ").strip()
            if iterations:
                try:
                    value = int(iterations)
                    self.config_manager.update_config('system', {'max_iterations': value})
                    print(f"✅ Max iterations set to {value}\n")
                except ValueError:
                    print("❌ Invalid value\n")

    def _format_generation_result(self, package: ContentPackage) -> str:
        """Format generation result for display"""

        result = f"""
{'='*70}
✅ CONTENT GENERATION COMPLETE!
{'='*70}

📊 Quality Score: {package.quality_score}/10
📝 Script: {package.word_count} words (~{package.estimated_duration:.1f} minutes)
🎬 Visual Scenes: {package.scene_count}
🔄 Iterations: {package.iteration_count}
⏱️  Processing Time: {package.total_processing_time:.1f}s

✅ Validation Status: {'PASSED' if package.validation_report['passes_validation'] else 'NEEDS IMPROVEMENT'}

💡 Next Steps:
   - Type /status to see detailed metrics
   - Type /save to save this content
   - Type /refine to improve quality further
   - Describe changes you'd like to make

{'='*70}
"""
        return result

    def _format_refinement_result(self, old_package: ContentPackage, new_package: ContentPackage) -> str:
        """Format refinement result"""

        improvement = new_package.quality_score - old_package.quality_score

        result = f"""
{'='*70}
✅ REFINEMENT COMPLETE!
{'='*70}

📊 Quality Improvement: {old_package.quality_score}/10 → {new_package.quality_score}/10 ({improvement:+.1f})
📝 Script: {new_package.word_count} words
🎬 Scenes: {new_package.scene_count}

{'='*70}
"""
        return result

    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string to integer"""
        try:
            # Extract number from string
            import re
            match = re.search(r'\d+', duration_str)
            if match:
                return int(match.group())
            return 15
        except:
            return 15


def main():
    """Main entry point for chat interface"""
    import sys

    # Check for API key
    import os
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("\n❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("\nPlease set your API key:")
        print("   export ANTHROPIC_API_KEY='your-api-key-here'\n")
        sys.exit(1)

    try:
        interface = ChatInterface()
        interface.start_interactive_session()
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋\n")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}\n")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
