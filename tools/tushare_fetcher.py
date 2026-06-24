#!/usr/bin/env python3
"""
tushare_fetcher.py — A 股数据获取 CLI（基于 TuShare Pro）

用法：
    python3 tools/tushare_fetcher.py quote 002407.SZ           # 估值快照
    python3 tools/tushare_fetcher.py financials 002407.SZ      # 财务指标
    python3 tools/tushare_fetcher.py income 002407.SZ          # 利润表
    python3 tools/tushare_fetcher.py update 002407.SZ          # 更新单只
    python3 tools/tushare_fetcher.py update-all                # 批量更新 watchlist
    python3 tools/tushare_fetcher.py batch-quote               # 批量估值快照
"""

import json
import os
import sys
import time
from datetime import datetime

# 将 tools 目录加入 path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tushare_client import TuShareClient

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
WATCHLIST_FILE = os.path.join(DATA_DIR, "watchlist.json")
A_SHARE_FILE = os.path.join(DATA_DIR, "a_share_fundamentals.json")


def _fmt_mv(val):
    """格式化市值（TuShare 返回万元）"""
    if val is None:
        return "N/A"
    yi = val / 10000  # 万元 -> 亿元
    if yi >= 10000:
        return f"{yi / 10000:.2f} 万亿"
    return f"{yi:.2f} 亿"


def _fmt_pct(val):
    """格式化百分比"""
    if val is None:
        return "N/A"
    return f"{val:.2f}%"


def _fmt_num(val, decimals=2):
    """格式化数字"""
    if val is None:
        return "N/A"
    return f"{val:.{decimals}f}"


def _fmt_yi(val):
    """元 -> 亿元"""
    if val is None:
        return "N/A"
    return f"{val / 1e8:.2f} 亿"


# ------------------------------------------------------------------
# 命令：quote — 估值快照
# ------------------------------------------------------------------

def cmd_quote(client, ts_codes):
    """查询最新估值快照"""
    td = client.get_latest_trade_date()
    print(f"\n{'=' * 70}")
    print(f"  A 股估值快照  交易日: {td}")
    print(f"{'=' * 70}")
    print(f"  {'代码':<12} {'收盘':>8} {'PE(TTM)':>10} {'PB':>8} {'总市值':>12} {'换手率':>8}")
    print(f"  {'-' * 12} {'-' * 8} {'-' * 10} {'-' * 8} {'-' * 12} {'-' * 8}")

    for code in ts_codes:
        try:
            rows = client.get_daily_basic(code, td)
            if not rows:
                # 如果今天没有数据，尝试前一天
                rows = client.get_daily_basic(code)
            if rows:
                r = rows[0]
                close = _fmt_num(r.get("close"))
                pe = _fmt_num(r.get("pe_ttm"))
                pb = _fmt_num(r.get("pb"))
                mv = _fmt_mv(r.get("total_mv"))
                turnover = _fmt_pct(r.get("turnover_rate"))
                print(f"  {code:<12} {close:>8} {pe:>10} {pb:>8} {mv:>12} {turnover:>8}")
            else:
                print(f"  {code:<12} {'无数据':>8}")
        except Exception as e:
            print(f"  {code:<12} ❌ {e}")
        time.sleep(0.15)

    print()


# ------------------------------------------------------------------
# 命令：financials — 财务指标
# ------------------------------------------------------------------

def cmd_financials(client, ts_code):
    """查询最近季度财务指标"""
    print(f"\n{'=' * 70}")
    print(f"  {ts_code} 财务指标（最近 8 个报告期）")
    print(f"{'=' * 70}")

    rows = client.get_fina_indicator(ts_code, limit=8)
    if not rows:
        print("  无数据")
        return

    print(f"\n  {'报告期':<12} {'EPS':>8} {'ROE':>8} {'毛利率':>8} {'净利率':>8} {'营收同比':>10} {'扣非利润同比':>12}")
    print(f"  {'-' * 12} {'-' * 8} {'-' * 8} {'-' * 8} {'-' * 8} {'-' * 10} {'-' * 12}")

    for r in rows:
        end_date = r.get("end_date", "")
        # 格式化日期 20260331 -> 2026Q1
        if len(end_date) == 8:
            y, m = end_date[:4], end_date[4:6]
            q = {"03": "Q1", "06": "Q2", "09": "Q3", "12": "Q4"}.get(m, m)
            label = f"{y}{q}"
        else:
            label = end_date

        eps = _fmt_num(r.get("eps"))
        roe = _fmt_pct(r.get("roe"))
        gm = _fmt_pct(r.get("grossprofit_margin"))
        nm = _fmt_pct(r.get("netprofit_margin"))
        op_yoy = _fmt_pct(r.get("op_yoy"))
        dt_yoy = _fmt_pct(r.get("dt_netprofit_yoy"))

        print(f"  {label:<12} {eps:>8} {roe:>8} {gm:>8} {nm:>8} {op_yoy:>10} {dt_yoy:>12}")

    print()


# ------------------------------------------------------------------
# 命令：income — 利润表
# ------------------------------------------------------------------

