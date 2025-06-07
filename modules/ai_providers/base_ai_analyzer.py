from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import pandas as pd

class BaseAIAnalyzer(ABC):
    """
    AI分析器基础抽象类，定义所有AI供应商必须实现的接口
    """
    
    def __init__(self, api_key: str, **kwargs):
        """
        初始化AI分析器
        
        Args:
            api_key: API密钥
            **kwargs: 其他配置参数
        """
        self.api_key = api_key
        self.config = kwargs
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """验证配置是否正确"""
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def analyze_with_image(self, prompt: str, image_path: str) -> str:
        """
        使用图片进行分析（多模态）
        
        Args:
            prompt: 分析提示词
            image_path: 图片路径
            
        Returns:
            分析结果
        """
        pass
    
    def _prepare_analysis_data(self, stock_data: pd.DataFrame, indicators: Dict[str, Any], 
                              financial_data: Dict[str, Any], news_data: List[Dict[str, Any]], 
                              stock_code: str, stock_name: str) -> Dict[str, Any]:
        """
        准备用于分析的数据（所有子类共用）
        """
        analysis_data = {}
        
        # 基本信息
        analysis_data['股票代码'] = stock_code
        analysis_data['股票名称'] = stock_name
        
        # 提取最近的价格数据
        if not stock_data.empty:
            latest_data = stock_data.iloc[-1]
            earliest_data = stock_data.iloc[0]
            
            analysis_data['当前价格'] = float(latest_data['close'])
            analysis_data['开盘价'] = float(latest_data['open'])
            analysis_data['最高价'] = float(latest_data['high'])
            analysis_data['最低价'] = float(latest_data['low'])
            analysis_data['成交量'] = float(latest_data['volume'])
            analysis_data['日期'] = latest_data['date'].strftime('%Y-%m-%d')
            
            # 计算区间涨跌幅
            price_change = (latest_data['close'] - earliest_data['close']) / earliest_data['close'] * 100
            analysis_data['区间涨跌幅'] = round(price_change, 2)
            
            # 提取最近N天的收盘价和成交量趋势
            recent_days = min(30, len(stock_data))
            analysis_data['最近价格趋势'] = stock_data['close'].tail(recent_days).tolist()
            analysis_data['最近成交量趋势'] = stock_data['volume'].tail(recent_days).tolist()
            analysis_data['最近日期'] = [d.strftime('%Y-%m-%d') for d in stock_data['date'].tail(recent_days)]
        
        # 提取关键技术指标
        if indicators:
            latest_idx = -1  # 最新数据索引
            
            # 移动平均线
            analysis_data['MA5'] = float(indicators['MA5'].iloc[latest_idx]) if 'MA5' in indicators and not indicators['MA5'].empty else None
            analysis_data['MA10'] = float(indicators['MA10'].iloc[latest_idx]) if 'MA10' in indicators and not indicators['MA10'].empty else None
            analysis_data['MA20'] = float(indicators['MA20'].iloc[latest_idx]) if 'MA20' in indicators and not indicators['MA20'].empty else None
            analysis_data['MA30'] = float(indicators['MA30'].iloc[latest_idx]) if 'MA30' in indicators and not indicators['MA30'].empty else None
            
            # MACD
            analysis_data['MACD'] = float(indicators['MACD'].iloc[latest_idx]) if 'MACD' in indicators and not indicators['MACD'].empty else None
            analysis_data['MACD_signal'] = float(indicators['MACD_signal'].iloc[latest_idx]) if 'MACD_signal' in indicators and not indicators['MACD_signal'].empty else None
            analysis_data['MACD_hist'] = float(indicators['MACD_hist'].iloc[latest_idx]) if 'MACD_hist' in indicators and not indicators['MACD_hist'].empty else None
            
            # KDJ
            analysis_data['KDJ_K'] = float(indicators['K'].iloc[latest_idx]) if 'K' in indicators and not indicators['K'].empty else None
            analysis_data['KDJ_D'] = float(indicators['D'].iloc[latest_idx]) if 'D' in indicators and not indicators['D'].empty else None
            analysis_data['KDJ_J'] = float(indicators['J'].iloc[latest_idx]) if 'J' in indicators and not indicators['J'].empty else None
            
            # RSI
            analysis_data['RSI6'] = float(indicators['RSI6'].iloc[latest_idx]) if 'RSI6' in indicators and not indicators['RSI6'].empty else None
            analysis_data['RSI12'] = float(indicators['RSI12'].iloc[latest_idx]) if 'RSI12' in indicators and not indicators['RSI12'].empty else None
            analysis_data['RSI24'] = float(indicators['RSI24'].iloc[latest_idx]) if 'RSI24' in indicators and not indicators['RSI24'].empty else None
            
            # 布林带
            analysis_data['BOLL_upper'] = float(indicators['BOLL_upper'].iloc[latest_idx]) if 'BOLL_upper' in indicators and not indicators['BOLL_upper'].empty else None
            analysis_data['BOLL_middle'] = float(indicators['BOLL_middle'].iloc[latest_idx]) if 'BOLL_middle' in indicators and not indicators['BOLL_middle'].empty else None
            analysis_data['BOLL_lower'] = float(indicators['BOLL_lower'].iloc[latest_idx]) if 'BOLL_lower' in indicators and not indicators['BOLL_lower'].empty else None
        
        # 提取关键财务数据
        if financial_data:
            analysis_data['财务数据'] = financial_data
        
        # 提取新闻数据
        if news_data:
            analysis_data['新闻数据'] = news_data
        
        return analysis_data
    
    def _build_prompt(self, analysis_data: Dict[str, Any], stock_code: str, stock_name: str) -> str:
        """
        构建提示词（所有子类共用）
        """
        import json
        from datetime import datetime
        
        # 将分析数据转换为JSON字符串
        data_json = json.dumps(analysis_data, ensure_ascii=False, indent=2)
        
        # 构建提示词
        prompt = f"""
        你是一位专业的股票分析师，请基于以下数据分析 {stock_name}({stock_code}) 的技术面和基本面情况，并预测未来可能的走势。
        
        数据信息如下：
        ```json
        {data_json}
        ```
        
        请提供以下分析：
        1. 股票基本情况概述
        2. 技术指标分析（包括移动平均线、MACD、KDJ、RSI、布林带等）
        3. 基本面分析（基于财务数据）
        4. 市场情绪分析（基于新闻数据）
        5. 预测未来一周上涨的概率（范围为0-100，0为下跌，100为上涨）
        6. 投资建议和风险提示
        
        请用专业、客观的语言进行分析，避免过度乐观或悲观的偏见。分析应该基于数据，而不是个人情感。
        请使用markdown格式输出，使用适当的标题、列表和强调，使分析报告更易于阅读。
        """
        
        return prompt
    
    def _add_disclaimer(self, analysis_result: str, stock_code: str, stock_name: str) -> str:
        """
        添加时间戳和免责声明
        """
        from datetime import datetime
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        disclaimer = "\n\n免责声明：本分析报告由AI自动生成，仅供参考，不构成任何投资建议。投资有风险，入市需谨慎。"
        
        full_result = f"# {stock_name}({stock_code}) AI投资分析报告\n\n生成时间: {current_time}\n\n{analysis_result}\n\n{disclaimer}"
        
        return full_result