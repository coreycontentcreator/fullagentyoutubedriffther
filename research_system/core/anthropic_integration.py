"""
Anthropic API Integration for Claude Intelligence
Provides high-level interface for AI-powered research synthesis and analysis
"""

import anthropic
from typing import Dict, Any, List, Optional, Union
import logging
import json
import asyncio
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ClaudeModel(Enum):
    """Available Claude models"""
    SONNET_4_5 = "claude-sonnet-4-5-20250929"
    SONNET_3_5 = "claude-3-5-sonnet-20241022"
    HAIKU_3_5 = "claude-3-5-haiku-20241022"
    OPUS_3 = "claude-3-opus-20240229"


@dataclass
class ClaudeResponse:
    """Response from Claude API"""
    content: str
    model: str
    usage: Dict[str, int]
    stop_reason: str
    raw_response: Any = None


class AnthropicIntegration:
    """
    Integration layer for Anthropic's Claude API
    Handles all AI-powered research synthesis and analysis
    """

    def __init__(self, api_key: str, default_model: str = ClaudeModel.SONNET_4_5.value):
        """
        Initialize Anthropic integration

        Args:
            api_key: Anthropic API key
            default_model: Default model to use
        """
        if not api_key:
            raise ValueError("Anthropic API key is required")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.default_model = default_model
        self.total_tokens_used = 0

        logger.info(f"Anthropic integration initialized with model: {default_model}")

    def generate_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        system_prompt: Optional[str] = None,
        thinking_enabled: bool = False
    ) -> ClaudeResponse:
        """
        Generate a completion using Claude

        Args:
            prompt: User prompt
            model: Model to use (defaults to self.default_model)
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (0.0-1.0)
            system_prompt: System prompt to guide behavior
            thinking_enabled: Enable extended thinking for complex tasks

        Returns:
            ClaudeResponse object with generated content
        """
        model = model or self.default_model

        try:
            # Build messages
            messages = [{"role": "user", "content": prompt}]

            # Build request parameters
            request_params = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            }

            # Add system prompt if provided
            if system_prompt:
                request_params["system"] = system_prompt

            # Enable thinking mode if requested
            if thinking_enabled:
                request_params["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": 10000
                }

            # Make API call
            response = self.client.messages.create(**request_params)

            # Extract content
            content = ""
            for block in response.content:
                if block.type == "text":
                    content += block.text

            # Track token usage
            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
            self.total_tokens_used += usage["input_tokens"] + usage["output_tokens"]

            logger.info(f"Generated completion using {model} ({usage['output_tokens']} tokens)")

            return ClaudeResponse(
                content=content,
                model=model,
                usage=usage,
                stop_reason=response.stop_reason,
                raw_response=response
            )

        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            raise

    def synthesize_research(
        self,
        papers: List[Dict[str, Any]],
        topic: str,
        focus_areas: Optional[List[str]] = None
    ) -> str:
        """
        Synthesize research findings from multiple papers using Claude

        Args:
            papers: List of research papers with metadata
            topic: Research topic
            focus_areas: Specific areas to focus on

        Returns:
            Synthesized research summary
        """
        # Prepare paper summaries
        paper_summaries = []
        for i, paper in enumerate(papers[:30], 1):  # Limit to 30 for context
            summary = f"""
Paper {i}:
Title: {paper.get('title', 'Unknown')}
Authors: {', '.join(paper.get('authors', [])[:3])}
Year: {paper.get('year', 'Unknown')}
Source: {paper.get('source', 'Unknown')}
Abstract: {paper.get('abstract', 'No abstract available')[:500]}
Citations: {paper.get('citation_count', 0)}
"""
            paper_summaries.append(summary)

        papers_text = "\n---\n".join(paper_summaries)

        # Build synthesis prompt
        system_prompt = """You are a world-class academic research synthesizer. Your task is to:
1. Analyze research papers from multiple sources
2. Identify key themes, patterns, and insights
3. Synthesize findings into a coherent narrative
4. Highlight novel insights and contradictions
5. Maintain academic rigor and proper attribution"""

        focus_text = ""
        if focus_areas:
            focus_text = f"\n\nFocus particularly on these areas: {', '.join(focus_areas)}"

        prompt = f"""Synthesize the following research papers on the topic: "{topic}"{focus_text}

Research Papers:
{papers_text}

Please provide a comprehensive synthesis that includes:
1. **Overview**: Main themes and consensus
2. **Key Insights**: Novel findings and important discoveries
3. **Contradictions**: Any conflicting findings or debates
4. **Knowledge Gaps**: What's missing or needs more research
5. **Implications**: Practical or theoretical implications

Format your response in clear, well-structured markdown."""

        response = self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4096,
            temperature=0.7,
            thinking_enabled=True  # Enable thinking for complex synthesis
        )

        return response.content

    def analyze_credibility(
        self,
        paper: Dict[str, Any],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze the credibility of a research paper using Claude

        Args:
            paper: Research paper metadata
            context: Additional context for analysis

        Returns:
            Credibility analysis with scores
        """
        system_prompt = """You are an expert academic evaluator specializing in research credibility assessment.
Analyze papers based on: author credentials, publication venue, methodology, citation patterns, and bias indicators."""

        context_text = f"\n\nContext: {context}" if context else ""

        prompt = f"""Analyze the credibility of this research paper:{context_text}

Title: {paper.get('title', 'Unknown')}
Authors: {', '.join(paper.get('authors', []))}
Publication: {paper.get('publication', 'Unknown')}
Year: {paper.get('year', 'Unknown')}
Citations: {paper.get('citation_count', 0)}
Abstract: {paper.get('abstract', 'No abstract')}

Provide a JSON response with:
{{
  "credibility_score": 0-10,
  "author_reputation": 0-10,
  "publication_quality": 0-10,
  "methodology_rigor": 0-10,
  "bias_indicators": ["list of potential biases"],
  "strengths": ["key strengths"],
  "weaknesses": ["key weaknesses"],
  "overall_assessment": "brief summary"
}}

Return ONLY valid JSON, no other text."""

        response = self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1024,
            temperature=0.3
        )

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback if response isn't valid JSON
            logger.warning("Could not parse credibility analysis as JSON")
            return {
                "credibility_score": 7.0,
                "overall_assessment": response.content
            }

    def fact_check_claim(
        self,
        claim: str,
        evidence: List[Dict[str, Any]],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fact-check a claim against multiple sources

        Args:
            claim: Claim to fact-check
            evidence: List of evidence sources
            context: Additional context

        Returns:
            Fact-check result with confidence and supporting evidence
        """
        evidence_text = "\n\n".join([
            f"Source {i+1} ({ev.get('source', 'Unknown')}):\n{ev.get('content', '')[:500]}"
            for i, ev in enumerate(evidence[:10])
        ])

        context_text = f"\n\nContext: {context}" if context else ""

        system_prompt = """You are an expert fact-checker specializing in academic research.
Evaluate claims based on evidence quality, source credibility, and logical consistency."""

        prompt = f"""Fact-check this claim against the provided evidence:{context_text}

Claim: "{claim}"

Evidence:
{evidence_text}

Provide a JSON response with:
{{
  "verdict": "SUPPORTED" | "PARTIALLY_SUPPORTED" | "CONTRADICTED" | "INSUFFICIENT_EVIDENCE",
  "confidence": 0-10,
  "supporting_evidence": ["list of supporting points"],
  "contradicting_evidence": ["list of contradictions"],
  "reasoning": "detailed explanation",
  "caveats": ["important limitations or caveats"]
}}

Return ONLY valid JSON."""

        response = self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1024,
            temperature=0.2
        )

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            logger.warning("Could not parse fact-check result as JSON")
            return {
                "verdict": "INSUFFICIENT_EVIDENCE",
                "confidence": 5.0,
                "reasoning": response.content
            }

    def generate_insights(
        self,
        research_data: Dict[str, Any],
        research_question: str
    ) -> List[str]:
        """
        Generate novel insights from research data

        Args:
            research_data: Structured research data
            research_question: Research question to address

        Returns:
            List of novel insights
        """
        system_prompt = """You are a world-class research analyst specializing in identifying novel insights.
Look for: unexpected connections, contradictions, gaps, emerging patterns, and practical implications."""

        prompt = f"""Based on this research data, generate novel insights for the question: "{research_question}"

Research Data:
{json.dumps(research_data, indent=2)[:3000]}

Provide 5-10 novel, actionable insights that go beyond surface-level observations.
Format as a JSON array of strings.

Return ONLY a valid JSON array: ["insight 1", "insight 2", ...]"""

        response = self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2048,
            temperature=0.8,
            thinking_enabled=True
        )

        try:
            insights = json.loads(response.content)
            if isinstance(insights, list):
                return insights
        except json.JSONDecodeError:
            pass

        # Fallback: parse as text
        insights = [line.strip() for line in response.content.split('\n')
                   if line.strip() and not line.strip().startswith('[')]
        return insights[:10]

    def identify_knowledge_gaps(
        self,
        research_synthesis: str,
        topic: str
    ) -> List[str]:
        """
        Identify knowledge gaps in research

        Args:
            research_synthesis: Synthesized research
            topic: Research topic

        Returns:
            List of identified knowledge gaps
        """
        system_prompt = """You are an expert at identifying research gaps and unexplored areas.
Focus on: methodological limitations, understudied areas, conflicting findings, and emerging questions."""

        prompt = f"""Analyze this research synthesis and identify knowledge gaps for the topic: "{topic}"

Research Synthesis:
{research_synthesis[:3000]}

Identify 5-10 specific knowledge gaps or research opportunities.
Format as a JSON array of strings.

Return ONLY a valid JSON array: ["gap 1", "gap 2", ...]"""

        response = self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1024,
            temperature=0.7
        )

        try:
            gaps = json.loads(response.content)
            if isinstance(gaps, list):
                return gaps
        except json.JSONDecodeError:
            pass

        # Fallback
        gaps = [line.strip() for line in response.content.split('\n')
               if line.strip() and not line.strip().startswith('[')]
        return gaps[:10]

    def get_usage_stats(self) -> Dict[str, int]:
        """
        Get API usage statistics

        Returns:
            Dictionary with usage stats
        """
        return {
            "total_tokens_used": self.total_tokens_used
        }

    def reset_usage_stats(self) -> None:
        """Reset usage statistics"""
        self.total_tokens_used = 0
        logger.info("Usage statistics reset")
