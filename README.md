# ComGround: Measuring Common Ground in LLMs through Category Norms and Tacit Coordination

[![Kaggle Competition](https://img.shields.io/badge/Kaggle-Social%20Cognition%20Track-blue)](https://www.kaggle.com/competitions/measuring-abc)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)]()

**ComGround** is a benchmark for evaluating whether large language models (LLMs) share the *common ground* that underpins human social cognition -- the shared knowledge, beliefs, and cultural salience that enable communication and coordination.

> Submitted to **Kaggle Measuring Progress Toward AGI -- Social Cognition Track** ($20,000 prize, under review stage).

---

## Overview

Common ground is a core component of social cognition: when asked to name "a fruit," most people say "apple"; when asked to independently pick the same US city, most say "New York." Both reveal the same underlying capacity -- shared cultural knowledge that makes certain items more *salient*.

ComGround probes this capacity through **two complementary tasks**:

| Task | Name | What it tests | Scale |
|------|------|---------------|-------|
| **Task 1** | Category-Norm Replication | Does the LLM share the *accessibility structure* of human semantic memory? | 70 categories |
| **Task 2** | Tacit Coordination | Can two independent LLM agents converge on the same option *without communication*? | 410 items, 31 domains |

### Key Findings

- All six evaluated models capture the ordinal structure of human category norms (Spearman's $\rho > 0.74$), but fine-grained alignment is weak (first-response match < 0.56).
- Tacit coordination rates range from **0.53 to 0.88** (chance = 0.25), with substantial domain and culture variation.
- Knowledge alignment (Task 1) does **not** predict coordination ability (Task 2) -- these are distinct facets of common ground.

---

## Project Structure

```
2026_Kaggle/
├── benchmarks/                  # kbench benchmark implementations
│   ├── benchmark1_category_norms.py    # Task 1: Category-Norm Alignment
│   └── benchmark2_coordination.py      # Task 2: Tacit Coordination
├── data/
│   ├── benchmark1/
│   │   └── human_norms.json            # Human normative data (Castro et al., 2021)
│   ├── benchmark2/
│   │   ├── coordination_items.json     # 410 coordination items (31 domains)
│   │   └── item_quality.json           # Item quality metrics
│   └── output/                         # Evaluation results across models
├── notebooks/
│   ├── social_cognition_benchmark.ipynb
│   ├── bench1_ana.ipynb               # Task 1 analysis
│   └── bench2_ana.ipynb               # Task 2 analysis
├── scripts/                            # Dataset generation & analysis scripts
│   ├── generate_dataset.py             # Full dataset generator
│   ├── evaluate_dataset.py             # Multi-model evaluation
│   ├── evaluate_item_quality.py        # Item quality analysis
│   └── ...
├── writings/                           # Paper (ACM format)
│   ├── samples/CK_benchmark.tex        # Main paper
│   └── figures/                        # All paper figures
├── requirements.txt
└── CLAUDE.md                           # AI assistant project memory
```

---

## Task 1: Category-Norm Replication

Directly replicates the classic cognitive psychology paradigm from Castro, Curley, & Hertzog (2021). Given a category label (e.g., "A bird"), the LLM freely generates exemplars. The resulting frequency distribution is compared against human normative data across **70 categories**.

### Alignment Metrics

| Metric | Description |
|--------|-------------|
| Top-K Overlap | Jaccard similarity of top-K exemplars (human vs. LLM) |
| Rank Correlation | Spearman's $\rho$ between frequency rankings |
| First-Response Match | Whether the LLM's top exemplar matches the human modal response |
| Frequency Correlation | Pearson's $r$ over shared exemplar frequencies |

### Results Summary

| Model | Composite | Top-5 | $\rho$ | FRM | $r$ |
|-------|-----------|-------|--------|-----|-----|
| Gemini 2.5 Flash | **0.526** | 0.428 | 0.784 | 0.557 | 0.321 |
| Gemma 4 26B | 0.518 | **0.456** | 0.765 | 0.514 | **0.330** |
| GLM-5 | 0.497 | 0.421 | 0.747 | 0.514 | 0.295 |
| Claude Sonnet 4.6 | 0.469 | 0.385 | 0.749 | 0.471 | 0.244 |
| DeepSeek R1 | 0.451 | 0.368 | **0.783** | 0.371 | 0.260 |
| GPT-oss 20B | 0.413 | 0.314 | 0.752 | 0.314 | 0.245 |

---

## Task 2: Tacit Coordination

Two independent LLM agents are shown the same category with 4 options, but with options **shuffled in different orders**. They must independently choose the same option without any communication.

### Design Principles

1. **No leading language** -- Categories are strictly neutral (e.g., "US Cities", not "Most Famous US Cities")
2. **Shuffled option order** -- Each agent sees independently randomized options
3. **Bilingual & cross-cultural** -- Every item exists in English and Chinese; culture-sensitive domains have US/China variants

### Domain Taxonomy (31 domains, 8 macro-categories)

| Category | Domains | Cognitive Mechanism |
|----------|---------|---------------------|
| Perception | Colors, Shapes, Spatial Directions, Extremes | Perceptual prototype |
| Symbolism | Numbers, Time Anchors, Emotions | Symbolic salience |
| Biology | Animals, Plants, Fruits, Body Parts, Senses | Biological prototype |
| Artifacts | Tools, Clothing, Vehicles, Furniture | Functional typicality |
| Places | Rooms, Public Places, Institutions, Geographic Entities | Spatial routine |
| Norms | Family Roles, Occupations, Social Norms | Role prototype |
| Culture | Holidays, Food, Drinks, Famous People, Media, Brands | Collective memory |
| Digital | Digital Platforms, Internet Culture | Platform familiarity |

### Coordination Rate (100 simulated agents per item, chance = 0.25)

| Model | Perception | Symbolism | Biology | Artifacts | Places | Norms | Culture | Digital | **Overall** |
|-------|-----------|-----------|---------|-----------|--------|-------|---------|---------|-------------|
| DeepSeek R1 | 0.800 | 0.825 | 0.840 | **0.875** | **0.917** | **0.925** | **0.890** | **0.950** | **0.880** |
| Claude Sonnet 4.6 | **0.950** | 0.750 | **0.880** | 0.850 | 0.833 | 0.825 | 0.860 | 0.925 | 0.859 |
| GLM-5 | 0.650 | **0.875** | 0.860 | 0.825 | 0.767 | 0.600 | 0.790 | 0.750 | 0.771 |
| Gemma 4 26B | 0.725 | 0.800 | 0.540 | 0.675 | 0.783 | 0.575 | 0.830 | 0.825 | 0.734 |
| Gemini 2.5 Flash | 0.650 | 0.750 | 0.640 | 0.850 | 0.733 | 0.575 | 0.720 | 0.825 | 0.717 |
| GPT-oss 20B | 0.375 | 0.500 | 0.520 | 0.625 | 0.567 | 0.500 | 0.540 | 0.575 | 0.529 |

---

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Configure API Keys

Create a `.env` file:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Run Benchmarks

```python
import kaggle_benchmarks as kbench
from benchmarks.benchmark1_category_norms import category_norm_alignment
from benchmarks.benchmark2_coordination import tacit_coordination

# Task 1: Category-Norm Alignment
score, std = category_norm_alignment(llm)

# Task 2: Tacit Coordination
coord_rate, std = tacit_coordination(llm)
```

### Generate New Items

```bash
# Single domain
python scripts/generate_dataset.py -d Numbers -o data/generated_items

# All domains
python scripts/generate_dataset.py --all-domains -o data/generated_items
```

---

## Item Quality Control

Each coordination item is validated along two dimensions to prevent surface-level shortcuts:

- **Semantic distance**: Embedding-based cosine distances between options (mean = 0.54, gap = 0.035)
- **Corpus frequency**: Zipf-scale log frequencies from wordfreq (mean = 3.89, gap = 0.40)

Shannon entropy analysis confirms that options are nearly indistinguishable by these surface metrics (mean = 1.997 / 2.0 bits), ensuring coordination requires internalized cultural knowledge rather than statistical cues.

---

## Citation

```bibtex
@article{peng2026comground,
  title={ComGround: Measuring Common Ground in LLMs through Category Norms and Tacit Coordination},
  author={Peng, Xinyue},
  journal={Kaggle Measuring Progress Toward AGI - Social Cognition Track},
  year={2026}
}
```

## References

- Battig, W. F., & Montague, W. E. (1969). Category norms of verbal items in 56 categories.
- Castro, S. E., Curley, T. M., & Hertzog, C. (2021). Category norm updates: A revised corpus.
- Clark, H. H. (1996). *Using Language*.
- Mehta, J., Starmer, C., & Sugden, R. (1994). The nature of salience.
- Schelling, T. C. (1960). *The Strategy of Conflict*.

---

## License

MIT License

---

<br/>
<br/>

---

# ComGround：通过类别常模与默契协调测量大语言模型的共同基础

[![Kaggle 竞赛](https://img.shields.io/badge/Kaggle-社会认知赛道-blue)](https://www.kaggle.com/competitions/measuring-abc)

**ComGround** 是一个用于评估大语言模型（LLM）是否具备人类社会认知核心能力——*共同基础*（common ground）的基准测试。共同基础是支撑人际沟通与协作的共享知识、信念和文化显著性。

> 本项目提交至 **Kaggle Measuring Progress Toward AGI -- 社会认知赛道**（奖金 $20,000，结果暂未公布）。

---

## 概述

共同基础是社会认知的核心组成部分：当被问到"一种水果"时，大多数人首先想到"苹果"；当被要求独立选择同一个美国城市时，大多数人选择"纽约"。这两个例子揭示了同一种底层能力——让某些事物更加*显著*的共享文化知识。

ComGround 通过**两个互补任务**来探测这种能力：

| 任务 | 名称 | 测试内容 | 规模 |
|------|------|----------|------|
| **任务 1** | 类别常模复制 | LLM 是否与人类共享语义记忆的*可及性结构*？ | 70 个类别 |
| **任务 2** | 默契协调 | 两个独立的 LLM 智能体能否在*无通信*的情况下收敛到同一选项？ | 410 个条目，31 个领域 |

### 核心发现

- 所有六个被评估模型均捕捉到了人类类别常模的序数结构（Spearman $\rho > 0.74$），但细粒度对齐较弱（首答匹配 < 0.56）。
- 默契协调率从 **0.53 到 0.88** 不等（随机概率 = 0.25），在领域和文化维度上存在显著差异。
- 知识对齐（任务 1）**不能**预测协调能力（任务 2）——它们是共同基础的两个独立维度。

---

## 项目结构

```
2026_Kaggle/
├── benchmarks/                  # kbench 基准测试实现
│   ├── benchmark1_category_norms.py    # 任务 1：类别常模对齐
│   └── benchmark2_coordination.py      # 任务 2：默契协调
├── data/
│   ├── benchmark1/
│   │   └── human_norms.json            # 人类常模数据 (Castro et al., 2021)
│   ├── benchmark2/
│   │   ├── coordination_items.json     # 410 个协调条目（31 个领域）
│   │   └── item_quality.json           # 条目质量指标
│   └── output/                         # 多模型评估结果
├── notebooks/                          # 分析笔记本
├── scripts/                            # 数据集生成与分析脚本
├── writings/                           # 论文（ACM 格式）
└── requirements.txt
```

---

## 任务 1：类别常模复制

直接复现 Castro, Curley, & Hertzog (2021) 的经典认知心理学范式。给定类别标签（如"一种鸟"），LLM 自由生成样例，将其频率分布与 70 个类别的人类常模数据进行比较。

### 对齐指标

| 指标 | 说明 |
|------|------|
| Top-K 重叠度 | 人类与 LLM 前 K 个样例的 Jaccard 相似度 |
| 秩相关 | 频率排序间的 Spearman $\rho$ |
| 首答匹配 | LLM 最频繁样例是否与人类众数响应一致 |
| 频率相关 | 共有样例的 Pearson $r$ |

---

## 任务 2：默契协调

两个独立的 LLM 智能体看到相同类别的 4 个选项，但选项**以不同顺序排列**。它们必须在无通信的情况下独立选择同一选项。

### 设计原则

1. **无引导性语言**——类别严格中性（如"美国城市"，而非"最著名的美国城市"）
2. **选项顺序打乱**——每个智能体看到独立随机化的选项
3. **双语与跨文化**——每个条目均有中英文版本；文化敏感领域区分美国/中国语境

### 领域分类（31 个领域，8 个宏观类别）

| 类别 | 领域 | 认知机制 |
|------|------|----------|
| 感知 | 颜色、形状、空间方向、极端值 | 感知原型 |
| 象征 | 数字、时间锚点、情绪 | 象征显著性 |
| 生物 | 动物、植物、水果、身体部位、感官 | 生物原型 |
| 人造物 | 工具、服装、交通工具、家具 | 功能典型性 |
| 地点 | 房间、公共场所、机构、地理实体 | 空间惯例 |
| 规范 | 家庭角色、职业、社会规范 | 角色原型 |
| 文化 | 节日、食物、饮品、名人、媒体、品牌 | 集体记忆 |
| 数字 | 数字平台、网络文化 | 平台熟悉度 |

---

## 快速开始

### 安装

```bash
pip install -r requirements.txt
```

### 配置 API 密钥

创建 `.env` 文件：

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### 运行基准测试

```python
import kaggle_benchmarks as kbench
from benchmarks.benchmark1_category_norms import category_norm_alignment
from benchmarks.benchmark2_coordination import tacit_coordination

# 任务 1：类别常模对齐
score, std = category_norm_alignment(llm)

# 任务 2：默契协调
coord_rate, std = tacit_coordination(llm)
```

### 生成新条目

```bash
# 单个领域
python scripts/generate_dataset.py -d Numbers -o data/generated_items

# 全部领域
python scripts/generate_dataset.py --all-domains -o data/generated_items
```

---

## 条目质量控制

每个协调条目从两个维度验证，防止表面统计线索带来的快捷方式：

- **语义距离**：基于嵌入的选项间余弦距离（均值 = 0.54，差距 = 0.035）
- **语料库频率**：wordfreq 的 Zipf 对数频率（均值 = 3.89，差距 = 0.40）

Shannon 熵分析确认选项在这两个表面指标上几乎不可区分（均值 = 1.997 / 2.0 bits），确保协调需要内化的文化知识而非统计线索。

---

## 引用

```bibtex
@article{peng2026comground,
  title={ComGround: Measuring Common Ground in LLMs through Category Norms and Tacit Coordination},
  author={Peng, Xinyue},
  journal={Kaggle Measuring Progress Toward AGI - Social Cognition Track},
  year={2026}
}
```

## 参考文献

- Battig, W. F., & Montague, W. E. (1969). Category norms of verbal items in 56 categories.
- Castro, S. E., Curley, T. M., & Hertzog, C. (2021). Category norm updates: A revised corpus.
- Clark, H. H. (1996). *Using Language*.
- Mehta, J., Starmer, C., & Sugden, R. (1994). The nature of salience.
- Schelling, T. C. (1960). *The Strategy of Conflict*.

---

## 许可证

MIT License
