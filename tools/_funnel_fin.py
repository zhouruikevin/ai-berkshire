#!/usr/bin/env python3
"""临时批量取数：东财 F10 主要财务指标，输出漏斗筛选需要的字段。

用法: python3 tools/_funnel_fin.py 002484 600460 ...
"""
import json
import subprocess
import sys

FIELDS = [
    ("REPORT_DATE_NAME", "期间"),
    ("TOTALOPERATEREVE", "营收"),
    ("TOTALOPERATEREVETZ", "营收YoY%"),
    ("PARENTNETPROFIT", "归母净利"),
    ("PARENTNETPROFITTZ", "归母YoY%"),
    ("KCFJCXSYJLRTZ", "扣非YoY%"),
    ("ROEJQ", "ROE加权%"),
    ("XSMLL", "毛利率%"),
    ("XSJLL", "净利率%"),
    ("ZCFZL", "资产负债率%"),
    ("NCO_NETPROFIT", "经现/净利"),
    ("NETCASH_OPERATE_PK", "经营现金流"),
    ("TOTAL_SHARE", "总股本"),
]


def fetch(code):
    market = "SH" if code.startswith(("6", "9", "5")) else "SZ"
    url = (
        "https://datacenter.eastmoney.com/securities/api/data/get"
        f"?type=RPT_F10_FINANCE_MAINFINADATA&sty=ALL"
        f"&filter=(SECUCODE%3D%22{code}.{market}%22)"
        "&p=1&ps=12&sr=-1&st=REPORT_DATE&source=HSF10&client=PC"
    )
    out = subprocess.run(
        ["/usr/bin/curl", "-s", "--noproxy", "*", "-H", "User-Agent: Mozilla/5.0", url],
        capture_output=True, timeout=25,
    ).stdout.decode("utf-8", "ignore")
    try:
        return json.loads(out)["result"]["data"]
    except Exception as e:
        print(f"  !! {code} 取数失败: {e}")
        return []


def fmt(v, key):
    if v is None:
        return "NA"
    if key in ("TOTALOPERATEREVE", "PARENTNETPROFIT", "NETCASH_OPERATE_PK"):
        return f"{v/1e8:.2f}亿"
    if key == "TOTAL_SHARE":
        return f"{v/1e8:.2f}亿股"
    if isinstance(v, float):
        return f"{v:.2f}"
    return str(v)


for code in sys.argv[1:]:
    rows = fetch(code)
    if not rows:
        continue
    name = rows[0].get("SECURITY_NAME_ABBR", code)
    print(f"\n########## {name} ({code}) ##########")
    # 只取年报 + 最近两期非年报
    picked = []
    n_interim = 0
    for r in rows:
        rt = r.get("REPORT_TYPE", "")
        if rt == "年报":
            picked.append(r)
        elif n_interim < 3:
            picked.append(r)
            n_interim += 1
        if len(picked) >= 8:
            break
    for r in picked:
        parts = [f"{lbl}={fmt(r.get(k), k)}" for k, lbl in FIELDS]
        print("  " + " | ".join(parts))
