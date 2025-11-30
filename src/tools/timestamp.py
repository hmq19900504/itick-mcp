"""
Current Timestamp Tool - 当前时间戳工具
获取当前时间（东八区），支持多种格式输出
"""
from typing import Dict, Any, Optional
from datetime import datetime
import pytz


class TimestampTool:
    """当前时间戳工具 - 获取东八区时间"""
    
    name = "current_timestamp"
    description = """获取当前时间（东八区 UTC+8），支持多种输出格式。

⏰ **时区信息**:
- 时区: 东八区 (UTC+8 / Asia/Shanghai)
- 覆盖地区: 中国大陆、香港、澳门、台湾、新加坡等

📅 **支持格式**:
- datetime: 完整日期时间 (2025-11-30 10:30:00)
- date: 仅日期 (2025-11-30)
- time: 仅时间 (10:30:00)
- timestamp: Unix时间戳 (1732936200)
- readable: 可读中文格式 (2025年11月30日 10:30:00)

💡 **主要用途**:
- 获取当前时间用于时间范围查询
- 记录操作时间戳
- 时间格式转换
- 生成日期参数

📍 **使用建议**:
- 查询K线时用于生成end_date参数
- 记录查询时间
- 计算时间差

💡 **示例查询**:
- "获取当前时间"
- "今天的日期是什么"
- "现在几点了"
"""
    
    parameters = {
        "type": "object",
        "properties": {
            "format": {
                "type": "string",
                "description": "时间输出格式。datetime=完整时间, date=仅日期, time=仅时间, timestamp=Unix时间戳, readable=中文格式",
                "enum": ["datetime", "date", "time", "timestamp", "readable"],
                "default": "datetime"
            }
        },
        "required": []
    }
    
    @staticmethod
    async def run(arguments: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
        """执行工具逻辑"""
        try:
            format_type = arguments.get("format", "datetime")
            
            # 获取东八区时间
            tz = pytz.timezone('Asia/Shanghai')
            now = datetime.now(tz)
            
            # 格式化输出
            if format_type == "datetime":
                result_time = now.strftime("%Y-%m-%d %H:%M:%S")
            elif format_type == "date":
                result_time = now.strftime("%Y-%m-%d")
            elif format_type == "time":
                result_time = now.strftime("%H:%M:%S")
            elif format_type == "timestamp":
                result_time = str(int(now.timestamp()))
            elif format_type == "readable":
                result_time = now.strftime("%Y年%m月%d日 %H:%M:%S")
            else:
                result_time = now.strftime("%Y-%m-%d %H:%M:%S")
            
            # 获取星期
            weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            weekday = weekdays[now.weekday()]
            
            output = f"""## 🕐 当前东八区时间

**时间信息**
- 格式: {format_type}
- 时间: {result_time}
- 星期: {weekday}
- 时区: 东八区 (UTC+8)

**详细信息**
- 完整时间: {now.strftime("%Y-%m-%d %H:%M:%S")}
- Unix时间戳: {int(now.timestamp())}

---
*时间更新于: {now.strftime("%Y-%m-%d %H:%M:%S")}*
"""
            
            return {
                "content": [{
                    "type": "text",
                    "text": output
                }]
            }
            
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"❌ 获取时间戳时发生错误: {str(e)}"
                }],
                "isError": True
            }
