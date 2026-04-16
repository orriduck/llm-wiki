# Python PII 检测库对比

> PII（Personally Identifiable Information，个人身份信息）检测是隐私合规的核心环节。本页横向对比主流 Python PII 检测库，覆盖使用难度、可扩展性、检测准确度、支持范围等维度。

---

## 快速选型

| 使用场景 | 推荐库 |
|---------|-------|
| 企业级生产环境，需要高度定制 | **Microsoft Presidio** |
| 快速集成，API 简单 | **scrubadub** |
| LLM 应用隐私防护 | **DataFog** |
| 数据库 / 数据仓库扫描 | **PIICatcher** |
| 代码仓库敏感信息检测 | **detect-secrets** |
| 高精度深度学习检测 | **pii-masker** |
| 研究 / 风险评分 | **pii-codex** |

---

## 一、Microsoft Presidio

**仓库：** https://github.com/microsoft/presidio  
**安装：** `pip install presidio-analyzer presidio-anonymizer`  
**协议：** MIT  
**维护状态：** 活跃（最新版 2.2.362，2026 年 3 月）

### 核心定位

微软开源的企业级 PII 框架，支持文本、图片、结构化数据中的 PII 检测、脱敏、匿名化。是目前生态最完善的方案。

### 使用难度

中等。基本用法简洁，深度定制需理解识别器（Recognizer）体系：

```python
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()
results = analyzer.analyze(
    text="My name is John and my phone is 212-555-5555",
    language="en"
)
# results 包含实体类型、位置、置信度
```

匿名化：

```python
from presidio_anonymizer import AnonymizerEngine

anonymizer = AnonymizerEngine()
anonymized = anonymizer.anonymize(text, results)
```

### 可扩展性 ★★★★★

架构高度模块化：

- **PatternRecognizer**：正则 + 上下文验证，最简单的扩展方式
- **EntityRecognizer**：完全自定义逻辑（ML 模型、外部 API 等）
- **AdHocRecognizer**：运行时动态注入，无需重启
- **上下文增强**：基于上下文词提升/降低置信度
- **可追溯性**：内置决策追踪，便于调试

```python
from presidio_analyzer import PatternRecognizer, Pattern

# 自定义中国手机号识别器
cn_phone = PatternRecognizer(
    supported_entity="CN_PHONE",
    patterns=[Pattern("CN_PHONE", r"1[3-9]\d{9}", 0.7)],
    context=["手机", "电话", "联系"]
)
analyzer.registry.add_recognizer(cn_phone)
```

### 检测准确度 ★★★★

默认使用 spaCy `en_core_web_lg` NER 模型，结合：
- 正则模式匹配
- 命名实体识别（NER）
- 上下文感知增强

每条结果附带置信度分数，可按阈值过滤。

### 支持的 PII 类型（默认英语）

`PERSON`、`PHONE_NUMBER`、`EMAIL_ADDRESS`、`LOCATION`、`CREDIT_CARD`、`US_SSN`、`US_BANK_NUMBER`、`IBAN_CODE`、`IP_ADDRESS`、`URL`、`DATE_TIME`、`NRP`（国籍/宗教/政治）、`MEDICAL_LICENSE`、`CRYPTO`（比特币钱包）等 20+ 种。

### 多语言支持

默认仅英语；多语言需额外配置（不同语言的 spaCy 模型 + 上下文词汇），官方提供了西班牙语、德语等示例，中文需自行接入。

---

## 二、scrubadub

**仓库：** https://github.com/LeapBeyond/scrubadub  
**安装：** `pip install scrubadub`  
**维护状态：** 活跃（v2.0.0）

### 核心定位

轻量级 PII 清洗库，API 极简，开箱即用，插件体系灵活。适合快速集成或原型阶段。

### 使用难度 ★★（最简单）

```python
import scrubadub

# 一行清洗
clean_text = scrubadub.clean("John Smith's email is john@example.com")
# → "{NAME}'s email is {EMAIL_ADDRESS}"
```

### 可扩展性 ★★★★

- **Detector 继承**：自定义检测器只需继承 `scrubadub.detectors.Detector`
- **插件注册**：通过 Python entry_points 自动发现第三方插件
- **动态管理**：`add_detector()` / `remove_detector()` 运行时增删
- **官方扩展包**：`scrubadub_spacy`（NER）、`scrubadub_address`（地址）、`scrubadub_stanford`（Stanford NER）

