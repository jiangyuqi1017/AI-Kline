import os
import argparse
from dotenv import load_dotenv

from modules.data_fetcher import StockDataFetcher
from modules.technical_analyzer import TechnicalAnalyzer
from modules.visualizer import Visualizer
from modules.ai_analyzer import AIAnalyzer

# 加载环境变量
load_dotenv()

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='AI看线 - A股技术分析与AI预测工具（支持多AI供应商）')
    parser.add_argument('--stock_code', type=str, required=True, help='股票代码，例如：000001')
    parser.add_argument('--period', type=str, default='1年', 
                       choices=['1年', '6个月', '3个月', '1个月', '1周'],
                       help='分析周期，默认为1年')
    parser.add_argument('--save_path', type=str, default='./output', help='结果保存路径')
    parser.add_argument('--ai_provider', type=str, 
                       choices=['openai', 'siliconflow', 'deepseek', 'gemini', 'auto'],
                       help='AI供应商选择，auto为自动选择可用供应商')
    parser.add_argument('--show_providers', action='store_true', 
                       help='显示所有AI供应商状态')
    parser.add_argument('--model', type=str, help='指定使用的模型名称')
    parser.add_argument('--temperature', type=float, help='设置温度参数（0.0-1.0）')
    
    args = parser.parse_args()
    
    # 如果只是查看供应商状态
    if args.show_providers:
        print("AI供应商状态检查:")
        print("=" * 50)
        AIAnalyzer.show_provider_status()
        return
    
    print(f"AI看线 - 开始分析股票: {args.stock_code}")
    print("=" * 60)
    
    # 确保输出目录存在
    os.makedirs(args.save_path, exist_ok=True)
    
    # 初始化各模块
    data_fetcher = StockDataFetcher()
    technical_analyzer = TechnicalAnalyzer()
    visualizer = Visualizer()
    
    # 准备AI分析器参数
    ai_kwargs = {}
    if args.model:
        ai_kwargs['model'] = args.model
    if args.temperature is not None:
        ai_kwargs['temperature'] = args.temperature
    
    # 创建AI分析器
    try:
        if args.ai_provider == 'auto' or args.ai_provider is None:
            ai_analyzer = AIAnalyzer(**ai_kwargs)
        else:
            ai_analyzer = AIAnalyzer(provider=args.ai_provider, **ai_kwargs)
        
        # 显示使用的AI供应商信息
        provider_info = ai_analyzer.get_provider_info()
        print(f"使用AI供应商: {provider_info['provider_name']}")
        print(f"使用模型: {provider_info['model']}")
        print()
        
    except Exception as e:
        print(f"❌ AI分析器初始化失败: {e}")
        print("\n请检查API密钥配置，或使用 --show_providers 查看供应商状态")
        return
    
    try:
        # 获取股票数据
        print(f"正在获取 {args.stock_code} 的历史数据...")
        stock_data = data_fetcher.fetch_stock_data(args.stock_code, args.period)
        
        if stock_data.empty:
            print(f"❌ 未能获取到股票 {args.stock_code} 的数据，请检查股票代码是否正确")
            return
        
        print(f"✅ 成功获取 {len(stock_data)} 条交易数据")
        
        # 获取财务和新闻数据
        print(f"正在获取 {args.stock_code} 的财务和新闻数据...")
        financial_data = data_fetcher.fetch_financial_data(args.stock_code)
        news_data = data_fetcher.fetch_news_data(args.stock_code)
        
        print(f"✅ 成功获取财务数据: {len(financial_data)} 项")
        print(f"✅ 成功获取新闻数据: {len(news_data)} 条")
        
        # 计算技术指标
        print("正在计算技术指标...")
        indicators = technical_analyzer.calculate_indicators(stock_data)
        print(f"✅ 成功计算 {len(indicators)} 个技术指标")
        
        # 生成可视化图表
        print("正在生成K线图和技术指标图...")
        chart_path = visualizer.create_charts(stock_data, indicators, args.stock_code, args.save_path)
        print(f"✅ 图表已保存至: {chart_path}")
        
        # AI分析预测
        print(f"正在使用 {provider_info['provider_name']} 分析预测未来走势...")
        analysis_result = ai_analyzer.analyze(
            stock_data, indicators, financial_data, news_data, args.stock_code, args.save_path
        )
        
        # 保存分析结果
        result_path = os.path.join(args.save_path, f"{args.stock_code}_analysis_result.txt")
        with open(result_path, 'w', encoding='utf-8') as f:
            f.write(analysis_result)
        
        print(f"✅ AI分析完成，结果已保存至: {result_path}")
        
        print(f"\n🎉 分析完成！")
        print(f"📊 K线图和技术指标图: {chart_path}")
        print(f"🤖 AI分析结果: {result_path}")
        print(f"🔧 使用的AI供应商: {provider_info['provider_name']} ({provider_info['model']})")
        
        # 显示分析结果预览
        print(f"\n📋 分析结果预览:")
        print("-" * 50)
        print(analysis_result[:500] + "..." if len(analysis_result) > 500 else analysis_result)
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
    except Exception as e:
        print(f"❌ 分析过程中出错: {e}")
        print("\n请检查:")
        print("1. 网络连接是否正常")
        print("2. 股票代码是否正确")
        print("3. API密钥是否有效")
        print("4. API调用限制是否超出")

def show_help():
    """显示详细帮助信息"""
    help_text = """
AI看线 - A股技术分析与AI预测工具

支持的AI供应商:
• OpenAI: GPT-4o等模型，多模态分析能力强
• SiliconFlow: Qwen2.5等开源模型，中文理解优秀
• DeepSeek: DeepSeek-V3模型，推理能力强
• Gemini: Google Gemini 2.5，功能全面

使用示例:
1. 使用默认供应商分析:
   python main.py --stock_code 000001

2. 指定AI供应商:
   python main.py --stock_code 000001 --ai_provider openai

3. 指定模型和参数:
   python main.py --stock_code 000001 --ai_provider openai --model gpt-4o --temperature 0.1

4. 查看供应商状态:
   python main.py --show_providers

5. 长期分析:
   python main.py --stock_code 600519 --period 1年 --ai_provider gemini

注意事项:
• 请确保在.env文件中配置至少一个AI供应商的API密钥
• 不同供应商的分析结果可能存在差异
• 分析结果仅供参考，不构成投资建议
"""
    print(help_text)

if __name__ == "__main__":
    # 检查是否请求帮助
    import sys
    if len(sys.argv) == 1 or '--help' in sys.argv or '-h' in sys.argv:
        show_help()
    else:
        main()