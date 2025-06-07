# AI看线 - A股技术分析与AI预测工具

## 项目简介

AI看线是一个基于Python的A股分析工具，结合了传统技术分析和人工智能预测功能。利用K线图，技术指标，财务数据，新闻数据对股票进行全面分析及预测。该工具支持**多个AI供应商**，包括OpenAI、SiliconFlow、DeepSeek、Gemini等，提供更可靠和多样化的分析结果。

## 🚀 新特性

### 多AI供应商支持
- **OpenAI**: GPT-4o等模型，多模态分析能力强
- **SiliconFlow**: Qwen2.5等开源模型，中文理解优秀，性价比高
- **DeepSeek**: DeepSeek-V3模型，数学推理和逻辑分析能力出色
- **Gemini**: Google Gemini 2.5，多模态能力全面

### 智能fallback机制
- 自动检测可用的API密钥
- 主供应商失效时自动切换到备用供应商
- 确保分析服务的高可用性

### 灵活配置
- 支持环境变量配置
- 支持JSON配置文件
- 每个供应商可独立配置模型参数

## 功能特点

- **数据获取**：使用AKShare获取A股股票的历史交易数据、财务数据和新闻信息
- **技术分析**：计算多种技术指标，包括MA、MACD、KDJ、RSI、布林带等
- **可视化**：生成静态和交互式K线图及技术指标图表
- **AI分析**：支持多个AI供应商，提供多样化的分析视角
- **多模态分析**：结合K线图和数据进行综合分析（支持的供应商）
- **Web界面**：提供简洁美观的Web界面，方便用户输入股票代码查看分析结果
- **MCP SERVER**：提供MCP SERVER支持，支持通过LLM交互，随时分析股票

## 安装说明

### 环境要求

- Python 3.8+
- 依赖包：见`requirements.txt`

### 安装步骤

1. 克隆或下载本项目到本地

2. 安装依赖包

```bash
pip install -r requirements.txt
```

3. 创建`.env`文件，配置AI供应商API密钥

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，添加至少一个AI供应商的API密钥
```

### API密钥获取

| 供应商 | 获取地址 | 特点 |
|--------|----------|------|
| OpenAI | [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys) | 多模态能力强，通用性好 |
| SiliconFlow | [https://cloud.siliconflow.cn/](https://cloud.siliconflow.cn/) | 开源模型集合，中文优秀 |
| DeepSeek | [https://platform.deepseek.com/](https://platform.deepseek.com/) | 推理能力强，成本低 |
| Gemini | [https://ai.google.dev/](https://ai.google.dev/) | 免费额度，功能全面 |

## 使用方法

### 命令行使用

```bash
# 使用默认AI供应商
python main.py --stock_code 000001 --period 1年 --save_path ./output

# 使用指定AI供应商
python main.py --stock_code 000001 --ai_provider openai
```

参数说明：
- `--stock_code`：股票代码，必填参数
- `--period`：分析周期，可选值："1年"、"6个月"、"3个月"、"1个月"，默认为"1年"
- `--save_path`：结果保存路径，默认为"./output"
- `--ai_provider`：AI供应商，可选值："openai"、"siliconflow"、"deepseek"、"gemini"

### Web界面使用

启动Web服务：

```bash
python web_app.py
```

然后在浏览器中访问 http://localhost:5000 即可使用Web界面：

1. 在表单中输入股票代码（例如：000001）
2. 选择分析周期
3. 选择AI供应商（可选）
4. 点击"开始分析"按钮
5. 等待分析完成后查看结果

### 多AI供应商对比分析

```python
from modules.ai_analyzer import AIAnalyzer

# 显示所有供应商状态
AIAnalyzer.show_provider_status()

# 使用不同供应商分析同一只股票
providers = ['gemini', 'openai', 'siliconflow', 'deepseek']
for provider in providers:
    analyzer = AIAnalyzer(provider=provider)
    result = analyzer.analyze(stock_data, indicators, financial_data, news_data, stock_code, save_path)
