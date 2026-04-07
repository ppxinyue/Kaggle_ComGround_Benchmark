# Scripts for Tacit Coordination Benchmark

This directory contains scripts for generating and testing the Tacit Coordination Dataset.

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys**:
   Edit `.env` file and add your API keys:
   ```bash
   # Required for item generation
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

   # Optional: for Anthropic
   ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

## Scripts

### Core Modules

- **`task_definition.py`** - Data structures and quality metrics
  - `TacitCoordinationItem` - Item data structure
  - `QualityMetrics` - Quality filtering logic
  - `compute_distance_metrics()` - Embedding-based metrics
  - `compute_salience_metrics()` - LLM-based salience metrics
  - `get_generation_prompt()` - Prompt templates

- **`test_task_definition.py`** - Test suite (15 tests)
  ```bash
  python scripts/test_task_definition.py
  ```

### Generation Scripts

- **`pilot_test.py`** - Quick pilot test (3 items)
  ```bash
  python scripts/pilot_test.py
  ```

- **`generate_dataset.py`** - Full dataset generator
  ```bash
  # Generate single domain
  python scripts/generate_dataset.py -d Numbers -o data/generated_items

  # Generate all domains
  python scripts/generate_dataset.py --all-domains -o data/generated_items

  # Resume from previous run (skip existing)
  python scripts/generate_dataset.py --all-domains --skip-existing -o data/generated_items
  ```

## Quality Metrics

Each generated item is analyzed using:

| Metric | Description | Threshold |
|--------|-------------|-----------|
| `min_distance` | Min semantic distance from focal to others | ≥ 0.4 |
| `avg_distance` | Avg semantic distance from focal to others | - |
| `focal_salience` | LLM salience probability for focal option | ≥ 0.5 |
| `entropy` | Entropy of option probability distribution | ≤ 1.2 |
| `max_margin` | Margin between top 2 options | ≥ 0.2 |

## Output Format

### Item JSON
```json
{
  "item_id": "Numbers_universal_en_000",
  "domain": "Numbers",
  "category": "Numbers 1-10",
  "options": ["1", "3", "7", "10"],
  "focal_option": "7",
  "culture": "universal",
  "language": "en",
  "quality_metrics": {
    "min_distance": 0.52,
    "avg_distance": 0.68,
    "focal_salience": 0.82,
    "entropy": 0.95,
    "max_margin": 0.45,
    "passes_filter": true
  }
}
```

## CLI Options

```
python scripts/generate_dataset.py [OPTIONS]

Options:
  -d, --domain TEXT      Specific domain to generate
  -c, --culture TEXT     Culture: us, china, universal
  -l, --language TEXT    Language: en, zh
  -a, --all-domains      Generate all domains
  -o, --output PATH      Output directory (default: data/generated_items)
  -p, --provider TEXT    LLM provider: openai or anthropic
  -n, --num-items INT    Target items per domain (default: 20)
  -s, --skip-existing    Skip domains with existing output files
```

## Example Workflow

1. **Run pilot test** to verify setup:
   ```bash
   python scripts/pilot_test.py
   ```

2. **Generate single domain** to test quality:
   ```bash
   python scripts/generate_dataset.py -d Numbers -n 5
   ```

3. **Generate full dataset** (takes time):
   ```bash
   python scripts/generate_dataset.py --all-domains
   ```
