import os
import json
import base64
from typing import Dict, Any, List
import pandas as pd
import requests
from PIL import Image

from .base_ai_analyzer import BaseAIAnalyzer

class SiliconFlowAnalyzer(BaseAIAnalyzer):
    """
    SiliconFlow模型分析器实现
    """
    
    def __init__(self, api_key: str, **kwargs):
        """
        初始化SiliconFlow分析器
        
        Args:
            api_key: SiliconFlow API密钥
            **kwargs: 其他配置参数
                - model: 模型名称，默认为deepseek-ai/DeepSeek-R1
                - base_url: API基础URL
                - max_tokens: 最大token数
                - temperature: 温度参数
        """
        # 先设置属性，再调用父类初始化
        self.model = kwargs.get('model', 'deepseek-ai/DeepSeek-R1')
        self.max_tokens = kwargs.get('max_tokens', 64000)
        self.temperature = kwargs.get('temperature', 0.7)
        self.base_url = kwargs.get('base_url', 'https://api.siliconflow.cn/v1')
        
        super().__init__(api_key, **kwargs)
        
        # 设置请求头
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def _validate_config(self) -> None:
        """验证SiliconFlow配置"""
        if not self.api_key:
            raise ValueError("SiliconFlow API密钥不能为空")
        
        # 验证模型名称
        valid_models = [
            'Qwen/Qwen3-32B',
            'Qwen/Qwen3-30B-A3B',
            'deepseek-ai/DeepSeek-V3',
            'deepseek-ai/DeepSeek-R1',
            'meta-llama/Llama-3.1-405B-Instruct',
            'THUDM/glm-4-9b-chat'
        ]
        if self.model not in valid_models:
            print(f"警告: 模型 {self.model} 可能不受支持")
    
    def analyze(self, stock_data: pd.DataFrame, indicators: Dict[str, Any], 
               financial_data: Dict[str, Any], news_data: List[Dict[str, Any]], 
               stock_code: str, save_path: str) -> str:
        """
        使用SiliconFlow分析股票数据并预测未来走势
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
            
            # 检查是否有图片，如果有则使用多模态分析
            image_path = os.path.join(save_path, f"charts/{stock_code}_technical_analysis.png")
            if os.path.exists(image_path) and 'VL' in self.model:
                analysis_result = self.analyze_with_image(prompt, image_path)
            else:
                # 纯文本分析
                analysis_result = self._analyze_text_only(prompt)
            
            # 添加时间戳和免责声明
            full_result = self._add_disclaimer(analysis_result, stock_code, stock_name)
            
            return full_result
            
        except Exception as e:
            return f"SiliconFlow分析过程中出错: {str(e)}"
    
    def analyze_with_image(self, prompt: str, image_path: str) -> str:
        """
        使用SiliconFlow进行图片+文本分析
        """
        try:
            # 编码图片为base64
            image_base64 = self._encode_image(image_path)
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一位专业的股票分析师，请基于提供的K线图和数据分析股票的技术面和基本面情况，并预测未来走势。"
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
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
            
        except Exception as e:
            # 如果多模态分析失败，回退到纯文本分析
            print(f"多模态分析失败，回退到纯文本分析: {e}")
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
                    "content": "你是一位专业的股票分析师，请基于提供的数据分析股票的技术面和基本面情况，并预测未来走势。"
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
    
    def _encode_image(self, image_path: str) -> str:
        """
        将图片编码为base64字符串
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
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