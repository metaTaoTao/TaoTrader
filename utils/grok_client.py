"""
Grok API 客户端
用于调用 Grok API 进行事件驱动分析
"""

import requests
import os
import json
from typing import Dict, Optional, List

import os
import requests
from typing import Dict


class GrokClient:
    """Grok API 客户端"""

    def __init__(self, api_key: str = None):
        """
        初始化 Grok 客户端

        Args:
            api_key: Grok API密钥，如果不提供则从环境变量读取
        """
        self.api_key = api_key or os.getenv('GROK_API_KEY')
        self.base_url = "https://api.x.ai/v1"

        if not self.api_key:
            raise ValueError("❌ 未设置 GROK_API_KEY 环境变量")

    def chat(self, messages: list, model: str = "grok-4-fast-reasoning") -> Dict:
        """
        调用 Grok Chat API

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            model: 模型名称，默认 "grok-3" (平衡一致性和工具集成，适合事件检测任务)

        Returns:
            Grok API 响应

        Note:
            推荐的模型: grok-3 (高一致性，减少hallucination); grok-4-fast-reasoning (快速推理，但需低temperature)
            其他选项: grok-4-fast-non-reasoning (快速检索), grok-3-mini (最便宜)
        """
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "messages": messages,
            "model": model,
            "temperature": 0.2,  # 降低温度，提高一致性和减少虚构（hallucination）
            "top_p": 0.9,  # 新增：核采样，约束随机输出，进一步减少变异
            "seed": 42,  # 新增：固定随机种子，确保相同输入输出一致（如果API支持）
            "max_tokens": 2000,  # 缩短：限制输出长度，避免冗余，节省成本
            "stream": False
        }

        try:
            # 缩短超时时间，提高响应效率
            response = requests.post(url, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            print("❌ Grok API 请求超时（120秒）")
            raise
        except requests.exceptions.RequestException as e:
            print(f"❌ Grok API 请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应内容: {e.response.text}")
            raise
        except ValueError as e:  # 新增：捕获JSON解析错误
            print(f"❌ JSON 解析失败: {e}")
            raise

def get_grok_client() -> Optional[GrokClient]:
    """获取 Grok 客户端实例"""
    try:
        return GrokClient()
    except ValueError as e:
        print(str(e))
        return None


if __name__ == "__main__":
    # 测试代码
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    client = GrokClient()
    
    # 测试消息
    test_data = {
        "timestamp": "2024-10-04 12:00:00",
        "top_gainers": [
            {"rank": 1, "symbol": "BTCUSDT", "return_24h": 5.2}
        ]
    }
    
    result = client.analyze_market_data(test_data)
    print(result['analysis'])

