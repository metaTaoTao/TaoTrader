# bot_command/discord_ticker_command.py

import discord
import sys
import os
import pandas as pd
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_local_mapping_table():
    """加载本地映射表"""
    mapping_file = 'coin_mapping_table.csv'
    
    if not os.path.exists(mapping_file):
        return None, "映射表文件不存在"
    
    try:
        df = pd.read_csv(mapping_file)
        return df, None
    except Exception as e:
        return None, f"读取映射表失败: {str(e)}"

def find_ticker_info(df, ticker):
    """从映射表中查找ticker信息"""
    # 直接匹配ticker
    result = df[df['ticker'].str.upper() == ticker.upper()]
    
    if not result.empty:
        return result.iloc[0].to_dict()
    
    # 如果没找到，尝试匹配base_symbol
    base_symbol = ticker.upper()
    
    # 移除常见的quote currencies
    quote_currencies = ['USDT', 'USDC', 'BTC', 'ETH', 'BNB', 'BUSD', 'FDUSD']
    for quote in quote_currencies:
        if ticker.upper().endswith(quote):
            base_symbol = ticker.upper()[:-len(quote)]
            break
    
    # 通过base_symbol匹配
    result = df[df['base_symbol'].str.upper() == base_symbol]
    if not result.empty:
        return result.iloc[0].to_dict()
    
    return None

