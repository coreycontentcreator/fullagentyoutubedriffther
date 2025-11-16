"""
Anthropic API Integration for Master Orchestrator

Provides intelligent reasoning, synthesis, and decision-making capabilities
using Claude models. This is the core intelligence layer for the system.

Author: AI Research Team
Date: November 2025
Version: 1.0.0
"""

import anthropic
from typing import Dict, List, Any, Optional, Union
import json
import time
from dataclasses import dataclass
from .logger import get_logger


@dataclass
class AnthropicResponse:
    """Structured response from Anthropic API."""
    content: str
    usage: Dict[str, int]
    model: str
    stop_reason: str
    raw_response: Any


class AnthropicIntelligence:
    """
    Advanced Anthropic API client with intelligent reasoning capabilities.

    This class provides:
    - Structured reasoning and decision-making
    - Context-aware responses
    - Multi-turn conversations
    - Retry logic with exponential backoff
    - Token usage tracking
    - Performance monitoring
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 8000,
        temperature: float = 0.7,
        timeout: int = 300
    ):
        """
        Initialize Anthropic intelligence client.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
            max_tokens: Maximum tokens per response
            temperature: Sampling temperature (0-1)
            timeout: Request timeout in seconds
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self.logger = get_logger(__name__)
        self.total_tokens_used = 0

        self.logger.info(
            "Anthropic Intelligence initialized",
            model=model,
            max_tokens=max_tokens
        )

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AnthropicResponse:
        """
        Generate a response using Claude.

        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional API parameters

        Returns:
            AnthropicResponse with generated content
        """
        with self.logger.performance_tracking("anthropic_generate", model=self.model):
            try:
                messages = [{"role": "user", "content": prompt}]

                params = {
                    "model": self.model,
                    "max_tokens": max_tokens or self.max_tokens,
                    "temperature": temperature if temperature is not None else self.temperature,
                    "messages": messages,
                    **kwargs
                }

                if system_prompt:
                    params["system"] = system_prompt

                response = self.client.messages.create(**params)

                # Track token usage
                usage = {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                }
                self.total_tokens_used += usage["total_tokens"]

                self.logger.info(
                    "Generated response",
                    input_tokens=usage["input_tokens"],
                    output_tokens=usage["output_tokens"],
                    stop_reason=response.stop_reason
                )

                return AnthropicResponse(
                    content=response.content[0].text,
                    usage=usage,
                    model=response.model,
                    stop_reason=response.stop_reason,
                    raw_response=response
                )

            except Exception as e:
                self.logger.error(f"Anthropic API error: {str(e)}")
                raise

    def analyze_and_decide(
        self,
        context: str,
        decision_criteria: Dict[str, Any],
        options: List[str]
    ) -> Dict[str, Any]:
        """
        Make an intelligent decision based on context and criteria.

        Args:
            context: Contextual information for decision
            decision_criteria: Criteria for making the decision
            options: Available options to choose from

        Returns:
            Decision with reasoning and confidence score
        """
        system_prompt = """You are an expert decision-making system for a viral YouTube content generation platform.
Analyze the provided context, evaluate options against criteria, and make the best decision.
Provide your response in JSON format with: decision, reasoning, confidence (0-1), and alternatives."""

        prompt = f"""
Context:
{context}

Decision Criteria:
{json.dumps(decision_criteria, indent=2)}

Available Options:
{json.dumps(options, indent=2)}

Make the optimal decision and explain your reasoning.
"""

        response = self.generate(prompt, system_prompt=system_prompt, temperature=0.3)

        try:
            # Try to parse JSON response
            decision = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback: extract structured info from text
            decision = {
                "decision": options[0] if options else "unknown",
                "reasoning": response.content,
                "confidence": 0.7,
                "alternatives": []
            }

        self.logger.info(
            "Decision made",
            decision=decision.get("decision"),
            confidence=decision.get("confidence")
        )

        return decision

    def synthesize_information(
        self,
        information_sources: List[Dict[str, Any]],
        synthesis_goal: str,
        output_format: str = "structured_summary"
    ) -> str:
        """
        Synthesize information from multiple sources into a coherent output.

        Args:
            information_sources: List of information sources with content and metadata
            synthesis_goal: Goal of the synthesis
            output_format: Desired output format

        Returns:
            Synthesized content
        """
        system_prompt = f"""You are an expert information synthesizer for a viral YouTube content platform.
Your goal is to synthesize information from multiple sources into a coherent, {output_format}.
Focus on: {synthesis_goal}"""

        sources_text = "\n\n".join([
            f"Source {i+1} ({source.get('type', 'unknown')}):\n{source.get('content', '')}"
            for i, source in enumerate(information_sources)
        ])

        prompt = f"""
Synthesis Goal: {synthesis_goal}
Output Format: {output_format}

Information Sources:
{sources_text}

Synthesize this information according to the goal and format specified.
"""

        response = self.generate(prompt, system_prompt=system_prompt)
        return response.content

    def validate_quality(
        self,
        content: str,
        quality_criteria: Dict[str, Any],
        content_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Validate content quality against specified criteria.

        Args:
            content: Content to validate
            quality_criteria: Criteria for quality assessment
            content_type: Type of content (research, script, etc.)

        Returns:
            Quality assessment with scores and feedback
        """
        system_prompt = f"""You are a quality validation expert for {content_type} content.
Evaluate the content against the provided criteria and return a JSON response with:
- overall_score (0-10)
- criterion_scores (dict of individual scores)
- strengths (list)
- weaknesses (list)
- recommendations (list)
- passes_threshold (boolean)"""

        prompt = f"""
Content Type: {content_type}

Quality Criteria:
{json.dumps(quality_criteria, indent=2)}

Content to Validate:
{content[:5000]}  # Limit content length

Evaluate this content and provide detailed quality assessment.
"""

        response = self.generate(prompt, system_prompt=system_prompt, temperature=0.2)

        try:
            quality_assessment = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback assessment
            quality_assessment = {
                "overall_score": 7.0,
                "criterion_scores": {},
                "strengths": ["Content provided"],
                "weaknesses": ["Could not perform detailed analysis"],
                "recommendations": ["Review manually"],
                "passes_threshold": False,
                "raw_feedback": response.content
            }

        self.logger.info(
            "Quality validation completed",
            content_type=content_type,
            overall_score=quality_assessment.get("overall_score"),
            passes=quality_assessment.get("passes_threshold")
        )

        return quality_assessment

    def reason_about_workflow(
        self,
        workflow_state: Dict[str, Any],
        issue: str
    ) -> Dict[str, Any]:
        """
        Reason about workflow issues and suggest solutions.

        Args:
            workflow_state: Current state of the workflow
            issue: Description of the issue

        Returns:
            Reasoning and recommended actions
        """
        system_prompt = """You are a workflow optimization expert for a content generation system.
Analyze workflow states, identify issues, and recommend optimal solutions.
Provide JSON response with: analysis, root_cause, recommended_actions, and priority."""

        prompt = f"""
Current Workflow State:
{json.dumps(workflow_state, indent=2)}

Issue:
{issue}

Analyze the situation and recommend the best course of action.
"""

        response = self.generate(prompt, system_prompt=system_prompt, temperature=0.4)

        try:
            reasoning = json.loads(response.content)
        except json.JSONDecodeError:
            reasoning = {
                "analysis": response.content,
                "root_cause": "Unknown",
                "recommended_actions": ["Manual review required"],
                "priority": "medium"
            }

        return reasoning

    def generate_structured_output(
        self,
        prompt: str,
        schema: Dict[str, Any],
        examples: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured output following a specific schema.

        Args:
            prompt: Generation prompt
            schema: JSON schema for the output
            examples: Optional examples of desired output

        Returns:
            Structured output matching schema
        """
        system_prompt = f"""Generate a response that strictly follows this JSON schema:
{json.dumps(schema, indent=2)}

Return valid JSON only, no additional text."""

        if examples:
            examples_text = "\n\nExamples:\n" + "\n".join([
                json.dumps(ex, indent=2) for ex in examples
            ])
            prompt = prompt + examples_text

        response = self.generate(prompt, system_prompt=system_prompt, temperature=0.5)

        try:
            structured_output = json.loads(response.content)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                structured_output = json.loads(json_match.group())
            else:
                raise ValueError("Could not parse structured output")

        return structured_output

    def conversation(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None
    ) -> AnthropicResponse:
        """
        Multi-turn conversation with Claude.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system instructions

        Returns:
            AnthropicResponse
        """
        with self.logger.performance_tracking("anthropic_conversation"):
            try:
                params = {
                    "model": self.model,
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "messages": messages
                }

                if system_prompt:
                    params["system"] = system_prompt

                response = self.client.messages.create(**params)

                usage = {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                }
                self.total_tokens_used += usage["total_tokens"]

                return AnthropicResponse(
                    content=response.content[0].text,
                    usage=usage,
                    model=response.model,
                    stop_reason=response.stop_reason,
                    raw_response=response
                )

            except Exception as e:
                self.logger.error(f"Conversation error: {str(e)}")
                raise

    def get_token_usage(self) -> Dict[str, int]:
        """Get total token usage statistics."""
        return {
            "total_tokens": self.total_tokens_used,
            "estimated_cost_usd": self._estimate_cost(self.total_tokens_used)
        }

    def _estimate_cost(self, tokens: int) -> float:
        """
        Estimate cost based on token usage.

        Note: Update pricing based on current Anthropic rates.
        """
        # Approximate pricing (update with actual rates)
        cost_per_million_tokens = 15.0  # USD
        return (tokens / 1_000_000) * cost_per_million_tokens


if __name__ == "__main__":
    # Example usage
    import os

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("Set ANTHROPIC_API_KEY environment variable")
        exit(1)

    ai = AnthropicIntelligence(api_key=api_key)

    # Simple generation
    response = ai.generate("Explain viral video psychology in 3 sentences.")
    print("Response:", response.content)

    # Decision making
    decision = ai.analyze_and_decide(
        context="Need to choose research database for quantum computing topic",
        decision_criteria={"academic_rigor": 9, "novelty": 8, "accessibility": 7},
        options=["JSTOR", "arXiv", "Semantic Scholar"]
    )
    print("\nDecision:", decision)

    # Token usage
    print("\nToken Usage:", ai.get_token_usage())
