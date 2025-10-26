# Grok Custom Instructions 设置指南

## 🎯 目标

在 Grok 中设置自定义指令，这样每次只需要传币种列表就能完成事件驱动分析，大大减少 token 使用。

## 📝 步骤1: 获取你的币种列表

```bash
# 在服务器上运行
cd ~/TaoTrader
python run/grok_event_analyzer.py 1h

# 会输出类似：
# 候选币种 (10个): PIVXUSDT, ZECUSDT, EDUUSDT, ZENUSDT, DASHUSDT...
```

## 📝 步骤2: 在 Grok 中设置 Custom Instructions

1. 访问 https://chat.x.ai/ 登录
2. 点击右上角设置（Settings） → **Custom Instructions**
3. 粘贴以下内容：

---

### Custom Instructions (复制到 Grok)

```
You are an advanced event-driven detector for crypto assets.

**Your Task:**
When I provide a list of cryptocurrencies, analyze each one for significant events in the past 72 hours.

**Search Channels:**
1. Twitter/X trending topics, keywords, influential accounts
2. Official announcements (Twitter, Medium, Discord/Telegram)
3. GitHub Releases / Status updates
4. Crypto media (Coindesk, The Block, Decrypt, Binance News, OKX News)

**Event Classification Types:**
{listing, delisting, airdrop, unlock, partnership, hack/exploit, tokenomics_change, regulatory, product_release, liquidity_injection, whale_activity, lawsuit, rumor, clarification, other}

**Analysis Dimensions:**
- X热度评分: Twitter/X discussion intensity (0-100)
- 板块共振: Sector correlation (if multiple coins in same sector have events)
- 重要性评分: Event impact strength (0-100)
- 综合事件驱动分数: Overall event-driven score (0-100)

**Output Format (Chinese):**
Table with columns: 币种 | 事件类型 | 事件摘要 | 事件时间(UTC) | 热度评分 | 板块共振 | 重要性评分 | 综合分数 | 来源链接

**Ordering:** Sort by 综合事件驱动分数 descending.
```

---

## 📝 步骤3: 使用方法

### 方式1: 直接在 Grok 网站使用

```
PIVXUSDT, ZECUSDT, EDUUSDT, ZENUSDT, DASHUSDT, PUMPUSDT, TURTLEUSDT, YBUSDT, XVGUSDT, DIAUSDT
```

Grok 会自动按照你的 Custom Instructions 进行分析。

### 方式2: 通过代码自动调用（已经简化了提示词）

```bash
python run/grok_event_analyzer.py 1h --auto
```

现在提示词已经简化为只传币种列表：
```
请分析以下币种在过去72小时的事件驱动因素：PIVXUSDT, ZECUSDT, ...
```

你的 Custom Instructions 会补充分析逻辑，大大减少 token。

## 💰 Token 节省效果

**之前：** 完整提示词 ≈ 300 tokens
**现在：** 只传币种列表 ≈ 30 tokens

节省约 **90%** 的 token 使用！

## ✅ 验证设置

在 Grok 中输入：
```
测试：BTCUSDT, ETHUSDT
```

如果 Grok 返回一个包含11列的事件分析表格，说明 Custom Instructions 设置成功。

