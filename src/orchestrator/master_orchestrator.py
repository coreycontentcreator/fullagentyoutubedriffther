"""
Master Orchestrator - Core Coordination System

This is the central intelligence that coordinates all gatekeepers,
databases, and workflows for the viral YouTube synthesis system.

The Master Orchestrator:
- Coordinates Research, Viral Analysis, and Content Synthesis Gatekeepers
- Manages vector database for learning and pattern storage
- Handles YouTube video analysis requests
- Provides chat-based user interaction
- Ensures quality validation and iteration control
- Implements world-class modular architecture

Author: AI Research Team
Date: November 2025
Version: 1.0.0
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.config_manager import ConfigurationManager, get_config
from utils.logger import LoggerFactory, get_logger, StructuredLogger
from utils.anthropic_client import AnthropicIntelligence
from interfaces.gatekeeper_interface import (
    BaseGatekeeper,
    GatekeeperFactory,
    GatekeeperStatus,
    GatekeeperResult,
    QualityMetrics,
    QualityDecision
)
from interfaces.vector_database_interface import (
    VectorDatabaseInterface,
    MockVectorDatabase,
    ViralStrategy,
    ViralTier
)


class WorkflowType(Enum):
    """Types of workflows supported by the orchestrator."""
    FULL_PIPELINE = "full_pipeline"  # Research -> Viral -> Content
    RESEARCH_ONLY = "research_only"
    VIRAL_ANALYSIS = "viral_analysis"
    CONTENT_GENERATION = "content_generation"
    YOUTUBE_ANALYSIS = "youtube_analysis"
    CUSTOM = "custom"


class WorkflowStatus(Enum):
    """Status of workflow execution."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class WorkflowRequest:
    """User request for workflow execution."""
    workflow_type: WorkflowType
    topic: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: f"req_{datetime.utcnow().timestamp()}")


