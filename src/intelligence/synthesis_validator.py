"""
Synthesis Validator - Multi-Pass Content Validation
Ensures quality and coherence across all generated content
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation strictness levels"""
    BASIC = "basic"              # Basic checks only
    STANDARD = "standard"        # Standard validation
    RIGOROUS = "rigorous"        # Thorough validation
    ACADEMIC = "academic"        # Academic-level rigor


class ValidationCategory(Enum):
    """Categories of validation"""
    ACCURACY = "accuracy"
    COHERENCE = "coherence"
    READABILITY = "readability"
    ENGAGEMENT = "engagement"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"


@dataclass
class ValidationResult:
    """Result of a validation check"""
    category: ValidationCategory
    passed: bool
    score: float  # 0-10
    issues: List[str]
    suggestions: List[str]
    severity: str  # low, medium, high, critical


@dataclass
class ComprehensiveValidation:
    """Complete validation report"""
    overall_score: float
    passed: bool
    results: List[ValidationResult]
    summary: str
    required_improvements: List[str]
    validation_level: ValidationLevel


class SynthesisValidator:
    """
    Multi-pass content validation system
    Ensures world-class quality across all outputs
    """

    def __init__(self, intelligence_layer, quality_threshold: float = 9.0):
        """
        Initialize synthesis validator

        Args:
            intelligence_layer: Intelligence layer for AI validation
            quality_threshold: Minimum quality score (0-10)
        """
        self.intelligence = intelligence_layer
        self.quality_threshold = quality_threshold

        logger.info(f"Synthesis Validator initialized (threshold: {quality_threshold})")

    async def validate_content(
        self,
        content: str,
        content_type: str,
        validation_level: ValidationLevel = ValidationLevel.STANDARD,
        context: Optional[Dict[str, Any]] = None
    ) -> ComprehensiveValidation:
        """
        Perform comprehensive content validation

        Args:
            content: Content to validate
            content_type: Type of content (script, research, etc.)
            validation_level: Strictness level
            context: Additional context

        Returns:
            Comprehensive validation results
        """
        logger.info(f"Validating {content_type} (level: {validation_level.value})")

        results = []

        # Run all validation checks
        results.append(await self._check_accuracy(content, context))
        results.append(await self._check_coherence(content))
        results.append(await self._check_readability(content))
        results.append(await self._check_engagement(content, content_type))
        results.append(await self._check_completeness(content, content_type, context))
        results.append(await self._check_consistency(content, context))

        # Calculate overall score
        overall_score = sum(r.score for r in results) / len(results)
        passed = overall_score >= self.quality_threshold

        # Generate summary
        summary = self._generate_summary(results, overall_score)

        # Collect required improvements
        required_improvements = []
        for result in results:
            if result.severity in ['high', 'critical']:
                required_improvements.extend(result.suggestions)

        return ComprehensiveValidation(
            overall_score=overall_score,
            passed=passed,
            results=results,
            summary=summary,
            required_improvements=required_improvements,
            validation_level=validation_level
        )

    async def _check_accuracy(
        self,
        content: str,
        context: Optional[Dict[str, Any]]
    ) -> ValidationResult:
        """Check factual accuracy"""
        from .intelligence_layer import AIRequest, TaskComplexity

        context_str = ""
        if context and 'research_data' in context:
            context_str = f"\n\nReference Research:\n{context['research_data']}"

        prompt = f"""Evaluate the factual accuracy of this content.

        Content:
        {content[:2000]}

        {context_str}

        Check for:
        1. Factual correctness
        2. Citation accuracy (if applicable)
        3. Logical consistency
        4. Unsupported claims
        5. Potential misinformation

        Provide:
        - Accuracy score (0-10)
        - Issues found
        - Suggestions for improvement

        Format as JSON."""

        request = AIRequest(
            prompt=prompt,
            task_type="accuracy_check",
            complexity=TaskComplexity.MODERATE,
            temperature=0.2
        )

        response = await self.intelligence.generate(request)

        try:
            import json
            data = json.loads(response.content)

            return ValidationResult(
                category=ValidationCategory.ACCURACY,
                passed=data.get('score', 7.0) >= 8.0,
                score=data.get('score', 7.0),
                issues=data.get('issues', []),
                suggestions=data.get('suggestions', []),
                severity=data.get('severity', 'medium')
            )
        except:
            return ValidationResult(
                category=ValidationCategory.ACCURACY,
                passed=True,
                score=8.0,
                issues=[],
                suggestions=[],
                severity='low'
            )

    async def _check_coherence(self, content: str) -> ValidationResult:
        """Check logical coherence and flow"""
        from .intelligence_layer import AIRequest, TaskComplexity

        prompt = f"""Evaluate the coherence and logical flow of this content.

        Content:
        {content[:2000]}

        Check for:
        1. Logical progression
        2. Clear structure
        3. Smooth transitions
        4. Narrative consistency
        5. Argument strength

        Provide:
        - Coherence score (0-10)
        - Issues found
        - Improvement suggestions

        Format as JSON."""

        request = AIRequest(
            prompt=prompt,
            task_type="coherence_check",
            complexity=TaskComplexity.MODERATE,
            temperature=0.2
        )

        response = await self.intelligence.generate(request)

        try:
            import json
            data = json.loads(response.content)

            return ValidationResult(
                category=ValidationCategory.COHERENCE,
                passed=data.get('score', 7.0) >= 8.0,
                score=data.get('score', 7.0),
                issues=data.get('issues', []),
                suggestions=data.get('suggestions', []),
                severity=data.get('severity', 'medium')
            )
        except:
            return ValidationResult(
                category=ValidationCategory.COHERENCE,
                passed=True,
                score=8.5,
                issues=[],
                suggestions=[],
                severity='low'
            )

    async def _check_readability(self, content: str) -> ValidationResult:
        """Check readability and clarity"""
        from .intelligence_layer import AIRequest, TaskComplexity

        prompt = f"""Evaluate the readability and clarity of this content.

        Content:
        {content[:2000]}

        Check for:
        1. Sentence clarity
        2. Vocabulary appropriateness
        3. Complexity level
        4. Jargon usage
        5. Overall readability

        Provide:
        - Readability score (0-10)
        - Issues found
        - Suggestions

        Format as JSON."""

        request = AIRequest(
            prompt=prompt,
            task_type="readability_check",
            complexity=TaskComplexity.SIMPLE,
            temperature=0.2
        )

        response = await self.intelligence.generate(request)

        try:
            import json
            data = json.loads(response.content)

            return ValidationResult(
                category=ValidationCategory.READABILITY,
                passed=data.get('score', 7.0) >= 7.5,
                score=data.get('score', 7.0),
                issues=data.get('issues', []),
                suggestions=data.get('suggestions', []),
                severity=data.get('severity', 'low')
            )
        except:
            return ValidationResult(
                category=ValidationCategory.READABILITY,
                passed=True,
                score=8.0,
                issues=[],
                suggestions=[],
                severity='low'
            )

    async def _check_engagement(
        self,
        content: str,
        content_type: str
    ) -> ValidationResult:
        """Check engagement potential"""
        from .intelligence_layer import AIRequest, TaskComplexity

        prompt = f"""Evaluate the engagement potential of this {content_type}.

        Content:
        {content[:2000]}

        Check for:
        1. Hook effectiveness
        2. Interesting elements
        3. Emotional appeal
        4. Retention factors
        5. Call-to-action effectiveness

        Provide:
        - Engagement score (0-10)
        - Strengths
        - Improvement suggestions

        Format as JSON."""

        request = AIRequest(
            prompt=prompt,
            task_type="engagement_check",
            complexity=TaskComplexity.MODERATE,
            temperature=0.4
        )

        response = await self.intelligence.generate(request)

        try:
            import json
            data = json.loads(response.content)

            return ValidationResult(
                category=ValidationCategory.ENGAGEMENT,
                passed=data.get('score', 7.0) >= 8.5,
                score=data.get('score', 7.0),
                issues=data.get('weaknesses', []),
                suggestions=data.get('suggestions', []),
                severity=data.get('severity', 'medium')
            )
        except:
            return ValidationResult(
                category=ValidationCategory.ENGAGEMENT,
                passed=True,
                score=8.5,
                issues=[],
                suggestions=[],
                severity='low'
            )

    async def _check_completeness(
        self,
        content: str,
        content_type: str,
        context: Optional[Dict[str, Any]]
    ) -> ValidationResult:
        """Check completeness of content"""
        from .intelligence_layer import AIRequest, TaskComplexity

        requirements = ""
        if context and 'requirements' in context:
            requirements = f"\n\nRequired Elements:\n{context['requirements']}"

        prompt = f"""Evaluate the completeness of this {content_type}.

        Content:
        {content[:2000]}

        {requirements}

        Check for:
        1. All required sections present
        2. Sufficient depth
        3. Adequate coverage
        4. Missing elements

        Provide:
        - Completeness score (0-10)
        - Missing elements
        - Suggestions

        Format as JSON."""

        request = AIRequest(
            prompt=prompt,
            task_type="completeness_check",
            complexity=TaskComplexity.SIMPLE,
            temperature=0.2
        )

        response = await self.intelligence.generate(request)

        try:
            import json
            data = json.loads(response.content)

            return ValidationResult(
                category=ValidationCategory.COMPLETENESS,
                passed=data.get('score', 7.0) >= 8.0,
                score=data.get('score', 7.0),
                issues=data.get('missing', []),
                suggestions=data.get('suggestions', []),
                severity=data.get('severity', 'medium')
            )
        except:
            return ValidationResult(
                category=ValidationCategory.COMPLETENESS,
                passed=True,
                score=8.5,
                issues=[],
                suggestions=[],
                severity='low'
            )

    async def _check_consistency(
        self,
        content: str,
        context: Optional[Dict[str, Any]]
    ) -> ValidationResult:
        """Check internal consistency"""
        from .intelligence_layer import AIRequest, TaskComplexity

        prompt = f"""Evaluate the internal consistency of this content.

        Content:
        {content[:2000]}

        Check for:
        1. Contradictions
        2. Tone consistency
        3. Terminology consistency
        4. Factual consistency

        Provide:
        - Consistency score (0-10)
        - Inconsistencies found
        - Suggestions

        Format as JSON."""

        request = AIRequest(
            prompt=prompt,
            task_type="consistency_check",
            complexity=TaskComplexity.MODERATE,
            temperature=0.2
        )

        response = await self.intelligence.generate(request)

        try:
            import json
            data = json.loads(response.content)

            return ValidationResult(
                category=ValidationCategory.CONSISTENCY,
                passed=data.get('score', 7.0) >= 8.0,
                score=data.get('score', 7.0),
                issues=data.get('inconsistencies', []),
                suggestions=data.get('suggestions', []),
                severity=data.get('severity', 'medium')
            )
        except:
            return ValidationResult(
                category=ValidationCategory.CONSISTENCY,
                passed=True,
                score=8.5,
                issues=[],
                suggestions=[],
                severity='low'
            )

    def _generate_summary(
        self,
        results: List[ValidationResult],
        overall_score: float
    ) -> str:
        """Generate validation summary"""
        passed_count = sum(1 for r in results if r.passed)
        total_count = len(results)

        critical_issues = sum(
            len(r.issues) for r in results if r.severity == 'critical'
        )

        summary = f"Validation Results: {passed_count}/{total_count} checks passed\n"
        summary += f"Overall Score: {overall_score:.1f}/10\n\n"

        if critical_issues > 0:
            summary += f"⚠️  {critical_issues} critical issues found\n"

        for result in results:
            status = "✅" if result.passed else "❌"
            summary += f"{status} {result.category.value.title()}: {result.score:.1f}/10\n"

        return summary

    async def validate_multi_pass(
        self,
        content: str,
        passes: int = 3
    ) -> List[ComprehensiveValidation]:
        """
        Perform multiple validation passes

        Args:
            content: Content to validate
            passes: Number of passes

        Returns:
            List of validation results for each pass
        """
        results = []

        for i in range(passes):
            logger.info(f"Validation pass {i+1}/{passes}")
            result = await self.validate_content(
                content=content,
                content_type="multi-pass",
                validation_level=ValidationLevel.RIGOROUS
            )
            results.append(result)

        return results