### 检测准确度 ★★★

主要依赖正则匹配，spaCy 扩展安装后可提升 NER 精度。准确度整体低于 Presidio。

### 支持的 PII 类型

邮箱、电话、姓名、信用卡、地址、邮政编码等，通过插件可扩展。

### 多语言支持

本地化（locale）支持较好，格式 `xx_YY`：
- 电话号码：通过 libphonenumber 支持全球大多数地区
- 地址：加拿大、美国、英国
- spaCy 扩展：依赖对应语言的 spaCy 模型

---

## 三、DataFog

**仓库：** https://github.com/DataFog/datafog-python  
**安装：** `pip install datafog`  
**协议：** MIT  
**维护状态：** 目前最活跃（v4.3.0，2026 年 2 月）

### 核心定位

专为 **LLM 隐私防护**设计的现代 PII 库，支持在调用 LLM 前自动脱敏、输出后还原，同时支持图片 OCR 场景。

### 使用难度 ★★

```python
from datafog import DataFog

fog = DataFog()
redacted = fog.redact("Call me at 555-1234, my SSN is 123-45-6789")
# → "Call me at [PHONE_NUMBER], my SSN is [US_SSN]"
```

### 可扩展性 ★★★

- 多引擎支持：正则（最快）、NLP（精度更高）
- LLM 包装器：自动处理 prompt/response 的脱敏与还原
- 函数装饰器：作为可复用的隐私守护层

### 检测准确度 ★★★★

正则 + NLP 混合管道，生产级准确度。

### 特色功能

- **LLM 集成**：包装 OpenAI 等 API 调用，全自动匿名化
- **图片 + OCR**：支持从图片中检测 PII
- **隐私优先遥测**：不收集任何输入内容或 PII

---

## 四、PIICatcher

**仓库：** https://github.com/tokern/piicatcher  
**安装：** `pip install piicatcher`  
**维护状态：** 活跃

### 核心定位

专为**数据库和文件系统**设计的 PII 扫描器，与数据目录（Datahub、Amundsen）集成，适合数据治理场景。

### 使用难度 ★★★

```bash
# CLI 扫描 PostgreSQL
piicatcher run -c "postgresql://user:pass@host/db"

# 输出到 Datahub
piicatcher run -c "..." --catalog datahub
```

### 可扩展性 ★★★

- 两种扫描引擎：CommonRegex（正则）、spaCy NER
- `piicatcher_spacy` 插件

### 检测准确度 ★★★

正则 + NER 双引擎，准确度中等，以覆盖广度为优先。

### 支持的 PII 类型

`PHONE`、`EMAIL`、`CREDIT_CARD`、`ADDRESS`、`PERSON`、`LOCATION`、`BIRTH_DATE`、`GENDER`、`NATIONALITY`、`IP_ADDRESS`、`SSN`、`USER_NAME`、`PASSWORD`

### 支持的数据库

SQLite 3.24+、MySQL 5.6+、PostgreSQL 9.4+，以及文件系统

### 特色功能

- **增量扫描**：仅扫描新增或未扫描的列，节省时间
- **数据目录标签**：自动为 Datahub / Amundsen 打标签
- **Docker 镜像**：容器化部署

---

## 五、detect-secrets

**仓库：** https://github.com/Yelp/detect-secrets  
**安装：** `pip install detect-secrets`  
**维护状态：** 活跃

### 核心定位

Yelp 开源，**专注于代码仓库中的密钥/凭证检测**，而非通用 PII。定位是 DevSecOps 工具，常作为 pre-commit hook 使用。

### 使用难度 ★★

```bash
# 扫描仓库生成基线文件
detect-secrets scan > .secrets.baseline

# 审计基线
detect-secrets audit .secrets.baseline

# pre-commit hook 自动拦截
```

### 可扩展性 ★★★

- 内置插件：KeywordDetector、RegexBasedDetector（AWS、Slack、Stripe 等）
- 自定义插件扩展

### 检测准确度 ★★★★（密钥场景）

启发式正则 + 基线白名单机制，针对密钥场景误报率低。

### 支持的类型

**注意：检测目标是密钥/凭证，不是传统 PII**  
API Key、AWS 凭证、Slack Token、Stripe Key、数据库密码、私钥等

---

## 六、pii-masker（HydroXai）

**仓库：** https://github.com/HydroXai/pii-masker  
**维护状态：** 活跃（2024 年）