```

### MCP SERVER使用

启动MCP服务：
```bash
uv run mcp_server.py
```

然后在MCP客户端中配置（streamable-http）：
http://localhost:8000/mcp 

## 项目结构

```
AI看线/
├── main.py                 # 主程序入口
├── web_app.py              # Web应用入口
├── multi_ai_example.py     # 多AI供应商使用示例
├── requirements.txt        # 依赖包列表
├── .env                    # 环境变量配置（需自行创建）
├── .env.example            # 环境变量配置示例
├── ai_config.json          # AI配置文件（可选）
├── modules/                # 功能模块
│   ├── __init__.py
│   ├── data_fetcher.py     # 数据获取模块
│   ├── technical_analyzer.py # 技术分析模块
│   ├── visualizer.py       # 可视化模块
│   ├── ai_analyzer.py      # AI分析模块（支持多供应商）
│   └── ai_providers/       # AI供应商实现
│       ├── __init__.py
│       ├── base_ai_analyzer.py    # 基础抽象类
│       ├── ai_factory.py          # 工厂类和配置管理
│       ├── openai_analyzer.py     # OpenAI实现
│       ├── siliconflow_analyzer.py # SiliconFlow实现
│       ├── deepseek_analyzer.py   # DeepSeek实现
│       └── gemini_analyzer.py     # Gemini实现
├── templates/              # Web模板目录
│   └── index.html          # 主页模板
├── static/                 # 静态资源目录
└── output/                 # 输出结果目录（运行时自动创建）
```

## AI供应商特点对比

| 供应商 | 模型 | 多模态 | 特点 | 成本 | 推荐场景 |
|--------|------|--------|------|------|----------|
| OpenAI | GPT-4o, GPT-4 | ✅ | 通用能力强，响应快 | 中等 | 多模态分析 |
| SiliconFlow | Qwen2.5-72B | ✅* | 中文理解强，性价比高 | 低 | 中文分析，成本敏感 |
| DeepSeek | DeepSeek-V3 | ❌ | 推理能力强，逻辑好 | 低 | 复杂推理分析 |
| Gemini | Gemini-2.5 | ✅ | 功能全面，有免费额度 | 免费+付费 | 默认推荐 |

*部分模型支持

## 配置说明

### 环境变量配置（.env文件）

```bash
# 至少配置一个AI供应商
OPENAI_API_KEY=your_openai_key
SILICONFLOW_API_KEY=your_siliconflow_key  
DEEPSEEK_API_KEY=your_deepseek_key
GEMINI_API_KEY=your_gemini_key

# 默认供应商（可选）
DEFAULT_AI_PROVIDER=gemini
```

### AI配置文件（ai_config.json，可选）

```json
{
  "default_provider": "gemini",
  "providers": {
    "openai": {
      "model": "gpt-4o",
      "max_tokens": 4000,
      "temperature": 0.1
    },
    "siliconflow": {
      "model": "Qwen/Qwen2.5-72B-Instruct",
      "max_tokens": 4000,
      "temperature": 0.1
    }
  }
}
```

## 使用示例

查看 `multi_ai_example.py` 文件，了解如何：
- 使用不同AI供应商进行分析
- 对比多个供应商的分析结果
- 配置和使用特定模型

```python
# 使用特定供应商分析
from modules.ai_analyzer import AIAnalyzer

analyzer = AIAnalyzer(provider='openai')  # 或 'siliconflow', 'deepseek', 'gemini'
result = analyzer.analyze(stock_data, indicators, financial_data, news_data, stock_code, save_path)
```

## 故障排除

### 常见问题

1. **AI分析失败**
   - 检查API密钥是否正确配置
   - 查看网络连接是否正常
   - 确认API额度是否充足

2. **供应商切换**
   - 系统会自动尝试其他可用供应商
   - 可手动指定backup供应商

3. **模型不支持**
   - 检查模型名称是否正确
   - 参考文档中的支持模型列表

### 查看供应商状态

```python
from modules.ai_analyzer import AIAnalyzer
AIAnalyzer.show_provider_status()
```

## 注意事项

- 本工具仅供学习和研究使用，不构成任何投资建议
- AI分析结果基于历史数据和当前信息，不能保证未来走势的准确性
- 使用前请确保已正确配置至少一个AI供应商的API密钥
- 股票数据获取依赖于AKShare库，可能受到网络和数据源的限制
- 不同AI供应商的分析结果可能存在差异，建议综合参考
- 本项目为QuantML开源项目，转载或使用需注明出处，商业使用请联系微信号QuantML

## 免责声明

本工具提供的分析和预测仅供参考，不构成任何投资建议。投资有风险，入市需谨慎。用户应对自己的投资决策负责。AI分析结果基于算法模型，可能存在偏差，请谨慎参考。