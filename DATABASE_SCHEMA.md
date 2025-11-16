# Vector Database Schema Documentation

## Overview

The vector database stores all research data, viral strategies, video analysis, and output data using OpenAI embeddings for semantic search and retrieval. The Content Retriever Agent gatekeeps all access to this database.

## Content Types

### 1. RESEARCH (`ContentType.RESEARCH`)

Stores academic research from Research Gatekeeper.

**Fields:**
- `content`: Full research text
- `embedding`: Vector embedding (OpenAI text-embedding-3-large)
- `metadata`:
  - `topic`: Research topic
  - `sources`: List of databases used (JSTOR, Semantic Scholar, etc.)
  - `key_insights`: List of key findings
  - `citations`: List of citation objects
  - `num_sources`: Count of sources
  - `num_citations`: Count of citations
  - `quality_score`: Research quality (0-10, minimum 8.0)

**Example:**
```json
{
  "id": "a1b2c3d4e5f6g7h8",
  "content_type": "research",
  "content": "Quantum computing represents a paradigm shift...",
  "metadata": {
    "topic": "Quantum Computing",
    "sources": ["JSTOR", "Semantic Scholar", "arXiv"],
    "key_insights": ["Quantum supremacy achieved", "Error correction improved"],
    "citations": [
      {"title": "Quantum Advances", "author": "Smith et al.", "year": "2025"}
    ],
    "quality_score": 9.5
  }
}
```

### 2. VIRAL_STRATEGY (`ContentType.VIRAL_STRATEGY`)

Stores viral optimization strategies from Viral Analyser Gatekeeper.

**Fields:**
- `content`: Complete strategy description
- `embedding`: Vector embedding
- `viral_tier`: Performance tier (Gold/Silver/Bronze/Pending)
- `metadata`:
  - `topic`: Content topic
  - `hooks`: List of hook variations
  - `num_hooks`: Count of hooks
  - `psychology_triggers`: List of triggers used
  - `num_triggers`: Count of triggers
  - `retention_strategy`: Retention approach
  - `engagement_strategy`: Engagement approach
  - `viral_score`: Predicted score (0-10, minimum 9.0)
  - `video_duration`: Target length in minutes
  - `target_audience`: Audience description

**Example:**
```json
{
  "id": "h8g7f6e5d4c3b2a1",
  "content_type": "viral_strategy",
  "viral_tier": "gold",
  "content": "Hook: 'What if computers could break all encryption?'...",
  "metadata": {
    "topic": "Quantum Computing",
    "hooks": [
      "What if computers could break all encryption?",
      "The quantum revolution that terrifies governments"
    ],
    "psychology_triggers": ["Curiosity Gap", "Fear", "Authority"],
    "viral_score": 9.7,
    "video_duration": 15,
    "target_audience": "Tech enthusiasts 25-40"
  }
}
```

### 3. VIDEO_ANALYSIS (`ContentType.VIDEO_ANALYSIS`)

Stores analyzed YouTube videos from Viral Analyser Gatekeeper.

**Fields:**
- `content`: Complete analysis text
- `embedding`: Vector embedding
- `viral_tier`: Classified tier based on metrics
- `metadata`:
  - `video_id`: YouTube video ID
  - `video_url`: Full URL
  - `metrics`: Object containing:
    - `title`: Video title
    - `channel`: Channel name
    - `views`: View count
    - `likes`: Like count
    - `comments`: Comment count
    - `engagement_rate`: Engagement percentage
    - `retention_rate`: Retention percentage
    - `hook_analysis`: Hook effectiveness data
  - `identified_triggers`: List of psychology triggers found
  - `num_triggers`: Count of triggers
  - `structure`: Video structure breakdown

**Viral Tier Classification:**
- **Gold**: 1M+ views, 10%+ engagement, 60%+ retention
- **Silver**: 500K+ views, 7%+ engagement, 50%+ retention
- **Bronze**: 100K+ views, 5%+ engagement, 40%+ retention
- **Pending**: Below thresholds