### 核心定位

基于深度学习（DeBERTa-v3 / Longformer）的高精度 PII 检测器，准确度优先。

### 使用难度 ★★★

需要加载 Transformer 模型，依赖较重：

```python
from pii_masker import PIIMasker

masker = PIIMasker()
result = masker.mask("John Doe lives at 123 Main St, call 555-1234")
```

### 可扩展性 ★★★

Transformer 架构可微调，但定制成本高于规则系统。

### 检测准确度 ★★★★★

- DeBERTa-v3 模型：PII 识别和脱敏准确度 **>95%**
- 新版 Longformer（4096 token）：在长文档场景再提升 ~4%
- Bi-LSTM 头增强序列理解
- 符合 GDPR / CCPA 合规要求

### 适用场景

需要最高准确度、计算资源充足、可接受推理延迟的场景。

---

## 七、pii-codex

**仓库：** https://github.com/EdyVision/pii-codex  
**安装：** `pip install pii-codex[detections]`  
**维护状态：** 学术/研究（发表于 JOSS 期刊）

### 核心定位

研究向工具，在 PII 检测之上增加**风险等级评估**层，输出严重程度分类和统计摘要。

### 使用难度 ★★★

```python
from pii_codex.services.analysis_service import PIIAnalysisService

service = PIIAnalysisService()
result = service.analyze_item("My SSN is 123-45-6789")
# 返回：实体类型 + 风险等级（Non-Identifiable / Semi-Identifiable / Identifiable）
```

### 特色功能

- **风险分级**：Non-Identifiable、Semi-Identifiable、Identifiable 三级
- **风险评分**：集合级别的统计分析（均值、分布）
- **多检测后端**：Presidio、Azure Cognitive、AWS Comprehend 可切换

---

## 综合对比表

| 维度 | Presidio | scrubadub | DataFog | PIICatcher | detect-secrets | pii-masker | pii-codex |
|------|----------|-----------|---------|------------|----------------|------------|-----------|
| **使用难度** | 中 | 低 | 低 | 中 | 低 | 中高 | 中 |
| **可扩展性** | ★★★★★ | ★★★★ | ★★★ | ★★★ | ★★★ | ★★★ | ★★★ |
| **检测准确度** | ★★★★ | ★★★ | ★★★★ | ★★★ | ★★★★（密钥） | ★★★★★ | ★★★★ |
| **支持 PII 类型** | 最全（20+） | 较全 | 较全 | 较全 | 仅密钥/凭证 | 较全 | 依赖后端 |
| **多语言** | 可配置 | 最好 | 有限 | 有限 | 无 | 无 | 有限 |
| **维护活跃度** | ★★★★★ | ★★★★ | ★★★★★ | ★★★★ | ★★★★ | ★★★★ | ★★★ |
| **数据库扫描** | 否 | 否 | 否 | ✓ | 否 | 否 | 否 |
| **LLM 集成** | 需自行封装 | 需自行封装 | ✓ 原生支持 | 否 | 否 | 否 | 否 |
| **推理开销** | 低~中 | 低 | 低~中 | 低~中 | 低 | 高（GPU 推荐） | 中 |
| **协议** | MIT | — | MIT | — | — | — | — |

---

## 深度说明

### 关于多语言（含中文）

主流库对中文支持都较弱，需额外适配：

- **Presidio**：需接入 `zh_core_web_*` spaCy 模型，并为中文特有实体（身份证、手机号等）编写自定义 PatternRecognizer
- **scrubadub**：locale 体系设计合理，但中文 Detector 需自行实现
- **其余库**：基本无中文支持，需完全自定义

### 关于检测 vs 脱敏

大多数库同时提供检测（返回位置/类型）和脱敏（替换/掩码）两个层次：

- **Presidio**：`presidio-analyzer`（检测）+ `presidio-anonymizer`（脱敏）分包
- **scrubadub**：直接返回清洗后文本，也可获取原始 Filth 对象
- **DataFog**：一键脱敏，支持还原（reversible anonymization）

### 关于准确度 vs 速度权衡

```
速度优先：detect-secrets > scrubadub > DataFog（正则引擎）> Presidio
精度优先：pii-masker > Presidio（NER模式）> DataFog（NLP引擎）> scrubadub
```

---

## 相关页面

- [[ruff]] — Python 代码质量工具链
- [[mypy]] — Python 静态类型检查

---

*最后更新：2026-04-16*
