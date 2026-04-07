---
name: AGI Benchmark Research Plan
description: Research plan for Kaggle Measuring Progress Toward AGI - Social Cognition track
type: project
---

# Tacit Coordination Benchmark - Research Plan

## Competition Context
- **Track**: Social Cognition ($20,000 prize)
- **Focus**: Can the model understand and navigate social situations - beyond producing polite text?
- **Submission Deadline**: April 16, 2026
- **Key Requirement**: Create Kaggle Benchmark using kaggle-benchmarks SDK

## Benchmark Design: Tacit Coordination & Common Ground

### Core Concept
Measure how well LLMs can align on **common knowledge** across different domains without explicit communication. Two agents must independently select the same item from a category, testing their shared cultural/semantic knowledge.

**Critical Constraint**: 题目不得包含任何引导性语言（如 "most famous"、"traditional"），只提供类别和选项，让 agent 完全依赖内隐文化知识做出选择。

### Task Categories (36 domains)

| Category | Domains | Items |
|----------|---------|-------|
| Basic Cognitive | Numbers, Colors, Shapes, Directions, Time | 100 |
| Social & Cultural | Cities, Countries, Famous People, Brands, Foods, Drinks, Holidays, Sports, Music, Movies, Animals, Occupations | 240 |
| Biological World | Animals, Plants, Body Parts, Senses | 80 |
| Objects & Functions | Tools, Vehicles, Clothing, Furniture | 80 |
| Abstract Concepts | Emotions, Weather, Seasons, Arts, Books | 100 |
| Space & Location | Rooms, Buildings, Locations | 60 |
| Social Roles | Occupations, Family Roles | 40 |
| Media & Entertainment | Movies, Music | 40 |
| Digital World | Digital, Tech | 40 |
| Nature | Nature | 20 |

**Total**: 720 items × 2 languages (English/Chinese) = 1440 items

### Task Structure

```python
# Example task format
@kbench.task(name="tacit_coordination")
def tacit_coordination_task(
    llm,
    item_id: str,
    domain: str,
    category: str,           # ONLY category, no leading questions
    options: list[str],      # 4 options, randomized order
    culture: str,            # "us", "china", "universal"
    language: str            # "en" or "zh"
) -> dict:
    """
    Test if two agents would pick the same option without communication.
    Returns: selected option, confidence, reasoning
    """
```

### Prompt Design

```
You are playing a coordination game with another agent.
If you both select the SAME option, you each get $1.
You cannot communicate - you must rely on what seems most obvious.
Note: The other agent sees the SAME options, but in a DIFFERENT order.

{category}

{options}

Which option do you choose? Respond with the exact option text.
```

## Research Plan

### Phase 1: Dataset Generation with Statistical Analysis (Days 1-5)

#### Step 1.1: LLM-Based Item Generation (Day 1-2)
**Goal**: Generate 720 items across 36 domains using structured prompting

**Generation Process**:
1. 使用标准化脚本调用 LLM 生成题目
2. 每个领域生成 25 道题（预留 5 道用于筛选）
3. 每道题包含：
   - `domain`: 领域类别
   - `category`: 类别描述（无引导性语言）
   - `options`: 4 个选项
   - `culture`: "us"/"china"/"universal"
   - `focal_option`: 预期的最显著选项

**Prompt Template**:
```python
generation_prompt = """
Generate 5 tacit coordination items for the {domain} domain.

Requirements:
1. Category should be descriptive but NOT leading (no "most famous", "traditional", etc.)
2. 4 options: 1 focal (most salient), 3 distractors (plausible but less salient)
3. Culture: {culture}
4. Language: {language}

Output JSON format:
[{
    "category": "category description",
    "options": ["option1", "option2", "option3", "option4"],
    "focal_option": "most salient option",
    "rationale": "why this is the focal option"
}]
"""
```

#### Step 1.2: Statistical Quality Analysis (Day 3-4)
**Goal**: 对生成的题目进行统计分析，筛选高质量题目

**分析维度**:

1. **Option Distance Analysis**（选项距离分析）
   - 使用 embedding 模型计算 4 个选项之间的语义距离
   - 指标：
     - `min_distance`: focal option 到其他选项的最小距离
     - `avg_distance`: focal option 到其他选项的平均距离
     - `std_distance`: 所有选项间距离的标准差
   - 假设：模型倾向于选择距离其他选项最远（最独特）的选项

2. **Salience Score**（显著性得分）
   - 使用 LLM 对每个选项进行显著性打分
   - 计算 softmax 概率分布
   - 指标：
     - `focal_salience`: focal option 的概率
     - `entropy`: 概率分布的熵（越低越集中）
     - `max_margin`: 第一名与第二名的概率差

3. **Domain-Level Statistics**（领域级统计）
   - 每个领域内题目的平均质量指标
   - 识别质量较差的领域，重新生成

**筛选标准**:
```python
quality_filters = {
    "min_distance": 0.4,           # focal option 需要足够独特
    "focal_salience": 0.5,         # focal option 显著性 > 50%
    "entropy": 1.2,                # 熵不超过阈值（避免过于模糊）
    "max_margin": 0.2              # 第一名优势明显
}
```

#### Step 1.3: Validation and Iteration (Day 5)
**Goal**: 验证题目质量，进行迭代优化

**验证步骤**:
1. 人工抽查每个领域 5 道题
2. 对统计指标边缘的题目进行人工审核
3. 质量不达标的题目重新生成

**Deliverable**:
- 720 道高质量题目的 JSON 文件
- 每道题的统计质量指标
- 题目质量报告（可视化）

### Phase 2: Task Implementation (Days 6-8)
**Goal**: Build kaggle-benchmarks tasks

**Tasks**:
1. Set up kaggle-benchmarks environment
2. Create task decorator for each domain
3. Implement assertions (match checking, confidence calibration)
4. Add metadata tracking (response time, reasoning if requested)

**Test**:
- Local test with mock data
- Kaggle notebook integration test
- Verify leaderboard format

**Deliverable**: Working Python notebook with all tasks

### Phase 3: Multi-Model Evaluation (Days 9-11)
**Goal**: Run benchmark on multiple models

**Tasks**:
1. Select 5-6 frontier models (GPT-4o, Claude 3.5, Gemini, etc.)
2. Run full benchmark (720 items × N models)
3. Compute metrics:
   - Coordination success rate (exact match)
   - Domain-wise performance
   - Difficulty correlation
   - Inter-model agreement

**Test**: Statistical significance tests, confidence intervals

**Deliverable**: Results dataframe with all model scores

### Phase 4: Analysis & Writeup (Days 12-14)
**Goal**: Prepare competition submission

**Tasks**:
1. Analyze patterns in failures
2. Create visualizations (domain heatmaps, model comparisons)
3. Write 1500-word writeup following template
4. Create Kaggle Benchmark entity
5. Attach public notebook

**Test**: Peer review of writeup, validation of benchmark URL

**Deliverable**: Final submission package

## Success Metrics

1. **Discriminatory Power**: Models should score between 30-70% (not all fail or all succeed)
2. **Domain Variance**: Show which knowledge domains are better aligned
3. **Novel Insight**: Reveal how LLMs share/disagree on common ground
4. **Code Quality**: Clean, reproducible, well-documented

## Required Permissions

None identified yet - all work can be done with:
- Kaggle account (already have)
- Standard Kaggle benchmark quota ($50/day provided)
- Open access models on Kaggle platform

## Key References

- Clark, H. H. (1996). *Using Language*
- Measuring Progress Toward AGI paper (DeepMind)
- Kaggle Benchmarks documentation
