# Content Synthesis System
## World-Class YouTube Documentary Content Generation with AI

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen)

**The Content Synthesis System is an advanced, AI-powered content generation platform that creates production-ready YouTube documentary scripts with world-class quality standards.**

---

## 🌟 Features

### Core Capabilities

✅ **Complete Script Generation**
- Production-ready scripts (5,000-15,000 words)
- Natural, engaging narrative flow
- Optimized for audience retention
- Multi-pass quality validation

✅ **Visual Scene Architecture**
- Shot-by-shot visual descriptions
- Detailed camera movements and lighting
- B-roll requirements and suggestions
- Graphics and text overlay specifications

✅ **Production Planning**
- Comprehensive equipment lists
- Budget estimates and timelines
- Shooting checklists
- Post-production workflows

✅ **Narrative Optimization**
- Three-act story structure
- Emotional arc analysis
- Pacing and rhythm optimization
- Hook placement and tension management

✅ **Quality Assurance**
- Multi-pass validation (5 passes)
- Quality scores (0-10 scale)
- Iterative refinement (up to 7 iterations)
- Threshold-based gatekeeping (default: 9.0/10)

✅ **Anthropic Claude Integration**
- Powered by Claude Sonnet 4.5
- Advanced reasoning and synthesis
- Natural language generation
- Context-aware responses

✅ **Dynamic Scaling**
- Adapts to video duration (5-60+ minutes)
- Scales complexity based on topic
- Adjustable quality levels (standard/high/world-class)
- Resource-aware processing

✅ **Modular Architecture**
- Independent subagent access
- Pipeline or standalone operation
- Easy integration into larger systems
- Extensible design

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│           CONTENT SYNTHESIS GATEKEEPER                       │
│  (Orchestrates all subagents with quality validation)       │
└────────────┬────────────────────────────────────────────────┘
             │
     ┌───────┴───────┐
     │               │
     ▼               ▼
┌─────────────┐ ┌──────────────────┐
│ Anthropic   │ │   Configuration  │
│   Client    │ │     Manager      │
│ (Claude AI) │ │  (Dynamic Scale) │
└─────────────┘ └──────────────────┘
     │
     │
┌────┴───────────────────────────────────────────────────────┐
│                   SUBAGENT LAYER                            │
│  (6 specialized subagents for content creation)            │
└────┬──────────┬──────────────┬──────────────┬──────────────┘
     │          │              │              │
     ▼          ▼              ▼              ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│  Script  │ │  Visual  │ │Production│ │  Narrative   │
│Architect │ │  Scene   │ │  Notes   │ │  Structure   │
│          │ │Architect │ │Generator │ │    Engine    │
└──────────┘ └──────────┘ └──────────┘ └──────────────┘
     │          │              │              │
     └──────────┴──────────────┴──────────────┘
                      │
                      ▼
            ┌──────────────────┐
            │     Content      │
            │    Validator     │
            │ (Multi-pass QA)  │
            └──────────────────┘
```

---

## 🚀 Quick Start

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key
export ANTHROPIC_API_KEY='your-api-key-here'

# 3. Run the system
python main.py
```

### First Generation

```bash
# Interactive mode (recommended)
python main.py

# CLI mode
python main.py --topic "The Future of AI" --duration 15

# Quick start example
python examples/quick_start.py
```

---

## 💻 Usage Examples

### Interactive Chat Interface

```bash
$ python main.py

==================================================================
  CONTENT SYNTHESIS SYSTEM - Interactive Chat Interface
==================================================================

Welcome! I can help you create world-class YouTube documentary content.

You: Create a 15-minute documentary about quantum computing