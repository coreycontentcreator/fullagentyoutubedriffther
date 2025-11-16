"""
Reasoning Engine - Causal Reasoning and Pattern Detection
Advanced logical reasoning capabilities
"""

import logging
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ReasoningType(Enum):
    """Types of reasoning"""
    DEDUCTIVE = "deductive"      # General to specific
    INDUCTIVE = "inductive"      # Specific to general
    ABDUCTIVE = "abductive"      # Best explanation
    CAUSAL = "causal"           # Cause and effect
    ANALOGICAL = "analogical"    # By analogy


@dataclass
class ReasoningStep:
    """Single step in reasoning chain"""
    step_number: int
    reasoning_type: ReasoningType
    premise: str
    inference: str
    conclusion: str
    confidence: float


@dataclass
class ReasoningChain:
    """Complete chain of reasoning"""
    steps: List[ReasoningStep]
    final_conclusion: str
    overall_confidence: float
    reasoning_path: str


class ReasoningEngine:
    """
    Advanced reasoning engine for causal analysis and pattern detection
    """

    def __init__(self, intelligence_layer):
        """
        Initialize reasoning engine

        Args:
            intelligence_layer: Intelligence layer for AI operations
        """
        self.intelligence = intelligence_layer
        logger.info("Reasoning Engine initialized")

    async def analyze_causal_relationships(
        self,
        phenomenon: str,
        context: str
    ) -> Dict[str, Any]:
        """
        Analyze causal relationships in a phenomenon

        Args:
            phenomenon: The phenomenon to analyze
            context: Additional context

        Returns:
            Causal analysis results
        """
        from .intelligence_layer import AIRequest, TaskComplexity

        prompt = f"""Analyze the causal relationships in the following phenomenon.

        Phenomenon: {phenomenon}

        Context: {context}

        Provide:
        1. Primary causes (direct causation)
        2. Secondary causes (contributing factors)
        3. Mediating variables
        4. Causal chain (step-by-step)
        5. Confidence level for each relationship

        Format as structured JSON."""

        request = AIRequest(
            prompt=prompt,
            task_type="causal_analysis",
            complexity=TaskComplexity.COMPLEX,
            temperature=0.3
        )

        response = await self.intelligence.generate(request)

        try:
            import json
            return json.loads(response.content)
        except:
            return {
                "primary_causes": [],
                "secondary_causes": [],
                "raw_analysis": response.content
            }

    async def detect_contradictions(
        self,
        statements: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Detect contradictions between statements

        Args:
            statements: List of statements to analyze

        Returns:
            List of detected contradictions
        """
        from .intelligence_layer import AIRequest, TaskComplexity

        statements_text = "\n".join([
            f"{i+1}. {stmt}"
            for i, stmt in enumerate(statements)
        ])

        prompt = f"""Analyze these statements for contradictions.

        Statements:
        {statements_text}

        For each contradiction found, provide:
        1. Statement IDs that contradict
        2. Nature of contradiction
        3. Severity (low/medium/high)
        4. Resolution suggestions

        Format as JSON array."""

        request = AIRequest(
            prompt=prompt,
            task_type="contradiction_detection",
            complexity=TaskComplexity.MODERATE,
            temperature=0.2
        )

        response = await self.intelligence.generate(request)

        try:
            import json
            return json.loads(response.content)
        except:
            return []

    async def identify_patterns(
        self,
        data: List[Any],
        pattern_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Identify patterns in data

        Args:
            data: Data to analyze
            pattern_type: Type of patterns to look for

        Returns:
            Identified patterns and their characteristics
        """
        from .intelligence_layer import AIRequest, TaskComplexity

        data_str = "\n".join([str(item) for item in data])

        prompt = f"""Identify {pattern_type} patterns in this data.

        Data:
        {data_str}

        Provide:
        1. Patterns found (describe each)
        2. Pattern frequency/strength
        3. Statistical significance
        4. Outliers or anomalies
        5. Predictive insights

        Format as JSON."""

        request = AIRequest(
            prompt=prompt,
            task_type="pattern_detection",
            complexity=TaskComplexity.COMPLEX,
            temperature=0.4
        )

        response = await self.intelligence.generate(request)

        try:
            import json
            return json.loads(response.content)
        except:
            return {
                "patterns": [],
                "raw_analysis": response.content
            }

    async def build_reasoning_chain(
        self,
        question: str,
        evidence: List[str],
        reasoning_type: ReasoningType = ReasoningType.DEDUCTIVE
    ) -> ReasoningChain:
        """
        Build a complete reasoning chain

        Args:
            question: Question to answer
            evidence: Supporting evidence
            reasoning_type: Type of reasoning to use

        Returns:
            Complete reasoning chain
        """
        from .intelligence_layer import AIRequest, TaskComplexity

        evidence_text = "\n".join([f"- {e}" for e in evidence])

        prompt = f"""Build a {reasoning_type.value} reasoning chain to answer this question.

        Question: {question}

        Evidence:
        {evidence_text}

        Provide step-by-step reasoning:
        1. Start with premises
        2. Show each inference step
        3. Explain logical connections
        4. Build to final conclusion
        5. Assess confidence at each step

        Format as structured JSON with steps array."""

        request = AIRequest(
            prompt=prompt,
            task_type="reasoning_chain",
            complexity=TaskComplexity.EXPERT,
            temperature=0.3
        )

        response = await self.intelligence.generate(request)

        try:
            import json
            data = json.loads(response.content)

            steps = []
            for i, step_data in enumerate(data.get('steps', [])):
                step = ReasoningStep(
                    step_number=i + 1,
                    reasoning_type=reasoning_type,
                    premise=step_data.get('premise', ''),
                    inference=step_data.get('inference', ''),
                    conclusion=step_data.get('conclusion', ''),
                    confidence=step_data.get('confidence', 0.5)
                )
                steps.append(step)

            return ReasoningChain(
                steps=steps,
                final_conclusion=data.get('final_conclusion', ''),
                overall_confidence=data.get('overall_confidence', 0.5),
                reasoning_path=response.content
            )

        except Exception as e:
            logger.error(f"Failed to parse reasoning chain: {e}")
            return ReasoningChain(
                steps=[],
                final_conclusion="Unable to build reasoning chain",
                overall_confidence=0.0,
                reasoning_path=response.content
            )

    async def evaluate_argument_strength(
        self,
        argument: str,
        criteria: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate the strength of an argument

        Args:
            argument: Argument to evaluate
            criteria: Optional evaluation criteria

        Returns:
            Argument strength evaluation
        """
        from .intelligence_layer import AIRequest, TaskComplexity

        criteria_text = ""
        if criteria:
            criteria_text = "\n".join([f"- {c}" for c in criteria])

        prompt = f"""Evaluate the strength of this argument.

        Argument: {argument}

        {f'Evaluation Criteria:\n{criteria_text}' if criteria else ''}

        Assess:
        1. Logical validity
        2. Premise soundness
        3. Evidence quality
        4. Reasoning clarity
        5. Potential fallacies
        6. Overall strength (0-10)

        Format as JSON."""

        request = AIRequest(
            prompt=prompt,
            task_type="argument_evaluation",
            complexity=TaskComplexity.MODERATE,
            temperature=0.2
        )

        response = await self.intelligence.generate(request)

        try:
            import json
            return json.loads(response.content)
        except:
            return {
                "strength": 5.0,
                "raw_evaluation": response.content
            }

    async def generate_hypothesis(
        self,
        observations: List[str],
        domain: str
    ) -> List[Dict[str, Any]]:
        """
        Generate hypotheses from observations (abductive reasoning)

        Args:
            observations: List of observations
            domain: Domain context

        Returns:
            List of hypotheses with plausibility scores
        """
        from .intelligence_layer import AIRequest, TaskComplexity

        obs_text = "\n".join([f"{i+1}. {obs}" for i, obs in enumerate(observations)])

        prompt = f"""Generate plausible hypotheses to explain these observations in the {domain} domain.

        Observations:
        {obs_text}

        For each hypothesis:
        1. Description
        2. Explanatory power (how well it explains observations)
        3. Plausibility (0-1)
        4. Testable predictions
        5. Required evidence

        Provide 3-5 hypotheses ranked by plausibility.
        Format as JSON array."""

        request = AIRequest(
            prompt=prompt,
            task_type="hypothesis_generation",
            complexity=TaskComplexity.COMPLEX,
            temperature=0.6
        )

        response = await self.intelligence.generate(request)

        try:
            import json
            return json.loads(response.content)
        except:
            return []

    async def analogical_reasoning(
        self,
        source_domain: str,
        target_domain: str,
        problem: str
    ) -> Dict[str, Any]:
        """
        Apply analogical reasoning between domains

        Args:
            source_domain: Domain with known solution
            target_domain: Domain to apply analogy to
            problem: Problem to solve

        Returns:
            Analogical mapping and solution
        """
        from .intelligence_layer import AIRequest, TaskComplexity

        prompt = f"""Use analogical reasoning to solve this problem.

        Source Domain: {source_domain}
        Target Domain: {target_domain}
        Problem: {problem}

        Provide:
        1. Structural mapping between domains
        2. Key similarities and differences
        3. Analogical solution
        4. Validity assessment
        5. Limitations of the analogy

        Format as JSON."""

        request = AIRequest(
            prompt=prompt,
            task_type="analogical_reasoning",
            complexity=TaskComplexity.COMPLEX,
            temperature=0.5
        )

        response = await self.intelligence.generate(request)

        try:
            import json
            return json.loads(response.content)
        except:
            return {
                "mapping": {},
                "solution": response.content
            }

    def explain_reasoning(self, chain: ReasoningChain) -> str:
        """
        Generate human-readable explanation of reasoning chain

        Args:
            chain: Reasoning chain to explain

        Returns:
            Human-readable explanation
        """
        explanation = f"Reasoning Path ({len(chain.steps)} steps):\n\n"

        for step in chain.steps:
            explanation += f"Step {step.step_number} ({step.reasoning_type.value}):\n"
            explanation += f"  Premise: {step.premise}\n"
            explanation += f"  Inference: {step.inference}\n"
            explanation += f"  Conclusion: {step.conclusion}\n"
            explanation += f"  Confidence: {step.confidence:.2f}\n\n"

        explanation += f"Final Conclusion: {chain.final_conclusion}\n"
        explanation += f"Overall Confidence: {chain.overall_confidence:.2f}"

        return explanation
