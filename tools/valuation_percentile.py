#!/usr/bin/env python3
"""历史估值分位工具 — 以「周」为单位计算个股历史 PE/PB 时间序列，并定位
当前值与远期预估值在历史分布中的百分位。零外部依赖（仅 stdlib）。

为 AI Berkshire 的 valuation-percentile skill 提供确定性计算，避免 LLM 心算。

回溯窗口默认 2 年（约 ~104 个周样本），外部可通过 --years/--start 指定更长年限、
无上限。分位是「相对该股回溯窗口内自身」的相对位置，不等于跨牛熊周期的绝对贵贱。

用法（由 Skill 自动调用）：
    # A股端到端（自动拉 TuShare 逐日 pe_ttm/pb → 周频 → 分位）
    python3 tools/valuation_percentile.py ashare 600519 --growth 12
    python3 tools/valuation_percentile.py ashare 600519 --forward-eps 78.5

    # 美股/港股：先取 Yahoo 周线价
    python3 tools/valuation_percentile.py weekly-prices 0700.HK
    python3 tools/valuation_percentile.py weekly-prices NVDA --years 2

    # 美股/港股：用周线价 + 历史季度 TTM EPS 组装 PE 序列并定位
    python3 tools/valuation_percentile.py pe-series \
        --prices prices.json \
        --eps '[{"date":"2024-03-31","eps_ttm":3.2}, ...]' \
        --forward-eps 5.1

    # 通用分位积木：给定历史数值序列，定位当前值(+远期值)
    python3 tools/valuation_percentile.py percentile \
        --series '[10,20,30,40]' --current 25 --forward 18

配置（.env 或环境变量，仅 ashare 需要）：
    TUSHARE_TOKEN / TUSHARE_API_URL  —— 复用 tushare_fetcher 的配置

需要 Python >= 3.8，零外部依赖。
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date, datetime, timedelta

# 复用同目录 tushare_fetcher 的 A股取数能力（_api_call/normalize_code/_load_env）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DEFAULT_LOOKBACK_YEARS = 2  # 默认回溯窗口；外部可通过 --years/--start 指定更长年限

# 分位区间划分（统一口径）：低分位=便宜，高分位=贵
_BANDS = [
    (20, "低估区"),
    (40, "偏低"),
    (60, "合理"),
    (80, "偏高"),
    (101, "高估区"),
]


# ---------------------------------------------------------------------------
# 分位与分布统计（纯 stdlib，无 numpy）
# ---------------------------------------------------------------------------

def percentile_rank(values: list[float], x: float) -> float:
    """x 在 values 中的百分位（0–100）。

    采用中点法处理并列：pct = (小于 x 的个数 + 0.5·等于 x 的个数) / N。
    含义：数值越小分位越低（越便宜）。空序列返回 -1 表示无法计算。
    """
    n = len(values)
    if n == 0:
        return -1.0
    below = sum(1 for v in values if v < x)
    equal = sum(1 for v in values if v == x)
    return round((below + 0.5 * equal) / n * 100, 1)


def quantile(sorted_values: list[float], q: float) -> float | None:
    """线性插值分位数（q∈[0,1]），口径同 numpy 默认 'linear'。"""
    n = len(sorted_values)
    if n == 0:
        return None
    if n == 1:
        return sorted_values[0]
    idx = q * (n - 1)
    lo = int(idx)
    hi = min(lo + 1, n - 1)
    frac = idx - lo
    return round(sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * frac, 4)


def distribution_stats(values: list[float]) -> dict:
    """历史分布关键分位：min/p10/p25/median/p75/p90/max + 样本数。"""
    if not values:
        return {"样本数": 0}
    s = sorted(values)
    return {
        "样本数": len(s),
        "min": round(s[0], 4),
        "p10": quantile(s, 0.10),
        "p25": quantile(s, 0.25),
        "median": quantile(s, 0.50),
        "p75": quantile(s, 0.75),
        "p90": quantile(s, 0.90),
        "max": round(s[-1], 4),
    }


def band_of(pct: float) -> str:
    """百分位 → 区间标签。pct<0（无法计算）返回『数据不足』。"""
    if pct < 0:
        return "数据不足"
    for upper, label in _BANDS:
        if pct < upper:
            return label
    return "高估区"


def locate(values: list[float], x: float | None, label: str) -> dict | None:
    """把某个观测值 x 定位到历史分布 values 中：返回值/百分位/区间。"""
    if x is None:
        return None
    pct = percentile_rank(values, x)
    return {"指标": label, "当前值": round(x, 4), "历史百分位": pct, "所处区间": band_of(pct)}


# ---------------------------------------------------------------------------
# 日期与周频重采样
# ---------------------------------------------------------------------------

def _resolve_range(start: str | None, years: int | None) -> tuple[str, str]:
    """解析回溯区间，返回 (start_date, end_date)。

    优先级：显式 --start > --years > 默认 DEFAULT_LOOKBACK_YEARS 年。
    2 年只是默认值，外部指定更长年限时按指定的来，不设上限。
    """
    today = date.today()
    if start:
        try:
            s = datetime.strptime(start, "%Y%m%d").date()
        except ValueError as exc:
            raise SystemExit(f"valuation_percentile: --start 需为 YYYYMMDD，收到 {start!r}") from exc
    else:
        yrs = years if years and years > 0 else DEFAULT_LOOKBACK_YEARS
        s = today - timedelta(days=365 * yrs)
    return s.strftime("%Y%m%d"), today.strftime("%Y%m%d")


def _weekly_resample(rows: list[dict], date_key: str, date_fmt: str) -> list[dict]:
    """按 ISO (year, week) 分组，每周取交易日最大（最后一个交易日）的那行。

    rows 已含所需字段；返回按日期升序的周频行列表。
    """
    buckets: dict[tuple[int, int], dict] = {}
    for r in rows:
        raw = r.get(date_key)
        if not raw:
            continue
        try:
            d = datetime.strptime(str(raw), date_fmt).date()
        except ValueError:
            continue
        iso = d.isocalendar()
        key = (iso[0], iso[1])
        prev = buckets.get(key)
        if prev is None or d > prev["_d"]:
            buckets[key] = {**r, "_d": d}
    weekly = sorted(buckets.values(), key=lambda x: x["_d"])
    for w in weekly:
        w.pop("_d", None)
    return weekly


# ---------------------------------------------------------------------------
# A股：TuShare daily_basic 逐日 pe_ttm/pb → 周频 → 分位
# ---------------------------------------------------------------------------

def _fetch_daily_basic(code: str, start: str, end: str) -> list[dict]:
    """按年分段拉取 daily_basic，规避单次返回条数上限；合并去重。"""
    from tushare_fetcher import _api_call  # 延迟导入，避免无 token 时 percentile 也报错

    start_y = int(start[:4])
    end_y = int(end[:4])
    seen: dict[str, dict] = {}
    for y in range(start_y, end_y + 1):
        seg_start = max(start, f"{y}0101")
        seg_end = min(end, f"{y}1231")
        rows = _api_call(
            "daily_basic",
            {"ts_code": code, "start_date": seg_start, "end_date": seg_end},
            "ts_code,trade_date,close,pe_ttm,pb",
        )
        for r in rows:
            td = r.get("trade_date")
            if td:
                seen[td] = r  # 同一交易日去重
    return list(seen.values())


def cmd_ashare(code: str, start: str | None, years: int | None, growth: float | None,
               forward_eps: float | None, forward_bvps: float | None) -> None:
    from tushare_fetcher import normalize_code

    code = normalize_code(code)
    start_date, end_date = _resolve_range(start, years)

    daily = _fetch_daily_basic(code, start_date, end_date)
    if not daily:
        raise SystemExit(f"valuation_percentile: {code} 在 {start_date}–{end_date} 无 daily_basic 数据")

    weekly = _weekly_resample(daily, "trade_date", "%Y%m%d")

    def _num(v):
        return float(v) if isinstance(v, (int, float)) else None

    # PE 分布剔除亏损期（pe_ttm<=0/空）；PB 剔除<=0/空。同时保留逐周历史序列。
    pe_series, pe_dropped = [], 0
    pb_series, pb_dropped = [], 0
    weekly_series = []  # 供报告呈现「历史 PE 数据」
    for w in weekly:
        pe = _num(w.get("pe_ttm"))
        pb = _num(w.get("pb"))
        weekly_series.append({
            "date": w.get("trade_date"),
            "pe_ttm": round(pe, 4) if pe is not None else None,
            "pb": round(pb, 4) if pb is not None else None,
        })
        if pe is not None and pe > 0:
            pe_series.append(pe)
        else:
            pe_dropped += 1
        if pb is not None and pb > 0:
            pb_series.append(pb)
        else:
            pb_dropped += 1

    latest = weekly[-1]
    cur_pe = _num(latest.get("pe_ttm"))
    cur_pb = _num(latest.get("pb"))
    cur_close = _num(latest.get("close"))

    result: dict = {
        "code": code,
        "market": "A股",
        "数据区间": {"start": start_date, "end": end_date, "trade_date_last": latest.get("trade_date")},
        "样本": {"周样本数": len(weekly),
                 "PE有效周数": len(pe_series), "PE剔除亏损周数": pe_dropped,
                 "PB有效周数": len(pb_series), "PB剔除周数": pb_dropped},
        "PE_TTM": {
            "当前": locate(pe_series, cur_pe if (cur_pe and cur_pe > 0) else None, "当前PE_TTM"),
            "历史分布": distribution_stats(pe_series),
        },
        "PB": {
            "当前": locate(pb_series, cur_pb if (cur_pb and cur_pb > 0) else None, "当前PB"),
            "历史分布": distribution_stats(pb_series),
        },
    }

    # 远期 PE：forward_pe = current_pe/(1+g) 或 close/forward_eps
    fwd_pe = None
    fwd_note = None
    if forward_eps is not None:
        if forward_eps > 0 and cur_close:
            fwd_pe = cur_close / forward_eps
            fwd_note = f"close({cur_close})/forward_eps({forward_eps})"
    elif growth is not None and cur_pe and cur_pe > 0:
        g = growth / 100.0
        if (1 + g) > 0:
            fwd_pe = cur_pe / (1 + g)
            fwd_note = f"current_pe({round(cur_pe,2)})/(1+{growth}%)"
    if fwd_pe is not None:
        loc = locate(pe_series, fwd_pe, "远期PE")
        loc["计算方式"] = fwd_note
        loc["说明"] = "远期PE基于预估盈利，对照的是历史TTM(trailing)分布，属近似定位"
        result["远期PE"] = loc
        if cur_pe and cur_pe > 0:
            result["PE_TTM"]["当前"] = result["PE_TTM"]["当前"] or {}
            result["PE_TTM"]["当前"]["隐含EPS_TTM"] = (
                round(cur_close / cur_pe, 4) if cur_close else None
            )

    # 远期 PB：需外部给出远期每股净资产(BVPS)，否则不计算（避免臆造假设）
    if forward_bvps is not None and forward_bvps > 0 and cur_close:
        fwd_pb = cur_close / forward_bvps
        loc = locate(pb_series, fwd_pb, "远期PB")
        loc["计算方式"] = f"close({cur_close})/forward_bvps({forward_bvps})"
        loc["说明"] = "远期PB基于预估每股净资产，对照历史PB分布，属近似定位"
        result["远期PB"] = loc
    else:
        result["远期PB"] = {"指标": "远期PB", "值": None,
                            "说明": "未计算：需 --forward-bvps 提供远期每股净资产；不臆造"}

    result["周频历史序列"] = weekly_series  # 报告可据此呈现历史 PE/PB 数据/走势

    print(json.dumps(result, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# 美股/港股：Yahoo 周线价（模式复用 stock_screener.fetch_prices_curl）
# ---------------------------------------------------------------------------

def _yahoo_weekly(ticker: str, years: int) -> list[dict]:
    end_ts = int(datetime.now().timestamp())
    start_ts = int((datetime.now() - timedelta(days=365 * years + 7)).timestamp())
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        f"?period1={start_ts}&period2={end_ts}&interval=1wk"
    )
    try:
        res = subprocess.run(
            ["curl", "-s", "-H", "User-Agent: Mozilla/5.0", url],
            capture_output=True, text=True, timeout=20,
        )
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"valuation_percentile: 拉取 {ticker} 周线失败 — {exc}") from exc
    if res.returncode != 0:
        raise SystemExit(f"valuation_percentile: curl 拉取 {ticker} 返回码 {res.returncode}")
    try:
        data = json.loads(res.stdout)
        chart = data.get("chart", {}).get("result", [{}])[0]
        ts = chart.get("timestamp", []) or []
        closes = chart.get("indicators", {}).get("quote", [{}])[0].get("close", []) or []
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"valuation_percentile: 解析 {ticker} 周线 JSON 失败 — {exc}") from exc
    rows = []
    for i, t in enumerate(ts):
        c = closes[i] if i < len(closes) else None
        if c:
            rows.append({"date": datetime.fromtimestamp(t).strftime("%Y-%m-%d"),
                         "close": round(float(c), 4)})
    return rows


def cmd_weekly_prices(ticker: str, years: int) -> None:
    rows = _yahoo_weekly(ticker, years)
    if not rows:
        raise SystemExit(f"valuation_percentile: {ticker} 无周线数据")
    print(json.dumps({"ticker": ticker, "years": years, "count": len(rows),
                      "prices": rows}, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# 美股/港股：周线价 + 历史季度 TTM EPS → 逐周 PE → 分位
# ---------------------------------------------------------------------------

def _load_json_arg(raw: str, what: str):
    """参数既可是内联 JSON，也可是文件路径。"""
    if os.path.exists(raw):
        with open(raw, encoding="utf-8") as f:
            return json.load(f)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"valuation_percentile: {what} 既非有效 JSON 也非存在的文件 — {raw!r}") from exc


def _eps_asof(eps_sorted: list[tuple[str, float]], d: str) -> float | None:
    """前向填充：取 date<=d 的最近一期 TTM EPS。"""
    chosen = None
    for edate, eps in eps_sorted:
        if edate <= d:
            chosen = eps
        else:
            break
    return chosen


def cmd_pe_series(prices_arg: str, eps_arg: str, current_price: float | None,
                  forward_eps: float | None) -> None:
    prices_raw = _load_json_arg(prices_arg, "--prices")
    prices = prices_raw.get("prices") if isinstance(prices_raw, dict) else prices_raw
    eps_raw = _load_json_arg(eps_arg, "--eps")

    eps_sorted = sorted(
        ((str(e["date"]), float(e["eps_ttm"])) for e in eps_raw if e.get("eps_ttm") is not None),
        key=lambda x: x[0],
    )
    if not eps_sorted:
        raise SystemExit("valuation_percentile: --eps 为空或缺少 eps_ttm 字段")

    pe_series = []
    matched = 0
    for p in prices:
        d, c = str(p["date"]), float(p["close"])
        eps = _eps_asof(eps_sorted, d)
        if eps and eps > 0:
            pe_series.append(c / eps)
            matched += 1
    if not pe_series:
        raise SystemExit("valuation_percentile: 无法组装 PE 序列（EPS 全为空/负或日期不匹配）")

    last_price = float(prices[-1]["close"])
    last_eps = _eps_asof(eps_sorted, str(prices[-1]["date"]))
    cur_price = current_price if current_price is not None else last_price
    cur_pe = (cur_price / last_eps) if (last_eps and last_eps > 0) else None

    result = {
        "market": "美股/港股",
        "样本": {"周样本数": len(prices), "PE有效周数": matched},
        "PE_TTM": {
            "当前": locate(pe_series, cur_pe, "当前PE_TTM"),
            "历史分布": distribution_stats(pe_series),
        },
        "数据局限": "历史 TTM EPS 由外部(web/财报)补入，可能有缺口/口径差异，可靠性低于A股tushare口径",
    }
    if forward_eps is not None and forward_eps > 0:
        fwd_pe = cur_price / forward_eps
        loc = locate(pe_series, fwd_pe, "远期PE")
        loc["计算方式"] = f"current_price({cur_price})/forward_eps({forward_eps})"
        loc["说明"] = "远期PE基于预估盈利，对照历史trailing分布，属近似定位"
        result["远期PE"] = loc
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# 通用分位积木
# ---------------------------------------------------------------------------

def cmd_percentile(series_arg: str, current: float, forward: float | None) -> None:
    raw = _load_json_arg(series_arg, "--series")
    values = [float(v) for v in raw if isinstance(v, (int, float))]
    if not values:
        raise SystemExit("valuation_percentile: --series 为空")
    result = {
        "样本数": len(values),
        "历史分布": distribution_stats(values),
        "当前": locate(values, current, "当前值"),
    }
    if forward is not None:
        result["远期"] = locate(values, forward, "远期值")
    print(json.dumps(result, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="历史估值分位工具（PE/PB 周频分位）")
    sub = parser.add_subparsers(dest="command", required=True)

    p_a = sub.add_parser("ashare", help="A股端到端：TuShare 逐日→周频→PE/PB分位")
    p_a.add_argument("code", help="股票代码，如 600519 或 600519.SH")
    p_a.add_argument("--start", help="起始日 YYYYMMDD（优先于 --years）")
    p_a.add_argument("--years", type=int,
                     help=f"回溯年数（默认 {DEFAULT_LOOKBACK_YEARS}，无上限）")
    p_a.add_argument("--growth", type=float, help="未来一年净利/EPS一致预期增速(%%)，用于远期PE")
    p_a.add_argument("--forward-eps", type=float, dest="forward_eps",
                     help="远期每股收益（优先于 --growth）")
    p_a.add_argument("--forward-bvps", type=float, dest="forward_bvps",
                     help="远期每股净资产，用于远期PB（缺省则远期PB不计算）")

    p_w = sub.add_parser("weekly-prices", help="美股/港股 Yahoo 周线价")
    p_w.add_argument("ticker", help="代码，如 NVDA 或 0700.HK")
    p_w.add_argument("--years", type=int, default=DEFAULT_LOOKBACK_YEARS,
                     help=f"回溯年数（默认 {DEFAULT_LOOKBACK_YEARS}，无上限）")

    p_p = sub.add_parser("pe-series", help="周线价+历史TTM EPS 组装PE序列并定位")
    p_p.add_argument("--prices", required=True, help="周线价 JSON 或文件路径")
    p_p.add_argument("--eps", required=True, help='历史TTM EPS JSON：[{"date","eps_ttm"},...]')
    p_p.add_argument("--current-price", type=float, dest="current_price",
                     help="当前价（默认用序列最后一周收盘）")
    p_p.add_argument("--forward-eps", type=float, dest="forward_eps", help="远期每股收益")

    p_pct = sub.add_parser("percentile", help="通用分位：给定序列定位当前/远期值")
    p_pct.add_argument("--series", required=True, help="历史数值 JSON 数组或文件路径")
    p_pct.add_argument("--current", type=float, required=True, help="当前值")
    p_pct.add_argument("--forward", type=float, help="远期值（可选）")

    args = parser.parse_args()
    if args.command == "ashare":
        cmd_ashare(args.code, args.start, args.years, args.growth,
                   args.forward_eps, args.forward_bvps)
    elif args.command == "weekly-prices":
        cmd_weekly_prices(args.ticker, args.years)
    elif args.command == "pe-series":
        cmd_pe_series(args.prices, args.eps, args.current_price, args.forward_eps)
    elif args.command == "percentile":
        cmd_percentile(args.series, args.current, args.forward)


if __name__ == "__main__":
    main()
