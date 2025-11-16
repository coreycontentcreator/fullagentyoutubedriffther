"""
Chat Interface Demo

Interactive demonstration of the chat interface capabilities.

Author: AI Research Team
Date: November 2025
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from orchestrator.chat_interface import ChatInterface
from utils.anthropic_client import AnthropicIntelligence
from utils.logger import LoggerFactory


def main():
    """Run interactive chat demo."""
    print("="*70)
    print("Master Orchestrator - Chat Interface Demo")
    print("="*70)

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n⚠️  ANTHROPIC_API_KEY not found in environment.")
        print("   Set it in .env file or export it:")
        print("   export ANTHROPIC_API_KEY=your_key_here\n")
        return

    # Setup logging
    LoggerFactory.configure(
        log_dir=Path(__file__).parent.parent / "logs",
        log_level="INFO"
    )

    # Initialize AI and chat interface
    print("\nInitializing chat interface...")
    ai = AnthropicIntelligence(api_key=api_key)
    chat = ChatInterface(ai)

    # Start session
    session = chat.start_session()
    print("\n" + "="*70)
    print(session.messages[0].content)
    print("="*70)

    # Example conversations
    examples = [
        "What can you do?",
        "Create a viral video about quantum computing",
        "I need help understanding the system",
        "Analyze this video: https://youtube.com/watch?v=dQw4w9WgXcQ"
    ]

    print("\nDemonstration Mode - Pre-programmed Examples:")
    print("(In production, this would be an interactive chat)\n")

    for i, message in enumerate(examples, 1):
        print(f"\n{i}. User: {message}")
        print("-" * 70)

        response = chat.process_message(message)

        print(f"Assistant Action: {response['action']}")
        print(f"Response:\n{response['message'][:500]}")
        if len(response['message']) > 500:
            print("... (truncated)")

        # Show additional info for certain actions
        if response.get('parameters'):
            print(f"\nExtracted Parameters:")
            for key, value in response.get('parameters', {}).items():
                print(f"  - {key}: {value}")

    # Show conversation history
    print("\n" + "="*70)
    print("Conversation History Summary:")
    print("="*70)
    history = chat.get_conversation_history(limit=20)
    print(f"Total messages in session: {len(history)}")
    print(f"Session ID: {session.session_id}")

    print("\n" + "="*70)
    print("Demo completed!")
    print("="*70)
    print("\nTo run interactively, modify this script to use input():")
    print("""
# Interactive mode example:
while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit']:
        break
    response = chat.process_message(user_input)
    print(f"Assistant: {response['message']}")
""")


if __name__ == "__main__":
    main()
