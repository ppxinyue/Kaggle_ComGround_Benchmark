---
name: Tacit Coordination Task Design v3
description: Bilingual tacit coordination benchmark with 36 domains, 20 questions each, balanced US/China cultural contexts
type: project
---

# Tacit Coordination Task Design (v3)

## Core Concept
两个agent在没有通信的情况下，必须从**顺序随机打乱的**4个选项中选择同一个项目。成功则各获得$1奖励。这测试的是人类（和模型）之间shared cultural knowledge的对齐程度。

## 题目设计原则

### 禁止引导性语言
题目中**不得包含**任何暗示或引导性语言，包括但不限于：
- "most famous"（最著名）
- "traditional"（传统）
- "typical"（典型）
- "best"（最好）
- "most important"（最重要）
- "primary"（主要）
- 形容词或最高级

### 正确的题目格式
只提供**类别/语境** + **选项**，让agent完全依赖内隐文化知识做出选择。

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

这确保测试的是纯粹的 **tacit coordination** 能力，而非对问题表述的响应。

## 题库规格

- **总Domain数**: 36个
- **每Domain题数**: 20道
- **总题数**: 720道
- **语言**: 英文、中文（完全对应，仅语言不同）
- **总Item数**: 720 × 2 = 1440个items

## Task Format

### 统一的题目形式
```
You are playing a coordination game with another agent.
If you both select the SAME option, you each get $1.
You cannot communicate - you must rely on what seems most obvious.
Note: The other agent sees the SAME options, but in a DIFFERENT order.

[Category/Context]
[Options - randomized order for each agent]

Which option do you choose? Respond with the exact option text.
```

### 数据结构
```python
{
    # 题目元数据
    "item_id": str,              # 题目唯一标识
    "item_id_en": str,           # 英文版本ID
    "item_id_zh": str,           # 中文版本ID
    "domain": str,               # Domain类别
    "language": str,             # "en" 或 "zh"
    "culture": str,              # "us", "china", 或 "universal"
    "category": str,             # 具体类别描述
    "options": list[str],        # 4个选项（标准顺序）
    "focal_option": str,         # 最salient的选项（人类数据验证）

    # 人类数据（Prolific收集后添加）
    "human_n": int,              # 人类被试数量
    "human_agreement_rate": float,  # 人类协调成功率
    "human_selection_dist": dict,   # 选项选择分布
}
```

## 双语与文化平衡设计

### 翻译原则
- **完全对应**: 每道题都有英文和中文两个版本
- **内容一致**: 除了语言，其他所有要素相同
- **文化标记**: 每道题标记文化背景 (us/china/universal)

### 文化敏感Domain的题目分配

以下domain需要文化平衡，每domain 20道题分配为：
- **10道题：美国文化背景**
- **10道题：中国文化背景**

#### 文化敏感Domain列表 (12个)

| Domain | 美国文化示例 | 中国文化示例 |
|--------|-------------|-------------|
| **Cities** | "US Cities" → NYC | "Chinese Cities" → Beijing |
| **Countries** | "Baseball Countries" → US | "Confucius Countries" → China |
| **Famous People** | "US Founding Fathers" → Washington | "Chinese Philosophers" → Confucius |
| **Foods** | "American Breakfast" → pancakes | "Chinese Breakfast" → 豆浆油条 |
| **Drinks** | "American Coffee" → Starbucks | "Chinese Tea" → 龙井 |
| **Holidays** | "US Winter Holidays" → Christmas | "Chinese New Year Foods" → 饺子 |
| **Sports** | "American Sports" → basketball | "Chinese Sports" → 乒乓球 |
| **Brands** | "American Car Brands" → Ford | "Chinese Tech Brands" → 华为 |
| **Music** | "American Music Genres" → Jazz | "Chinese Instruments" → 古筝 |
| **Movies** | "Hollywood Genres" → Action | "Chinese Movie Types" → 武侠 |
| **Animals** | "US National Animals" → Bald eagle | "Chinese Symbolic Animals" → Dragon |
| **Colors** | "US Celebration Colors" → Red/Blue | "Chinese Lucky Colors" → Red |

### 文化通用Domain (24个)

