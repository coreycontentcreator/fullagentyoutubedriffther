# Advanced Research System with Gatekeeper

A world-class, AI-powered academic research system with quality gates, multi-database integration, and intelligent synthesis powered by Claude (Anthropic).

## Overview

This system implements a sophisticated research gatekeeper that:
- **Searches 6+ academic databases** simultaneously (JSTOR, PubMed, arXiv, Semantic Scholar, CrossRef, OpenAlex)
- **Validates source credibility** using AI and heuristic analysis
- **Synthesizes findings** using Claude AI for deep insights
- **Enforces quality standards** with configurable thresholds
- **Tracks citations** with multiple export formats
- **Fact-checks claims** against academic literature
- **Provides chat interface** for natural interaction

## Features

### 🔬 Multi-Database Research
- 6 integrated sources: JSTOR (primary), Semantic Scholar, CrossRef, arXiv, PubMed, OpenAlex
- Parallel querying for speed
- Smart deduplication
- Source prioritization

### 🤖 AI-Powered Intelligence
- Claude Integration for synthesis
- Insight generation
- Knowledge gap detection
- Fact checking

### ✅ Quality Gates
- Academic Rigor: ≥8.0/10
- Source Diversity validation
- Citation Quality assessment
- Credibility Scoring

## Quick Start

1. **Install**:
```bash
pip install -r requirements.txt
```

2. **Configure**:
```bash
export ANTHROPIC_API_KEY="your_key_here"
export OPENALEX_EMAIL="your.email@example.com"
```

3. **Run**:
```bash
python -m research_system.chat.chat_interface
```

## Usage Examples

### Chat Interface
```bash
python -m research_system.chat.chat_interface
```

### Python API
```python
from research_system.core.research_gatekeeper import ResearchGatekeeper

# Initialize
gatekeeper = ResearchGatekeeper()

# Conduct research
report = gatekeeper.conduct_research(
    topic="Quantum Computing Breakthroughs",
    year_from=2020
)

print(f"Found {len(report.papers)} papers")
print(f"Quality Score: {report.validation_result.overall_score}/10")
print(f"Synthesis: {report.synthesis}")
```

### Fact Checking
```python
# Fact check a claim
result = gatekeeper.fact_check_claim(
    claim="Quantum computers can break RSA encryption",
    topic="quantum computing cryptography"
)

print(f"Verdict: {result['verdict']}")
print(f"Confidence: {result['confidence']}/10")
```

## Configuration

Edit `research_system/config/config.yaml`:

```yaml
research:
  min_quality_threshold: 8.0  # Quality gate
  max_papers_per_source: 20
  parallel_requests: true

  source_priorities:
    jstor: 10  # Primary source
    semantic_scholar: 9
    crossref: 8
```

## Architecture

### Components

1. **Research Gatekeeper** - Main coordinator
2. **Academic Research Aggregator** - Multi-database coordination
3. **Citation Tracker** - Citation management
4. **Credibility Analyzer** - Source quality assessment
5. **Insight Synthesizer** - AI-powered synthesis
6. **Fact Checker** - Claim validation
7. **Research Validator** - Quality enforcement

### Adding Custom Sources

```python
from research_system.sources.base_source import BaseResearchSource

class MyCustomSource(BaseResearchSource):
    def search(self, query, **kwargs):
        # Implement search
        pass

    def get_paper_details(self, paper_id):
        # Implement details retrieval
        pass

# Register
gatekeeper.aggregator.add_custom_source(MyCustomSource(), priority=7)
```

## System Requirements

- Python 3.8+
- Internet connection
- Anthropic API key (required)
- 2GB+ RAM recommended

## API Keys

### Required
- **Anthropic**: Get from https://console.anthropic.com/

### Optional (Enhance Features)
- **JSTOR**: For unique academic insights
- **Semantic Scholar**: Higher rate limits
- **PubMed**: Higher rate limits

### Free (No Key Needed)
- arXiv
- CrossRef (optional key for higher limits)
- OpenAlex (email recommended for polite pool)

## Output

Research reports saved to `research_system/outputs/`:
- JSON format with complete metadata
- Includes papers, synthesis, insights, validation scores

## Quality Standards

The system enforces academic standards:
- **Academic Rigor**: ≥8.0/10 (70%+ peer-reviewed)
- **Source Diversity**: Multiple independent sources
- **Citation Quality**: Highly-cited papers included
- **Credibility**: ≥9.0/10 average source credibility
- **Novelty**: Recent research (40%+ from last 5 years)

## Troubleshooting

### No Results Found
- Check API keys are configured
- Verify internet connection
- Try broader search terms

### Low Quality Scores
- System will suggest improvements
- Add more sources (JSTOR recommended)
- Expand year range

### AI Features Not Working
- Verify ANTHROPIC_API_KEY is set
- Check API key permissions
- Review API usage limits

## Development

### Project Structure
```
research_system/
├── core/               # Core components
│   ├── config_manager.py
│   ├── anthropic_integration.py
│   ├── academic_research_aggregator.py
│   └── research_gatekeeper.py
├── sources/            # Research source integrations
├── subagents/          # Specialized subagents
├── validation/         # Quality validation
├── chat/               # Chat interface
├── config/             # Configuration files
├── outputs/            # Generated reports
└── cache/              # Cached data
```

## License

MIT License - Feel free to use and modify

## Contributing

Contributions welcome! Areas for enhancement:
- Additional research sources
- Enhanced AI analysis
- Visualization features
- Performance optimizations

## Support

For issues or questions:
- Review documentation
- Check configuration
- Verify API keys

---

**Built with Claude AI** - Advanced research synthesis and analysis
**Version**: 1.0.0
**Status**: Production Ready ✅
