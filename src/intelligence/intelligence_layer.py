"""
Intelligence Layer - Main AI Reasoning and Synthesis Engine
Coordinates all AI operations across the system
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AIModel(Enum):
    """Supported AI models"""
    CLAUDE_OPUS = "claude-opus-4-20250514"
    CLAUDE_SONNET = "claude-sonnet-4-20250514"
    CLAUDE_HAIKU = "claude-haiku-4-20250319"
    GPT4 = "gpt-4-turbo"
    GPT4_MINI = "gpt-4o-mini"


class TaskComplexity(Enum):
    """Task complexity levels for model selection"""
    SIMPLE = "simple"        # Quick validations, simple tasks
    MODERATE = "moderate"    # Standard content generation
    COMPLEX = "complex"      # Research synthesis, complex reasoning
    EXPERT = "expert"        # Highest quality, maximum capability


@dataclass
class AIRequest:
    """Request to the AI layer"""
    prompt: str
    task_type: str
    complexity: TaskComplexity
    context: Optional[Dict[str, Any]] = None
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    stream: bool = False
    model_preference: Optional[AIModel] = None


@dataclass
class AIResponse:
    """Response from the AI layer"""
    content: str
    model_used: str
    tokens_used: int
    confidence_score: float
    reasoning_steps: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class IntelligenceLayer:
    """
    Main AI reasoning and synthesis engine
    Coordinates all AI operations with optimal model selection
    """

    def __init__(self, anthropic_client, openai_client=None):
        """
        Initialize the intelligence layer

        Args:
            anthropic_client: Anthropic API client
            openai_client: OpenAI API client (optional)
        """
        self.anthropic_client = anthropic_client
        self.openai_client = openai_client
        self.model_capabilities = self._init_model_capabilities()

        logger.info("Intelligence Layer initialized")

    def _init_model_capabilities(self) -> Dict[TaskComplexity, AIModel]:
        """Map task complexity to optimal model"""
        return {
            TaskComplexity.SIMPLE: AIModel.CLAUDE_HAIKU,
            TaskComplexity.MODERATE: AIModel.CLAUDE_SONNET,
            TaskComplexity.COMPLEX: AIModel.CLAUDE_SONNET,
            TaskComplexity.EXPERT: AIModel.CLAUDE_OPUS,
        }

    def _select_model(self, request: AIRequest) -> str:
        """
        Select optimal model based on task complexity

        Args:
            request: AI request with complexity level

        Returns:
            Model identifier string
        """
        if request.model_preference:
            return request.model_preference.value

        optimal_model = self.model_capabilities.get(
            request.complexity,
            AIModel.CLAUDE_SONNET
        )

        logger.debug(f"Selected {optimal_model.value} for {request.complexity.value} task")
        return optimal_model.value

    async def generate(self, request: AIRequest) -> AIResponse:
        """
        Generate AI response with optimal model selection

        Args:
            request: AI generation request

        Returns:
            AI response with content and metadata
        """
        try:
            model = self._select_model(request)

            # Prepare the prompt
            messages = [
                {
                    "role": "user",
                    "content": request.prompt
                }
            ]

            # Add context if provided
            if request.context:
                context_str = self._format_context(request.context)
                messages[0]["content"] = f"{context_str}\n\n{request.prompt}"

            # Determine max tokens
            max_tokens = request.max_tokens or self._get_default_tokens(request.complexity)

            logger.info(f"Generating with {model}, max_tokens={max_tokens}")

            # Call Anthropic API
            if request.stream:
                # Streaming response
                response_content = ""
                async for chunk in self.anthropic_client.stream_message(
                    messages=messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=request.temperature
                ):
                    response_content += chunk

                return AIResponse(
                    content=response_content,
                    model_used=model,
                    tokens_used=len(response_content.split()),  # Approximate
                    confidence_score=0.85,
                    metadata={"streamed": True}
                )
            else:
                # Standard response
                response = await self.anthropic_client.create_message(
                    messages=messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=request.temperature
                )

                content = response.content[0].text

                return AIResponse(
                    content=content,
                    model_used=model,
                    tokens_used=response.usage.output_tokens,
                    confidence_score=self._calculate_confidence(response),
                    metadata={
                        "input_tokens": response.usage.input_tokens,
                        "stop_reason": response.stop_reason
                    }
                )

        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            raise

    def generate_sync(self, request: AIRequest) -> AIResponse:
        """
        Synchronous version of generate

        Args:
            request: AI generation request

        Returns:
            AI response
        """
        try:
            model = self._select_model(request)
            max_tokens = request.max_tokens or self._get_default_tokens(request.complexity)

            logger.info(f"Generating (sync) with {model}")

            # Prepare prompt with context
            prompt = request.prompt
            if request.context:
                context_str = self._format_context(request.context)
                prompt = f"{context_str}\n\n{request.prompt}"

            # Call Anthropic API (sync)
            response = self.anthropic_client.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=request.temperature
            )

            return AIResponse(
                content=response,
                model_used=model,
                tokens_used=len(response.split()),
                confidence_score=0.85,
                metadata={"sync": True}
            )

        except Exception as e:
            logger.error(f"Sync generation failed: {e}")
            raise

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary as a string"""
        context_parts = []
        for key, value in context.items():
            context_parts.append(f"**{key.upper()}**:\n{value}")
        return "\n\n".join(context_parts)

    def _get_default_tokens(self, complexity: TaskComplexity) -> int:
        """Get default max tokens based on complexity"""
        token_map = {
            TaskComplexity.SIMPLE: 1024,
            TaskComplexity.MODERATE: 4096,
            TaskComplexity.COMPLEX: 8192,
            TaskComplexity.EXPERT: 16384,
        }
        return token_map.get(complexity, 4096)

    def _calculate_confidence(self, response: Any) -> float:
        """
        Calculate confidence score based on response characteristics

        Args:
            response: API response object

        Returns:
            Confidence score (0-1)
        """
        # Simple heuristic - can be enhanced
        if not hasattr(response, 'stop_reason'):
            return 0.75

        if response.stop_reason == "end_turn":
            return 0.95
        elif response.stop_reason == "max_tokens":
            return 0.70
        else:
            return 0.80

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text

        Args:
            text: Text to analyze

        Returns:
            Sentiment analysis results
        """
        request = AIRequest(
            prompt=f"""Analyze the sentiment of the following text. Provide:
            1. Overall sentiment (positive/negative/neutral)
            2. Sentiment score (0-10)
            3. Key emotional indicators
            4. Tone analysis

            Text: {text}

            Respond in JSON format.""",
            task_type="sentiment_analysis",
            complexity=TaskComplexity.SIMPLE,
            temperature=0.3
        )

        response = await self.generate(request)

        # Parse JSON response
        try:
            import json
            result = json.loads(response.content)
            return result
        except:
            return {
                "sentiment": "neutral",
                "score": 5.0,
                "raw_response": response.content
            }

    async def extract_key_concepts(self, text: str, max_concepts: int = 10) -> List[str]:
        """
        Extract key concepts from text

        Args:
            text: Text to analyze
            max_concepts: Maximum number of concepts

        Returns:
            List of key concepts
        """
        request = AIRequest(
            prompt=f"""Extract the {max_concepts} most important concepts from this text.
            Return ONLY a JSON array of concept strings.

            Text: {text}""",
            task_type="concept_extraction",
            complexity=TaskComplexity.SIMPLE,
            temperature=0.2
        )

        response = await self.generate(request)

        try:
            import json
            concepts = json.loads(response.content)
            return concepts[:max_concepts]
        except:
            # Fallback: split by newlines
            return [line.strip('- ').strip()
                   for line in response.content.split('\n')
                   if line.strip()][:max_concepts]

    async def validate_accuracy(
        self,
        claim: str,
        sources: List[str]
    ) -> Tuple[bool, float, str]:
        """
        Validate accuracy of a claim against sources

        Args:
            claim: Claim to validate
            sources: List of source texts

        Returns:
            Tuple of (is_accurate, confidence, reasoning)
        """
        sources_text = "\n\n".join([f"Source {i+1}: {s}" for i, s in enumerate(sources)])

        request = AIRequest(
            prompt=f"""Validate this claim against the provided sources.

            Claim: {claim}

            {sources_text}

            Respond with:
            1. Is the claim accurate? (true/false)
            2. Confidence level (0.0-1.0)
            3. Detailed reasoning

            Format as JSON.""",
            task_type="fact_checking",
            complexity=TaskComplexity.MODERATE,
            temperature=0.1
        )

        response = await self.generate(request)

        try:
            import json
            result = json.loads(response.content)
            return (
                result.get('accurate', False),
                result.get('confidence', 0.5),
                result.get('reasoning', response.content)
            )
        except:
            return (True, 0.5, response.content)

    async def synthesize_insights(self, data_points: List[Dict[str, Any]]) -> str:
        """
        Synthesize insights from multiple data points

        Args:
            data_points: List of data dictionaries

        Returns:
            Synthesized insights
        """
        data_str = "\n\n".join([
            f"Data Point {i+1}:\n" + "\n".join([f"  {k}: {v}" for k, v in dp.items()])
            for i, dp in enumerate(data_points)
        ])

        request = AIRequest(
            prompt=f"""Synthesize key insights from these data points.
            Identify patterns, connections, and novel insights.

            {data_str}

            Provide a comprehensive synthesis.""",
            task_type="insight_synthesis",
            complexity=TaskComplexity.COMPLEX,
            temperature=0.6
        )

        response = await self.generate(request)
        return response.content

    def get_model_stats(self) -> Dict[str, Any]:
        """Get statistics about model usage"""
        return {
            "available_models": [model.value for model in AIModel],
            "complexity_mapping": {
                c.value: m.value
                for c, m in self.model_capabilities.items()
            },
            "anthropic_available": self.anthropic_client is not None,
            "openai_available": self.openai_client is not None
        }