以下domain较少受文化影响，20道题无需文化分区：

| Domain | Example |
|--------|---------|
| **Numbers** | "Pick a number 1-10" → 7 |
| **Shapes** | "Most stable shape" → triangle |
| **Directions** | "Sun rises in the..." → east |
| **Time** | "Wake up time" → 7am |
| **Body Parts** | "See with your..." → eyes |
| **Senses** | "Hear with your..." → ears |
| **Tools** | "Cut with a..." → knife |
| **Vehicles** | "Fly in a..." → airplane |
| **Clothing** | "Wear on feet" → shoes |
| **Furniture** | "Sleep on a..." → bed |
| **Rooms** | "Cook in the..." → kitchen |
| **Buildings** | "Buy food at..." → supermarket |
| **Locations** | "Study at the..." → library |
| **Occupations** | "Treats patients" → doctor |
| **Family Roles** | "Male parent" → father |
| **Emotions** | "Success brings..." → joy |
| **Weather** | "Frozen rain" → snow |
| **Seasons** | "Cold season" → winter |
| **Nature** | "Largest planet" → Jupiter |
| **Plants** | "Symbol of love" → rose |
| **Arts** | "Draw with a..." → pencil |
| **Books** | "Fiction type" → novel |
| **Digital** | "Search engine" → Google/百度 |
| **Tech** | "Phone brand" → Apple |

## 36 Domains 完整列表与题库分配

### Category 1: Basic Cognitive (5 domains, 100 items)
1. **Numbers** (20题, universal) - 数字显著性
2. **Colors** (20题, 10us/10china) - 颜色联想
3. **Shapes** (20题, universal) - 形状与概念
4. **Directions** (20题, universal) - 方向认知
5. **Time** (20题, universal) - 时间联想

### Category 2: Social & Cultural (12 domains, 240 items)
6. **Cities** (20题, 10us/10china) - 城市代表性
7. **Countries** (20题, 10us/10china) - 国家联想
8. **Famous People** (20题, 10us/10china) - 名人识别
9. **Brands** (20题, 10us/10china) - 品牌认知
10. **Foods** (20题, 10us/10china) - 食物典型性
11. **Drinks** (20题, 10us/10china) - 饮料联想
12. **Holidays** (20题, 10us/10china) - 节日联想
13. **Sports** (20题, 10us/10china) - 运动认知
14. **Music** (20题, 10us/10china) - 音乐类型
15. **Movies** (20题, 10us/10china) - 电影类型
16. **Animals** (20题, 10us/10china) - 动物象征
17. **Occupations** (20题, universal) - 职业认知

### Category 3: Biological World (4 domains, 80 items)
18. **Animals** (已在Social中) - 动物认知
19. **Plants** (20题, universal) - 植物联想
20. **Body Parts** (20题, universal) - 身体部位
21. **Senses** (20题, universal) - 感官功能

### Category 4: Objects & Functions (4 domains, 80 items)
22. **Tools** (20题, universal) - 工具用途
23. **Vehicles** (20题, universal) - 交通工具
24. **Clothing** (20题, universal) - 服装场合
25. **Furniture** (20题, universal) - 家具功能

### Category 5: Abstract Concepts (5 domains, 100 items)
26. **Emotions** (20题, universal) - 情绪联想
27. **Weather** (20题, universal) - 天气现象
28. **Seasons** (20题, universal) - 季节特征
29. **Arts** (20题, universal) - 艺术形式
30. **Books** (20题, universal) - 书籍类型

### Category 6: Space & Location (3 domains, 60 items)
31. **Rooms** (20题, universal) - 房间功能
32. **Buildings** (20题, universal) - 建筑用途
33. **Locations** (20题, universal) - 地点功能

### Category 7: Social Roles (2 domains, 40 items)
34. **Occupations** (已在Social中)
35. **Family Roles** (20题, universal) - 家庭角色

### Category 8: Media & Entertainment (2 domains, 40 items)
36. **Movies** (已在Social中)
37. **Music** (已在Social中)

### Category 9: Digital World (2 domains, 40 items)
38. **Digital** (20题, universal) - 数字平台
39. **Tech** (20题, universal) - 科技产品

