#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI看线 - 多AI供应商使用示例

本示例展示如何使用不同的AI供应商进行股票分析
"""

import os
from dotenv import load_dotenv

from modules.data_fetcher import StockDataFetcher
from modules.technical_analyzer import TechnicalAnalyzer
from modules.visualizer import Visualizer
from modules.ai_analyzer import AIAnalyzer

# 加载环境变量
load_dotenv()

def analyze_with_multiple_providers(stock_code, period='1年', save_path='./output'):
    """
    使用多个AI供应商分析同一只股票，对比分析结果
    """
    print(f"开始分析股票: {stock_code}")
    print("=" * 60)
    
    # 确保输出目录存在
    os.makedirs(save_path, exist_ok=True)
    
    # 初始化数据获取和分析模块
    data_fetcher = StockDataFetcher()
    technical_analyzer = TechnicalAnalyzer()
    visualizer = Visualizer()
    
    # 获取股票数据
    print(f"正在获取 {stock_code} 的历史数据...")
    stock_data = data_fetcher.fetch_stock_data(stock_code, period)
    
    if stock_data.empty:
        print(f"未能获取到股票 {stock_code} 的数据")
        return
    
    # 获取财务和新闻数据
    print(f"正在获取 {stock_code} 的财务和新闻数据...")
    financial_data = data_fetcher.fetch_financial_data(stock_code)
    news_data = data_fetcher.fetch_news_data(stock_code)
    
    # 计算技术指标
    print("正在计算技术指标...")
    indicators = technical_analyzer.calculate_indicators(stock_data)
    
    # 生成可视化图表
    print("正在生成K线图和技术指标图...")
    chart_path = visualizer.create_charts(stock_data, indicators, stock_code, save_path)
    
    # 显示可用的AI供应商状态
    print("\n当前AI供应商状态:")
    AIAnalyzer.show_provider_status()
    print()
    
    # 定义要测试的AI供应商
    providers = ['gemini', 'openai', 'siliconflow', 'deepseek']
    results = {}
    
    # 使用不同的AI供应商进行分析
    for provider in providers:
        print(f"\n{'='*20} 使用 {provider.upper()} 分析 {'='*20}")
        
        try:
            # 创建AI分析器实例
            ai_analyzer = AIAnalyzer(provider=provider)
            
            # 显示当前使用的供应商信息
            provider_info = ai_analyzer.get_provider_info()
            print(f"供应商: {provider_info['provider_name']}")
            print(f"模型: {provider_info['model']}")
            print()
            
            # 进行AI分析
            print("正在使用AI分析预测未来走势...")
            analysis_result = ai_analyzer.analyze(
                stock_data, indicators, financial_data, news_data, stock_code, save_path
            )
            
            # 保存分析结果
            result_path = os.path.join(save_path, f"{stock_code}_{provider}_analysis_result.txt")
            with open(result_path, 'w', encoding='utf-8') as f:
                f.write(analysis_result)
            
            results[provider] = {
                'success': True,
                'result': analysis_result,
                'file_path': result_path
            }
            
            print(f"✅ {provider.upper()} 分析完成")
            print(f"结果已保存至: {result_path}")
            
        except Exception as e:
            print(f"❌ {provider.upper()} 分析失败: {str(e)}")
            results[provider] = {
                'success': False,
                'error': str(e)
            }
    
    # 生成对比报告
    print(f"\n{'='*20} 分析结果汇总 {'='*20}")
    
    successful_analyses = [p for p, r in results.items() if r['success']]
    failed_analyses = [p for p, r in results.items() if not r['success']]
    
    print(f"成功分析的供应商: {', '.join(successful_analyses) if successful_analyses else '无'}")
    print(f"失败的供应商: {', '.join(failed_analyses) if failed_analyses else '无'}")
    
    if successful_analyses:
        print(f"\nK线图和技术指标图已保存至: {chart_path}")
        print("各供应商分析结果文件:")
        for provider in successful_analyses:
            print(f"  - {provider.upper()}: {results[provider]['file_path']}")
    
    return results

def analyze_with_specific_provider(stock_code, provider='siliconflow', period='1年', save_path='./output'):
    """
    使用指定的AI供应商分析股票
    """
    print(f"使用 {provider.upper()} 分析股票: {stock_code}")
    print("=" * 60)
    
    # 确保输出目录存在
    os.makedirs(save_path, exist_ok=True)
    
    # 初始化各模块
    data_fetcher = StockDataFetcher()
    technical_analyzer = TechnicalAnalyzer()
    visualizer = Visualizer()
    ai_analyzer = AIAnalyzer(provider=provider)
    
    # 获取股票数据
    print(f"正在获取 {stock_code} 的历史数据...")
    stock_data = data_fetcher.fetch_stock_data(stock_code, period)
    
    # 获取财务和新闻数据
    print(f"正在获取 {stock_code} 的财务和新闻数据...")
    financial_data = data_fetcher.fetch_financial_data(stock_code)
    news_data = data_fetcher.fetch_news_data(stock_code)
    
    # 计算技术指标
    print("正在计算技术指标...")
    indicators = technical_analyzer.calculate_indicators(stock_data)
    
    # 生成可视化图表
    print("正在生成K线图和技术指标图...")
    chart_path = visualizer.create_charts(stock_data, indicators, stock_code, save_path)
    
    # AI分析预测
    print("正在使用AI分析预测未来走势...")
    analysis_result = ai_analyzer.analyze(
        stock_data, indicators, financial_data, news_data, stock_code, save_path
    )
    
    # 保存分析结果
    result_path = os.path.join(save_path, f"{stock_code}_analysis_result.txt")
    with open(result_path, 'w', encoding='utf-8') as f:
        f.write(analysis_result)
    
    print(f"\n分析完成！")
    print(f"K线图和技术指标图已保存至: {chart_path}")
    print(f"AI分析结果已保存至: {result_path}")
    
    # 显示使用的供应商信息
    provider_info = ai_analyzer.get_provider_info()
    print(f"\n使用的AI供应商: {provider_info['provider_name']}")
    print(f"使用的模型: {provider_info['model']}")
    
    return analysis_result

def show_provider_comparison():
    """
    显示各AI供应商的特点对比
    """
    print("AI供应商特点对比:")
    print("=" * 80)
    
    providers_info = {
        'OpenAI': {
            'models': 'GPT-4o, GPT-4, GPT-3.5-turbo',
            'multimodal': '✅ 支持',
            'features': '通用能力强，响应速度快，多模态分析能力出色',
            'cost': '中等',
            'recommendation': '推荐用于需要多模态分析的场景'
        },
        'SiliconFlow': {
            'models': 'Qwen2.5-72B, GLM-4, Llama-3.1',
            'multimodal': '✅ 支持(部分模型)',
            'features': '开源模型集合，中文理解能力强，性价比高',
            'cost': '低',
            'recommendation': '推荐用于中文文本分析，成本敏感场景'
        },
        'DeepSeek': {
            'models': 'DeepSeek-V3, DeepSeek-Chat',
            'multimodal': '❌ 暂不支持',
            'features': '数学推理能力强，逻辑分析能力出色，代码理解能力强',
            'cost': '低',
            'recommendation': '推荐用于需要复杂推理的技术分析'
        },
        'Gemini': {
            'models': 'Gemini-2.5-Flash, Gemini-1.5-Pro',
            'multimodal': '✅ 支持',
            'features': '多模态能力强，分析全面，上下文理解能力出色',
            'cost': '免费额度+付费',
            'recommendation': '推荐作为默认选择，功能全面'
        }
    }
    
    for provider, info in providers_info.items():
        print(f"\n🤖 {provider}")
        print(f"  模型: {info['models']}")
        print(f"  多模态: {info['multimodal']}")
        print(f"  特点: {info['features']}")
        print(f"  成本: {info['cost']}")
        print(f"  推荐: {info['recommendation']}")

if __name__ == "__main__":
    # 显示供应商对比信息
    show_provider_comparison()
    print()
    
    # 示例1: 使用默认供应商分析平安银行
    print("示例1: 使用默认供应商分析平安银行(000001)")
    analyze_with_specific_provider('000001')
    
    print("\n" + "="*80 + "\n")
    
    # 示例2: 使用多个供应商对比分析贵州茅台
    print("示例2: 使用多个供应商对比分析贵州茅台(600519)")
    # analyze_with_multiple_providers('600519')
    
    print("\n" + "="*80 + "\n")
    
    # 示例3: 使用特定供应商分析
    print("示例3: 使用OpenAI分析中国平安(601318)")
    # analyze_with_specific_provider('601318', provider='openai')
    
    # 您可以尝试分析其他股票，例如:
    # analyze_with_specific_provider('000858', provider='siliconflow')  # 五粮液
    # analyze_with_specific_provider('002415', provider='deepseek')     # 海康威视
    # analyze_with_multiple_providers('000002')                        # 万科A