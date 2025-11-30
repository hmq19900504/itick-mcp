# iTick API 市场支持说明

## 📊 测试结果总结 (2025-11-30)

### ✅ 支持的市场和指数

**A股市场（完全支持）**
- ✅ 上证指数 (`SH.000001`)
- ✅ 深证成指 (`SZ.399001`)  
- ✅ 创业板指 (`SZ.399006`)
- ✅ 沪深300 (`SH.000300`)
- ✅ 中证500 (`SH.000905`)
- ✅ 科创50 (`SH.000688`)

### ❌ 不支持/需要付费订阅的市场

**港股市场**
- ❌ 恒生指数 (`HK.HSI`) - API返回空数据
- ❌ 恒生科技 (`HK.HSTECH`) - API返回空数据

**美股市场**
- ❌ 纳斯达克 (`US.IXIC`, `US.NDX`) - API返回空数据
- ❌ 标普500 (`US.SPX`, `US..SPX`) - API返回空数据  
- ❌ 道琼斯 (`US.DJI`, `US..DJI`) - API返回空数据

## 🔍 技术原因

### 1. API订阅限制
iTick API采用订阅制，不同套餐提供不同市场的数据访问权限：
- **基础版**：仅支持A股市场（沪深）
- **专业版**：可能包含港股数据
- **旗舰版**：包含全球市场数据

当前使用的API Key可能是**基础版**，只能访问A股数据。

### 2. 数据返回格式
- 支持的市场：返回完整的JSON数据对象
- 不支持的市场：返回 `None` 或空对象 `{}`

### 3. 错误处理
原代码在遇到 `None` 时会抛出异常：
```python
# 错误代码
latest_price = quote_data.get('ld', 0)  # quote_data为None时报错
```

## ✅ 已实施的修复

### 修复1: 空数据检查
在 `src/tools/index_analysis.py` 中添加了数据验证：

```python
quote_data = await client.get_stock_quote(str(region), str(code))

# 检查quote_data是否为None或空
if not quote_data:
    raise Exception(f"API返回空数据，可能是指数代码不正确或未订阅该市场")
```

### 修复2: 更友好的错误提示
现在会显示明确的错误信息，而不是 `'NoneType' object has no attribute 'get'`

## 📝 使用建议

### 对于普通用户
1. **仅使用A股指数进行分析**，这些是完全支持的：
   ```python
   {
       "indices": [
           {"region": "SH", "code": "000001", "name": "上证指数"},
           {"region": "SZ", "code": "399006", "name": "创业板指"},
           {"region": "SH", "code": "000300", "name": "沪深300"}
       ]
   }
   ```

2. **避免使用港股和美股指数**，除非升级API套餐

### 对于需要港股/美股数据的用户
1. **联系iTick客服**升级API订阅套餐
2. 了解不同套餐的价格和支持的市场范围
3. 升级后更新 `.env` 中的 `ITICK_API_KEY`

### 查询API订阅信息
访问 iTick 官网或联系客服：
- 官网: https://itick.org
- 查看当前套餐包含的市场范围
- 了解升级选项

## 🔧 代码改进建议

### 建议1: 添加市场可用性检查
在工具描述中明确说明支持的市场：

```python
description = """
⚠️ **市场支持**:
- ✅ A股市场: 完全支持（沪深所有指数）
- ❓ 港股市场: 需要专业版API订阅
- ❓ 美股市场: 需要旗舰版API订阅

当前API Key订阅级别可能仅支持A股数据。
"""
```

### 建议2: 预检查机制
在批量分析前先检查哪些市场可用：

```python
async def check_market_availability(client):
    """检查哪些市场可用"""
    test_codes = {
        "A股": ("SH", "000001"),
        "港股": ("HK", "HSI"),
        "美股": ("US", "IXIC")
    }
    
    available = []
    for market, (region, code) in test_codes.items():
        try:
            data = await client.get_stock_quote(region, code)
            if data:
                available.append(market)
        except:
            pass
    
    return available
```

## 📊 当前工作状态

- ✅ A股指数分析：完全可用
- ✅ 错误处理：已改进，不会崩溃
- ✅ 错误提示：更加明确
- ⚠️ 港股/美股：需要升级API订阅

## 🚀 下一步行动

1. **短期**：继续使用A股指数进行分析
2. **中期**：评估是否需要升级API订阅
3. **长期**：考虑支持多个数据源（备用方案）
