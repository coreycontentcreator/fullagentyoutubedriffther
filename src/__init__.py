"""
Viral YouTube Synthesis System - Master Orchestrator Module

A world-class, modular system for generating viral YouTube content
using AI-powered research, viral analysis, and content synthesis.

Version: 1.0.0
Author: AI Research Team
Date: November 2025
"""

__version__ = "1.0.0"
__author__ = "AI Research Team"

from .orchestrator.master_orchestrator import MasterOrchestrator, WorkflowRequest, WorkflowType
from .orchestrator.chat_interface import ChatInterface
from .config.config_manager import ConfigurationManager, get_config
from .utils.logger import get_logger, LoggerFactory

__all__ = [
    "MasterOrchestrator",
    "WorkflowRequest",
    "WorkflowType",
    "ChatInterface",
    "ConfigurationManager",
    "get_config",
    "get_logger",
    "LoggerFactory"
]
