"""
Anthropic Claude API Integration
Provides intelligent text generation and analysis capabilities
"""
import anthropic
from typing import Dict, Any, List, Optional, Union
import logging
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GenerationResult:
    """Result from AI generation"""
    content: str
    model: str
    tokens_used: int
    stop_reason: str
    metadata: Dict[str, Any]


class AnthropicClient:
    """
    High-level Anthropic Claude API client
    Provides intelligent text generation with retry logic and error handling
    """

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929",
                 max_tokens: int = 8000, temperature: float = 0.7, timeout: int = 300):
        """
        Initialize Anthropic client

        Args:
            api_key: Anthropic API key
            model: Claude model to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-1.0)
            timeout: Request timeout in seconds
        """
        if not api_key:
            raise ValueError("Anthropic API key is required")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout
        self.total_tokens_used = 0

        logger.info(f"Anthropic client initialized with model: {model}")

    def generate(
            self,
            prompt: str,
            system_prompt: Optional[str] = None,
            max_tokens: Optional[int] = None,
            temperature: Optional[float] = None,
            stop_sequences: Optional[List[str]] = None,
            metadata: Optional[Dict[str, Any]] = None
    ) -> GenerationResult:
        """
        Generate text using Claude

        Args:
            prompt: User prompt
            system_prompt: System instructions
            max_tokens: Override default max tokens
            temperature: Override default temperature
            stop_sequences: Sequences that stop generation
            metadata: Additional metadata to include

        Returns:
            GenerationResult with generated content
        """
        try:
            # Build message
            messages = [{"role": "user", "content": prompt}]

            # Build request parameters
            params = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": temperature if temperature is not None else self.temperature,
            }

            if system_prompt:
                params["system"] = system_prompt

            if stop_sequences:
                params["stop_sequences"] = stop_sequences

            # Make API call with retry logic
            response = self._call_with_retry(params)

            # Extract content
            content = response.content[0].text

            # Track token usage
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            self.total_tokens_used += tokens_used

            result = GenerationResult(
                content=content,
                model=response.model,
                tokens_used=tokens_used,
                stop_reason=response.stop_reason,
                metadata=metadata or {}
            )

            logger.info(f"Generated {len(content)} characters using {tokens_used} tokens")

            return result

        except Exception as e:
            logger.error(f"Error in generate: {e}")
            raise

    def generate_with_examples(
            self,
            prompt: str,
            examples: List[Dict[str, str]],
            system_prompt: Optional[str] = None,
            **kwargs
    ) -> GenerationResult:
        """
        Generate text with few-shot examples

        Args:
            prompt: User prompt
            examples: List of example conversations [{"user": "...", "assistant": "..."}]
            system_prompt: System instructions
            **kwargs: Additional generation parameters

        Returns:
            GenerationResult
        """
        # Build messages with examples
        messages = []
        for example in examples:
            messages.append({"role": "user", "content": example["user"]})
            messages.append({"role": "assistant", "content": example["assistant"]})

        messages.append({"role": "user", "content": prompt})

        # Build parameters
        params = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get('max_tokens', self.max_tokens),
            "temperature": kwargs.get('temperature', self.temperature),
        }

        if system_prompt:
            params["system"] = system_prompt

        # Make API call
        response = self._call_with_retry(params)

        content = response.content[0].text
        tokens_used = response.usage.input_tokens + response.usage.output_tokens
        self.total_tokens_used += tokens_used

        return GenerationResult(
            content=content,
            model=response.model,
            tokens_used=tokens_used,
            stop_reason=response.stop_reason,
            metadata=kwargs.get('metadata', {})
        )

    def generate_structured(
            self,
            prompt: str,
            structure_description: str,
            system_prompt: Optional[str] = None,
            **kwargs
    ) -> GenerationResult:
        """
        Generate structured output (JSON, YAML, etc.)

        Args:
            prompt: User prompt
            structure_description: Description of expected structure
            system_prompt: System instructions
            **kwargs: Additional parameters

        Returns:
            GenerationResult
        """
        # Enhanced system prompt for structured output
        structured_system = f"""You are an AI assistant that generates structured, well-formatted output.

{structure_description}

Always ensure your output follows the exact structure specified. Be precise and thorough."""

        if system_prompt:
            structured_system = f"{system_prompt}\n\n{structured_system}"

        return self.generate(
            prompt=prompt,
            system_prompt=structured_system,
            **kwargs
        )

    def analyze(
            self,
            content: str,
            analysis_prompt: str,
            system_prompt: Optional[str] = None,
            **kwargs
    ) -> GenerationResult:
        """
        Analyze content using Claude

        Args:
            content: Content to analyze
            analysis_prompt: What to analyze for
            system_prompt: System instructions
            **kwargs: Additional parameters

        Returns:
            GenerationResult with analysis
        """
        full_prompt = f"""{analysis_prompt}

Content to analyze:
{content}

Provide a detailed analysis."""

        return self.generate(
            prompt=full_prompt,
            system_prompt=system_prompt,
            **kwargs
        )

    def refine(
            self,
            content: str,
            refinement_instructions: str,
            system_prompt: Optional[str] = None,
            **kwargs
    ) -> GenerationResult:
        """
        Refine existing content

        Args:
            content: Content to refine
            refinement_instructions: How to refine it
            system_prompt: System instructions
            **kwargs: Additional parameters

        Returns:
            GenerationResult with refined content
        """
        prompt = f"""{refinement_instructions}

Original content:
{content}

Provide the refined version:"""

        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            **kwargs
        )

    def _call_with_retry(self, params: Dict[str, Any], max_retries: int = 3) -> Any:
        """
        Call Anthropic API with exponential backoff retry

        Args:
            params: API parameters
            max_retries: Maximum number of retries

        Returns:
            API response
        """
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(**params)
                return response

            except anthropic.RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limit hit, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise

            except anthropic.APITimeoutError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"API timeout, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise

            except anthropic.APIConnectionError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Connection error, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise

            except Exception as e:
                logger.error(f"Unexpected error in API call: {e}")
                raise

        raise Exception("Max retries exceeded")

    def get_token_usage(self) -> int:
        """Get total tokens used in this session"""
        return self.total_tokens_used

    def reset_token_usage(self):
        """Reset token usage counter"""
        self.total_tokens_used = 0

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        Rough approximation: 1 token ≈ 4 characters

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        return len(text) // 4

    def validate_prompt_length(self, prompt: str, max_input_tokens: int = 100000) -> bool:
        """
        Validate that prompt doesn't exceed token limits

        Args:
            prompt: Prompt to validate
            max_input_tokens: Maximum input tokens

        Returns:
            True if valid, raises ValueError if not
        """
        estimated = self.estimate_tokens(prompt)

        if estimated > max_input_tokens:
            raise ValueError(
                f"Prompt too long: ~{estimated} tokens (max: {max_input_tokens})"
            )

        return True
