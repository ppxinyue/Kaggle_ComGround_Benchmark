# Claude Code Project Memory - Tacit Coordination Benchmark

> **Companion AI for Kaggle Measuring Progress Toward AGI - Social Cognition Track**

## Project Overview

**Competition**: Kaggle Measuring Progress Toward AGI - Social Cognition
**Track**: Social Cognition ($20,000 prize)
**Submission Deadline**: April 16, 2026
**Focus**: Can LLMs understand and navigate social situations beyond producing polite text?

---

## Core Benchmark Concept: Tacit Coordination

### What We're Testing

**Tacit Coordination**: Two agents must independently select the same item from a category WITHOUT explicit communication. This tests:
- Shared cultural knowledge alignment
- Common ground understanding
- Implicit knowledge coordination

### Critical Design Principle

**NO LEADING LANGUAGE** - 题目不得包含任何引导性语言，包括但不限于：
- "most famous"（最著名）
- "traditional"（传统）
- "typical"（典型）
- "best"（最好）
- "most important"（最重要）

**错误示例**（包含引导）:
```
What is the most famous city in the United States?
Options: New York, Los Angeles, Chicago, Houston
```

**正确示例**（无引导）:
```
US Cities
Options: New York, Los Angeles, Chicago, Houston
```

**只提供类别/语境 + 选项**，让 agent 完全依赖内隐文化知识做出选择。

---

## Task Structure

### Prompt Format
```
You are playing a coordination game with another agent.
If you both select the SAME option, you each get $1.
You cannot communicate - you must try to coordinate.
Note: The other agent sees the SAME options, but in a DIFFERENT order.

[Category/Context]
[Options - randomized order for each agent]

Which option do you choose? Respond with the exact option text.
```

### Data Structure
```python
{
    # Metadata
    "item_id": str,              # Unique identifier
    "item_id_en": str,           # English version ID
    "item_id_zh": str,           # Chinese version ID
    "domain": str,               # Domain category
    "language": str,             # "en" or "zh"
    "culture": str,              # "us", "china", or "universal"
    "category": str,             # Category description (NO leading language!)
    "options": list[str],        # 4 options (standard order)
    "focal_option": str,         # Most salient option

    # Quality metrics
    "quality_metrics": {
        "min_distance": float,      # Semantic distance from focal to others
        "avg_distance": float,      # Average distance
        "focal_salience": float,    # LLM salience probability
        "entropy": float,           # Distribution entropy
        "max_margin": float         # Margin between top 2
    }
}
```

---

## 36 Research Domains

### Category 1: Basic Cognitive (5 domains, 100 items)
1. **Numbers** - Number salience (1-10 → 7)
2. **Colors** - Color associations (10us/10china)
3. **Shapes** - Shape concepts
4. **Directions** - Directional cognition
5. **Time** - Temporal associations

### Category 2: Social & Cultural (12 domains, 240 items)
6. **Cities** - City representativeness (10us/10china)
7. **Countries** - Country associations (10us/10china)
8. **Famous People** - Celebrity recognition (10us/10china)
9. **Brands** - Brand awareness (10us/10china)
10. **Foods** - Food typicality (10us/10china)
11. **Drinks** - Beverage associations (10us/10china)
12. **Holidays** - Holiday associations (10us/10china)
13. **Sports** - Sport cognition (10us/10china)
14. **Music** - Music genres (10us/10china)
15. **Movies** - Movie types (10us/10china)
16. **Animals** - Animal symbolism (10us/10china)
17. **Occupations** - Professional roles (universal)

### Other Categories
- **Biological World**: Plants, Body Parts, Senses (80 items)
- **Objects & Functions**: Tools, Vehicles, Clothing, Furniture (80 items)
- **Abstract Concepts**: Emotions, Weather, Seasons, Arts, Books (100 items)
- **Space & Location**: Rooms, Buildings, Locations (60 items)
- **Social Roles**: Family Roles (40 items)
- **Digital World**: Digital, Tech (40 items)
- **Nature**: Natural phenomena (20 items)

**Total**: 720 items × 2 languages (English/Chinese) = 1440 items

---

## Research Phases

### Phase 1: Dataset Generation with Statistical Analysis (Days 1-5)

#### Step 1.1: LLM-Based Item Generation
- Use standardized scripts to generate 720 items across 36 domains
- Generate 20 items per domain
- Each item: domain, category (NO leading language), 4 options, culture tag, focal option

#### Step 1.2: Statistical Quality Analysis

**Option Distance Analysis**:
- Use embedding model to compute semantic distances between options
- Metrics: `min_distance`, `avg_distance`, `std_distance`
- Hypothesis: Models tend to choose semantically distant (most unique) options

#### Step 1.3: Validation and Iteration
- Manual sampling of 5 items per domain
- Review items with borderline metrics
- Regenerate substandard items

**Deliverable**: 720 high-quality items JSON with quality metrics

### Phase 2: Task Implementation (Days 6-8)
- Set up kaggle-benchmarks environment
- Create task decorators
- Implement assertions and metadata tracking
- Local testing and integration

### Phase 3: Multi-Model Evaluation (Days 9-11)
- Run benchmark on 5-6 frontier models
- Compute metrics: coordination rate, domain performance, inter-model agreement
- Statistical significance testing

### Phase 4: Analysis & Writeup (Days 12-14)
- Analyze failure patterns
- Create visualizations
- Write 1500-word submission
- Create Kaggle Benchmark entity

---

## Evaluation Metrics

### Model Coordination Rate
For each item:
1. Call LLM 100 times (simulating 100 subjects, randomizing option order each time)
2. Compute pair-wise agreement for each subject with the other 99
3. Average across all pairs as the model coordination rate

```
Coordination_Rate(item) = sum(matches) / (100 * 99 / 2)
```

### Model-Human Alignment
Compare model's most frequent choice vs human's most frequent choice

```
Alignment(item) = 1 if mode(model_choices) == mode(human_choices) else 0
Overall_Alignment = sum(Alignment) / total_items
```

### Domain-Level Analysis
- Average model coordination rate per domain
- Model-human alignment per domain
- Cultural difference analysis (US vs China items)
- Language difference analysis (English vs Chinese)

---


---

## Success Metrics

1. **Discriminatory Power**: Models score 30-70% (not all fail or all succeed)
2. **Domain Variance**: Show which knowledge domains are better aligned
3. **Novel Insight**: Reveal how LLMs share/disagree on common ground
4. **Code Quality**: Clean, reproducible, well-documented


---

## References

- Clark, H. H. (1996). *Using Language*
- Measuring Progress Toward AGI paper (DeepMind)
- Kaggle Benchmarks documentation

---

## Important Notes for AI Assistant

1. **Never use leading language** when generating or modifying items
2. **Category should be neutral**: "US Cities" not "Most Famous US Cities"
3. **Quality metrics are critical**: Each item must pass distance and salience thresholds
4. **Cultural balance matters**: Culture-sensitive domains need 10us/10china split
5. **Bilingual consistency**: English and Chinese versions must be identical except language