### Category 10: Nature (1 domain, 20 items)
40. **Nature** (20题, universal) - 自然现象

> 注：以上分类有重叠，实际为36个独立domain

## 双语题目示例

### 示例1: Numbers (Universal)
**English:**
```
Numbers 1-10
Options: 1, 3, 7, 10
```

**Chinese:**
```
数字1-10
选项：1, 3, 7, 10
```

### 示例2: Cities (US Culture)
**English:**
```
US Cities
Options: New York, Los Angeles, Chicago, Houston
```

**Chinese:**
```
美国城市
选项：纽约, 洛杉矶, 芝加哥, 休斯顿
```

### 示例3: Cities (China Culture)
**English:**
```
Chinese Cities
Options: Beijing, Shanghai, Guangzhou, Shenzhen
```

**Chinese:**
```
中国城市
选项：北京, 上海, 广州, 深圳
```

### 示例4: Foods (US Culture)
**English:**
```
American Breakfast
Options: Pancakes, Eggs and bacon, Cereal, Toast
```

**Chinese:**
```
美式早餐
选项：煎饼, 鸡蛋培根, 麦片, 吐司
```

### 示例5: Foods (China Culture)
**English:**
```
Chinese Breakfast
Options: Congee and youtiao, Dumplings, Soy milk, Baozi
```

**Chinese:**
```
中式早餐
选项：粥油条, 饺子, 豆浆, 包子
```

## 评估指标

### 模型协调成功率 (Model Coordination Rate)
对每道题：
1. 调用LLM 100次，模拟100个被试（每次randomize选项顺序）
2. 对每个被试，计算其与其他99个被试的选择一致性
3. 取所有pair的平均作为该题的模型协调成功率

**公式**:
```
Coordination_Rate(item) = sum(matches) / (100 * 99 / 2)
其中 matches = number of agreeing pairs
```

### 模型-人类对齐度 (Model-Human Alignment)
1. 比较模型最常选择的选项 vs 人类最常选择的选项
2. 计算一致性比例

**公式**:
```
Alignment(item) = 1 if mode(model_choices) == mode(human_choices) else 0
Overall_Alignment = sum(Alignment) / total_items
```

### Domain-level分析
- 每个domain的平均模型协调成功率
- 每个domain的模型-人类对齐度
- 文化差异分析 (US vs China items)
- 语言差异分析 (English vs Chinese)

## Prolific实验设计

### 被试招募
- **英文版**: 招募美国/英国被试
- **中文版**: 招募中国大陆被试（或海外华人）
- **每语言被试数**: 建议至少100人
- **每人完成题数**: 72题（36 domains × 2题，或随机抽样）

### 实验流程
1. 给出清晰的instructions（包括奖励机制）
2. 每题4个选项随机排序
3. 记录选择和反应时间
4. 事后attention check

### 奖励机制
- Prolific上：基于真实奖励（每成功协调一对奖励小额）
- 或简化为固定报酬 + performance bonus

## 数据收集计划

### Phase 1: 题库生成
- 生成720道英文题
- 翻译为720道中文题
- 审查文化平衡性

### Phase 2: Pilot测试
- 小规模测试（10人/语言）
- 检查题目清晰度
- 去除有问题的题目

### Phase 3: 正式数据收集
- Prolific大规模数据收集
- 每语言100+被试
- 收集选择分布数据

### Phase 4: 模型评估
- 调用LLM完成所有题目
- 计算协调成功率和人类对齐度
- 分析domain/culture/language差异

## 实施时间线

| Week | 任务 |
|------|------|
| 1-2 | 题库生成（720英文题） |
| 3 | 翻译和审校 |
| 4 | Pilot测试 |
| 5-6 | Prolific数据收集 |
| 7-8 | 模型评估 |
| 9-10 | 分析和写up |

## 关键决策点

1. **题库生成方式**: 手工 vs 半自动（LLM生成+人工审核）
2. **Prolific预算**: 200被试 × 72题 × ~$0.10/题 ≈ $1440
3. **LLM调用成本**: 720题 × 100次 × 成本
4. **文化平衡验证**: 如何确保US/China题目难度相当？