**Example:**
```json
{
  "id": "z9y8x7w6v5u4t3s2",
  "content_type": "video_analysis",
  "viral_tier": "gold",
  "content": "Analysis: This video achieves high retention through...",
  "metadata": {
    "video_id": "abc123xyz",
    "video_url": "https://youtube.com/watch?v=abc123xyz",
    "metrics": {
      "title": "Quantum Computers Will Change Everything",
      "channel": "Tech Explained",
      "views": 2500000,
      "likes": 150000,
      "engagement_rate": 12.5,
      "retention_rate": 65.0
    },
    "identified_triggers": ["Curiosity Gap", "Authority", "Transformation"],
    "structure": {
      "intro": "0-15s",
      "main": "15s-12m",
      "conclusion": "12m-15m"
    }
  }
}
```

### 4. OUTPUT_DATA (`ContentType.OUTPUT_DATA`)

Stores final outputs from Content Synthesis Gatekeeper.

**Fields:**
- `content`: Final output content (script, scenes, etc.)
- `embedding`: Vector embedding
- `metadata`:
  - `output_type`: Type (script, visual_scenes, production_notes)
  - `topic`: Content topic
  - `quality_score`: Quality rating (0-10, minimum 9.0)
  - `viral_score`: Predicted viral performance
  - `production_ready`: Boolean flag
  - `word_count`: Word count
  - `related_research_id`: Link to research entry
  - `related_strategy_id`: Link to viral strategy entry

**Example:**
```json
{
  "id": "r2s3t4u5v6w7x8y9",
  "content_type": "output_data",
  "content": "FULL SCRIPT: [Opening Hook - 0:00-0:15]...",
  "metadata": {
    "output_type": "script",
    "topic": "Quantum Computing",
    "quality_score": 9.8,
    "viral_score": 9.5,
    "production_ready": true,
    "word_count": 12500,
    "related_research_id": "a1b2c3d4e5f6g7h8",
    "related_strategy_id": "h8g7f6e5d4c3b2a1"
  }
}
```

## Data Flow

### Indexing Flow (Gatekeepers → Content Retriever Agent → Vector Database)

```
┌─────────────────────────┐
│  Research Gatekeeper    │
│  (Academic Research)    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Viral Analyser          │
│ Gatekeeper              │
│ (Strategy + Analysis)   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Content Synthesis       │
│ Gatekeeper              │
│ (Final Output)          │
└───────────┬─────────────┘
            │
            ▼
    ┌───────────────────────────┐
    │ Content Retriever Agent   │
    │ (Validates & Indexes)     │
    └───────────┬───────────────┘
                │
                ▼
        ┌───────────────────┐
        │ Vector Database   │
        │ (OpenAI Embeddings)│
        └───────────────────┘
```

### Retrieval Flow (Gatekeepers ← Content Retriever Agent ← Vector Database)

```
┌─────────────────────────┐
│  Gatekeeper Request     │
│  "Find viral strategies │
│   for quantum computing"│
└───────────┬─────────────┘
            │
            ▼
    ┌───────────────────────────┐
    │ Content Retriever Agent   │
    │ - Generate query embedding│
    │ - Search vector DB        │
    │ - Apply filters & ranking │
    └───────────┬───────────────┘
                │
                ▼
        ┌───────────────────┐
        │ Vector Database   │
        │ - Similarity search│
        │ - Return top_k    │
        └───────────┬───────┘
                    │
                    ▼
    ┌───────────────────────────┐
    │ Content Retriever Agent   │
    │ - Sort by viral score     │
    │ - Format results          │
    └───────────┬───────────────┘
                │
                ▼
        ┌───────────────┐
        │  Gatekeeper   │
        │  (Uses data)  │
        └───────────────┘
```

## Storage Format

### File Structure

```
data/
└── vector_db/
    └── vector_db.json        # Main database file
```

### JSON Structure

```json
{
  "version": "1.0",
  "embedding_model": "text-embedding-3-large",
  "last_updated": "2025-11-16T12:00:00",
  "entries": [
    {
      "id": "unique_id_here",
      "content": "Full text content...",
      "content_type": "research|viral_strategy|video_analysis|output_data",
      "embedding": [0.123, -0.456, 0.789, ...],  // 3072 dimensions
      "metadata": { /* type-specific fields */ },
      "timestamp": "2025-11-16T12:00:00",
      "viral_tier": "gold|silver|bronze|pending"
    }
  ]
}
```

