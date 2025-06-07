# modules/ai_providers/__init__.py

from .base_ai_analyzer import BaseAIAnalyzer
from .ai_factory import AIAnalyzerFactory, AIAnalyzerConfig

# 导入具体的分析器实现
try:
    from .openai_analyzer import OpenAIAnalyzer
except ImportError:
    OpenAIAnalyzer = None

try:
    from .siliconflow_analyzer import SiliconFlowAnalyzer
except ImportError:
    SiliconFlowAnalyzer = None

try:
    from .deepseek_analyzer import DeepSeekAnalyzer
except ImportError:
    DeepSeekAnalyzer = None

try:
    from .gemini_analyzer import GeminiAnalyzer
except ImportError:
    GeminiAnalyzer = None

__all__ = [
    'BaseAIAnalyzer',
    'AIAnalyzerFactory',
    'AIAnalyzerConfig',
    'OpenAIAnalyzer',
    'SiliconFlowAnalyzer', 
    'DeepSeekAnalyzer',
    'GeminiAnalyzer'
]