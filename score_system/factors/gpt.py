import os
import openai
import time
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# Load API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL_NAME = "gpt-3.5-turbo"

def query_fund_flow_raw_prompt_by_tokens(token_list: list, model: str = MODEL_NAME, delay_sec: float = 1.0) -> str:
    """
    Send raw prompt with token list to GPT to retrieve fund flow analysis from the web.
    """
    token_str = ", ".join(token_list)
    prompt = f"""
我在分析币种的资金流支持情况。请你从网络上获取 {token_str} 这些币种的最新数据，包括：

- 叙事板块（如 AI、RWA、GameFi 等）
- 部署链（如 Ethereum、Solana）
- 是否是某个 DeFi 协议的主币（如 Pendle 是 Pendle 协议主币）
- 链上 TVL 的 1天、7天变化
- 交易量变化
- 总结这些币是否有资金层面支持其强势走势

请返回如下格式的结构化 JSON：

```json
{{
  "TAO": {{
    "narrative": "AI",
    "chain": "Ethereum",
    "protocol_token": false,
    "tvl_change_1d": "+2.5%",
    "tvl_change_7d": "+10.1%",
    "volume_change": "+150%",
    "summary": "TAO 是一个 AI 板块币种，TVL 增长，交易量放大，有资金确认。",
    "fund_flow_score": 89
  }}
}}
```
评分范围 0-100，越高越强。
    """

    try:
        time.sleep(delay_sec)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个加密市场分析专家，可以联网收集链上数据、资金流、交易量等信息，分析币种强弱。"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ GPT 查询失败: {e}"

# Example usage
if __name__ == "__main__":
    token_list = ["TAO", "FET", "ONDO"]
    output = query_fund_flow_raw_prompt_by_tokens(token_list)
    print(output)
