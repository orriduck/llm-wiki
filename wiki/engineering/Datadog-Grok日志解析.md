# Datadog Grok Log Parsing / Datadog Grok 日志解析

> Datadog Grok parsing turns semi-structured log text into searchable structured attributes. Use it when logs are not already valid JSON, or when a text attribute contains nested formats such as key-value, JSON, CSV, XML, URLs, or user agents.
>
> Datadog Grok 日志解析用于把半结构化日志文本转换成可搜索的结构化属性。适用于日志本身不是合法 JSON，或者某个文本属性里嵌套了 key-value、JSON、CSV、XML、URL、User-Agent 等格式的场景。

**Primary sources / 主要来源**

> **主要来源**

- [Datadog Parsing documentation](https://docs.datadoghq.com/logs/log_configuration/parsing/)
  > [Datadog Parsing 官方文档](https://docs.datadoghq.com/logs/log_configuration/parsing/)
- [Datadog regex Grok guide](https://docs.datadoghq.com/logs/guide/regex_log_parsing/)
  > [Datadog Grok 正则指南](https://docs.datadoghq.com/logs/guide/regex_log_parsing/)
- [Datadog query-time extractions](https://docs.datadoghq.com/logs/explorer/calculated_fields/extractions/)
  > [Datadog 查询时提取文档](https://docs.datadoghq.com/logs/explorer/calculated_fields/extractions/)

---

## Mental Model / 心智模型

Datadog parses JSON-formatted logs automatically. Grok Parser is for other formats: classic text logs, logfmt-like strings, prefixed JSON, glog, CSV, XML, or custom application logs.

> Datadog 会自动解析 JSON 格式日志。Grok Parser 主要用于其他格式：传统文本日志、类似 logfmt 的字符串、前缀后带 JSON 的日志、glog、CSV、XML，或自定义应用日志。

A Grok rule is a constrained regular expression with reusable tokens and typed post-processing. The main syntax is:

> Grok 规则可以理解为“带可复用 token 和类型后处理的受约束正则表达式”。核心语法是：

```text
%{MATCHER:EXTRACT:FILTER}
```

| Part / 部分 | Meaning / 含义 | Example / 示例 |
|---|---|---|
| `MATCHER` | What to match / 匹配什么内容 | `word`, `integer`, `date("MM/dd/yyyy")`, `regex("[^}]*")` |
| `EXTRACT` | Where to store the captured value / 把捕获结果写到哪个属性 | `user.name`, `http.status_code`, `logger.thread_id` |
| `FILTER` | How to transform the captured value / 对捕获值做什么后处理 | `json`, `keyvalue`, `csv(...)`, `lowercase`, `scale(...)` |

A basic rule:

> 一个基础规则：

```text
MyParsingRule %{word:user} connected on %{date("MM/dd/yyyy"):connect_date}
```

For this log:

> 对于这条日志：

```text
john connected on 11/08/2017
```

Datadog extracts `user = john` and parses the date into an epoch timestamp in milliseconds.

> Datadog 会提取 `user = john`，并把日期解析成毫秒级 epoch timestamp。

---

## Ingest-Time vs Query-Time / 写入时解析 vs 查询时解析

Datadog has two related but different Grok contexts: ingest-time parsing in Log Pipelines, and query-time extraction in Log Explorer calculated fields.

> Datadog 有两个相关但不同的 Grok 使用场景：Log Pipelines 里的写入时解析，以及 Log Explorer calculated fields 里的查询时提取。

| Dimension / 维度 | Ingest-time Grok Parser / 写入时 Grok Parser | Query-time Extraction / 查询时提取 |
|---|---|---|
| When it runs / 运行时机 | Before logs are indexed or routed through later processors / 日志索引或进入后续处理器之前 | During exploration in Log Explorer / 在 Log Explorer 查询分析时 |
| Scope / 作用范围 | Long-term pipeline behavior / 长期管道行为 | Ad hoc analysis and calculated fields / 临时分析和计算字段 |
| Matchers / 匹配器 | Full Datadog matcher set / 完整 Datadog matcher 集合 | Only `data`, `integer`, `notSpace`, `number`, `word` / 仅支持 `data`、`integer`、`notSpace`、`number`、`word` |
| Filters / 过滤器 | Full filter set such as `json`, `keyvalue`, `csv`, `xml`, `url` / 完整过滤器集合，如 `json`、`keyvalue`、`csv`、`xml`、`url` | Only numeric casting filters `number` and `integer` / 仅支持数值转换过滤器 `number` 和 `integer` |
| Best use / 最适合 | Production parsing, remapping, enrichment, facets, routing / 生产解析、字段 remap、富化、facet、路由 | Investigating raw logs without changing pipelines / 不改 pipeline 的原始日志调查 |

Use query-time extraction when you are exploring. Promote the rule into an ingest-time pipeline when the field becomes operationally important.

> 探索阶段用查询时提取；一旦字段变成长期运维、告警、dashboard 或 facet 所需，就应把规则提升到写入时 pipeline。

---

## Rule Execution Semantics / 规则执行语义

In a single Grok Parser, multiple parsing rules are evaluated top to bottom. Only the first matching rule parses a given log event.

> 在同一个 Grok Parser 中，多条解析规则会从上到下依次尝试。每条日志只会由第一条命中的规则解析。

Important constraints:

> 重要约束：

- Rule names must be unique inside the same parser.
  > 同一个 parser 内规则名必须唯一。
- Rule names may contain alphanumeric characters, `_`, and `.`, and must start with an alphanumeric character.
  > 规则名只能包含字母数字、`_` 和 `.`，且必须以字母数字开头。
- A rule must match the entire log entry from beginning to end.
  > 规则必须匹配整条日志，从开头到结尾。
- Empty or null properties are not displayed in the parsed output.
  > 空值或 null 属性不会出现在解析输出里。
- Explicitly handle newlines and large whitespace gaps with `\n` and `\s+`.
  > 遇到换行或大量空白时，要用 `\n` 和 `\s+` 显式处理。
- A rule can reference helper rules defined above it.
  > 规则可以引用在它之前定义的 helper rules。

Operational implication: order rules from most specific to most general. Put broad fallback patterns near the bottom.

> 运维含义：规则应从最具体排到最宽泛。宽松兜底规则应放在底部。

---

## Core Matchers / 核心 Matchers

These matchers are available both at query time and ingest time:

> 这些 matcher 在查询时和写入时都可用：

| Matcher / 匹配器 | Meaning / 含义 | Notes / 备注 |
|---|---|---|
| `word` | Matches a word-like token / 匹配单词型 token | Equivalent to a word-boundary `\w+` style match / 类似带词边界的 `\w+` |
| `notSpace` | Matches until the next space / 匹配到下一个空格前 | Good for paths, IDs, compact tokens / 适合路径、ID、紧凑 token |
| `number` | Matches decimal floating point and parses as double / 匹配浮点数并解析为 double | Query-time compatible / 查询时可用 |
| `integer` | Matches integer and parses as integer / 匹配整数并解析为 integer | Query-time compatible / 查询时可用 |
| `data` | Matches arbitrary text / 匹配任意文本 | Convenient but risky in long rules / 方便但在长规则中有风险 |

Ingest-time-only matchers include:

> 仅写入时可用的 matcher 包括：

| Matcher / 匹配器 | Meaning / 含义 | Typical use / 常见用途 |
|---|---|---|
| `date("pattern"[, "timezoneId"[, "localeId"]])` | Parses a date into epoch milliseconds / 将日期解析成毫秒级 epoch | Application timestamps / 应用时间戳 |
| `regex("pattern")` | Matches a custom regex / 匹配自定义正则 | Precise delimiters, custom IDs / 精确分隔符、自定义 ID |
| `boolean("truePattern", "falsePattern")` | Parses boolean values / 解析布尔值 | Non-standard true/false strings / 非标准真假值 |
| `numberStr`, `integerStr` | Match numbers but keep them as strings / 匹配数字但保留为字符串 | IDs that look numeric / 看似数字的 ID |
| `numberExt`, `integerExt` | Numeric matchers with scientific notation support / 支持科学计数法的数值匹配 | Scientific measurements / 科学计量值 |
| `doubleQuotedString`, `singleQuotedString`, `quotedString` | Quoted strings / 引号字符串 | Message fragments, command args / 消息片段、命令参数 |
| `uuid`, `mac`, `ipv4`, `ipv6`, `ip` | Common infrastructure tokens / 常见基础设施 token | Trace IDs, network fields / trace ID、网络字段 |
| `hostname`, `ipOrHost`, `port` | Host and network endpoint fields / 主机和网络端点字段 | Service logs, proxy logs / 服务日志、代理日志 |

---

## Core Filters / 核心 Filters

Filters post-process a matched value. Query-time only supports numeric casting filters, while ingest-time supports many structural parsers.

> Filter 会对匹配值做后处理。查询时只支持数值转换类 filter；写入时支持许多结构化解析器。

| Filter / 过滤器 | Meaning / 含义 | Example use / 示例用途 |
|---|---|---|
| `number` | Cast match to double / 转为 double | Latency, usage, ratio / 延迟、用量、比例 |
| `integer` | Cast match to integer / 转为 integer | Status code, count / 状态码、计数 |
| `boolean` | Cast true/false-like strings / 转换真假字符串 | Feature flags / 功能开关 |
| `nullIf("value")` | Return null for a sentinel value / 遇到哨兵值时返回 null | `-`, `N/A`, `unknown` / `-`、`N/A`、`unknown` |
| `json` | Parse valid JSON / 解析合法 JSON | Text prefix plus JSON payload / 文本前缀加 JSON 负载 |
| `keyvalue(...)` | Parse key-value or logfmt-like text / 解析 key-value 或类似 logfmt 的文本 | `user=john action=click` |
| `csv(headers[, separator[, quotingcharacter]])` | Parse CSV or TSV / 解析 CSV 或 TSV | Flat exported records / 扁平导出记录 |
| `xml` | Parse XML into JSON-like attributes / 将 XML 解析成 JSON 风格属性 | XML payload logs / XML 负载日志 |
| `url` | Parse URL members / 解析 URL 组成部分 | Domain, path, query params / 域名、路径、查询参数 |
| `querystring` | Extract URL query key-value pairs / 提取 URL 查询参数键值对 | `?productId=...` |
| `useragent(...)` | Parse user-agent fields / 解析 User-Agent 字段 | Browser, OS, device / 浏览器、系统、设备 |
| `decodeuricomponent` | Decode URI components / 解码 URI component | `%2Fservice%2Ftest` -> `/service/test` |
| `lowercase`, `uppercase` | Normalize casing / 规范大小写 | Environment, region, enum values / 环境、区域、枚举值 |
| `scale(factor)` | Multiply numeric value by a factor / 数值乘以系数 | Percent to ratio, seconds to milliseconds / 百分比转比例、秒转毫秒 |
| `array(...)` | Parse token sequence into an array / 将 token 序列解析成数组 | Lists embedded in logs / 日志中的列表 |

---

## Common Recipes / 常见配方

### Key-Value or Logfmt / Key-Value 或 Logfmt

Use `keyvalue` when the log already contains field names.

> 当日志本身已经包含字段名时，优先用 `keyvalue`。

```text
rule %{data::keyvalue}
```

Input:

> 输入：

```text
user=john connect_date=11/08/2017 id=123 action=click
```

Output:

> 输出：

```json
{
  "user": "john",
  "connect_date": "11/08/2017",
  "id": 123,
  "action": "click"
}
```

If the separator is not `=`, pass it explicitly.

> 如果分隔符不是 `=`，需要显式传入。

```text
rule %{data::keyvalue(": ")}
```

Add allowed characters when unquoted values contain characters such as `/` or `:`.

> 当未加引号的值中包含 `/` 或 `:` 等字符时，要加入 allowlist。

```text
rule %{data::keyvalue("=","/:")}
```

### Text Prefix Plus JSON / 文本前缀加 JSON

Use `json` when the useful payload is a JSON object after a text prefix.

> 当有用负载是文本前缀后的 JSON 对象时，用 `json`。

```text
parsing_rule %{date("MMM dd HH:mm:ss"):timestamp} %{word:host} %{word:app}\[%{number:logger.thread_id}\]: %{notSpace:server} %{data::json}
```

This pattern parses the leading syslog-like fields and then lets the JSON filter extract the nested object.

> 这个模式先解析前面的类 syslog 字段，再交给 JSON filter 提取嵌套对象。

### Date Parsing / 日期解析

Use `date(...)` to parse log timestamps, but remember that parsing a date attribute does not automatically set the official Datadog log timestamp.

> 用 `date(...)` 解析日志时间戳，但要记住：解析出 date 属性并不会自动设置 Datadog 的官方日志时间。

```text
%{date("yyyy-MM-dd'T'HH:mm:ss.SSSZ"):timestamp}
```

If that parsed date should become the event timestamp, add a Log Date Remapper processor after the Grok Parser.

> 如果这个解析日期应成为事件时间，需要在 Grok Parser 后增加 Log Date Remapper processor。

### Optional Fields / 可选字段

Wrap optional fragments in `()?`, including the whitespace that belongs to the optional fragment.

> 用 `()?` 包住可选片段，同时把属于可选片段的空格也放进去。

```text
MyParsingRule %{word:user.firstname} (%{integer:user.id} )?connected on %{date("MM/dd/yyyy"):connect_date}
```

If the space is placed outside the optional group, one of the formats may fail to match.

> 如果空格放在可选组外，其中一种格式可能无法匹配。

### Alternating Patterns / 二选一模式

Use alternation for logs where one position can contain different typed values.

> 当日志某个位置可能出现不同类型的值时，用 alternation。

```text
MyParsingRule (%{integer:user.id}|%{word:user.firstname}) connected on %{date("MM/dd/yyyy"):connect_date}
```

This allows one rule to handle both `12345 connected...` and `john connected...`.

> 这样一条规则可以同时处理 `12345 connected...` 和 `john connected...`。

### CSV and TSV / CSV 与 TSV

Use `csv(headers[, separator[, quotingcharacter]])` when the log is a delimited record.

> 当日志是分隔符记录时，使用 `csv(headers[, separator[, quotingcharacter]])`。

```text
myParsingRule %{data:user:csv("first_name,last_name,street_number,street_name,city")}
```

For TSV, use `tab` as the separator.

> 对 TSV，使用 `tab` 作为分隔符。

```text
myParsingRule %{data:record:csv("key1,key2,key3","tab")}
```

### Glog Format / Glog 格式

Kubernetes components often use glog-like lines. A typical pattern extracts severity, timestamp, thread ID, source file, line number, and message.

> Kubernetes 组件常使用类似 glog 的日志行。典型规则会提取级别、时间戳、线程 ID、源文件、行号和消息。

```text
kube_scheduler %{regex("\\w"):level}%{date("MMdd HH:mm:ss.SSSSSS"):timestamp}\s+%{number:logger.thread_id} %{notSpace:logger.name}:%{number:logger.lineno}\] %{data:msg}
```

### Discarding Suffix Text / 丢弃尾部文本

Use `data` at the end when remaining text is safe to ignore or store.

> 当尾部剩余文本可以安全忽略或存储时，可在末尾使用 `data`。

```text
MyParsingRule Usage\:\s+%{number:usage}%{data:ignore}
```

For `Usage: 24.3%`, this extracts `usage = 24.3` and `ignore = "%"`.

> 对 `Usage: 24.3%`，这会提取 `usage = 24.3` 和 `ignore = "%"`.

---

## Helper Rules / Helper Rules

Helper rules define reusable named fragments for a Grok Parser. They make complex rules shorter and keep repeated tokens consistent.

> Helper rules 用于为 Grok Parser 定义可复用的命名片段。它们能缩短复杂规则，并让重复 token 保持一致。

Example log:

> 示例日志：

```text
john id:12345 connected on 11/08/2017 on server XYZ in production
```

Parsing rule:

> 解析规则：

```text
MyParsingRule %{user} %{connection} %{server}
```

Helpers:

> Helper：

```text
user %{word:user.name} id:%{integer:user.id}
connection connected on %{date("MM/dd/yyyy"):connect_date}
server on server %{notSpace:server.name} in %{notSpace:server.env}
```

Use helper rules when a parser has multiple similar formats, such as HTTP access logs from several services that share the same timestamp, host, or request token layout.

> 当一个 parser 中有多种相似格式时，应使用 helper rules，例如多个服务的 HTTP access logs 共享同样的时间戳、host 或 request token 布局。

---

## Regex and Performance / 正则与性能

Datadog Grok rules must match the entire log line. Conceptually, treat each rule as if it were wrapped with `^ ... $`.

> Datadog Grok 规则必须匹配整条日志。可以把每条规则理解为隐式带有 `^ ... $`。

The `data` matcher is convenient but can create performance issues in long or ambiguous patterns. Datadog's regex guide describes `data` as behaving like a lazy wildcard. It may expand step by step and trigger backtracking.

> `data` matcher 很方便，但在长规则或含糊规则中可能带来性能问题。Datadog 的正则指南把 `data` 描述为类似 lazy wildcard：它可能逐步扩展并触发回溯。

Prefer explicit delimiter-based regex when possible:

> 尽量优先使用基于分隔符的显式 regex：

```text
%{regex("[^}]*"):payload}
```

Instead of a broad matcher:

> 而不是宽泛 matcher：

```text
%{data:payload}
```

Use `data` sparingly:

> 谨慎使用 `data`：

- Good: capture everything until the end, such as `%{data::json}` or `%{data::keyvalue}`.
  > 适合：捕获直到行尾的所有内容，例如 `%{data::json}` 或 `%{data::keyvalue}`。
- Good: capture a whole message when there is no reliable endpoint.
  > 适合：没有可靠终点时捕获整个 message。
- Risky: place several `data` matchers in the middle of a long rule.
  > 有风险：在长规则中间放多个 `data` matcher。
- Better: anchor to stable delimiters with `[^<delimiter>]*`.
  > 更好：用 `[^<delimiter>]*` 锚定到稳定分隔符。

Inside `%{regex("...")}`, backslashes are parsed as string escapes first, so escape them twice.

> 在 `%{regex("...")}` 中，反斜杠会先作为字符串转义处理，因此需要双重转义。

```text
%{regex("\\d{2}")}  # matches two digits / 匹配两位数字
```

---

## Attribute Naming / 属性命名

Use stable, semantic attribute names because parsed attributes often become facets, measures, monitors, dashboards, or remapping inputs.

> 使用稳定且语义化的属性名，因为解析出的属性常会成为 facet、measure、monitor、dashboard 或 remapping 输入。

Recommended patterns:

> 推荐模式：

| Field type / 字段类型 | Suggested names / 建议命名 |
|---|---|
| User / 用户 | `user.id`, `user.name`, `usr.id` if following Datadog standard attributes / `user.id`、`user.name`，若遵循 Datadog 标准属性可用 `usr.id` |
| HTTP / HTTP | `http.method`, `http.status_code`, `http.url`, `http.route` |
| Logger / 日志器 | `logger.name`, `logger.thread_id`, `logger.lineno` |
| Network / 网络 | `network.client.ip`, `network.destination.port`, `host.name` |
| Service context / 服务上下文 | `service`, `env`, `version`, `source` |

Prefer nested names for related fields. Avoid overly generic names like `id`, `name`, or `status` unless the surrounding context is already obvious.

> 相关字段优先使用嵌套名称。避免过泛的 `id`、`name`、`status`，除非上下文已经很明确。

---

## Pipeline Placement / Pipeline 中的位置

In a production log pipeline, Grok Parser is usually early, because later processors depend on structured attributes.

> 在生产日志 pipeline 中，Grok Parser 通常放得较早，因为后续 processor 往往依赖结构化属性。

A common sequence:

> 常见顺序：

1. Filter logs by `source`, `service`, environment, or other stable routing attributes.
   > 先按 `source`、`service`、环境或其他稳定路由属性过滤日志。
2. Apply Grok Parser to extract fields from `message` or another text attribute.
   > 对 `message` 或其他文本属性应用 Grok Parser，提取字段。
3. Apply remappers such as status remapper, date remapper, service remapper, or trace ID remapper.
   > 应用 status remapper、date remapper、service remapper 或 trace ID remapper 等。
4. Add enrichment, normalization, or category processors.
   > 增加富化、规范化或分类 processor。
5. Use parsed fields for facets, monitors, dashboards, and downstream routing.
   > 将解析字段用于 facets、monitors、dashboards 和下游路由。

If parsing a field other than `message`, use the Grok processor's advanced setting to set the source text attribute.

> 如果要解析的不是 `message`，在 Grok processor 的 advanced setting 中设置源文本属性。

---

## Debugging Checklist / 调试清单

When a Grok rule does not match, check these in order:

> 当 Grok 规则无法匹配时，按顺序检查：

1. Does the rule match the entire log line, including prefix, suffix, punctuation, whitespace, and newline?
   > 规则是否匹配了整条日志，包括前缀、后缀、标点、空白和换行？
2. Are spaces inside optional groups placed correctly?
   > 可选组中的空格位置是否正确？
3. Are regex backslashes double-escaped inside `%{regex("...")}`?
   > `%{regex("...")}` 中的反斜杠是否做了双重转义？
4. Is the rule order correct, with specific rules above broad ones?
   > 规则顺序是否正确，具体规则是否放在宽泛规则之前？
5. Is a query-time extraction accidentally using an ingest-time-only matcher or filter?
   > 是否在查询时提取中误用了仅写入时支持的 matcher 或 filter？
6. Is `data` causing ambiguous matching or timeout-like behavior?
   > `data` 是否造成了含糊匹配或类似超时的行为？
7. Is the timestamp parsed but not remapped as the official event date?
   > 时间戳是否只是被解析出来，但没有 remap 成官方事件时间？
8. Are empty, null, or missing values expected to appear even though Datadog suppresses them?
   > 是否期待空值、null 或缺失值出现，而 Datadog 实际会隐藏它们？

---

## Practical Design Rules / 实用设计规则

Start with samples from real logs, not invented examples. Include at least one normal case, one edge case, and one malformed or partial case.

> 从真实日志样本开始，而不是凭空写例子。至少包含一个正常样本、一个边界样本、一个畸形或不完整样本。

Prefer structure-aware filters over manual regex when the embedded format is real JSON, key-value, CSV, XML, URL, or query string.

> 如果嵌入格式确实是 JSON、key-value、CSV、XML、URL 或 query string，优先使用对应结构化 filter，而不是手写正则。

Keep rules narrow enough to fail loudly when the log format changes. A parser that silently matches the wrong fields is worse than one that fails during testing.

> 规则应足够窄，让日志格式变化时能明显失败。静默匹配错误字段的 parser，比测试时直接失败的 parser 更危险。

Use helper rules for shared fragments, but avoid turning a small parser into a mini programming language. If helper indirection makes the parser hard to read, inline the one-off pattern.

> 对共享片段使用 helper rules，但不要把小 parser 写成一门迷你编程语言。如果 helper 间接层让规则难读，就把一次性 pattern 内联。

Use query-time extraction to validate value before changing ingestion. Once a field powers alerts, dashboards, cost allocation, or routing, move it into an ingest-time Grok Parser.

> 用查询时提取先验证字段价值。字段一旦用于告警、dashboard、成本归因或路由，就迁移到写入时 Grok Parser。

---

## Quick Reference / 速查

| Goal / 目标 | Pattern / 模式 |
|---|---|
| Parse key-value log / 解析 key-value 日志 | `%{data::keyvalue}` |
| Parse JSON after prefix / 解析前缀后的 JSON | `prefix %{data::json}` |
| Parse custom ID until `]` / 解析直到 `]` 前的自定义 ID | `%{regex("[^\\]]*"):custom.id}` |
| Parse URL / 解析 URL | `%{data:http.url:url}` |
| Parse query string / 解析 query string | `%{data:http.url_details.queryString:querystring}` |
| Parse CSV / 解析 CSV | `%{data:record:csv("a,b,c")}` |
| Parse optional user ID / 解析可选用户 ID | `(%{integer:user.id} )?` |
| Parse one of two value types / 解析两种值之一 | `(%{integer:user.id}|%{word:user.name})` |
| Cast number / 转成数字 | `%{notSpace:latency:number}` or `%{number:latency}` |
| Keep numeric-looking ID as string / 将看似数字的 ID 保持为字符串 | `%{integerStr:account.id}` |

---

## Related Pages / 相关页面

- [[CloudWatch]] for AWS log collection and Logs Insights patterns.
  > [[CloudWatch]]：AWS 日志收集与 Logs Insights 模式。
- [[python-pii库对比]] for privacy-sensitive log redaction ideas before sending logs to external systems.
  > [[python-pii库对比]]：将日志发送到外部系统前的隐私敏感信息脱敏思路。
