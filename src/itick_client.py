"""
iTick API Client
封装 iTick API 调用，提供统一的接口和错误处理
"""
import httpx
from typing import Dict, Any, Optional, List
from .config import settings


class ItickAPIError(Exception):
    """iTick API 错误基类"""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class ItickClient:
    """iTick API 客户端"""
    
    # 错误码映射
    ERROR_MESSAGES = {
        "E001": "目标产品不存在，请检查股票代码是否正确",
        "E002": "API 认证失败，请检查 API Key 是否有效",
        "E003": "超过最大订阅数量限制，请联系客服升级套餐"
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化客户端
        
        Args:
            api_key: iTick API Key，如果不提供则从配置中读取
        """
        self.api_key = api_key or settings.itick_api_key
        self.base_url = settings.itick_api_base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求到 iTick API
        
        Args:
            method: HTTP 方法 (GET/POST)
            endpoint: API 端点路径
            params: 查询参数
            headers: 自定义请求头
            
        Returns:
            API 响应数据
            
        Raises:
            ItickAPIError: API 返回错误时抛出
        """
        url = f"{self.base_url}{endpoint}"
        
        # 构建请求头
        request_headers = {
            "accept": "application/json",
            "token": self.api_key
        }
        if headers:
            request_headers.update(headers)
        
        try:
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                headers=request_headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            # 检查 iTick API 错误码
            if data.get("code") != 0:
                error_code = data.get("msg", "UNKNOWN")
                error_message = self.ERROR_MESSAGES.get(
                    error_code, 
                    data.get("msg", "未知错误")
                )
                raise ItickAPIError(str(error_code), str(error_message))
            
            return data.get("data", {})
            
        except httpx.HTTPStatusError as e:
            raise ItickAPIError("HTTP_ERROR", f"HTTP 请求失败: {e.response.status_code}")
        except httpx.RequestError as e:
            raise ItickAPIError("NETWORK_ERROR", f"网络请求失败: {str(e)}")
    
    async def get_stock_quote(self, region: str, code: str) -> Dict[str, Any]:
        """
        获取股票实时报价
        
        Args:
            region: 市场代码 (HK/US/SH/SZ等)
            code: 股票代码
            
        Returns:
            实时报价数据
        """
        return await self._request(
            "GET",
            "/stock/quote",
            params={"region": region, "code": code}
        )
    
    async def get_stock_kline(
        self, 
        region: str, 
        code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "day",
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        获取股票K线数据
        
        Args:
            region: 市场代码
            code: 股票代码
            start_date: 起始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            period: 周期 (1min/5min/60min/day/week/month)
            limit: 返回数据条数限制
            
        Returns:
            K线数据列表
        """
        # 周期到 kType 的映射 (基于测试结果)
        period_to_ktype = {
            "1min": 1,
            "5min": 5,
            "60min": 8,
            "day": 2,
            "week": 3,
            "month": 4
        }
        
        ktype = period_to_ktype.get(period, 2)  # 默认日线
        
        params = {
            "region": region,
            "code": code,
            "kType": ktype
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if limit:
            params["limit"] = limit
        
        result = await self._request("GET", "/stock/kline", params=params)
        # K线数据应该是数组，如果不是则返回空数组
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "data" in result:
            return result.get("data", [])
        return []
    
    async def get_stock_tick(self, region: str, code: str) -> Dict[str, Any]:
        """
        获取股票Tick数据
        
        Args:
            region: 市场代码
            code: 股票代码
            
        Returns:
            Tick数据
        """
        return await self._request(
            "GET",
            "/stock/tick",
            params={"region": region, "code": code}
        )
    
    async def get_stock_depth(self, region: str, code: str) -> Dict[str, Any]:
        """
        获取股票盘口深度
        
        Args:
            region: 市场代码
            code: 股票代码
            
        Returns:
            盘口深度数据
        """
        return await self._request(
            "GET",
            "/stock/depth",
            params={"region": region, "code": code}
        )
    
    # ============ 指数 API ============
    
    async def get_index_quote(self, code: str, region: str = "GB") -> Dict[str, Any]:
        """
        获取指数实时报价
        
        注意：iTick 的指数 API 统一使用 region='GB'，无论是A股、港股还是美股指数
        
        Args:
            code: 指数代码（如：SPX, HSI, 000001, 399006）
            region: 市场代码（默认'GB'，指数API统一使用此值）
            
        Returns:
            实时报价数据
            
        Examples:
            标普500: code='SPX', region='GB'
            恒生指数: code='HSI', region='GB'
            上证指数: code='000001', region='GB'
            创业板指: code='399006', region='GB'
        """
        return await self._request(
            "GET",
            "/indices/quote",
            params={"region": region, "code": code}
        )
    
    async def get_index_kline(
        self,
        code: str,
        region: str = "GB",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "day",
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        获取指数K线数据
        
        注意：iTick 的指数 API 统一使用 region='GB'
        
        Args:
            code: 指数代码
            region: 市场代码（默认'GB'）
            start_date: 起始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            period: 周期 (1min/5min/60min/day/week/month)
            limit: 返回数据条数限制
            
        Returns:
            K线数据列表
        """
        # 周期到 kType 的映射
        period_to_ktype = {
            "1min": 1,
            "5min": 5,
            "60min": 8,
            "day": 2,
            "week": 3,
            "month": 4
        }
        
        ktype = period_to_ktype.get(period, 2)
        
        params = {
            "region": region,
            "code": code,
            "kType": ktype
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if limit:
            params["limit"] = limit
        
        result = await self._request("GET", "/indices/kline", params=params)
        # K线数据应该是数组
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "data" in result:
            return result.get("data", [])
        return []
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()


# 全局客户端实例
_client: Optional[ItickClient] = None


def get_client(api_key: Optional[str] = None) -> ItickClient:
    """
    获取全局 iTick 客户端实例
    
    Args:
        api_key: 可选的 API Key，用于覆盖默认配置
        
    Returns:
        ItickClient 实例
    """
    global _client
    if _client is None or api_key:
        _client = ItickClient(api_key)
    return _client
