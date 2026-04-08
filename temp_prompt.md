# 2026/4/8:0938
1. domain的划分不好。不具有代表性和全面性，cultural的部分可以，剩下需要重新规划。比如现在的basic cognitive里面的numbers和digital world里的number有区别吗？请你调研文献，给出一个合理的domain划分方案，并且给出每个domain的定义和包含的sub-domain。
| Category                                   | Domain                          | Culture Label | Primary Cognitive Mechanism                                |
| ------------------------------------------ | ------------------------------- | ------------: | ---------------------------------------------------------- |
| **Perceptual & Structural Salience**       | Colors                          |          Weak | Perceptual prototype; dominant feature salience            |
|                                            | Shapes                          |          Weak | Geometric prototypicality; symmetry bias                   |
|                                            | Spatial Directions              |          Weak | Spatial default anchoring; directional convention          |
|                                            | Position & Extremes             |          Weak | Center/edge salience; extremity bias                       |
| **Symbolic & Abstract Canonicality**       | Numbers                         |          Weak | Symbolic salience; roundness; memorability; canonicality   |
|                                            | Time Anchors                    |          Weak | Temporal convention; canonical reference points            |
|                                            | Emotions                        |          Weak | Conceptual prototype; affective salience                   |
| **Biological & Embodied World**            | Animals                         |          Weak | Familiarity; biological prototype; exposure frequency      |
|                                            | Plants / Fruits                 |          Weak | Everyday exposure; natural-category prototype              |
|                                            | Body Parts & Senses             |          Weak | Embodied salience; sensorimotor centrality                 |
| **Artifacts & Functional Objects**         | Tools                           |          Weak | Functional typicality; affordance salience                 |
|                                            | Clothing & Personal Items       |          Weak | Everyday-use prototype; frequency-based salience           |
|                                            | Vehicles                        |          Weak | Functional centrality; transport prototype                 |
|                                            | Furniture & Household Objects   |          Weak | Household routine salience; functional prototype           |
| **Places, Institutions & Spatial Scripts** | Rooms                           |          Weak | Domestic script; spatial routine knowledge                 |
|                                            | Public Places                   |        Strong | Shared meeting-point scripts; situational focal points     |
|                                            | Institutions                    |          Weak | Social function salience; institutional role knowledge     |
|                                            | Geographic Entities             |        Strong | Collective prominence; cultural/geographic common ground   |
| **Social Roles, Scripts & Norms**          | Family Roles                    |          Weak | Kinship prototype; relational centrality                   |
|                                            | Occupations                     |          Weak | Social role prototype; prestige/familiarity salience       |
|                                            | Everyday Social Norms           |        Strong | Normative scripts; common-ground expectations              |
| **Cultural Symbols & Collective Memory**   | Holidays & Festivals            |        Strong | Collective memory; ritual salience; cultural convention    |
|                                            | Food & Drink Culture            |        Strong | Cultural familiarity; identity-linked salience             |
|                                            | Famous People / Archetypes      |        Strong | Media exposure; symbolic prominence; collective memory     |
|                                            | Media & Pop Culture             |        Strong | Shared media exposure; recency and popularity salience     |
|                                            | Brands                          |        Strong | Consumer-symbol salience; advertising and exposure effects |
| **Digital & Technocultural Conventions**   | Digital Platforms & Devices     |        Strong | Platform familiarity; habitual digital exposure            |
|                                            | Internet Symbols & Tech Culture |        Strong | Interface conventions; internet-native symbolic salience   |

To construct a domain taxonomy for tacit coordination, we did not organize items solely by surface semantic topic. Instead, we selected domains based on the source of shared salience that could plausibly support coordination between two agents who cannot communicate. Specifically, we sought domains in which independent agents may converge because one option is more likely to function as a focal point—for example, due to perceptual prototypicality, symbolic canonicality, functional typicality, normative scripts, or culturally shared collective memory. Starting from a broad pool of candidate semantic categories, we iteratively grouped them into eight higher-level categories that reflect distinct coordination mechanisms, and retained domains that were (i) sufficiently interpretable as natural category labels, (ii) broad enough to support multiple item instantiations, and (iii) theoretically likely to elicit non-trivial but measurable human consensus. We additionally aimed to balance weakly culture-dependent domains (e.g., perceptual, embodied, and function-based categories) with strongly culture-dependent domains (e.g., holidays, brands, public places, and digital conventions), so that the benchmark can distinguish coordination grounded in broadly shared human experience from coordination that depends on culturally specific common ground. The final taxonomy contains 28 domains organized into 8 coordination-oriented categories, designed to maximize coverage of the major cognitive routes through which tacit coordination may emerge.

## 2026/4/8:1036
很好，以上完成的，是我们的第二组benchmark方案。我查阅文献发现，Castro, Curley, & Hertzog (2021) Category norms with a cross-sectional sample of adults in the United States: Consideration of cohort, age, and historical effects on semantic categories 这篇文章已经系统测量了246 名美国成年人对70 个 semantic categories的category norms。所以我认为我们应该先把这70个categories在LLM上测量一遍，先看看它们的表现如何。请你阅读这篇文献，给出一个详细的list，说明category和question的设计，以及一段可以放进paper的说明。再给我一段详细的prompt，我交给coder去实现这个benchmark。谢谢！

Benchmark 1: Human Category-Norm Replication.
Our first benchmark is a direct replication of a classic human common norm paradigm. Specifically, we adopt the semantic category generation task used in Castro, Curley, and Hertzog (2021), in which participants were shown one category label at a time and asked to produce as many category exemplars as possible within 30 seconds. We transfer this task structure to LLMs with minimal modification, preserving the original free-generation format. This enables a like-for-like comparison between human semantic norms and model-generated category structure.

ref paper:
A. 主干 category norms 文献（必须）
Battig & Montague (1969) — 历史基线
Van Overschelde et al. (2004) — 经典更新扩展
Castro et al. (2021) — 最新美国年龄分层更新
Yoon et al. (2004) — 中美文化比较核心
B. 如果你要强调跨文化/本土化
Bueno & Megherbi (2009) — French 70 categories
Marful et al. (2015) — Spanish 56 categories（我这次没直接抓到页面，但它被 PMC 文中明确列为已发表 Spanish norms）
Zheng et al. (2026/2025 online) — Australian updated norms
C. 如果你要解释认知机制
Buchanan et al. (2019) — semantic feature norms
117 concrete/abstract category production norms — 抽象概念扩展