"""
Content Synthesis Gatekeeper
Main coordinator for content creation with all subagents
Implements world-class quality standards with iterative refinement
"""
import time
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import logging
import json

from .scriptwriter import ScriptArchitect
from .visual_scene_architect import VisualSceneArchitect
from .production_notes_generator import ProductionNotesGenerator
from .narrative_structure_engine import NarrativeStructureEngine
from .content_validator import ContentValidator

logger = logging.getLogger(__name__)


@dataclass
class ContentPackage:
    """Complete content package output"""
    script: str
    word_count: int
    estimated_duration: float
    visual_scenes: List[Dict[str, Any]]
    scene_count: int
    production_notes: Dict[str, Any]
    narrative_analysis: Dict[str, Any]
    validation_report: Dict[str, Any]
    quality_score: float
    iteration_count: int
    total_processing_time: float
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class ContentSynthesisGatekeeper:
    """
    Content Synthesis Gatekeeper
    Orchestrates all content creation subagents with quality validation and iterative refinement
    """

    def __init__(self, anthropic_client, config):
        """
        Initialize Content Synthesis Gatekeeper

        Args:
            anthropic_client: AnthropicClient instance
            config: Configuration object (ContentSynthesisConfig)
        """
        self.anthropic_client = anthropic_client
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize all subagents
        self.script_architect = ScriptArchitect(anthropic_client, config)
        self.visual_architect = VisualSceneArchitect(anthropic_client, config)
        self.production_generator = ProductionNotesGenerator(anthropic_client, config)
        self.narrative_engine = NarrativeStructureEngine(anthropic_client, config)
        self.content_validator = ContentValidator(anthropic_client, config)

        self.logger.info("Content Synthesis Gatekeeper initialized with all subagents")

    async def generate_content(
            self,
            topic: str,
            research_data: Optional[Dict[str, Any]] = None,
            viral_strategy: Optional[Dict[str, Any]] = None,
            target_audience: str = "general audience",
            video_duration: int = 15,
            tone: str = "engaging but authoritative",
            style: str = "documentary",
            budget_level: str = "medium",
            enable_iteration: bool = True,
            max_iterations: Optional[int] = None
    ) -> ContentPackage:
        """
        Generate complete content package with quality validation

        Args:
            topic: Video topic
            research_data: Research findings and data
            viral_strategy: Viral optimization strategy
            target_audience: Target audience description
            video_duration: Target duration in minutes
            tone: Script tone
            style: Visual style
            budget_level: Production budget level
            enable_iteration: Enable iterative refinement
            max_iterations: Maximum refinement iterations (overrides config)

        Returns:
            ContentPackage with all generated content
        """
        start_time = time.time()

        self.logger.info(f"Starting content generation for topic: {topic}")
        self.logger.info(f"Target duration: {video_duration} minutes, Style: {style}, Tone: {tone}")

        # Set max iterations
        max_iter = max_iterations if max_iterations is not None else self.config.max_iterations if hasattr(self.config, 'max_iterations') else 5

        iteration = 0
        current_quality = 0.0
        quality_threshold = self.config.quality_threshold

        # Initialize with None
        script_result = None
        visual_result = None
        production_result = None
        narrative_result = None
        validation_result = None

        while iteration < max_iter:
            iteration += 1

            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"ITERATION {iteration}/{max_iter}")
            self.logger.info(f"{'='*60}")

            try:
                # STEP 1: Generate Script
                self.logger.info("\n[STEP 1/5] Generating script...")

                script_input = {
                    'topic': topic,
                    'research_data': research_data or {},
                    'target_audience': target_audience,
                    'video_duration': video_duration,
                    'tone': tone,
                    'style': style,
                    'viral_strategy': viral_strategy or {},
                    'hooks': viral_strategy.get('hooks', []) if viral_strategy else []
                }

                # If refining, add feedback
                if iteration > 1 and validation_result:
                    script_input['refinement_feedback'] = validation_result.data.get('recommendations', [])

                script_result = self.script_architect.process_sync(script_input)

                if not script_result.success:
                    raise Exception(f"Script generation failed: {script_result.errors}")

                self.logger.info(f"✓ Script generated ({script_result.data['word_count']} words)")

                # STEP 2: Generate Visual Scenes
                self.logger.info("\n[STEP 2/5] Generating visual scenes...")

                visual_input = {
                    'script': script_result.data['script'],
                    'topic': topic,
                    'style': style,
                    'budget': budget_level,
                    'location': 'mixed'
                }

                visual_result = self.visual_architect.process_sync(visual_input)

                if not visual_result.success:
                    raise Exception(f"Visual generation failed: {visual_result.errors}")

                self.logger.info(f"✓ Visual scenes generated ({visual_result.data['scene_count']} scenes)")

                # STEP 3: Analyze Narrative Structure
                self.logger.info("\n[STEP 3/5] Analyzing narrative structure...")

                narrative_input = {
                    'script': script_result.data['script'],
                    'target_audience': target_audience,
                    'video_duration': video_duration
                }

                narrative_result = self.narrative_engine.process_sync(narrative_input)

                if not narrative_result.success:
                    raise Exception(f"Narrative analysis failed: {narrative_result.errors}")

                self.logger.info(f"✓ Narrative analyzed (score: {narrative_result.data.get('narrative_quality_score', 0):.1f}/10)")

                # STEP 4: Generate Production Notes
                self.logger.info("\n[STEP 4/5] Generating production notes...")

                production_input = {
                    'script': script_result.data['script'],
                    'visual_scenes': visual_result.data['scenes'],
                    'budget_level': budget_level,
                    'crew_size': 'small',
                    'location': 'mixed',
                    'deadline': '2 weeks'
                }

                production_result = self.production_generator.process_sync(production_input)

                if not production_result.success:
                    raise Exception(f"Production notes generation failed: {production_result.errors}")

                self.logger.info(f"✓ Production notes generated")

                # STEP 5: Validate Content
                self.logger.info("\n[STEP 5/5] Validating content quality...")

                validation_input = {
                    'script': script_result.data['script'],
                    'visual_scenes': visual_result.data['scenes'],
                    'production_notes': production_result.data,
                    'narrative_analysis': narrative_result.data,
                    'research_data': research_data
                }

                validation_result = self.content_validator.process_sync(validation_input)

                if not validation_result.success:
                    raise Exception(f"Validation failed: {validation_result.errors}")

                current_quality = validation_result.data['overall_quality_score']

                self.logger.info(f"✓ Validation complete")
                self.logger.info(f"\nQuality Score: {current_quality:.1f}/10 (Threshold: {quality_threshold})")

                # Check if quality threshold is met
                if current_quality >= quality_threshold:
                    self.logger.info(f"\n✓ QUALITY THRESHOLD MET! ({current_quality:.1f} >= {quality_threshold})")
                    break

                elif not enable_iteration:
                    self.logger.info(f"\n⚠ Quality below threshold but iteration disabled")
                    break

                else:
                    self.logger.info(f"\n⟳ Quality below threshold - refinement needed")
                    self.logger.info(f"Recommendations:")
                    for rec in validation_result.data.get('recommendations', [])[:3]:
                        self.logger.info(f"  - [{rec['priority']}] {rec['recommendation']}")

            except Exception as e:
                self.logger.error(f"Error in iteration {iteration}: {str(e)}")

                if iteration == 1:
                    # First iteration failed - can't continue
                    raise

                # Use results from previous iteration
                break

        # Calculate total processing time
        total_time = time.time() - start_time

        # Compile final package
        content_package = self._compile_content_package(
            script_result=script_result,
            visual_result=visual_result,
            production_result=production_result,
            narrative_result=narrative_result,
            validation_result=validation_result,
            iteration_count=iteration,
            total_time=total_time,
            topic=topic,
            target_audience=target_audience,
            video_duration=video_duration
        )

        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"CONTENT GENERATION COMPLETE")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Final Quality Score: {content_package.quality_score:.1f}/10")
        self.logger.info(f"Iterations: {content_package.iteration_count}")
        self.logger.info(f"Total Time: {content_package.total_processing_time:.1f}s")
        self.logger.info(f"Script: {content_package.word_count} words")
        self.logger.info(f"Scenes: {content_package.scene_count}")
        self.logger.info(f"{'='*60}\n")

        return content_package

    def generate_content_sync(self, **kwargs) -> ContentPackage:
        """Synchronous wrapper for generate_content"""
        return asyncio.run(self.generate_content(**kwargs))

    def _compile_content_package(
            self,
            script_result,
            visual_result,
            production_result,
            narrative_result,
            validation_result,
            iteration_count: int,
            total_time: float,
            topic: str,
            target_audience: str,
            video_duration: int
    ) -> ContentPackage:
        """Compile all results into a ContentPackage"""

        return ContentPackage(
            script=script_result.data['script'],
            word_count=script_result.data['word_count'],
            estimated_duration=script_result.data['estimated_duration'],
            visual_scenes=visual_result.data['scenes'],
            scene_count=visual_result.data['scene_count'],
            production_notes=production_result.data,
            narrative_analysis=narrative_result.data,
            validation_report=validation_result.data,
            quality_score=validation_result.data['overall_quality_score'],
            iteration_count=iteration_count,
            total_processing_time=round(total_time, 2),
            metadata={
                'topic': topic,
                'target_audience': target_audience,
                'target_duration': video_duration,
                'generation_timestamp': time.time(),
                'subagent_scores': {
                    'script': script_result.quality_score,
                    'visual': visual_result.quality_score,
                    'production': production_result.quality_score,
                    'narrative': narrative_result.quality_score,
                    'validation': validation_result.quality_score
                },
                'tokens_used': script_result.data.get('tokens_used', 0)
            }
        )

    def save_content_package(self, package: ContentPackage, output_dir: str = "outputs") -> str:
        """
        Save content package to files

        Args:
            package: ContentPackage to save
            output_dir: Output directory

        Returns:
            Path to saved package
        """
        import os
        from datetime import datetime

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_slug = package.metadata['topic'].lower().replace(' ', '_')[:30]
        base_filename = f"{topic_slug}_{timestamp}"

        # Save complete package as JSON
        json_path = os.path.join(output_dir, f"{base_filename}_package.json")
        with open(json_path, 'w') as f:
            f.write(package.to_json())

        # Save script separately
        script_path = os.path.join(output_dir, f"{base_filename}_script.txt")
        with open(script_path, 'w') as f:
            f.write(package.script)

        # Save production notes
        notes_path = os.path.join(output_dir, f"{base_filename}_production_notes.json")
        with open(notes_path, 'w') as f:
            json.dump(package.production_notes, f, indent=2)

        # Save validation report
        validation_path = os.path.join(output_dir, f"{base_filename}_validation.json")
        with open(validation_path, 'w') as f:
            json.dump(package.validation_report, f, indent=2)

        self.logger.info(f"Content package saved to: {output_dir}/{base_filename}_*")

        return json_path

    def quick_generate(
            self,
            topic: str,
            video_duration: int = 15,
            style: str = "documentary"
    ) -> ContentPackage:
        """
        Quick generation with sensible defaults

        Args:
            topic: Video topic
            video_duration: Target duration in minutes
            style: Visual style

        Returns:
            ContentPackage
        """
        return self.generate_content_sync(
            topic=topic,
            video_duration=video_duration,
            style=style,
            target_audience="general audience",
            tone="engaging but authoritative",
            budget_level="medium",
            enable_iteration=True
        )
