"""Interface Definitions"""

from .gatekeeper_interface import (
    BaseGatekeeper,
    ResearchGatekeeperInterface,
    ViralAnalyserGatekeeperInterface,
    ContentSynthesisGatekeeperInterface,
    GatekeeperStatus,
    QualityDecision,
    QualityMetrics,
    GatekeeperResult,
    GatekeeperFactory
)
from .vector_database_interface import (
    VectorDatabaseInterface,
    MockVectorDatabase,
    ViralStrategy,
    ViralTier,
    SearchResult
)

__all__ = [
    "BaseGatekeeper",
    "ResearchGatekeeperInterface",
    "ViralAnalyserGatekeeperInterface",
    "ContentSynthesisGatekeeperInterface",
    "GatekeeperStatus",
    "QualityDecision",
    "QualityMetrics",
    "GatekeeperResult",
    "GatekeeperFactory",
    "VectorDatabaseInterface",
    "MockVectorDatabase",
    "ViralStrategy",
    "ViralTier",
    "SearchResult"
]
