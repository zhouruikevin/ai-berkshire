#!/usr/bin/env python3
"""临时批量取数：东财 F10 主营构成（分产品/分地区），只打印最新报告期。"""
import json
import subprocess
import sys

TYPE_LABEL = {"1": "分行业", "2": "分产品", "3": "分地区", "4": "分销售模式"}


def fetch(code):
    m = "SH" if code.startswith(("6", "9", "5")) else "SZ"
    url = f"https://emweb.securities.eastmoney.com/PC_HSF10/BusinessAnalysis/PageAjax?code={m}{code}"
    out = subprocess.run(
        ["/usr/bin/curl", "-s", "--noproxy", "*", "-H", "User-Agent: Mozilla/5.0", url],
        capture_output=True, timeout=25,
    ).stdout.decode("utf-8", "ignore")
    return json.loads(out)


for code in sys.argv[1:]:
    try:
        d = fetch(code)
        rows = d.get("zygcfx") or []
    except Exception as e:
        print(f"{code}: 取数失败 {e}")
        continue
    if not rows:
        print(f"{code}: 无主营构成数据")
        continue
    latest = rows[0]["REPORT_DATE"]
    print(f"\n########## {code} 主营构成 @ {latest[:10]} ##########")
    for r in rows:
        if r["REPORT_DATE"] != latest:
            continue
        inc = r.get("MAIN_BUSINESS_INCOME") or 0
        rat = r.get("MBI_RATIO")
        gp = r.get("GROSS_RPOFIT_RATIO")
        lbl = TYPE_LABEL.get(str(r.get("MAINOP_TYPE")), r.get("MAINOP_TYPE"))
        rat_s = f"{rat*100:.2f}%" if rat is not None else "NA"
        gp_s = f"{gp*100:.2f}%" if gp is not None else "NA"
        print(f"  [{lbl}] {r.get('ITEM_NAME')}: 收入={inc/1e8:.2f}亿 占比={rat_s} 毛利率={gp_s}")
