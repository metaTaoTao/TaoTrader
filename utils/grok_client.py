"""
Grok API 客户端
用于调用 Grok API 进行事件驱动分析
"""

import requests
import os
import json
from typing import Dict, Optional, List


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
            model: 模型名称，默认 "grok-4-fast-reasoning" (需要推理能力用于正负面判断)
        
        Returns:
            Grok API 响应
        
        Note:
            推荐的模型: grok-4-fast-reasoning (推理正负面、因果关系)
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
            "temperature": 0.7,
            "max_tokens": 2000,  # 减少token，降低成本和超时风险
            "stream": False
        }
        
        try:
            # 使用较长的超时，但也要及时失败避免浪费
            response = requests.post(url, headers=headers, json=data, timeout=600)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Grok API 请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应内容: {e.response.text}")
            raise
    
    def analyze_market_data(self, market_data: Dict, additional_context: str = "") -> Dict:
        """
        分析市场数据并获取事件驱动洞察
        
        Args:
            market_data: 市场数据字典
            additional_context: 额外的上下文信息
        
        Returns:
            分析结果字典
        """
        # 构建提示词
        prompt = self._build_analysis_prompt(market_data, additional_context)
        
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        print("🤖 正在调用 Grok API 进行分析...")
        response = self.chat(messages)
        
        # 解析响应
        if 'choices' in response and len(response['choices']) > 0:
            content = response['choices'][0]['message']['content']
            return {
                'analysis': content,
                'raw_response': response
            }
        else:
            return {'analysis': 'No response', 'raw_response': response}
    
    def _build_analysis_prompt(self, market_data: Dict, additional_context: str) -> str:
        """构建分析提示词"""
        prompt = f"""你是一位经验丰富的加密货币市场分析师。请分析以下24h涨幅榜数据，提供事件驱动分析。

市场数据：
{json.dumps(market_data, indent=2, ensure_ascii=False)}

{additional_context}

请提供以下分析：
1. **市场催化剂识别**：分析前几名涨幅币种，识别可能的驱动因素（技术突破、重大新闻、空投、合作等）
2. **板块关联性**：判断这些币种是否属于同一板块或生态系统，分析联动效应
3. **趋势可持续性**：基于成交额、涨幅幅度等指标，评估趋势可持续性
4. **风险提示**：指出潜在风险（如：价格异常、缺乏流动性、可能的抛售压力等）
5. **投资建议**：基于分析给出合理的投资建议（风险提示：不构成投资建议）

请用中文回答，格式清晰，条理分明。"""

        return prompt


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

