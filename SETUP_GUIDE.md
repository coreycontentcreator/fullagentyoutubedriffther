# Content Synthesis System - Setup Guide

## Quick Setup (5 minutes)

### 1. Prerequisites

- Python 3.8 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))
- 2GB free disk space

### 2. Installation

```bash
# Clone or download the repository
cd fullagentyoutubedriffther

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Key

Set your Anthropic API key as an environment variable:

**Linux/macOS:**
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY='your-api-key-here'
```

**Or create a `.env` file:**
```bash
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

### 4. Run the System

**Interactive Mode (Recommended):**
```bash
python main.py
```

**CLI Mode:**
```bash
python main.py --topic "The Future of AI" --duration 15
```

**Quick Start Example:**
```bash
python examples/quick_start.py
```

---

## Detailed Setup

### System Requirements

**Minimum:**
- Python 3.8+
- 4GB RAM
- Stable internet connection
- Anthropic API key

**Recommended:**
- Python 3.10+
- 8GB RAM
- Fast internet connection
- Claude Sonnet 4.5 API access

### Installation Methods

#### Method 1: Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Method 2: System-wide Installation

```bash
pip install -r requirements.txt
```

#### Method 3: Development Setup

```bash
# Install with development dependencies
pip install -r requirements.txt
pip install -e .  # Install in editable mode
```

### Configuration

#### Default Configuration

The system creates a default configuration file at `config/config.yaml`:

```yaml
anthropic:
  api_key: ${ANTHROPIC_API_KEY}
  model: claude-sonnet-4-5-20250929
  max_tokens: 8000
  temperature: 0.7
  timeout: 300

system:
  log_level: INFO
  output_dir: outputs
  max_iterations: 5
  quality_threshold: 9.0
  enable_caching: true
  cache_ttl: 3600

content_synthesis:
  min_script_length: 5000
  max_script_length: 15000
  target_video_duration: 15
  min_scene_count: 50
  max_scene_count: 200
  quality_threshold: 9.0
  enable_multi_pass_validation: true
  hook_interval: 120
```

#### Custom Configuration

Create a custom config file:

```bash
cp config/config.yaml config/my_config.yaml
# Edit my_config.yaml with your preferences
```

Use custom config:

```bash
python main.py --config config/my_config.yaml
```

### Directory Structure

After setup, your directory should look like:

```
fullagentyoutubedriffther/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config_manager.py
│   │   └── anthropic_client.py
│   ├── content_synthesis/
│   │   ├── __init__.py
│   │   ├── content_synthesis_gatekeeper.py
│   │   ├── scriptwriter.py
│   │   ├── visual_scene_architect.py
│   │   ├── production_notes_generator.py
│   │   ├── narrative_structure_engine.py
│   │   ├── content_validator.py
│   │   └── base_subagent.py
│   ├── chat_interface.py
│   └── __init__.py
├── config/
│   └── config.yaml
├── examples/
│   ├── quick_start.py
│   └── advanced_usage.py
├── outputs/
├── tests/
├── main.py
├── requirements.txt
├── README.md
└── SETUP_GUIDE.md
```

---

## Usage Modes

### 1. Interactive Chat Mode

The easiest way to use the system:

```bash
python main.py
```

Features:
- Natural language interaction
- Guided content generation
- Real-time feedback
- Project management
- Configuration adjustment

### 2. CLI Mode

For scripting and automation:

```bash
python main.py --topic "Your Topic" --duration 15 --style documentary
```

Options:
```bash
--topic          Video topic (required in CLI mode)
--duration       Duration in minutes (default: 15)
--style          Visual style (documentary/educational/cinematic)
--tone           Script tone (engaging/authoritative/casual)
--audience       Target audience (default: general audience)
--budget         Production budget (low/medium/high)
--no-iteration   Disable iterative refinement
--max-iterations Max refinement iterations (default: 5)
--output         Output directory (default: outputs)
--log-level      Logging level (DEBUG/INFO/WARNING/ERROR)
```

### 3. Python API

For integration into other applications:

```python
from src.core.config_manager import get_config_manager
from src.core.anthropic_client import AnthropicClient
from src.content_synthesis import ContentSynthesisGatekeeper

# Initialize
config_manager = get_config_manager()
anthropic_config = config_manager.get_anthropic_config()
anthropic_client = AnthropicClient(
    api_key=anthropic_config.api_key,
    model=anthropic_config.model
)

content_config = config_manager.get_content_synthesis_config()
gatekeeper = ContentSynthesisGatekeeper(anthropic_client, content_config)

# Generate content
package = gatekeeper.quick_generate(
    topic="The Future of AI",
    video_duration=15
)

# Access results
print(f"Quality: {package.quality_score}/10")
print(f"Script: {package.script}")
print(f"Scenes: {package.scene_count}")
```

---

## Troubleshooting

### Common Issues

#### 1. API Key Not Found

**Error:**
```
❌ ANTHROPIC API KEY NOT FOUND
```

**Solution:**
```bash
# Set environment variable
export ANTHROPIC_API_KEY='your-key-here'

# Or create .env file
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

#### 2. Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'anthropic'
```

**Solution:**
```bash
pip install -r requirements.txt
```

#### 3. Permission Errors

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'outputs'
```

**Solution:**
```bash
# Create outputs directory
mkdir -p outputs
chmod 755 outputs
```

#### 4. API Rate Limits

**Error:**
```
Rate limit exceeded
```

**Solution:**
- Wait a few minutes and retry
- Reduce `max_iterations` in config
- Use `--no-iteration` flag for faster generation

#### 5. Low Quality Scores

**Issue:** Generated content has quality score below threshold

**Solutions:**
1. Enable iteration:
   ```bash
   python main.py --topic "Your Topic"  # Iteration enabled by default
   ```

2. Increase max iterations:
   ```bash
   python main.py --topic "Your Topic" --max-iterations 7
   ```

3. Provide research data:
   ```python
   package = gatekeeper.generate_content_sync(
       topic="Your Topic",
       research_data={
           'key_findings': [...],
           'citations': [...]
       }
   )
   ```

---

## Performance Optimization

### 1. Faster Generation

```bash
# Disable iteration for quick drafts
python main.py --topic "Your Topic" --no-iteration

# Use shorter duration
python main.py --topic "Your Topic" --duration 5

# Lower quality threshold in config
```

### 2. Higher Quality

```bash
# Increase iterations
python main.py --topic "Your Topic" --max-iterations 7

# Scale for world-class quality
```

```python
config_manager.scale_for_request({
    'quality_level': 'world-class',
    'complexity': 'complex'
})
```

### 3. Cost Optimization

- Use `--no-iteration` for drafts
- Cache results (enabled by default)
- Shorter videos use fewer tokens
- Use specific topics (less token usage than broad topics)

---

## Next Steps

1. **Run Quick Start:**
   ```bash
   python examples/quick_start.py
   ```

2. **Try Interactive Mode:**
   ```bash
   python main.py
   ```

3. **Explore Advanced Features:**
   ```bash
   python examples/advanced_usage.py
   ```

4. **Read the Documentation:**
   - See `README.md` for features
   - See `API_DOCUMENTATION.md` for API reference
   - See examples in `examples/` directory

---

## Support

- Check documentation in `README.md`
- Review examples in `examples/`
- Check troubleshooting section above
- Review system logs in `content_synthesis.log`

---

**You're all set! Start creating world-class content! 🚀**
