#!/usr/bin/env python3
"""南向资金总量追踪工具 — 统计港股通(南向)每日净流入时间序列、区间累计与趋势。
零外部依赖（仅 stdlib）。

为 AI Berkshire 的 southbound-flow skill 提供确定性汇总，避免 LLM 心算。
南向 = 通过港股通从内地流入香港的资金（港股通沪 + 港股通深合计）；
单位一律换算为「人民币亿元」。

数据源：东方财富公开数据中心（无需 token）。
    GET https://datacenter-web.eastmoney.com/api/data/v1/get
    reportName=RPT_MUTUAL_DEAL_HISTORY, filter=(MUTUAL_TYPE="006")
    MUTUAL_TYPE=006 即南向合计（实测 006 = 002 港股通沪 + 004 港股通深）。
    NET_DEAL_AMT 为当日净流入，单位百万元（÷100 得亿元）——已用内部一致性
    交叉验证定标：NET_DEAL_AMT == BUY_AMT - SELL_AMT，且当日成交额 DEAL_AMT
    ≈1584亿、历史累计 ACCUM_DEAL_AMT≈5.45万亿，量级均自洽。

为何不用项目现成的 tushare：.env 指向的自建镜像对 A股接口真实，但对
moneyflow_hsgt(南向) 返回固定 ~543 亿的占位假数据（与东财真实值 5~205 亿的
波动完全不符）；官方 api.tushare.pro 又需积分≥2000 的有效 token。故南向以
东财为真实源。

用法（由 Skill 自动调用）：
    python3 tools/southbound_flow.py flow --days 30
    python3 tools/southbound_flow.py flow --days 100
    python3 tools/southbound_flow.py flow --start 20260101 --end 20260709

需要 Python >= 3.8，零外部依赖。
"""

from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
from datetime import datetime

DEFAULT_DAYS = 30            # 默认展示的交易日数（可 --days 任意放大，如 100）
_NET_TO_YI = 100.0          # NET_DEAL_AMT / BUY / SELL 单位百万元 → 亿元
_HOLD_TO_YI = 1e8           # HOLD_MARKET_CAP 单位元 → 亿元
_SOUTH_TYPE = "006"         # 东财 MUTUAL_TYPE：006=南向合计
_EM_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
_TIMEOUT = 20


# ---------------------------------------------------------------------------
# 通用辅助
# ---------------------------------------------------------------------------

def _to_float(v) -> float | None:
    """东财字段可能为 None/空串，安全转 float。"""
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _yi(v, divisor: float) -> float | None:
    """按 divisor 换算并四舍五入到 2 位（亿元）。"""
    f = _to_float(v)
    return round(f / divisor, 2) if f is not None else None


def _fmt_date(raw) -> str:
    """'2026-07-09 00:00:00' 或 'YYYYMMDD' -> 'YYYY-MM-DD'。"""
    s = str(raw)
    if len(s) >= 10 and s[4:5] == "-":
        return s[:10]
    if len(s) == 8 and s.isdigit():
        return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    return s


def _parse_ymd(v: str, flag: str) -> datetime:
    try:
        return datetime.strptime(v, "%Y%m%d")
    except ValueError as exc:
        raise SystemExit(f"southbound_flow: {flag} 需为 YYYYMMDD，收到 {v!r}") from exc


# ---------------------------------------------------------------------------
# 东财取数：南向合计每日历史
# ---------------------------------------------------------------------------

def _fetch_south(page_size: int) -> list[dict]:
    """拉取南向(006)最近 page_size 个交易日历史，按日期升序返回东财原始字段。"""
    params = {
        "reportName": "RPT_MUTUAL_DEAL_HISTORY",
        "columns": "ALL",
        "source": "WEB",
        "client": "WEB",
        "sortColumns": "TRADE_DATE",
        "sortTypes": "-1",             # 先按日期降序取最近 N，再翻转成升序
        "pageNumber": "1",
        "pageSize": str(max(page_size, 1)),
        "filter": f'(MUTUAL_TYPE="{_SOUTH_TYPE}")',
    }
    # filter 里的 = 和 " 必须百分号编码(%3D/%22)，括号可保留字面——与东财一致
    url = _EM_URL + "?" + urllib.parse.urlencode(params, safe='()')
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 — 网络/解析错误统一带上下文抛出
        raise SystemExit(f"southbound_flow: 东财请求失败 @ {url} — {exc}") from exc
    if not payload.get("success"):
        raise SystemExit(
            f"southbound_flow: 东财返回失败 code={payload.get('code')} "
            f"msg={payload.get('message')!r}"
        )
    data = (payload.get("result") or {}).get("data") or []
    if not data:
        raise SystemExit("southbound_flow: 东财返回空数据（南向 006）")
    data.sort(key=lambda r: str(r.get("TRADE_DATE")))  # 升序
    return data


