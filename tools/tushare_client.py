#!/usr/bin/env python3
"""
tushare_client.py — TuShare Pro API 统一客户端

零外部依赖（仅用 stdlib + curl），从 .env 读取凭证。

用法：
    from tushare_client import TuShareClient
    client = TuShareClient()
    data = client.query("daily_basic", {"ts_code": "002407.SZ", "trade_date": "20260623"},
                        "ts_code,trade_date,close,pe_ttm,pb,total_mv")
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta


def _load_env():
    """从项目根目录 .env 文件加载环境变量"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


class TuShareClient:
    """TuShare Pro API 客户端"""

    def __init__(self, token=None, api_url=None):
        _load_env()
        self.token = token or os.environ.get("TUSHARE_TOKEN", "")
        self.api_url = (api_url or os.environ.get("TUSHARE_API_URL", "http://api.tushare.pro")).rstrip("/")
        if not self.token:
            raise ValueError("TuShare token 未配置。请在 .env 中设置 TUSHARE_TOKEN")

    def query(self, api_name, params=None, fields=None):
        """
        通用 API 调用，返回 (fields, items) 元组。

        Args:
            api_name: API 名称，如 daily_basic, fina_indicator
            params: 请求参数字典
            fields: 返回字段（逗号分隔字符串）

        Returns:
            dict: {"fields": [...], "items": [...]}

        Raises:
            RuntimeError: API 返回错误
        """
        body = {
            "api_name": api_name,
            "token": self.token,
            "params": params or {},
        }
        if fields:
            body["fields"] = fields

        payload = json.dumps(body, ensure_ascii=False)

        try:
            result = subprocess.run(
                [
                    "curl", "-s", "-X", "POST",
                    f"{self.api_url}/api/pro",
                    "-H", "Content-Type: application/json",
                    "-d", payload,
                ],
                capture_output=True, text=True, timeout=30,
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"TuShare API 请求超时: {api_name}")

        if result.returncode != 0:
            raise RuntimeError(f"curl 失败 (exit {result.returncode}): {result.stderr}")

        try:
            resp = json.loads(result.stdout)
        except json.JSONDecodeError:
            raise RuntimeError(f"TuShare API 返回非 JSON: {result.stdout[:200]}")

        code = resp.get("code", -1)
        if code != 0:
            msg = resp.get("msg", "未知错误")
            raise RuntimeError(f"TuShare API 错误 [{api_name}]: {msg}")

        data = resp.get("data", {})
        return {"fields": data.get("fields", []), "items": data.get("items", [])}

    def _to_dataframe(self, result):
        """将 query() 结果转为 list[dict]"""
        fields = result["fields"]
        return [dict(zip(fields, row)) for row in result["items"]]

    # ------------------------------------------------------------------
    # 高层 API
    # ------------------------------------------------------------------

    def get_daily_basic(self, ts_code, trade_date=None):
        """
        每日指标：PE(TTM)/PB/总市值/流通市值/换手率

        Returns: list[dict]，按日期倒序
        """
        params = {"ts_code": ts_code}
        if trade_date:
            params["trade_date"] = trade_date
        fields = "ts_code,trade_date,close,pe_ttm,pb,total_mv,circ_mv,turnover_rate,dividend_yield,total_share,float_share"
        return self._to_dataframe(self.query("daily_basic", params, fields))

    def get_daily(self, ts_code, start_date=None, end_date=None):
        """
        日线行情

        Returns: list[dict]，按日期倒序
        """
        params = {"ts_code": ts_code}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        fields = "ts_code,trade_date,open,high,low,close,vol,amount,pct_chg"
        return self._to_dataframe(self.query("daily", params, fields))

    def get_fina_indicator(self, ts_code, limit=8):
        """
        财务指标（按报告期）：EPS/ROE/毛利率/净利率/营收同比/净利润同比
        自动去重（同一报告期保留最新一条）

        Returns: list[dict]，按报告期倒序
        """
        params = {"ts_code": ts_code, "limit": limit * 2}  # 多取一些，去重后保证数量
        fields = ("ts_code,end_date,eps,roe,grossprofit_margin,netprofit_margin,"
                  "op_yoy,dt_netprofit_yoy,or_yoy,current_ratio,debt_to_assets")
        rows = self._to_dataframe(self.query("fina_indicator", params, fields))
        # 按 end_date 去重，保留第一条（最新修正版）
        seen = set()
        deduped = []
        for r in rows:
            key = r.get("end_date")
            if key and key not in seen:
                seen.add(key)
                deduped.append(r)
        return deduped[:limit]

    def get_income(self, ts_code, limit=8):
        """
        利润表：营收/净利润/归母净利润/营业成本
        自动去重（同一报告期保留最新一条）

        Returns: list[dict]，按报告期倒序
        """
        params = {"ts_code": ts_code, "limit": limit * 2}
        fields = "ts_code,end_date,revenue,n_income,n_income_attr_p,total_cogs,operate_exp"
        rows = self._to_dataframe(self.query("income", params, fields))
        seen = set()
        deduped = []
        for r in rows:
            key = r.get("end_date")
            if key and key not in seen:
                seen.add(key)
                deduped.append(r)
        return deduped[:limit]

    def get_stock_basic(self, ts_code=None):
        """
        股票列表与基本信息

        Returns: list[dict]
        """
        params = {}
        if ts_code:
            params["ts_code"] = ts_code
        fields = "ts_code,symbol,name,area,industry,list_date,total_share,float_share"
        return self._to_dataframe(self.query("stock_basic", params, fields))

    def get_trade_cal(self, exchange="SSE", start_date=None, end_date=None):
        """
        交易日历

        Returns: list[dict]
        """
        params = {"exchange": exchange}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        fields = "exchange,cal_date,is_open"
        return self._to_dataframe(self.query("trade_cal", params, fields))

    def get_latest_trade_date(self, exchange="SSE"):
        """获取最近一个交易日"""
        today = datetime.now().strftime("%Y%m%d")
        start = (datetime.now() - timedelta(days=10)).strftime("%Y%m%d")
        cal = self.get_trade_cal(exchange, start, today)
        for day in cal:
            if day["is_open"] == 1:
                return day["cal_date"]
        return today


if __name__ == "__main__":
    # 快速连通性测试
    client = TuShareClient()
    print("=" * 60)
    print("TuShare Pro API 连通性测试")
    print("=" * 60)

    # 测试交易日历
    cal = client.get_trade_cal("SSE", "20260620", "20260623")
    print(f"  交易日历: {len(cal)} 条")
    for d in cal:
        status = "开市" if d["is_open"] else "休市"
        print(f"    {d['cal_date']} {status}")

    # 测试 daily_basic
    td = client.get_latest_trade_date()
    print(f"\n  最近交易日: {td}")

    test_code = "002407.SZ"
    basic = client.get_daily_basic(test_code, td)
    if basic:
        b = basic[0]
        print(f"\n  {test_code} 估值快照 ({td}):")
        print(f"    收盘价:   {b.get('close', 'N/A')}")
        print(f"    PE(TTM):  {b.get('pe_ttm', 'N/A')}")
        print(f"    PB:       {b.get('pb', 'N/A')}")
        total_mv = b.get("total_mv", 0)
        if total_mv:
            print(f"    总市值:   {total_mv / 10000:.2f} 亿元")
    print("\n  ✅ API 连通正常")
