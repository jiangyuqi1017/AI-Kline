import os
import json
import matplotlib
matplotlib.use('Agg')
from flask import Flask, render_template, request, jsonify, send_from_directory
from modules.data_fetcher import StockDataFetcher
from modules.technical_analyzer import TechnicalAnalyzer
from modules.visualizer import Visualizer
from modules.ai_analyzer import AIAnalyzer
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')

# 确保输出目录存在
os.makedirs('./output', exist_ok=True)
os.makedirs('./output/charts', exist_ok=True)

# 初始化各模块
data_fetcher = StockDataFetcher()
technical_analyzer = TechnicalAnalyzer()
visualizer = Visualizer()

@app.route('/')
def index():
    """首页"""
    # 获取可用的AI供应商信息
    available_providers = AIAnalyzer.get_available_providers()
    return render_template('index.html', providers=available_providers)

@app.route('/api/providers/status')
def get_providers_status():
    """获取AI供应商状态API"""
    try:
        available_providers = AIAnalyzer.get_available_providers()
        return jsonify({
            'success': True,
            'providers': available_providers
        })
    except Exception as e:
        return jsonify({'error': f'获取供应商状态时出错: {str(e)}'}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    """分析股票"""
    data = request.form
    stock_code = data.get('stock_code')
    period = data.get('period', '1年')
    ai_provider = data.get('ai_provider', 'auto')  # 新增AI供应商选择
    save_path = './output'
    
    if not stock_code:
        return jsonify({'error': '请输入股票代码'}), 400
    
    try:
        # 创建AI分析器
        try:
            if ai_provider == 'auto' or ai_provider == '':
                ai_analyzer = AIAnalyzer()
            else:
                ai_analyzer = AIAnalyzer(provider=ai_provider)
                
            # 获取使用的供应商信息
            provider_info = ai_analyzer.get_provider_info()
            print('$$$$$$$$$$$$$$')
            print(provider_info)
            
        except Exception as e:
            return jsonify({'error': f'AI分析器初始化失败: {str(e)}'}), 500
        
        # 获取股票数据
        stock_data = data_fetcher.fetch_stock_data(stock_code, period)
        
        if stock_data.empty:
            return jsonify({'error': f'未找到股票 {stock_code} 的数据'}), 404
        
        # 获取财务和新闻数据
        financial_data = data_fetcher.fetch_financial_data(stock_code)
        news_data = data_fetcher.fetch_news_data(stock_code)
        
        # 计算技术指标
        indicators = technical_analyzer.calculate_indicators(stock_data)
        
        # 生成可视化图表
        chart_path = visualizer.create_charts(stock_data, indicators, stock_code, save_path)
        
        # AI分析预测
        analysis_result = ai_analyzer.analyze(
            stock_data, indicators, financial_data, news_data, stock_code, save_path
        )
        
        # 保存分析结果
        result_path = os.path.join(save_path, f"{stock_code}_analysis_result.txt")
        with open(result_path, 'w', encoding='utf-8') as f:
            f.write(analysis_result)
        
        # 准备返回数据
        chart_files = []
        charts_dir = os.path.join(save_path, 'charts')
        if os.path.exists(charts_dir):
            for file in os.listdir(charts_dir):
                if file.startswith(stock_code) and (file.endswith('.png') or file.endswith('.html')):
                    chart_files.append(file)
        
        return jsonify({
            'success': True,
            'stock_code': stock_code,
            'charts': chart_files,
            'analysis_result': analysis_result,
            'provider_info': provider_info,  # 返回使用的AI供应商信息
            'data_stats': {  # 添加数据统计信息
                'data_points': len(stock_data),
                'financial_items': len(financial_data) if financial_data else 0,
                'news_items': len(news_data) if news_data else 0,
                'indicators_count': len(indicators) if indicators else 0
            }
        })
    
    except Exception as e:
        return jsonify({'error': f'分析过程中出错: {str(e)}'}), 500

@app.route('/output/charts/<path:filename>')
def serve_chart(filename):
    """提供图表文件"""
    return send_from_directory('output/charts', filename)

@app.route('/stock_info/<stock_code>')
def get_stock_info(stock_code):
    """获取股票基本信息"""
    try:
        import akshare as ak
        stock_info = ak.stock_individual_info_em(symbol=stock_code)
        if not stock_info.empty:
            # 转换为字典列表
            info_dict = {
                row['item']: row['value'] 
                for _, row in stock_info.iterrows()
            }
            return jsonify({'success': True, 'data': info_dict})
        else:
            return jsonify({'error': f'未找到股票 {stock_code} 的信息'}), 404
    except Exception as e:
        return jsonify({'error': f'获取股票信息时出错: {str(e)}'}), 500

@app.route('/api/providers/test/<provider>')
def test_provider(provider):
    """测试指定AI供应商的连接"""
    try:
        # 尝试创建分析器实例
        ai_analyzer = AIAnalyzer(provider=provider)
        provider_info = ai_analyzer.get_provider_info()
        
        return jsonify({
            'success': True,
            'message': f'{provider_info["provider_name"]} 连接成功',
            'provider_info': provider_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'连接 {provider} 失败: {str(e)}'
        }), 400

@app.route('/api/config')
def get_config():
    """获取当前配置信息"""
    try:
        # 获取可用供应商状态
        available_providers = AIAnalyzer.get_available_providers()
        
        # 获取环境变量中的默认供应商
        default_provider = os.getenv('DEFAULT_AI_PROVIDER', 'siliconflow')
        
        return jsonify({
            'success': True,
            'config': {
                'default_provider': default_provider,
                'available_providers': available_providers,
                'supported_periods': ['1年', '6个月', '3个月', '1个月', '1周']
            }
        })
    except Exception as e:
        return jsonify({'error': f'获取配置信息时出错: {str(e)}'}), 500

# 错误处理
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': '页面不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器内部错误'}), 500

# 添加一些有用的路由用于调试
@app.route('/debug/providers')
def debug_providers():
    """调试：显示所有AI供应商的详细状态"""
    try:
        from modules.ai_providers import AIAnalyzerFactory
        
        providers_status = AIAnalyzerFactory.check_api_keys()
        supported_providers = AIAnalyzerFactory.get_available_providers()

        print(providers_status)
        print(os.getenv('SILICONFLOW_API_KEY'))
        
        debug_info = {
            'supported_providers': supported_providers,
            'api_keys_status': providers_status,
            'environment_variables': {
                'OPENAI_API_KEY': '***' if os.getenv('OPENAI_API_KEY') else None,
                'SILICONFLOW_API_KEY': '***' if os.getenv('SILICONFLOW_API_KEY') else None,
                'DEEPSEEK_API_KEY': '***' if os.getenv('DEEPSEEK_API_KEY') else None,
                'GEMINI_API_KEY': '***' if os.getenv('GEMINI_API_KEY') else None,
                'DEFAULT_AI_PROVIDER': os.getenv('DEFAULT_AI_PROVIDER', 'gemini')
            }
        }
        
        return jsonify({
            'success': True,
            'debug_info': debug_info
        })
    except Exception as e:
        return jsonify({'error': f'调试信息获取失败: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 启动AI看线Web服务...")
    print("💡 访问 http://localhost:5001 开始使用")
    print("🔧 调试信息: http://localhost:5001/debug/providers")
    print("📊 API状态: http://localhost:5001/api/providers/status")
    
    # 显示AI供应商状态
    print("\n" + "="*50)
    AIAnalyzer.show_provider_status()
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)