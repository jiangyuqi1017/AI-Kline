import os
from typing import Dict, Any, List, Optional
import pandas as pd

from .ai_providers import AIAnalyzerFactory, AIAnalyzerConfig

class AIAnalyzer:
    """
    AI分析器主类，支持多个AI供应商
    """
    
    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None, **kwargs):
        """
        初始化AI分析器
        
        Args:
            provider: AI供应商名称，如果为None则使用配置文件中的默认供应商
            api_key: API密钥，如果为None则从环境变量获取
            **kwargs: 其他配置参数
        """
        # 加载配置
        self.config = AIAnalyzerConfig()
        
        # 确定使用的供应商
        if provider is None:
            provider = self.config.get_default_provider()
        
        # 获取供应商配置
        provider_config = self.config.get_provider_config(provider)
        provider_config.update(kwargs)  # 用传入的参数覆盖配置文件的参数
        
        # 创建分析器实例
        try:
            self.analyzer = AIAnalyzerFactory.create_analyzer(provider, api_key, **provider_config)
            self.provider = provider
            print(f"成功初始化 {AIAnalyzerFactory.SUPPORTED_PROVIDERS[provider]} 分析器")
        except Exception as e:
            print(f"初始化 {provider} 分析器失败: {e}")
            # 尝试使用备用供应商
            self._try_fallback_providers(api_key, **kwargs)
    
    def _try_fallback_providers(self, api_key: Optional[str], **kwargs):
        """
        尝试使用备用供应商
        """
        # 检查哪些供应商有可用的API密钥
        available_keys = AIAnalyzerFactory.check_api_keys()
        
        for provider, has_key in available_keys.items():
            if has_key and provider != self.config.get_default_provider():
                try:
                    provider_config = self.config.get_provider_config(provider)
                    provider_config.update(kwargs)
                    self.analyzer = AIAnalyzerFactory.create_analyzer(provider, api_key, **provider_config)
                    self.provider = provider
                    print(f"成功使用备用供应商 {AIAnalyzerFactory.SUPPORTED_PROVIDERS[provider]}")
                    return
                except Exception as e:
                    print(f"备用供应商 {provider} 也失败: {e}")
                    continue
        
        # 如果所有供应商都失败，抛出异常
        raise RuntimeError("所有AI供应商都无法使用，请检查API密钥配置")
    
    def analyze(self, stock_data: pd.DataFrame, indicators: Dict[str, Any], 
               financial_data: Dict[str, Any], news_data: List[Dict[str, Any]], 
               stock_code: str, save_path: str) -> str:
        """
        分析股票数据并预测未来走势
        
        Args:
            stock_data: 股票历史数据
            indicators: 技术指标数据
            financial_data: 财务数据
            news_data: 新闻数据
            stock_code: 股票代码
            save_path: 保存路径
            
        Returns:
            分析结果文本
        """
        if not hasattr(self, 'analyzer'):
            return "错误: AI分析器未正确初始化，请检查API密钥配置"
        
        try:
            result = self.analyzer.analyze(stock_data, indicators, financial_data, news_data, stock_code, save_path)
            # 在结果中添加使用的供应商信息
            provider_name = AIAnalyzerFactory.SUPPORTED_PROVIDERS[self.provider]
            result += f"\n\n---\n*本分析由 {provider_name} 提供*"
            return result
        except Exception as e:
            return f"AI分析过程中出错 ({self.provider}): {str(e)}"
    
    def get_provider_info(self) -> Dict[str, str]:
        """
        获取当前使用的供应商信息
        """
        if hasattr(self, 'analyzer'):
            return {
                'provider': self.provider,
                'provider_name': AIAnalyzerFactory.SUPPORTED_PROVIDERS[self.provider],
                'model': getattr(self.analyzer, 'model', 'Unknown')
            }
        return {'provider': 'None', 'provider_name': 'None', 'model': 'None'}
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, bool]:
        """
        获取所有可用的AI供应商及其状态
        
        Returns:
            供应商状态字典 {provider_name: is_available}
        """
        available_keys = AIAnalyzerFactory.check_api_keys()
        providers_info = AIAnalyzerFactory.get_available_providers()
        
        result = {}
        for provider_id, provider_name in providers_info.items():
            result[provider_name] = available_keys.get(provider_id, False)
        
        return result
    
    @classmethod
    def show_provider_status(cls):
        """
        显示所有供应商的状态
        """
        print("AI供应商状态:")
        print("-" * 40)
        
        available_providers = cls.get_available_providers()
        for provider_name, is_available in available_providers.items():
            status = "✅ 可用" if is_available else "❌ 未配置"
            print(f"{provider_name}: {status}")
        
        print("-" * 40)
        print("请在.env文件中配置相应的API密钥:")
        print("OPENAI_API_KEY=your_openai_key")
        print("SILICONFLOW_API_KEY=your_siliconflow_key")
        print("DEEPSEEK_API_KEY=your_deepseek_key")
        print("GEMINI_API_KEY=your_gemini_key")