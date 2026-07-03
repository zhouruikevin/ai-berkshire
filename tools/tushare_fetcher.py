#!/usr/bin/env python3
"""TuShare Pro 数据工具 — A股估值/财务/利润表，零外部依赖（仅 stdlib）。

为 AI Berkshire 的 financial-data skill 提供 A 股一手数据。直接按 TuShare
HTTP 协议 POST 到 `.env` 中配置的 `TUSHARE_API_URL`（支持自建/代理镜像），
不依赖 tushare 包（其 DataApi 写死官方地址，无法指向自定义镜像）。

用法（由 Skills 自动调用）：
    python3 tools/tushare_fetcher.py quote 002407.SZ        # 估值快照 PE_TTM/PB/市值
    python3 tools/tushare_fetcher.py batch-quote            # 批量估值（watchlist 中所有 A 股）
    python3 tools/tushare_fetcher.py financials 002407.SZ   # 财务指标 EPS/ROE/毛利率
    python3 tools/tushare_fetcher.py income 002407.SZ       # 利润表 营收/净利润 + 同比
    python3 tools/tushare_fetcher.py balancesheet 002407.SZ # 资产负债表 + 资产负债率
    python3 tools/tushare_fetcher.py cashflow 002407.SZ     # 现金流量表 经营/投资/筹资
    python3 tools/tushare_fetcher.py update 002407.SZ       # 更新本地缓存（单只）
    python3 tools/tushare_fetcher.py update-all             # 更新本地缓存（watchlist 全部 A 股）

配置（.env 或环境变量）：
    TUSHARE_TOKEN    TuShare（或镜像）token，必填
    TUSHARE_API_URL  API 地址；缺省用官方 http://api.tushare.pro

需要 Python >= 3.8，零外部依赖。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
WATCHLIST = ROOT / "data" / "watchlist.json"
CACHE_FILE = ROOT / "data" / "tushare_cache.json"  # 独立缓存，勿与美股 fundamentals.json 混用

_DEFAULT_URL = "http://api.tushare.pro"
_TIMEOUT = 20


def _load_env() -> dict:
    """读取 .env（若存在），环境变量优先。"""
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip()
    env.update({k: v for k, v in os.environ.items() if k.startswith("TUSHARE_")})
    return env


def _api_call(api_name: str, params: dict, fields: str) -> list[dict]:
    """按 TuShare HTTP 协议调用，返回 [dict, ...]（按接口原始顺序）。"""
    env = _load_env()
    token = env.get("TUSHARE_TOKEN")
    if not token:
        raise SystemExit(
            "tushare_fetcher: 缺少 TUSHARE_TOKEN。请在 .env 或环境变量中配置。"
        )
    url = (env.get("TUSHARE_API_URL") or _DEFAULT_URL).rstrip("/") + "/"
    body = json.dumps(
        {"api_name": api_name, "token": token, "params": params, "fields": fields}
    ).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 — 网络/解析错误统一带上下文抛出
        raise SystemExit(
            f"tushare_fetcher: 调用 {api_name}({params}) 失败 @ {url} — {exc}"
        ) from exc
    if payload.get("code") != 0:
        raise SystemExit(
            f"tushare_fetcher: {api_name} 返回错误 code={payload.get('code')} "
            f"msg={payload.get('msg')!r}"
        )
    data = payload.get("data") or {}
    cols = data.get("fields") or []
    return [dict(zip(cols, row)) for row in (data.get("items") or [])]


def normalize_code(code: str) -> str:
    """'002407' -> '002407.SZ'；已带后缀则原样返回（大写）。"""
    code = code.strip().upper()
    if "." in code:
        return code
    if code.startswith("6"):
        return f"{code}.SH"
    if code.startswith(("0", "3")):
        return f"{code}.SZ"
    if code.startswith(("4", "8")):
        return f"{code}.BJ"
    return code


def _is_a_share(code: str) -> bool:
    return normalize_code(code).endswith((".SH", ".SZ", ".BJ"))


def _latest(rows: list[dict], key: str) -> dict | None:
    """取 key（如 end_date/trade_date）最大的一行；同期多行时取字段最全的一行。

    TuShare 部分接口（如 cashflow）会对同一报告期返回多行（有的字段为空），
    故同期并列时选非空字段最多的那行，避免拿到残缺记录。
    """
    dated = [r for r in rows if r.get(key)]
    if not dated:
        return None
    top = max(r[key] for r in dated)
    tied = [r for r in dated if r[key] == top]
    return max(tied, key=lambda r: sum(v is not None for v in r.values()))


def _wan_to_yi(value) -> float | None:
    """万元 -> 亿元（TuShare 市值单位为万元）。"""
    return round(value / 10000, 2) if isinstance(value, (int, float)) else None


def get_quote(code: str) -> dict:
    code = normalize_code(code)
    rows = _api_call(
        "daily_basic",
        {"ts_code": code},
        "ts_code,trade_date,close,pe_ttm,pb,total_mv,circ_mv",
    )
    latest = _latest(rows, "trade_date")
    if not latest:
        return {"code": code, "error": "无 daily_basic 数据"}
    return {
        "code": code,
        "trade_date": latest.get("trade_date"),
        "close": latest.get("close"),
        "pe_ttm": latest.get("pe_ttm"),
        "pb": latest.get("pb"),
        "total_mv_亿": _wan_to_yi(latest.get("total_mv")),
        "circ_mv_亿": _wan_to_yi(latest.get("circ_mv")),
    }


def get_financials(code: str) -> dict:
    code = normalize_code(code)
    rows = _api_call(
        "fina_indicator",
        {"ts_code": code},
        "ts_code,end_date,eps,roe,roe_dt,grossprofit_margin,netprofit_margin",
    )
    latest = _latest(rows, "end_date")
    if not latest:
        return {"code": code, "error": "无 fina_indicator 数据"}
    return {
        "code": code,
        "end_date": latest.get("end_date"),
        "eps": latest.get("eps"),
        "roe": latest.get("roe"),
        "roe_dt": latest.get("roe_dt"),
        "gross_margin": latest.get("grossprofit_margin"),
        "net_margin": latest.get("netprofit_margin"),
    }


def get_income(code: str) -> dict:
    code = normalize_code(code)
    rows = _api_call(
        "income",
        {"ts_code": code},
        "ts_code,end_date,total_revenue,revenue,n_income,n_income_attr_p",
    )
    latest = _latest(rows, "end_date")
    if not latest:
        return {"code": code, "error": "无 income 数据"}
    result = {
        "code": code,
        "end_date": latest.get("end_date"),
        "total_revenue": latest.get("total_revenue"),
        "n_income": latest.get("n_income"),
        "n_income_attr_p": latest.get("n_income_attr_p"),
    }
    # 同比：找去年同一报告期（end_date 月日相同、年份 -1）
    end = latest.get("end_date") or ""
    if len(end) == 8:
        prior_key = str(int(end[:4]) - 1) + end[4:]
        prior = next((r for r in rows if r.get("end_date") == prior_key), None)
        if prior:
            for field, alias in (("total_revenue", "rev_yoy"), ("n_income", "ni_yoy")):
                cur, pre = latest.get(field), prior.get(field)
                if isinstance(cur, (int, float)) and isinstance(pre, (int, float)) and pre:
                    result[alias] = round((cur - pre) / abs(pre) * 100, 1)
    return result


def get_balancesheet(code: str) -> dict:
    code = normalize_code(code)
    rows = _api_call(
        "balancesheet",
        {"ts_code": code},
        "ts_code,end_date,total_assets,total_liab,"
        "total_hldr_eqy_exc_min_int,total_hldr_eqy_inc_min_int,money_cap",
    )
    latest = _latest(rows, "end_date")
    if not latest:
        return {"code": code, "error": "无 balancesheet 数据"}
    assets = latest.get("total_assets")
    liab = latest.get("total_liab")
    result = {
        "code": code,
        "end_date": latest.get("end_date"),
        "total_assets": assets,
        "total_liab": liab,
        "equity_attr_p": latest.get("total_hldr_eqy_exc_min_int"),
        "equity_incl_min": latest.get("total_hldr_eqy_inc_min_int"),
        "money_cap": latest.get("money_cap"),
    }
    if isinstance(assets, (int, float)) and isinstance(liab, (int, float)) and assets:
        result["debt_ratio_pct"] = round(liab / assets * 100, 2)
    return result


def get_cashflow(code: str) -> dict:
    code = normalize_code(code)
    rows = _api_call(
        "cashflow",
        {"ts_code": code},
        "ts_code,end_date,n_cashflow_act,n_cashflow_inv_act,"
        "n_cash_flows_fnc_act,free_cashflow",
    )
    latest = _latest(rows, "end_date")
    if not latest:
        return {"code": code, "error": "无 cashflow 数据"}
    return {
        "code": code,
        "end_date": latest.get("end_date"),
        "operating_cf": latest.get("n_cashflow_act"),
        "investing_cf": latest.get("n_cashflow_inv_act"),
        "financing_cf": latest.get("n_cash_flows_fnc_act"),
        "free_cashflow": latest.get("free_cashflow"),
    }


def _a_share_codes() -> list[str]:
    """从 watchlist.json 收集所有 A 股代码。"""
    if not WATCHLIST.exists():
        raise SystemExit(f"tushare_fetcher: 找不到 watchlist {WATCHLIST}")
    data = json.loads(WATCHLIST.read_text(encoding="utf-8"))
    codes = []
    for value in data.values():
        if isinstance(value, list):
            codes.extend(c for c in value if _is_a_share(c))
    # 去重保序
    seen, out = set(), []
    for c in codes:
        n = normalize_code(c)
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def cmd_quote(code: str) -> None:
    print(json.dumps(get_quote(code), ensure_ascii=False, indent=2))


def cmd_financials(code: str) -> None:
    print(json.dumps(get_financials(code), ensure_ascii=False, indent=2))


def cmd_income(code: str) -> None:
    print(json.dumps(get_income(code), ensure_ascii=False, indent=2))


def cmd_balancesheet(code: str) -> None:
    print(json.dumps(get_balancesheet(code), ensure_ascii=False, indent=2))


def cmd_cashflow(code: str) -> None:
    print(json.dumps(get_cashflow(code), ensure_ascii=False, indent=2))


def cmd_batch_quote() -> None:
    codes = _a_share_codes()
    if not codes:
        print(json.dumps({"note": "watchlist 中无 A 股代码"}, ensure_ascii=False))
        return
    print(json.dumps([get_quote(c) for c in codes], ensure_ascii=False, indent=2))


def _write_cache(records: dict) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    cache = {}
    if CACHE_FILE.exists():
        cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    cache.update(records)
    CACHE_FILE.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _full_record(code: str) -> dict:
    return {
        "quote": get_quote(code),
        "financials": get_financials(code),
        "income": get_income(code),
        "balancesheet": get_balancesheet(code),
        "cashflow": get_cashflow(code),
    }


def cmd_update(code: str) -> None:
    code = normalize_code(code)
    _write_cache({code: _full_record(code)})
    print(f"已更新缓存 {code} -> {CACHE_FILE.relative_to(ROOT)}")


def cmd_update_all() -> None:
    codes = _a_share_codes()
    if not codes:
        print("watchlist 中无 A 股代码，跳过。")
        return
    records = {}
    for c in codes:
        records[c] = _full_record(c)
        print(f"  已拉取 {c}")
    _write_cache(records)
    print(f"已更新 {len(records)} 只 A 股缓存 -> {CACHE_FILE.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="TuShare Pro A股数据工具")
    sub = parser.add_subparsers(dest="command", required=True)

    p_quote = sub.add_parser("quote", help="估值快照 PE_TTM/PB/市值")
    p_quote.add_argument("code", help="股票代码，如 002407 或 002407.SZ")

    p_batch = sub.add_parser("batch-quote", help="批量估值（watchlist 全部 A 股）")

    p_fin = sub.add_parser("financials", help="财务指标 EPS/ROE/毛利率")
    p_fin.add_argument("code", help="股票代码")

    p_inc = sub.add_parser("income", help="利润表 营收/净利润 + 同比")
    p_inc.add_argument("code", help="股票代码")

    p_bs = sub.add_parser("balancesheet", help="资产负债表 总资产/总负债/净资产/资产负债率")
    p_bs.add_argument("code", help="股票代码")

    p_cf = sub.add_parser("cashflow", help="现金流量表 经营/投资/筹资/自由现金流")
    p_cf.add_argument("code", help="股票代码")

    p_upd = sub.add_parser("update", help="更新本地缓存（单只）")
    p_upd.add_argument("code", help="股票代码")

    p_all = sub.add_parser("update-all", help="更新本地缓存（watchlist 全部 A 股）")

    args = parser.parse_args()
    dispatch = {
        "quote": lambda: cmd_quote(args.code),
        "batch-quote": cmd_batch_quote,
        "financials": lambda: cmd_financials(args.code),
        "income": lambda: cmd_income(args.code),
        "balancesheet": lambda: cmd_balancesheet(args.code),
        "cashflow": lambda: cmd_cashflow(args.code),
        "update": lambda: cmd_update(args.code),
        "update-all": cmd_update_all,
    }
    dispatch[args.command]()


if __name__ == "__main__":
    main()
