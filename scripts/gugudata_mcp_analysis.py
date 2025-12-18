#!/usr/bin/env python3
"""
使用GuguData MCP服务器获取300620实时数据
"""

import subprocess
import json
import time
from datetime import datetime

class GuguDataMCPAnalyzer:
    """GuguData MCP分析器"""

    def __init__(self):
        self.stock_code = "300620"
        self.stock_name = "光库科技"
        self.site_id = "5465645"

    def call_mcp_server(self, function_name, params=None):
        """调用MCP服务器"""
        try:
            # 构建MCP调用命令
            cmd = [
                "npx", "-y", "apifox-mcp-server@latest",
                f"--site-id={self.site_id}"
            ]

            # 创建MCP请求
            mcp_request = {
                "jsonrpc": "2.0",
                "id": int(time.time()),
                "method": function_name,
                "params": params or {}
            }

            print(f"🔍 调用MCP服务器: {function_name}")
            print(f"📋 请求参数: {params}")

            # 使用子进程调用MCP服务器
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # 发送请求
            request_json = json.dumps(mcp_request)
            stdout, stderr = process.communicate(input=request_json, timeout=30)

            print(f"📋 原始响应: {stdout[:200]}...")

            if process.returncode == 0 and stdout:
                print("✅ MCP服务器响应成功")
                try:
                    # 查找JSON内容
                    lines = stdout.strip().split('\n')
                    for line in lines:
                        if line.strip().startswith('{') or line.strip().startswith('['):
                            try:
                                response = json.loads(line.strip())
                                return response
                            except json.JSONDecodeError:
                                continue

                    print("⚠️ 响应中没有找到有效的JSON数据")
                    return None
                except Exception as e:
                    print(f"⚠️ 响应解析异常: {e}")
                    return None
            else:
                print(f"❌ MCP服务器调用失败")
                print(f"错误输出: {stderr}")
                return None

        except subprocess.TimeoutExpired:
            print("❌ MCP服务器调用超时")
            return None
        except Exception as e:
            print(f"❌ MCP服务器调用异常: {e}")
            return None

    def get_realtime_quote(self):
        """获取实时行情"""
        print("📊 获取实时行情数据...")
        print("-" * 50)

        # 先刷新API文档
        print("🔄 刷新API文档...")
        refresh_result = self.call_mcp_server("refresh_project_oas_lxo0xq", {"_": ""})

        if refresh_result:
            print("✅ API文档刷新成功")
        else:
            print("⚠️ API文档刷新失败，继续尝试...")

        # 读取API文档
        print("📖 读取API文档...")
        oas_result = self.call_mcp_server("read_project_oas_lxo0xq", {"_": ""})

        if oas_result and oas_result.get("result"):
            print("✅ 成功读取API文档")
            print("📄 文档内容预览:")
            content = oas_result["result"][:500]  # 只显示前500字符
            print(content)
            print("...")
        else:
            print("⚠️ API文档读取失败")

        # 现在尝试直接调用GuguData API（HTTP方式）
        print("\n🌐 尝试直接HTTP API调用...")
        return self.call_direct_http_api()

    def call_direct_http_api(self):
        """直接调用HTTP API"""
        import requests
        import json
        import time

        # GuguData可能的API端点
        api_endpoints = [
            "https://api.gugudata.com/api/stock/realtime",
            "https://www.gugudata.com/api/stock/realtime",
            "https://api.gugudata.com/api/stockcn/realtime",
            "https://www.gugudata.com/api/stockcn/realtime"
        ]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json',
            'X-API-Key': 'SQSM4ASGQT6UN363PWA9M6256764WYBS'
        }

        for endpoint in api_endpoints:
            try:
                print(f"🔍 尝试API端点: {endpoint}")

                params = {
                    'symbol': self.stock_code,
                    'apikey': 'SQSM4ASGQT6UN363PWA9M6256764WYBS',
                    'fields': 'all'
                }

                response = requests.get(endpoint, params=params, headers=headers, timeout=10)
                print(f"📊 响应状态码: {response.status_code}")

                if response.status_code == 200:
                    try:
                        data = response.json()
                        print("✅ 成功获取API响应")
                        print(f"📋 响应数据: {str(data)[:200]}...")
                        return data
                    except json.JSONDecodeError:
                        print(f"⚠️ JSON解析失败，响应内容: {response.text[:200]}...")

                elif response.status_code == 401:
                    print("⚠️ API密钥认证失败")
                elif response.status_code == 403:
                    print("⚠️ API访问被禁止")
                elif response.status_code == 404:
                    print("⚠️ API端点不存在")

            except Exception as e:
                print(f"⚠️ API调用异常: {e}")
                continue

        print("❌ 所有API端点都调用失败")
        return None

    def get_stock_info(self):
        """获取股票基本信息"""
        print("🏢 获取股票基本信息...")
        print("-" * 50)

        possible_functions = [
            "get_stock_info",
            "stock_info",
            "get_stock_basic",
            "query_stock_info"
        ]

        for func_name in possible_functions:
            print(f"\n🔄 尝试函数: {func_name}")
            params = {
                "symbol": self.stock_code,
                "api_key": "SQSM4ASGQT6UN363PWA9M6256764WYBS"
            }

            result = self.call_mcp_server(func_name, params)
            if result and result.get("result"):
                print("✅ 成功获取股票信息")
                return result["result"]

        return None

    def get_technical_analysis(self):
        """获取技术分析数据"""
        print("📈 获取技术分析数据...")
        print("-" * 50)

        possible_functions = [
            "get_technical_analysis",
            "technical_analysis",
            "get_technical",
            "query_technical"
        ]

        for func_name in possible_functions:
            print(f"\n🔄 尝试函数: {func_name}")
            params = {
                "symbol": self.stock_code,
                "api_key": "SQSM4ASGQT6UN363PWA9M6256764WYBS",
                "indicators": "ma,macd,rsi,kdj"
            }

            result = self.call_mcp_server(func_name, params)
            if result and result.get("result"):
                print("✅ 成功获取技术分析数据")
                return result["result"]

        return None

    def test_mcp_connection(self):
        """测试MCP连接"""
        print("🔗 测试MCP服务器连接...")
        print("-" * 50)

        # 首先测试基本的连接
        test_params = {
            "symbol": self.stock_code,
            "api_key": "SQSM4ASGQT6UN363PWA9M6256764WYBS"
        }

        result = self.call_mcp_server("ping", test_params)
        if result:
            print("✅ MCP服务器连接正常")
            return True
        else:
            print("❌ MCP服务器连接失败")
            return False

    def analyze_data(self, data):
        """分析获取到的数据"""
        print("\n📊 数据分析")
        print("=" * 60)

        if not data:
            print("❌ 没有数据可分析")
            return

        print(f"📋 数据类型: {type(data)}")
        print(f"📊 数据内容: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")

        # 尝试提取关键信息
        if isinstance(data, dict):
            print("\n🎯 提取关键信息:")
            key_fields = ['price', 'current_price', 'open', 'high', 'low', 'change', 'change_percent',
                          'volume', 'amount', 'turnover_rate', 'ma', 'macd', 'rsi']

            for field in key_fields:
                if field in data:
                    print(f"  • {field}: {data[field]}")

    def run_mcp_analysis(self):
        """运行MCP分析"""
        print("🚀 启动GuguData MCP分析")
        print("=" * 60)
        print(f"目标股票: {self.stock_name}({self.stock_code})")
        print(f"站点ID: {self.site_id}")
        print(f"API密钥: SQSM4ASGQT6UN363PWA9M6256764WYBS")
        print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # 测试连接
        if not self.test_mcp_connection():
            print("\n⚠️ MCP服务器连接失败，请检查:")
            print("  1. 网络连接是否正常")
            print("  2. MCP服务器是否正在运行")
            print("  3. API密钥是否正确")
            print("  4. 站点ID是否有效")
            return

        # 获取数据
        print("\n" + "="*60)
        quote_data = self.get_realtime_quote()

        if quote_data:
            self.analyze_data(quote_data)
        else:
            print("\n🔄 尝试获取基本信息...")
            stock_info = self.get_stock_info()
            if stock_info:
                self.analyze_data(stock_info)
            else:
                print("\n🔄 尝试获取技术分析...")
                technical_data = self.get_technical_analysis()
                if technical_data:
                    self.analyze_data(technical_data)

        print("\n" + "="*60)
        print("💡 如果数据获取成功，请查看上方分析结果")
        print("📝 如果获取失败，请检查MCP服务器配置")

def main():
    """主函数"""
    analyzer = GuguDataMCPAnalyzer()
    analyzer.run_mcp_analysis()

if __name__ == "__main__":
    main()