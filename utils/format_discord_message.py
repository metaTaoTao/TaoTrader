"""
Discord 消息格式化工具
将 Grok 分析结果转换为 Discord 友好的格式
"""

import re
from typing import Dict, List


def parse_grok_table(text: str) -> List[Dict]:
    """
    解析 Grok 输出的 Markdown 表格
    
    Args:
        text: Grok 输出的文本，包含 Markdown 表格
    
    Returns:
        List[Dict]: 解析后的数据列表
    """
    lines = text.strip().split('\n')
    data = []
    
    # 跳过表头和分隔线
    for i, line in enumerate(lines):
        if '|' in line and not line.startswith('|---'):
            # 移除首尾的 |
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            
            # 跳过表头行
            if '币种' in cells and '事件类型' in cells:
                continue
            
            if len(cells) >= 9:  # 确保有足够列
                data.append({
                    'symbol': cells[0],
                    'event_type': cells[1],
                    'event_summary': cells[2],
                    'time_utc': cells[3],
                    'heat_score': cells[4],
                    'sector': cells[5],
                    'importance_score': cells[6],
                    'comprehensive_score': cells[7],
                    'source_links': cells[8]
                })
    
    return data


def format_for_discord(data: List[Dict], max_items: int = 5) -> str:
    """
    将解析后的数据格式化为 Discord 友好格式
    
    Args:
        data: 解析后的数据列表
        max_items: 最多显示多少个币种
    
    Returns:
        str: 格式化后的 Discord 消息
    """
    # 过滤掉分数为0或没有事件的项目
    filtered_data = [item for item in data if item['comprehensive_score'] != '0' and item['comprehensive_score'] != '-']
    
    # 按综合分数排序
    try:
        filtered_data.sort(key=lambda x: int(x['comprehensive_score']), reverse=True)
    except (ValueError, TypeError):
        # 如果分数不是数字，保持原序
        pass
    
    # 只取前N个
    filtered_data = filtered_data[:max_items]
    
    if not filtered_data:
        return "❌ 未找到有效的事件驱动因素"
    
    # 构建 Discord Embed 格式的消息
    lines = []
    lines.append(f"**📊 事件驱动分析 (前 {len(filtered_data)} 名)**\n")
    
    for i, item in enumerate(filtered_data, 1):
        # 表情符号
        emoji = "🔴" if int(item['comprehensive_score']) >= 70 else "🟡" if int(item['comprehensive_score']) >= 50 else "🟢"
        
        lines.append(f"{emoji} **#{i} {item['symbol']}**")
        lines.append(f"   • 事件类型: {item['event_type']}")
        lines.append(f"   • 综合分数: **{item['comprehensive_score']}/100** (热度:{item['heat_score']}, 重要性:{item['importance_score']})")
        lines.append(f"   • 板块: {item['sector']}")
        lines.append(f"   • 事件: {item['event_summary']}")
        if item['time_utc'] != '-':
            lines.append(f"   • 时间: {item['time_utc']}")
        if item['source_links'] != '-':
            # 只取第一个链接
            links = item['source_links'].split(';')[0].strip()
            if links:
                lines.append(f"   • 来源: {links}")
        lines.append("")
    
    return '\n'.join(lines)


def format_simple_discord(text: str) -> str:
    """
    简化版本的 Discord 格式化
    直接从原文本中提取关键信息
    
    Args:
        text: Grok 输出文本
    
    Returns:
        str: 格式化后的消息
    """
    # 解析表格
    data = parse_grok_table(text)
    
    if not data:
        # 如果解析失败，尝试简单提取
        lines = text.split('\n')
        simple_lines = []
        simple_lines.append("**📊 事件驱动分析**\n")
        
        for line in lines:
            if '|' in line and any(emoji in line for emoji in ['🔴', '🟡', '🟢', '📊']):
                simple_lines.append(line)
        
        return '\n'.join(simple_lines) if len(simple_lines) > 1 else text
    
    # 使用标准格式化
    return format_for_discord(data)


def format_json_for_discord(json_data: List[Dict], max_items: int = 5) -> str:
    """
    将 JSON 数据格式化为 Discord 友好格式
    
    Args:
        json_data: JSON 数据列表
        max_items: 最多显示多少个币种
    
    Returns:
        str: 格式化后的 Discord 消息
    """
    if not json_data:
        return "❌ 未找到有效的事件驱动因素"
    
    # 过滤掉分数为0或没有事件的项目
    filtered_data = [
        item for item in json_data 
        if item.get('comprehensive_score', 0) and item.get('comprehensive_score', 0) != 0
    ]
    
    # 按综合分数排序
    try:
        filtered_data.sort(key=lambda x: int(x.get('comprehensive_score', 0)), reverse=True)
    except (ValueError, TypeError):
        pass
    
    # 只取前N个
    filtered_data = filtered_data[:max_items]
    
    if not filtered_data:
        return "❌ 未找到有效的事件驱动因素"
    
    # 构建 Discord Embed 格式的消息
    lines = []
    lines.append(f"**📊 事件驱动分析 (前 {len(filtered_data)} 名)**\n")
    
    for i, item in enumerate(filtered_data, 1):
        # 表情符号
        score = int(item.get('comprehensive_score', 0))
        emoji = "🔴" if score >= 70 else "🟡" if score >= 50 else "🟢"
        
        lines.append(f"{emoji} **#{i} {item.get('symbol', 'N/A')}**")
        lines.append(f"   • 事件类型: {item.get('event_type', 'N/A')}")
        lines.append(f"   • 综合分数: **{score}/100** (热度:{item.get('heat_score', 'N/A')}, 重要性:{item.get('importance_score', 'N/A')})")
        lines.append(f"   • 板块: {item.get('sector', 'N/A')}")
        lines.append(f"   • 事件: {item.get('event_summary', 'N/A')}")
        
        time_utc = item.get('time_utc', '-')
        if time_utc and time_utc != '-':
            lines.append(f"   • 时间: {time_utc}")
        
        source_links = item.get('source_links', [])
        if source_links:
            if isinstance(source_links, list) and source_links:
                lines.append(f"   • 来源: {source_links[0]}")
            elif isinstance(source_links, str) and source_links:
                lines.append(f"   • 来源: {source_links}")
        
        lines.append("")
    
    return '\n'.join(lines)


if __name__ == "__main__":
    # 测试代码
    test_json = [
        {
            "symbol": "ZECUSDT",
            "event_type": "regulatory",
            "event_summary": "监管审查",
            "time_utc": "2024-10-08 14:00",
            "heat_score": 75,
            "sector": "隐私币",
            "importance_score": 85,
            "comprehensive_score": 80,
            "source_links": ["https://example.com"]
        }
    ]
    
    result = format_json_for_discord(test_json)
    print(result)

