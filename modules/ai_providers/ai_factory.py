import os
from typing import Dict, Any, Optional
from .base_ai_analyzer import BaseAIAnalyzer

class AIAnalyzerFactory:
    """
    AI分析器工厂类，用于创建和管理不同的AI分析器
    """
    
    # 支持的AI供应商
    SUPPORTED_PROVIDERS = {
        'openai': 'OpenAI',
        'siliconflow': 'SiliconFlow', 
        'deepseek': 'DeepSeek',
        'gemini': 'Gemini'
    }
    
    @classmethod
    def create_analyzer(cls, provider: str, api_key: Optional[str] = None, **kwargs) -> BaseAIAnalyzer:
        """
        创建AI分析器实例
        
        Args:
            provider: AI供应商名称 ('openai', 'siliconflow', 'deepseek', 'gemini')
            api_key: API密钥，如果为None则从环境变量获取
            **kwargs: 其他配置参数
            
        Returns:
            AI分析器实例
            
        Raises:
            ValueError: 不支持的供应商或缺少API密钥
        """
        provider = provider.lower()
        
        if provider not in cls.SUPPORTED_PROVIDERS:
            raise ValueError(f"不支持的AI供应商: {provider}。支持的供应商: {list(cls.SUPPORTED_PROVIDERS.keys())}")
        
        # 获取API密钥
        if api_key is None:
            api_key = cls._get_api_key_from_env(provider)
        
        if not api_key:
            raise ValueError(f"未找到 {provider} 的API密钥，请设置环境变量或直接传入api_key参数")
        
        # 创建相应的分析器
        if provider == 'openai':
            from .openai_analyzer import OpenAIAnalyzer
            return OpenAIAnalyzer(api_key, **kwargs)
        
        elif provider == 'siliconflow':
            from .siliconflow_analyzer import SiliconFlowAnalyzer
            return SiliconFlowAnalyzer(api_key, **kwargs)
        
        elif provider == 'deepseek':
            from .deepseek_analyzer import DeepSeekAnalyzer
            return DeepSeekAnalyzer(api_key, **kwargs)
        
        elif provider == 'gemini':
            from .gemini_analyzer import GeminiAnalyzer
            return GeminiAnalyzer(api_key, **kwargs)
    
    @classmethod
    def _get_api_key_from_env(cls, provider: str) -> Optional[str]:
        """
        从环境变量获取API密钥
        """
        env_var_map = {
            'openai': 'OPENAI_API_KEY',
            'siliconflow': 'SILICONFLOW_API_KEY',
            'deepseek': 'DEEPSEEK_API_KEY',
            'gemini': 'GEMINI_API_KEY'
        }
        
        env_var = env_var_map.get(provider)
        if env_var:
            return os.getenv(env_var)
        return None
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, str]:
        """
        获取所有支持的AI供应商列表
        
        Returns:
            供应商字典 {provider_id: provider_name}
        """
        return cls.SUPPORTED_PROVIDERS.copy()
    
    @classmethod
    def check_api_keys(cls) -> Dict[str, bool]:
        """
        检查各个供应商的API密钥是否已配置
        
        Returns:
            检查结果字典 {provider: has_api_key}
        """
        result = {}
        for provider in cls.SUPPORTED_PROVIDERS:
            api_key = cls._get_api_key_from_env(provider)
            result[provider] = bool(api_key)
        return result

class AIAnalyzerConfig:
    """
    AI分析器配置类
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置
        
        Args:
            config_file: 配置文件路径（可选）
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置
        """
        default_config = {
            'default_provider': 'siliconflow',
            'providers': {
                'openai': {
                    'model': 'gpt-4o',
                    'max_tokens': 4000,
                    'temperature': 0.7
                },
                'siliconflow': {
                    'model': 'deepseek-ai/DeepSeek-V3', #'Qwen/Qwen3-30B-A3B', #'deepseek-ai/DeepSeek-R1', #'deepseek-ai/DeepSeek-V3', #'Qwen/Qwen3-32B',
                    'max_tokens': 4000,
                    'temperature': 0.7
                },
                'deepseek': {
                    'model': 'deepseek-chat',
                    'max_tokens': 4000,
                    'temperature': 0.7
                },
                'gemini': {
                    'model': 'gemini-2.5-flash-preview-04-17',
                    'temperature': 0,
                    'top_p': 0.95,
                    'top_k': 1
                }
            }
        }
        
        if self.config_file and os.path.exists(self.config_file):
            try:
                import json
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                # 合并配置
                default_config.update(file_config)
            except Exception as e:
                print(f"加载配置文件失败: {e}，使用默认配置")
        
        return default_config
    
    def get_default_provider(self) -> str:
        """获取默认供应商"""
        return self.config.get('default_provider', 'gemini')
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """获取指定供应商的配置"""
        return self.config.get('providers', {}).get(provider, {})
    
    def set_default_provider(self, provider: str) -> None:
        """设置默认供应商"""
        if provider in AIAnalyzerFactory.SUPPORTED_PROVIDERS:
            self.config['default_provider'] = provider
        else:
            raise ValueError(f"不支持的供应商: {provider}")
    
    def save_config(self) -> None:
        """保存配置到文件"""
        if self.config_file:
            try:
                import json
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"保存配置文件失败: {e}")