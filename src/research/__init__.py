"""
Research Gatekeeper Module - Multi-database academic research
Module 1 of the Modular Agentic System
"""

from .research_gatekeeper import ResearchGatekeeper
from .database_connector import DatabaseConnector
from .research_validator import ResearchValidator

__all__ = ['ResearchGatekeeper', 'DatabaseConnector', 'ResearchValidator']
