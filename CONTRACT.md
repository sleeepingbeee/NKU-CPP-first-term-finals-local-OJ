# 本地 OJ 出题数据契约（CONTRACT）

所有出题数据必须严格按本文件实现，后端 `oj/server.py` 只认这套格式。

## 1. 目录与文件

```
oj/
  problems/<id>.json          # 每题一个文件，题目元数据 + 题面 + 样例 + 检查项
  solutions/<id>.cpp          # 该题的参考解（C++17，标准输入输出）
  testdata/<id>/1.in  1.out   # 第 1 组必须与 json 里的样例完全一致
  testdata/<id>/2.in  2.out
  ...
  testdata/<id>/k.in  k.out   # k >= 6，编号从 1 连续，不得跳号
```

- `<id>` 命名（固定，不得自创）：
  `2022-1` `2022-2` `2022-3` `2023-1` `2023-2` `2023-3` `2023-4` `2023-5` `2024-1` `2024-2` `2024-3` `2025-1` `2025-2` `2025-3` `2025-4`
- 只写自己负责的 `<id>`，不要动别人的文件、不要动 `server.py` / `oj.html` / `judge.py` / `build.bat` / `tools/`。

## 2. `problems/<id>.json` 字段

```json
{
  "id": "2024-1",
  "year": 2024,
  "no": "第1题（A卷）",
  "title": "进制转换",
  "difficulty": "普及-",
  "tags": ["函数重载", "进制转换", "字符串"],
  "source": "2024 2-1 上机考试真题 · 第1题 A卷 · OJ #843",
  "timeLimitMs": 2000,
  "checker": "default",
  "statement": "### 题目描述\n...\n\n### 输入格式\n...\n\n### 输出格式\n...\n\n### 数据范围\n...\n\n### 样例说明\n...",
  "samples": [
    {"input": "3\nD 5\nB 1011\nd 65535\n", "output": "101\n11\n1111111111111111\n"}
  ],
  "checks": [
    {
      "name": "必须实现同名函数重载",
      "kind": "require",
      "pattern": "(?s)radixConvert.*radixConvert",
      "hint": "题目硬性要求：必须写出两个同名不同参数的重载函数，否则计 0 分。",
      "fatal": true
    },
    {
      "name": "禁止使用 itoa / strtol / bitset 等库函数",
      "kind": "forbid",
      "pattern": "\\b(itoa|strtol|stoi|stringstream|bitset)\\b",
      "hint": "必须手写按权展开法与取余法。",
      "fatal": true
    }
  ]
}
```

字段说明：

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | 是 | 见上表，必须与文件名一致 |
| `year` / `no` / `title` / `source` | 是 | 前端展示用；`title` 用原题名（可加小注），`no` 如「第2题（A卷）」 |
| `difficulty` | 是 | 入门 / 普及- / 普及 / 普及+ / 提高 |
| `tags` | 是 | 2~4 个考点词 |
| `timeLimitMs` | 是 | 统一写 `2000`（本地机器比 OJ 慢，别写 1000） |
| `checker` | 是 | `"default"`（默认逐行比对）或 `"float"`（实数答案，需同时给 `"eps": 1e-5`） |
| `statement` | 是 | **完整题面 markdown**（见 §4） |
| `samples` | 是 | 至少 1 组；`samples[0]` 必须与 `testdata/<id>/1.in` / `1.out` 内容**逐字符一致**（含末尾换行） |
| `checks` | 否 | 代码规范检查（对应本校真题的"必须结构体否则 0 分"这类硬性要求），0~4 条 |

`checks[].kind`：
- `"require"`：正则**必须**能匹配到（`re.search`，建议 `(?s)` 让 `.` 跨行）
- `"forbid"`：正则**不得**匹配到
- `fatal: true` 表示硬性要求（考场上违反会 0 分），前端会红字提示；`false`/省略为一般建议

正则注意 JSON 转义：`\\b`、`\\s`、`\\(`。

## 3. 测试数据要求

- 每题 **6~10 组**，`1.in`/`1.out` 为题目样例。
- 必须覆盖：样例、最小规模、边界值、以及本题的"坑"（例如只有 1 个点、有重合点、并列答案、n=0、超出范围等）。
- `.in` 用 UTF-8 + LF 换行；`.out` 由参考解生成（见 §5），不要手写。
- 数据规模控制在"本地 1 秒内跑完"，别造 1e7 级的大数据。

## 4. 题面（statement）写作规范

用中文 markdown，按以下顺序，缺一不可：

```
### 题目描述
（原题描述，忠实还原；可补充必要的解释）

### 输入格式
### 输出格式

### 数据范围
（原题给的范围；原题没写就写「本题未标注，按 …处理」）

### 输入样例 / 输出样例
（用 ``` 代码块给 1 组，与 samples[0] 一致；这组必须可运行）

### 提示
（可选：易错点、必须遵守的实现要求、A/B 卷差异说明）
```

**注意**：
- 题面要能独立看懂，不要出现"见上面截图"这类引用。
- 原题的输出字符串必须一字不差地写清（大小写、感叹号、空格），如 `Wrong input`、`No Distance!`、`Allocation failed`。
- 若本题只实现 A 卷（或只实现 B 卷），在 `提示` 里用一句说明另一卷的差异。

## 5. 参考解与生成期望输出

参考解 `solutions/<id>.cpp`：C++17、`#include <iostream>` 等，**从标准输入读、往标准输出写**，不要 `freopen`。写完必须用它生成所有 `.out`：

```bash
# 生成单组
python -X utf8 oj/tools/run_cpp.py oj/solutions/2024-1.cpp \
    --stdin oj/testdata/2024-1/1.in --out oj/testdata/2024-1/1.out

# 一次生成该题全部 .out（推荐）
python -X utf8 oj/tools/gen_expected.py 2024-1
```

生成后再用下面的方式自查每组都能跑通、无 TLE、输出非空：

```bash
python -X utf8 oj/tools/check_problem.py 2024-1
```

两个工具都支持 `--json`，方便脚本化。

## 6. 质量红线

1. `samples[0]` 与 `testdata/1.in|1.out` 不一致 → 前端样例展示与判题对不上，必须一致。
2. `.out` 不是参考解跑出来的（手写 / 猜的）→ 判题会错，绝对不允许。
3. 题面里出现未定义的输出格式（如该输出 `Yes` 却写 `YES`）→ 学生必错。
4. 文件名、编号不连续 → 后端加载失败。
