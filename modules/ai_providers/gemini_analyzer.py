import os
import json
from typing import Dict, Any, List
import pandas as pd
from PIL import Image
from google import genai
from google.genai import types

from .base_ai_analyzer import BaseAIAnalyzer

class GeminiAnalyzer(BaseAIAnalyzer):
    """
    Google Gemini模型分析器实现
    """
    
    def __init__(self, api_key: str, **kwargs):
        """
        初始化Gemini分析器
        
        Args:
            api_key: Gemini API密钥
            **kwargs: 其他配置参数
                - model: 模型名称，默认为gemini-2.5-flash-preview-04-17
                - temperature: 温度参数
                - top_p: top_p参数
                - top_k: top_k参数
        """
        # 先设置属性，再调用父类初始化
        self.model = kwargs.get('model', 'gemini-2.5-flash-preview-04-17')
        self.temperature = kwargs.get('temperature', 0)
        self.top_p = kwargs.get('top_p', 0.95)
        self.top_k = kwargs.get('top_k', 1)
        
        super().__init__(api_key, **kwargs)
        
        # 初始化Gemini客户端
        self.client = genai.Client(api_key=api_key)
    
    def _validate_config(self) -> None:
        """验证Gemini配置"""
        if not self.api_key:
            raise ValueError("Gemini API密钥不能为空")
        
        # 验证模型名称
        valid_models = [
            'gemini-2.5-flash-preview-04-17',
            'gemini-1.5-pro',
            'gemini-1.5-flash',
            'gemini-pro-vision'
        ]
        if self.model not in valid_models:
            print(f"警告: 模型 {self.model} 可能不受支持")
    
    def analyze(self, stock_data: pd.DataFrame, indicators: Dict[str, Any], 
               financial_data: Dict[str, Any], news_data: List[Dict[str, Any]], 
               stock_code: str, save_path: str) -> str:
        """
        使用Gemini分析股票数据并预测未来走势
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
            if os.path.exists(image_path):
                analysis_result = self.analyze_with_image(prompt, image_path)
            else:
                # 纯文本分析
                analysis_result = self._analyze_text_only(prompt)
            
            # 添加时间戳和免责声明
            full_result = self._add_disclaimer(analysis_result, stock_code, stock_name)
            
            return full_result
            
        except Exception as e:
            return f"Gemini分析过程中出错: {str(e)}"
    
    def analyze_with_image(self, prompt: str, image_path: str) -> str:
        """
        使用Gemini进行图片+文本分析
        """
        try:
            # 加载图片
            image = Image.open(image_path)
            
            # 调用Gemini API
            response = self.client.models.generate_content(
                model=self.model,
                config=types.GenerateContentConfig(
                    system_instruction="你是一位专业的股票分析师，请基于以下数据分析股票的K线图和基本面情况，并预测上涨的概率。",
                    temperature=self.temperature,
                    top_p=self.top_p,
                    top_k=self.top_k,
                    candidate_count=1,
                    seed=5,
                    presence_penalty=0.0,
                    frequency_penalty=0.0,
                ),
                contents=[image, prompt]
            )
            
            return response.text
            
        except Exception as e:
            # 如果多模态分析失败，回退到纯文本分析
            print(f"多模态分析失败，回退到纯文本分析: {e}")
            return self._analyze_text_only(prompt)
    
    def _analyze_text_only(self, prompt: str) -> str:
        """
        纯文本分析
        """
        response = self.client.models.generate_content(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction="你是一位专业的股票分析师，请基于提供的数据分析股票的技术面和基本面情况，并预测未来走势。",
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                candidate_count=1,
                seed=5,
                presence_penalty=0.0,
                frequency_penalty=0.0,
            ),
            contents=[prompt]
        )
        
        return response.text
    
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