def cmd_income(client, ts_code):
    """查询最近季度利润表"""
    print(f"\n{'=' * 70}")
    print(f"  {ts_code} 利润表（最近 8 个报告期）")
    print(f"{'=' * 70}")

    rows = client.get_income(ts_code, limit=8)
    if not rows:
        print("  无数据")
        return

    print(f"\n  {'报告期':<12} {'营收':>14} {'净利润':>14} {'归母净利润':>14}")
    print(f"  {'-' * 12} {'-' * 14} {'-' * 14} {'-' * 14}")

    for r in rows:
        end_date = r.get("end_date", "")
        if len(end_date) == 8:
            y, m = end_date[:4], end_date[4:6]
            q = {"03": "Q1", "06": "Q2", "09": "Q3", "12": "Q4"}.get(m, m)
            label = f"{y}{q}"
        else:
            label = end_date

        rev = _fmt_yi(r.get("revenue"))
        ni = _fmt_yi(r.get("n_income"))
        nip = _fmt_yi(r.get("n_income_attr_p"))

        print(f"  {label:<12} {rev:>14} {ni:>14} {nip:>14}")

    print()


# ------------------------------------------------------------------
# 命令：update / update-all — 更新本地数据
# ------------------------------------------------------------------

def _collect_stock_data(client, ts_code):
    """收集单只股票的完整数据"""
    td = client.get_latest_trade_date()

    # 1. 估值快照
    basic_rows = client.get_daily_basic(ts_code, td)
    if not basic_rows:
        basic_rows = client.get_daily_basic(ts_code)
    basic = basic_rows[0] if basic_rows else {}

    # 2. 财务指标
    fina = client.get_fina_indicator(ts_code, limit=8)

    # 3. 利润表
    inc = client.get_income(ts_code, limit=8)

    # 4. 股票基本信息
    info_rows = client.get_stock_basic(ts_code)
    info = info_rows[0] if info_rows else {}

    return {
        "ts_code": ts_code,
        "name": info.get("name", ""),
        "industry": info.get("industry", ""),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "trade_date": basic.get("trade_date", td),
        "quote": {
            "close": basic.get("close"),
            "pe_ttm": basic.get("pe_ttm"),
            "pb": basic.get("pb"),
            "total_mv": basic.get("total_mv"),  # 万元
            "circ_mv": basic.get("circ_mv"),     # 万元
            "turnover_rate": basic.get("turnover_rate"),
            "total_share": basic.get("total_share"),
            "float_share": basic.get("float_share"),
        },
        "fina_indicator": fina,
        "income": inc,
    }


def cmd_update(client, ts_codes):
    """更新本地数据"""
    os.makedirs(DATA_DIR, exist_ok=True)

    # 加载已有数据
    existing = {}
    if os.path.exists(A_SHARE_FILE):
        with open(A_SHARE_FILE) as f:
            existing = json.load(f)

    print(f"\n{'=' * 70}")
    print(f"  A 股数据更新  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'=' * 70}")

    for code in ts_codes:
        try:
            print(f"\n  📊 {code} ... ", end="", flush=True)
            data = _collect_stock_data(client, code)
            existing[code] = data
            name = data.get("name", "")
            pe = data["quote"].get("pe_ttm")
            close = data["quote"].get("close")
            pe_str = f"PE(TTM)={pe:.2f}" if pe else "PE=N/A"
            close_str = f"收盘={close}" if close else ""
            print(f"✅ {name}  {close_str}  {pe_str}")
        except Exception as e:
            print(f"❌ {e}")
        time.sleep(0.3)  # 限流

    # 保存
    with open(A_SHARE_FILE, "w") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    print(f"\n  已保存到: {A_SHARE_FILE}")
    print(f"  共 {len(existing)} 只股票\n")


# ------------------------------------------------------------------
# 命令：batch-quote — 批量估值
# ------------------------------------------------------------------

def cmd_batch_quote(client):
    """从 watchlist 批量查询估值"""
    ts_codes = _load_a_share_codes()
    if not ts_codes:
        print("  ⚠️ watchlist.json 中 a_share 分组为空")
        return
    cmd_quote(client, ts_codes)


def _load_a_share_codes():
    """从 watchlist.json 加载 A 股代码"""
    if not os.path.exists(WATCHLIST_FILE):
        return []
    with open(WATCHLIST_FILE) as f:
        wl = json.load(f)
    return wl.get("a_share", [])


# ------------------------------------------------------------------
# 主程序
# ------------------------------------------------------------------

def main():
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        return

    cmd = args[0]

    try:
        client = TuShareClient()
    except ValueError as e:
        print(f"  ❌ {e}")
        sys.exit(1)

    if cmd == "quote":
        codes = args[1:] if len(args) > 1 else _load_a_share_codes()
        if not codes:
            print("  用法: tushare_fetcher.py quote <ts_code> [ts_code2 ...]")
            return
        cmd_quote(client, codes)

    elif cmd == "financials":
        if len(args) < 2:
            print("  用法: tushare_fetcher.py financials <ts_code>")
            return
        cmd_financials(client, args[1])

    elif cmd == "income":
        if len(args) < 2:
            print("  用法: tushare_fetcher.py income <ts_code>")
            return
        cmd_income(client, args[1])

    elif cmd == "update":
        codes = args[1:] if len(args) > 1 else _load_a_share_codes()
        if not codes:
            print("  用法: tushare_fetcher.py update <ts_code> [ts_code2 ...]")
            return
        cmd_update(client, codes)

    elif cmd == "update-all":
        codes = _load_a_share_codes()
        if not codes:
            print("  ⚠️ watchlist.json 中 a_share 分组为空，请先填充股票代码")
            return
        cmd_update(client, codes)

    elif cmd == "batch-quote":
        cmd_batch_quote(client)

    else:
        print(f"  未知命令: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
