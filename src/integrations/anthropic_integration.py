"""
Anthropic Claude API Integration
Provides intelligent text generation, analysis, and reasoning
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import anthropic
from anthropic import Anthropic, AsyncAnthropic


class AnthropicIntegration:
    """
    Integration with Anthropic's Claude API for intelligent text generation
    and analysis. Supports both sync and async operations.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-5-20250929"):
        """
        Initialize Anthropic integration

        Args:
            api_key: Anthropic API key (defaults to env variable)
            model: Claude model to use
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key is required")

        self.model = model
        self.client = Anthropic(api_key=self.api_key)
        self.async_client = AsyncAnthropic(api_key=self.api_key)

        # Request tracking
        self.request_count = 0
        self.total_tokens_used = 0

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using Claude

        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            **kwargs: Additional API parameters

        Returns:
            Dict with 'text', 'usage', and 'metadata'
        """
        try:
            messages = [{"role": "user", "content": prompt}]

            params = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            }

            if system_prompt:
                params["system"] = system_prompt

            params.update(kwargs)

            response = self.client.messages.create(**params)

            # Track usage
            self.request_count += 1
            self.total_tokens_used += response.usage.input_tokens + response.usage.output_tokens

            return {
                'text': response.content[0].text,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens,
                    'total_tokens': response.usage.input_tokens + response.usage.output_tokens
                },
                'metadata': {
                    'model': response.model,
                    'stop_reason': response.stop_reason,
                    'timestamp': datetime.now().isoformat()
                }
            }

        except Exception as e:
            return {
                'text': '',
                'error': str(e),
                'usage': {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
            }

    async def generate_text_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Async version of generate_text"""
        try:
            messages = [{"role": "user", "content": prompt}]

            params = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            }

            if system_prompt:
                params["system"] = system_prompt

            params.update(kwargs)

            response = await self.async_client.messages.create(**params)

            # Track usage
            self.request_count += 1
            self.total_tokens_used += response.usage.input_tokens + response.usage.output_tokens

            return {
                'text': response.content[0].text,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens,
                    'total_tokens': response.usage.input_tokens + response.usage.output_tokens
                },
                'metadata': {
                    'model': response.model,
                    'stop_reason': response.stop_reason,
                    'timestamp': datetime.now().isoformat()
                }
            }

        except Exception as e:
            return {
                'text': '',
                'error': str(e),
                'usage': {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
            }

    def analyze_content(self, content: str, analysis_type: str = "general") -> Dict[str, Any]:
        """
        Analyze content with Claude

        Args:
            content: Content to analyze
            analysis_type: Type of analysis (general, viral, engagement, structure)

        Returns:
            Analysis results
        """
        system_prompts = {
            "general": "You are an expert content analyst. Provide detailed, structured analysis.",
            "viral": "You are a viral content expert. Analyze virality potential and engagement factors.",
            "engagement": "You are an engagement specialist. Analyze retention and interaction potential.",
            "structure": "You are a content structure analyst. Analyze narrative flow and pacing."
        }

        analysis_prompts = {
            "general": f"Analyze this content comprehensively:\n\n{content}",
            "viral": f"Analyze the viral potential of this content. Consider hooks, psychology triggers, engagement factors:\n\n{content}",
            "engagement": f"Analyze the engagement and retention potential:\n\n{content}",
            "structure": f"Analyze the narrative structure and flow:\n\n{content}"
        }

        system_prompt = system_prompts.get(analysis_type, system_prompts["general"])
        prompt = analysis_prompts.get(analysis_type, analysis_prompts["general"])

        return self.generate_text(prompt, system_prompt=system_prompt)

    def generate_hooks(self, topic: str, count: int = 10, context: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate multiple hook variations for a topic

        Args:
            topic: Main topic
            count: Number of hooks to generate
            context: Additional context

        Returns:
            List of hook dictionaries
        """
        context_str = f"\n\nContext: {context}" if context else ""

        prompt = f"""Generate {count} compelling video hooks for this topic: {topic}{context_str}

Each hook should:
1. Be 15 seconds or less when spoken
2. Create a curiosity gap
3. Use psychological triggers
4. Be immediately engaging
5. Promise clear value

Return as JSON array with format:
[
  {{
    "hook_text": "The actual hook text",
    "duration_estimate": 12,
    "psychology_triggers": ["curiosity", "novelty"],
    "virality_score": 8.5,
    "target_emotion": "curiosity"
  }}
]
"""

        system_prompt = "You are a viral content hook specialist. Generate hooks that stop scrolling and compel viewing."

        result = self.generate_text(prompt, system_prompt=system_prompt, temperature=0.8)

        try:
            # Extract JSON from response
            text = result['text']
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]

            hooks = json.loads(text.strip())
            return hooks if isinstance(hooks, list) else [hooks]
        except:
            # Fallback: return as single hook
            return [{
                "hook_text": result['text'],
                "duration_estimate": 15,
                "psychology_triggers": ["curiosity"],
                "virality_score": 7.0,
                "target_emotion": "curiosity"
            }]

    def score_virality(self, content: str, criteria: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Score content for viral potential

        Args:
            content: Content to score
            criteria: Specific criteria to evaluate

        Returns:
            Virality score and breakdown
        """
        criteria_str = json.dumps(criteria, indent=2) if criteria else "standard viral metrics"

        prompt = f"""Score this content for viral potential on a scale of 0-10.

Content:
{content}

Evaluation criteria: {criteria_str}

Provide detailed scoring as JSON:
{{
  "overall_score": 8.5,
  "hook_strength": 9.0,
  "psychology_triggers": 8.0,
  "retention_potential": 8.5,
  "engagement_likelihood": 8.0,
  "shareability": 9.0,
  "emotional_impact": 8.5,
  "breakdown": {{
    "strengths": ["list of strengths"],
    "weaknesses": ["list of weaknesses"],
    "recommendations": ["list of improvements"]
  }}
}}
"""

        system_prompt = "You are a viral content scoring expert. Provide accurate, data-driven virality assessments."

        result = self.generate_text(prompt, system_prompt=system_prompt, temperature=0.3)

        try:
            text = result['text']
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]

            return json.loads(text.strip())
        except:
            return {
                "overall_score": 5.0,
                "error": "Failed to parse scoring response",
                "raw_response": result['text']
            }

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return {
            'request_count': self.request_count,
            'total_tokens_used': self.total_tokens_used,
            'model': self.model
        }

    def reset_stats(self):
        """Reset usage statistics"""
        self.request_count = 0
        self.total_tokens_used = 0