@dataclass
class WorkflowResult:
    """Result from workflow execution."""
    workflow_type: WorkflowType
    status: WorkflowStatus
    outputs: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, QualityMetrics] = field(default_factory=dict)
    iteration_history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class MasterOrchestrator:
    """
    Master Orchestrator - Central Coordination System

    This class serves as the intelligent coordinator for the entire
    viral YouTube synthesis system. It manages gatekeepers, databases,
    workflows, and quality control.

    Key Features:
    - Modular gatekeeper coordination
    - Intelligent workflow routing
    - Quality validation and iteration control
    - Vector database integration for learning
    - YouTube video analysis coordination
    - Chat-based user interaction
    - Comprehensive logging and monitoring
    """

    def __init__(
        self,
        config: Optional[ConfigurationManager] = None,
        vector_db: Optional[VectorDatabaseInterface] = None
    ):
        """
        Initialize the Master Orchestrator.

        Args:
            config: Configuration manager instance
            vector_db: Vector database instance
        """
        # Configuration
        self.config = config or get_config()

        # Setup logging
        LoggerFactory.configure(
            log_dir=self.config.system.logs_dir,
            log_level=self.config.system.log_level
        )
        self.logger = get_logger(__name__)

        # Initialize Anthropic intelligence
        self.ai = AnthropicIntelligence(
            api_key=self.config.anthropic.api_key,
            model=self.config.anthropic.model,
            max_tokens=self.config.anthropic.max_tokens,
            temperature=self.config.anthropic.temperature
        )

        # Initialize vector database
        self.vector_db = vector_db or MockVectorDatabase()
        self.vector_db.initialize(self.config.get_vector_db_config())

        # Gatekeeper references (to be registered by external modules)
        self.research_gatekeeper: Optional[BaseGatekeeper] = None
        self.viral_gatekeeper: Optional[BaseGatekeeper] = None
        self.content_gatekeeper: Optional[BaseGatekeeper] = None

        # Workflow tracking
        self.active_workflows: Dict[str, WorkflowResult] = {}
        self.completed_workflows: List[WorkflowResult] = []

        # System state
        self.initialized = True
        self.total_requests_processed = 0

        self.logger.info(
            "Master Orchestrator initialized",
            model=self.config.anthropic.model,
            modular_mode=self.config.system.modular_mode,
            learning_enabled=self.config.system.enable_learning
        )

    # ==================== Gatekeeper Registration ====================

    def register_gatekeeper(
        self,
        gatekeeper_type: str,
        gatekeeper: BaseGatekeeper
    ):
        """
        Register a gatekeeper with the orchestrator.

        Args:
            gatekeeper_type: Type of gatekeeper (research, viral, content)
            gatekeeper: Gatekeeper instance
        """
        gatekeeper_type = gatekeeper_type.lower()

        if gatekeeper_type == "research":
            self.research_gatekeeper = gatekeeper
        elif gatekeeper_type == "viral":
            self.viral_gatekeeper = gatekeeper
        elif gatekeeper_type == "content":
            self.content_gatekeeper = gatekeeper
        else:
            raise ValueError(f"Unknown gatekeeper type: {gatekeeper_type}")

        GatekeeperFactory.register_gatekeeper(gatekeeper_type, gatekeeper)

        self.logger.info(
            f"Registered {gatekeeper_type} gatekeeper",
            gatekeeper_type=gatekeeper_type
        )

    def get_registered_gatekeepers(self) -> Dict[str, Optional[BaseGatekeeper]]:
        """Get all registered gatekeepers."""
        return {
            "research": self.research_gatekeeper,
            "viral": self.viral_gatekeeper,
            "content": self.content_gatekeeper
        }

    # ==================== Workflow Execution ====================

    def execute_workflow(self, request: WorkflowRequest) -> WorkflowResult:
        """
        Execute a workflow based on the request.

        Args:
            request: Workflow request

        Returns:
            WorkflowResult with outputs and quality metrics
        """
        self.total_requests_processed += 1

        self.logger.log_workflow_stage(
            stage="workflow_start",
            status="started",
            workflow_type=request.workflow_type.value,
            topic=request.topic,
            request_id=request.request_id
        )

        # Create result object
        result = WorkflowResult(
            workflow_type=request.workflow_type,
            status=WorkflowStatus.IN_PROGRESS
        )

        # Track active workflow
        self.active_workflows[request.request_id] = result

        try:
            # Route to appropriate workflow
            if request.workflow_type == WorkflowType.FULL_PIPELINE:
                result = self._execute_full_pipeline(request)
            elif request.workflow_type == WorkflowType.RESEARCH_ONLY:
                result = self._execute_research_workflow(request)
            elif request.workflow_type == WorkflowType.VIRAL_ANALYSIS:
                result = self._execute_viral_workflow(request)
            elif request.workflow_type == WorkflowType.CONTENT_GENERATION:
                result = self._execute_content_workflow(request)
            elif request.workflow_type == WorkflowType.YOUTUBE_ANALYSIS:
                result = self._execute_youtube_analysis(request)
            else:
                raise ValueError(f"Unsupported workflow type: {request.workflow_type}")

            result.status = WorkflowStatus.COMPLETED

            self.logger.log_workflow_stage(
                stage="workflow_complete",
                status="completed",
                workflow_type=request.workflow_type.value,
                request_id=request.request_id
            )

        except Exception as e:
            result.status = WorkflowStatus.FAILED
            result.error = str(e)

            self.logger.exception(
                "Workflow execution failed",
                workflow_type=request.workflow_type.value,
                error=str(e),
                request_id=request.request_id
            )

        finally:
            # Move to completed workflows
            self.completed_workflows.append(result)
            if request.request_id in self.active_workflows:
                del self.active_workflows[request.request_id]

        return result

    def _execute_full_pipeline(self, request: WorkflowRequest) -> WorkflowResult:
        """
        Execute full pipeline: Research -> Viral Analysis -> Content Synthesis.

        Args:
            request: Workflow request

        Returns:
            WorkflowResult with complete outputs
        """
        result = WorkflowResult(
            workflow_type=WorkflowType.FULL_PIPELINE,
            status=WorkflowStatus.IN_PROGRESS
        )

        # Stage 1: Research
        self.logger.log_workflow_stage("research", "started", topic=request.topic)

        if not self.research_gatekeeper:
            raise RuntimeError("Research gatekeeper not registered")

        research_result = self._execute_with_validation(
            gatekeeper=self.research_gatekeeper,
            input_data={"topic": request.topic, **request.parameters.get("research", {})},
            gatekeeper_name="research",
            min_quality=self.config.thresholds.research_quality_min
        )

        result.outputs["research"] = research_result.output
        result.quality_metrics["research"] = research_result.quality_metrics
        result.iteration_history.append({
            "stage": "research",
            "iterations": research_result.iteration_count,
            "quality": research_result.quality_metrics.overall_score if research_result.quality_metrics else 0
        })

        self.logger.log_workflow_stage("research", "completed")

        # Stage 2: Viral Analysis
        self.logger.log_workflow_stage("viral_analysis", "started")

        if not self.viral_gatekeeper:
            raise RuntimeError("Viral gatekeeper not registered")

        viral_input = {
            "topic": request.topic,
            "research_context": research_result.output,
            **request.parameters.get("viral", {})
        }

        viral_result = self._execute_with_validation(
            gatekeeper=self.viral_gatekeeper,
            input_data=viral_input,
            gatekeeper_name="viral",
            min_quality=self.config.thresholds.viral_potential_min
        )

        result.outputs["viral_strategy"] = viral_result.output
        result.quality_metrics["viral"] = viral_result.quality_metrics
        result.iteration_history.append({
            "stage": "viral_analysis",
            "iterations": viral_result.iteration_count,
            "quality": viral_result.quality_metrics.overall_score if viral_result.quality_metrics else 0
        })

        self.logger.log_workflow_stage("viral_analysis", "completed")

        # Stage 3: Content Synthesis
        self.logger.log_workflow_stage("content_synthesis", "started")

        if not self.content_gatekeeper:
            raise RuntimeError("Content gatekeeper not registered")

        content_input = {
            "research": research_result.output,
            "viral_strategy": viral_result.output,
            **request.parameters.get("content", {})
        }

        content_result = self._execute_with_validation(
            gatekeeper=self.content_gatekeeper,
            input_data=content_input,
            gatekeeper_name="content",
            min_quality=self.config.thresholds.script_quality_min
        )

        result.outputs["content"] = content_result.output
        result.quality_metrics["content"] = content_result.quality_metrics
        result.iteration_history.append({
            "stage": "content_synthesis",
            "iterations": content_result.iteration_count,
            "quality": content_result.quality_metrics.overall_score if content_result.quality_metrics else 0
        })

        self.logger.log_workflow_stage("content_synthesis", "completed")

        # Save outputs
        self._save_workflow_outputs(request.topic, result)

        return result

    def _execute_research_workflow(self, request: WorkflowRequest) -> WorkflowResult:
        """Execute research-only workflow."""
        result = WorkflowResult(
            workflow_type=WorkflowType.RESEARCH_ONLY,
            status=WorkflowStatus.IN_PROGRESS
        )

        if not self.research_gatekeeper:
            raise RuntimeError("Research gatekeeper not registered")

        research_result = self._execute_with_validation(
            gatekeeper=self.research_gatekeeper,
            input_data={"topic": request.topic, **request.parameters},
            gatekeeper_name="research",
            min_quality=self.config.thresholds.research_quality_min
        )

        result.outputs["research"] = research_result.output
        result.quality_metrics["research"] = research_result.quality_metrics

        return result

    def _execute_viral_workflow(self, request: WorkflowRequest) -> WorkflowResult:
        """Execute viral analysis workflow."""
        result = WorkflowResult(
            workflow_type=WorkflowType.VIRAL_ANALYSIS,
            status=WorkflowStatus.IN_PROGRESS
        )

        if not self.viral_gatekeeper:
            raise RuntimeError("Viral gatekeeper not registered")

        viral_result = self._execute_with_validation(
            gatekeeper=self.viral_gatekeeper,
            input_data=request.parameters,
            gatekeeper_name="viral",
            min_quality=self.config.thresholds.viral_potential_min
        )

        result.outputs["viral_strategy"] = viral_result.output
        result.quality_metrics["viral"] = viral_result.quality_metrics

        return result

    def _execute_content_workflow(self, request: WorkflowRequest) -> WorkflowResult:
        """Execute content generation workflow."""
        result = WorkflowResult(
            workflow_type=WorkflowType.CONTENT_GENERATION,
            status=WorkflowStatus.IN_PROGRESS
        )

        if not self.content_gatekeeper:
            raise RuntimeError("Content gatekeeper not registered")

        content_result = self._execute_with_validation(
            gatekeeper=self.content_gatekeeper,
            input_data=request.parameters,
            gatekeeper_name="content",
            min_quality=self.config.thresholds.script_quality_min
        )

        result.outputs["content"] = content_result.output
        result.quality_metrics["content"] = content_result.quality_metrics

        return result

    def _execute_youtube_analysis(self, request: WorkflowRequest) -> WorkflowResult:
        """Execute YouTube video analysis workflow."""
        result = WorkflowResult(
            workflow_type=WorkflowType.YOUTUBE_ANALYSIS,
            status=WorkflowStatus.IN_PROGRESS
        )

        video_url = request.parameters.get("video_url")
        if not video_url:
            raise ValueError("video_url is required for YouTube analysis")

        # TODO: Implement actual YouTube analysis
        # For now, return placeholder
        result.outputs["analysis"] = {
            "video_url": video_url,
            "status": "placeholder_analysis",
            "message": "YouTube analysis will be implemented by YouTube analyzer subagent"
        }

        return result

    def _execute_with_validation(
        self,
        gatekeeper: BaseGatekeeper,
        input_data: Dict[str, Any],
        gatekeeper_name: str,
        min_quality: float
    ) -> GatekeeperResult:
        """
        Execute gatekeeper with quality validation and iteration control.

        Args:
            gatekeeper: Gatekeeper to execute
            input_data: Input data
            gatekeeper_name: Name for logging
            min_quality: Minimum quality threshold

        Returns:
            GatekeeperResult after validation
        """
        max_iterations = self.config.thresholds.max_iterations
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            self.logger.info(
                f"Executing {gatekeeper_name} gatekeeper",
                iteration=iteration,
                max_iterations=max_iterations
            )

            # Execute gatekeeper
            if iteration == 1:
                gatekeeper_result = gatekeeper.process(input_data)
            else:
                # Iteration - use previous output
                gatekeeper_result = gatekeeper.iterate(
                    previous_output=gatekeeper_result.output,
                    quality_metrics=gatekeeper_result.quality_metrics
                )

            gatekeeper_result.iteration_count = iteration

            # Validate quality
            if gatekeeper_result.quality_metrics:
                quality_score = gatekeeper_result.quality_metrics.overall_score

                self.logger.log_gatekeeper_decision(
                    gatekeeper=gatekeeper_name,
                    decision="pass" if quality_score >= min_quality else "iterate",
                    quality_score=quality_score,
                    threshold=min_quality
                )

                if quality_score >= min_quality:
                    return gatekeeper_result

                if iteration >= max_iterations:
                    self.logger.warning(
                        f"{gatekeeper_name} reached max iterations",
                        final_quality=quality_score,
                        threshold=min_quality
                    )
                    return gatekeeper_result
            else:
                # No quality metrics - assume pass
                return gatekeeper_result

        return gatekeeper_result

    # ==================== Chat Integration ====================

    def process_chat_request(self, user_message: str) -> Dict[str, Any]:
        """
        Process a chat request from the user.

        Args:
            user_message: User's chat message

        Returns:
            Response with action and data
        """
        self.logger.info("Processing chat request", message_preview=user_message[:100])

        # Use AI to understand intent
        intent = self._understand_user_intent(user_message)

        # Route based on intent
        if intent["action"] == "full_pipeline":
            request = WorkflowRequest(
                workflow_type=WorkflowType.FULL_PIPELINE,
                topic=intent.get("topic"),
                parameters=intent.get("parameters", {})
            )
            result = self.execute_workflow(request)
            return self._format_chat_response(result)

        elif intent["action"] == "youtube_analysis":
            request = WorkflowRequest(
                workflow_type=WorkflowType.YOUTUBE_ANALYSIS,
                parameters={"video_url": intent.get("video_url")}
            )
            result = self.execute_workflow(request)
            return self._format_chat_response(result)

        elif intent["action"] == "help":
            return self._get_help_response()

        else:
            return {
                "response": "I understand you want to: " + intent.get("action", "unknown"),
                "suggestions": [
                    "Generate a viral YouTube video about [topic]",
                    "Analyze this YouTube video: [URL]",
                    "Research only: [topic]",
                    "Show me system status"
                ]
            }

    def _understand_user_intent(self, message: str) -> Dict[str, Any]:
        """
        Use AI to understand user intent from chat message.

        Args:
            message: User message

        Returns:
            Intent with action and extracted parameters
        """
        system_prompt = """You are an intent classifier for a viral YouTube content generation system.
Analyze user messages and extract:
- action: full_pipeline, research_only, viral_analysis, content_generation, youtube_analysis, help, status
- topic: if mentioned
- video_url: if mentioned
- parameters: any additional parameters

Return JSON only."""

        prompt = f"User message: {message}\n\nExtract intent:"

        try:
            response = self.ai.generate(prompt, system_prompt=system_prompt, temperature=0.3)
            intent = json.loads(response.content)
        except:
            # Fallback intent
            intent = {
                "action": "help",
                "message": message
            }

        return intent

    def _format_chat_response(self, result: WorkflowResult) -> Dict[str, Any]:
        """Format workflow result as chat response."""
        return {
            "status": result.status.value,
            "workflow": result.workflow_type.value,
            "summary": self._generate_result_summary(result),
            "outputs": result.outputs,
            "quality_scores": {
                k: v.overall_score for k, v in result.quality_metrics.items()
            } if result.quality_metrics else {}
        }

    def _generate_result_summary(self, result: WorkflowResult) -> str:
        """Generate human-readable summary of results."""
        if result.status == WorkflowStatus.FAILED:
            return f"Workflow failed: {result.error}"

        summary_parts = [f"Successfully completed {result.workflow_type.value}"]

        if result.quality_metrics:
            avg_quality = sum(
                m.overall_score for m in result.quality_metrics.values()
            ) / len(result.quality_metrics)
            summary_parts.append(f"Average quality: {avg_quality:.1f}/10")

        return ". ".join(summary_parts)

    def _get_help_response(self) -> Dict[str, Any]:
        """Get help response with available commands."""
        return {
            "response": "Master Orchestrator - Available Commands",
            "commands": {
                "Full Pipeline": "Generate complete viral video: 'Create a video about [topic]'",
                "Research Only": "Research only: 'Research [topic]'",
                "YouTube Analysis": "Analyze video: 'Analyze https://youtube.com/watch?v=...'",
                "Status": "System status: 'Show status' or 'How many videos generated?'"
            },
            "examples": [
                "Create a viral video about quantum computing",
                "Research the history of AI",
                "Analyze https://youtube.com/watch?v=dQw4w9WgXcQ"
            ]
        }

    # ==================== Utility Methods ====================

    def _save_workflow_outputs(self, topic: str, result: WorkflowResult):
        """Save workflow outputs to files."""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_'))[:50]
            output_dir = self.config.system.outputs_dir / f"{safe_topic}_{timestamp}"
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save each output
            for key, value in result.outputs.items():
                output_file = output_dir / f"{key}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(value, f, indent=2, default=str)

            # Save summary
            summary_file = output_dir / "summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "workflow_type": result.workflow_type.value,
                    "status": result.status.value,
                    "quality_metrics": {
                        k: asdict(v) for k, v in result.quality_metrics.items()
                    },
                    "iteration_history": result.iteration_history,
                    "timestamp": result.timestamp
                }, f, indent=2, default=str)

            self.logger.info(f"Saved outputs to {output_dir}")

        except Exception as e:
            self.logger.error(f"Failed to save outputs: {str(e)}")

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and statistics."""
        return {
            "initialized": self.initialized,
            "total_requests": self.total_requests_processed,
            "active_workflows": len(self.active_workflows),
            "completed_workflows": len(self.completed_workflows),
            "registered_gatekeepers": {
                k: v is not None
                for k, v in self.get_registered_gatekeepers().items()
            },
            "vector_db_stats": self.vector_db.get_collection_stats(),
            "ai_token_usage": self.ai.get_token_usage(),
            "config": {
                "modular_mode": self.config.system.modular_mode,
                "learning_enabled": self.config.system.enable_learning,
                "log_level": self.config.system.log_level
            }
        }

    def shutdown(self):
        """Gracefully shutdown the orchestrator."""
        self.logger.info(
            "Shutting down Master Orchestrator",
            total_requests=self.total_requests_processed,
            active_workflows=len(self.active_workflows)
        )
        self.initialized = False


if __name__ == "__main__":
    # Example usage
    print("Master Orchestrator - Example Usage\n")

    # Initialize
    orchestrator = MasterOrchestrator()

    # Show status
    status = orchestrator.get_system_status()
    print("System Status:")
    print(json.dumps(status, indent=2))

    # Example chat interaction
    print("\n" + "="*50)
    print("Chat Example:")
    response = orchestrator.process_chat_request("How do I use this system?")
    print(json.dumps(response, indent=2))
