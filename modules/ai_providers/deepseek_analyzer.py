import os
import json
from typing import Dict, Any, List
import pandas as pd
import requests

from .base_ai_analyzer import BaseAIAnalyzer

class DeepSeekAnalyzer(BaseAIAnalyzer):
    """
    DeepSeek模型分析器实现
    """
    
    def __init__(self, api_key: str, **kwargs):
        """
        初始化DeepSeek分析器
        
        Args:
            api_key: DeepSeek API密钥
            **kwargs: 其他配置参数
                - model: 模型名称，默认为deepseek-chat
                - base_url: API基础URL
                - max_tokens: 最大token数
                - temperature: 温度参数
        """
        # 先设置属性，再调用父类初始化
        self.model = kwargs.get('model', 'deepseek-chat')
        self.max_tokens = kwargs.get('max_tokens', 4000)
        self.temperature = kwargs.get('temperature', 0.1)
        self.base_url = kwargs.get('base_url', 'https://api.deepseek.com/v1')
        
        super().__init__(api_key, **kwargs)
        
        # 设置请求头
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def _validate_config(self) -> None:
        """验证DeepSeek配置"""
        if not self.api_key:
            raise ValueError("DeepSeek API密钥不能为空")
        
        # 验证模型名称
        valid_models = [
            'deepseek-chat',
            'deepseek-coder',
            'deepseek-v3'
        ]
        if self.model not in valid_models:
            print(f"警告: 模型 {self.model} 可能不受支持")
    
    def analyze(self, stock_data: pd.DataFrame, indicators: Dict[str, Any], 
               financial_data: Dict[str, Any], news_data: List[Dict[str, Any]], 
               stock_code: str, save_path: str) -> str:
        """
        使用DeepSeek分析股票数据并预测未来走势
        """
        try:
            # 获取股票名称
            stock_name = self._get_stock_name(stock_code)
            
            # 准备分析数据
            analysis_data = self._prepare_analysis_data(
                stock_data, indicators, financial_data, news_data, stock_code, stock_name
            )
            
            # 构建提示词
            prompt = self._build_prompt(analysis_data, stock_code, stock_name)
            
            # DeepSeek目前主要支持文本分析
            analysis_result = self._analyze_text_only(prompt)
            
            # 添加时间戳和免责声明
            full_result = self._add_disclaimer(analysis_result, stock_code, stock_name)
            
            return full_result
            
        except Exception as e:
            return f"DeepSeek分析过程中出错: {str(e)}"
    
    def analyze_with_image(self, prompt: str, image_path: str) -> str:
        """
        DeepSeek目前不支持图片分析，回退到纯文本分析
        """
        print("DeepSeek目前不支持多模态分析，使用纯文本分析")
        return self._analyze_text_only(prompt)
    
    def _analyze_text_only(self, prompt: str) -> str:
        """
        纯文本分析
        """
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位专业的股票分析师，拥有丰富的A股市场经验。请基于提供的数据进行深入的技术面和基本面分析，并给出专业的投资建议。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json=data,
            timeout=60
        )
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def _get_stock_name(self, stock_code: str) -> str:
        """
        获取股票名称
        """
        try:
            import akshare as ak
            stock_info = ak.stock_individual_info_em(symbol=stock_code)
            if not stock_info.empty:
                return stock_info.loc[stock_info['item'] == '股票简称', 'value'].values[0]
            else:
                return stock_code
        except:
            return stock_code