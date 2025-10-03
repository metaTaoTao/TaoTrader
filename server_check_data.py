#!/usr/bin/env python3
import os
import pickle
import pandas as pd

print("=== 服务器数据文件检查 ===")
print(f"当前工作目录: {os.getcwd()}")

# 检查output目录
output_dir = "output"
if os.path.exists(output_dir):
    print(f"✅ output目录存在: {output_dir}")
    files = os.listdir(output_dir)
    print(f"output目录内容: {files}")
else:
    print(f"❌ output目录不存在: {output_dir}")

print("\n=== 检查各时间周期数据文件 ===")
for timeframe in ['15m', '1h', '4h', '1d']:
    file_path = f'output/scores_{timeframe}.pkl'
    print(f"\n检查 {timeframe}:")
    print(f"  文件路径: {file_path}")
    
    if os.path.exists(file_path):
        print(f"  ✅ 文件存在")
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            if isinstance(data, dict):
                print(f"  - 数据类型: 字典")
                print(f"  - 时间戳: {data.get('timestamp', 'N/A')}")
                df = data['data']
            else:
                print(f"  - 数据类型: DataFrame")
                df = data
            
            print(f"  - 数据形状: {df.shape}")
            if not df.empty:
                top3 = df.nlargest(3, 'final_score')['symbol'].tolist()
                print(f"  - 前3名: {top3}")
            else:
                print(f"  - 数据为空")
                
        except Exception as e:
            print(f"  ❌ 读取错误: {e}")
    else:
        print(f"  ❌ 文件不存在")

print("\n=== 检查DataIO.load函数 ===")
try:
    from utils.file_helper import DataIO
    print("✅ DataIO模块导入成功")
    
    # 测试加载1小时数据
    try:
        data_1h = DataIO.load('scores_1h')
        print("✅ 1小时数据加载成功")
        if isinstance(data_1h, dict):
            print(f"  - 时间戳: {data_1h.get('timestamp', 'N/A')}")
        print(f"  - 数据类型: {type(data_1h)}")
    except Exception as e:
        print(f"❌ 1小时数据加载失败: {e}")
        
    # 测试加载15分钟数据
    try:
        data_15m = DataIO.load('scores_15m')
        print("✅ 15分钟数据加载成功")
        if isinstance(data_15m, dict):
            print(f"  - 时间戳: {data_15m.get('timestamp', 'N/A')}")
        print(f"  - 数据类型: {type(data_15m)}")
    except Exception as e:
        print(f"❌ 15分钟数据加载失败: {e}")
        
except Exception as e:
    print(f"❌ DataIO模块导入失败: {e}")