def _filter_by_range(rows: list[dict], start: str | None, end: str | None,
                     days: int) -> list[dict]:
    """按 --start/--end 或 days 截取。优先级：显式区间 > 最近 days 个交易日。"""
    if start or end:
        s = _parse_ymd(start, "--start") if start else None
        e = _parse_ymd(end, "--end") if end else None
        out = []
        for r in rows:
            d = datetime.strptime(_fmt_date(r.get("TRADE_DATE")), "%Y-%m-%d")
            if s and d < s:
                continue
            if e and d > e:
                continue
            out.append(r)
        return out
    return rows[-days:] if days < len(rows) else rows


# ---------------------------------------------------------------------------
# 子命令：flow —— 南向总量每日净流入 + 区间汇总
# ---------------------------------------------------------------------------

def cmd_flow(start: str | None, end: str | None, days: int | None) -> None:
    n = days if days and days > 0 else DEFAULT_DAYS
    # 区间模式多拉一些覆盖 start~end；否则拉 n + 冗余
    page = 5000 if (start or end) else max(n, 1) + 10
    rows = _filter_by_range(_fetch_south(page), start, end, n)
    if not rows:
        raise SystemExit("southbound_flow: 指定区间内无南向数据")

    daily = []
    for r in rows:
        daily.append({
            "日期": _fmt_date(r.get("TRADE_DATE")),
            "南向净流入_亿": _yi(r.get("NET_DEAL_AMT"), _NET_TO_YI),
            "买入_亿": _yi(r.get("BUY_AMT"), _NET_TO_YI),
            "卖出_亿": _yi(r.get("SELL_AMT"), _NET_TO_YI),
            "南向持股市值_亿": _yi(r.get("HOLD_MARKET_CAP"), _HOLD_TO_YI),
        })

    net_vals = [d["南向净流入_亿"] for d in daily if d["南向净流入_亿"] is not None]
    summary: dict = {"交易日数": len(daily)}
    if net_vals:
        cum = round(sum(net_vals), 2)
        hi = max(daily, key=lambda d: d["南向净流入_亿"] if d["南向净流入_亿"] is not None else -1e18)
        lo = min(daily, key=lambda d: d["南向净流入_亿"] if d["南向净流入_亿"] is not None else 1e18)
        last_in = net_vals[-1] >= 0
        streak = 0
        for v in reversed(net_vals):
            if (v >= 0) == last_in:
                streak += 1
            else:
                break
        summary.update({
            "区间累计净流入_亿": cum,
            "日均净流入_亿": round(cum / len(net_vals), 2),
            "净流入天数": sum(1 for v in net_vals if v > 0),
            "净流出天数": sum(1 for v in net_vals if v < 0),
            "最高流入日": {"日期": hi["日期"], "净流入_亿": hi["南向净流入_亿"]},
            "最低日": {"日期": lo["日期"], "净流入_亿": lo["南向净流入_亿"]},
            "近端连续方向": "净流入" if last_in else "净流出",
            "连续天数": streak,
        })

    # 期初→期末持股市值变化（仅用有值的首末日，最新一日东财偶尔缺市值）
    holds = [(d["日期"], d["南向持股市值_亿"]) for d in daily if d["南向持股市值_亿"]]
    if len(holds) >= 2:
        summary["持股市值变化"] = {
            "期初": {"日期": holds[0][0], "市值_亿": holds[0][1]},
            "期末": {"日期": holds[-1][0], "市值_亿": holds[-1][1]},
            "变化_亿": round(holds[-1][1] - holds[0][1], 2),
        }

    result = {
        "口径": "南向资金 = 港股通(沪+深)每日净流入；单位人民币亿元",
        "数据源": "东方财富 RPT_MUTUAL_DEAL_HISTORY (MUTUAL_TYPE=006)",
        "区间": f"{daily[0]['日期']} ~ {daily[-1]['日期']}",
        "总览": summary,
        "每日明细": daily,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="南向资金总量追踪（港股通净流入时间序列，数据源：东方财富）"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_f = sub.add_parser("flow", help="南向每日净流入 + 区间累计/趋势")
    p_f.add_argument("--days", type=int,
                     help=f"交易日数（默认 {DEFAULT_DAYS}，无上限，如 --days 100）")
    p_f.add_argument("--start", help="起始日 YYYYMMDD（与 --end 组合，优先于 --days）")
    p_f.add_argument("--end", help="结束日 YYYYMMDD")

    args = parser.parse_args()
    if args.command == "flow":
        cmd_flow(args.start, args.end, args.days)


if __name__ == "__main__":
    main()