## Embedding Dimensions

- **Model**: OpenAI `text-embedding-3-large`
- **Dimensions**: 3072
- **Similarity Metric**: Cosine similarity
- **Range**: [-1, 1] (higher is more similar)

## Quality Thresholds

As per workflow requirements:

| Content Type | Minimum Score | Gatekeeper Source |
|--------------|---------------|-------------------|
| Research | 8.0/10 | Research Gatekeeper |
| Viral Strategy | 9.0/10 | Viral Analyser Gatekeeper |
| Output Data | 9.0/10 | Content Synthesis Gatekeeper |
| Overall System | 9.0/10 | Master Orchestrator |

## Indexing Operations

### Content Retriever Agent Methods

1. **`index_research()`** - Index academic research
2. **`index_viral_strategy()`** - Index viral strategies
3. **`index_video_analysis()`** - Index YouTube video analysis
4. **`index_output()`** - Index final outputs

## Retrieval Operations

### Content Retriever Agent Methods

1. **`retrieve_research()`** - Get relevant research by topic
2. **`retrieve_viral_strategies()`** - Get viral strategies by topic/tier
3. **`retrieve_successful_patterns()`** - Get successful video patterns
4. **`retrieve_best_hooks()`** - Get top-performing hooks
5. **`retrieve_psychology_triggers()`** - Get effective triggers by topic
6. **`get_recommendations()`** - Get intelligent recommendations

## Search Parameters

### Similarity Search

```python
results = agent.retrieve_viral_strategies(
    topic="Quantum Computing",
    viral_tier=ViralTier.GOLD,  # Optional: Filter by tier
    top_k=5                      # Return top 5 results
)
```

### Filtering

- **By Content Type**: `ContentType.RESEARCH`, `ContentType.VIRAL_STRATEGY`, etc.
- **By Viral Tier**: `ViralTier.GOLD`, `ViralTier.SILVER`, `ViralTier.BRONZE`
- **By Quality Score**: Minimum quality threshold
- **By Similarity**: Minimum cosine similarity threshold

## Database Maintenance

### Quality Validation

```python
# Validate database quality
report = agent.validate_database_quality()

# Returns:
{
  "total_entries": 150,
  "quality_issues": [],
  "tier_distribution": {
    "gold": 25,
    "silver": 40,
    "bronze": 35
  },
  "health_status": "GOOD"
}
```

### Statistics

```python
# Get database statistics
stats = agent.get_database_stats()

# Returns:
{
  "total_entries": 150,
  "by_content_type": {
    "research": 30,
    "viral_strategy": 50,
    "video_analysis": 40,
    "output_data": 30
  },
  "by_viral_tier": {
    "gold": 25,
    "silver": 40,
    "bronze": 35,
    "pending": 0
  },
  "avg_viral_score": 9.3,
  "retrieval_history_count": 500
}
```

## Performance Considerations

### Optimization

1. **Caching**: Frequently accessed queries are cached
2. **Batch Processing**: Multiple entries indexed in batch
3. **Incremental Updates**: Only new/changed entries re-embedded
4. **Similarity Thresholds**: Minimum similarity reduces result set

### Scalability

- **Current**: Optimized for 1,000-10,000 entries
- **Storage**: ~5KB per entry (with 3072-dim embeddings)
- **Search Speed**: O(n) linear search (fast for <10K entries)
- **Future**: Can migrate to specialized vector DB (Pinecone, Weaviate) for >10K

## Integration with Workflow

As specified in `File_Inventory_Workflow_Full_System.md`:

1. **Process 4 (Video Analysis)** - Lines 557-564
   - Video metadata → Vector Database
   - Success patterns → Vector Database
   - Psychology triggers → Vector Database
   - Structure template → Vector Database

2. **Process 6 (Continuous Learning)** - Lines 683-761
   - Successful videos → Pattern extraction → Database update
   - Trigger effectiveness → Weight adjustments → Database update
   - Hook performance → Rankings → Database update

3. **Database Storage** - Lines 251-259
   - Successful video analysis
   - Viral hooks and strategies
   - Psychology trigger effectiveness
   - Retention patterns by topic
   - Research citations and findings

## API Reference

See `content_retriever_agent.py` for complete API documentation and usage examples.