async def ticker_command(interaction, symbol: str):
    """
    Discord Bot ticker查询命令（从本地映射表读取）
    用法: /ticker ANIMEUSDT 或 !ticker ANIMEUSDT
    """
    try:
        if not symbol:
            embed = discord.Embed(
                title="❗ 用法示例",
                description="`/ticker ANIMEUSDT` 或 `!ticker ANIMEUSDT`",
                color=0xff0000
            )
            embed.add_field(
                name="📍 支持格式",
                value=(
                    "• Binance格式：`ANIMEUSDT`, `BTCUSDT`\n"
                    "• OKX格式：`ANIME-USDT`, `BTC-USDT`"
                ),
                inline=False
            )
            embed.add_field(
                name="💡 示例",
                value="`/ticker MEUSDT`",
                inline=False
            )
            embed.add_field(
                name="⚡ 数据来源",
                value="本地映射表（每日更新）",
                inline=False
            )
            
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.followup.send(embed=embed)
            return

        ticker = symbol.upper()
        
        # 加载本地映射表
        df, error = load_local_mapping_table()
        if error:
            embed = discord.Embed(
                title="❌ 数据读取失败",
                description=f"无法读取本地数据：{error}",
                color=0xff0000
            )
            embed.add_field(
                name="💡 解决方案",
                value="请联系管理员更新映射表",
                inline=False
            )
            
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.followup.send(embed=embed)
            return
        
        # 从本地数据查找ticker信息
        coin_info = find_ticker_info(df, ticker)
        
        if not coin_info:
            embed = discord.Embed(
                title=f"❌ 未找到 {ticker} 的信息",
                color=0xff0000
            )
            embed.add_field(
                name="🔍 可能原因",
                value=(
                    "• ticker不存在于映射表中\n"
                    "• 映射表需要更新"
                ),
                inline=False
            )
            embed.add_field(
                name="💡 解决方案",
                value="请检查ticker拼写或联系管理员",
                inline=False
            )
            
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.followup.send(embed=embed)
            return
        
        # 格式化数字显示
        def format_number(value):
            if pd.isna(value) or value is None:
                return "N/A"
            try:
                num = float(value)
                if num >= 1e9:
                    return f"${num/1e9:.2f}B"
                elif num >= 1e6:
                    return f"${num/1e6:.2f}M"
                elif num >= 1e3:
                    return f"${num/1e3:.2f}K"
                else:
                    return f"${num:.2f}"
            except:
                return "N/A"
        
        # 处理categories字段（从分号分隔的字符串转换为列表）
        categories_str = coin_info.get('categories', '')
        if categories_str and isinstance(categories_str, str):
            categories = [cat.strip() for cat in categories_str.split(';') if cat.strip()]
        else:
            categories = []
        
        # 获取数据更新时间
        last_updated = coin_info.get('last_updated', 'N/A')
        
        # 构建Discord Embed
        embed = discord.Embed(
            title=f"🔍 {ticker} 分析结果",
            color=0x00ff00
        )
        
        # 基本信息
        embed.add_field(
            name="📛 币种名称",
            value=coin_info.get('name', 'Unknown'),
            inline=True
        )
        embed.add_field(
            name="🆔 CoinGecko ID",
            value=f"`{coin_info.get('coingecko_id', 'Unknown')}`",
            inline=True
        )
        embed.add_field(
            name="🏷️ Base Symbol",
            value=f"`{coin_info.get('base_symbol', 'Unknown').upper()}`",
            inline=True
        )
        
        # 市值排名
        rank = coin_info.get('market_cap_rank')
        if pd.notna(rank) and rank is not None:
            embed.add_field(
                name="🏆 市值排名",
                value=f"#{int(rank)}",
                inline=True
            )
        else:
            embed.add_field(
                name="🏆 市值排名",
                value="N/A",
                inline=True
            )
        
        # 市场数据
        embed.add_field(
            name="💰 市值 (MV)",
            value=f"`{format_number(coin_info.get('market_cap'))}`",
            inline=True
        )
        embed.add_field(
            name="💰 完全稀释估值 (FDV)",
            value=f"`{format_number(coin_info.get('fdv'))}`",
            inline=True
        )
        embed.add_field(
            name="💰 24h交易量",
            value=f"`{format_number(coin_info.get('volume_24h'))}`",
            inline=True
        )
        
        # 24h涨跌幅
        price_change = coin_info.get('price_change_24h')
        if pd.notna(price_change) and price_change is not None:
            try:
                change = float(price_change)
                emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                embed.add_field(
                    name="📊 24h涨跌幅",
                    value=f"{emoji} `{change:.2f}%`",
                    inline=True
                )
            except:
                pass
        
        # 板块分类
        if categories:
            categories_text = "\n".join([f"{i}. {cat}" for i, cat in enumerate(categories[:10], 1)])
            if len(categories) > 10:
                categories_text += f"\n... 还有 {len(categories) - 10} 个板块"
            embed.add_field(
                name="🏢 板块分类",
                value=categories_text,
                inline=False
            )
        else:
            embed.add_field(
                name="🏢 板块分类",
                value="⚠️ 暂无板块分类数据",
                inline=False
            )
        
        # 数据来源和时间
        embed.add_field(
            name="⚡ 数据来源",
            value="本地映射表",
            inline=True
        )
        if last_updated != 'N/A':
            embed.add_field(
                name="🕒 更新时间",
                value=last_updated,
                inline=True
            )
        
        embed.add_field(
            name="💡 再次查询",
            value=f"`/ticker {ticker}`",
            inline=True
        )
        
        embed.set_footer(
            text="TaoTrader Bot | 数据仅供参考，投资需谨慎",
            icon_url="https://cdn.discordapp.com/emojis/1234567890123456789.png"
        )
        embed.timestamp = discord.utils.utcnow()
        
        if not interaction.response.is_done():
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.followup.send(embed=embed)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ 查询出错",
            description=f"```{str(e)}```",
            color=0xff0000
        )
        error_embed.add_field(
            name="💡 解决方案",
            value="请稍后重试或联系管理员",
            inline=False
        )
        
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=error_embed)
            else:
                await interaction.followup.send(embed=error_embed)
        except:
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ 查询出错: {str(e)}\n\n💡 请稍后重试或联系管理员")
                else:
                    await interaction.followup.send(f"❌ 查询出错: {str(e)}\n\n💡 请稍后重试或联系管理员")
            except:
                # 最后尝试发送到频道
                await interaction.channel.send(f"❌ 查询出错: {str(e)}\n\n💡 请稍后重试或联系管理员")
