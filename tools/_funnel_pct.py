#!/usr/bin/env python3
"""临时批量取数：调用 valuation_percentile.py ashare，只打印分位摘要 + 关键时点PB。"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VP = ROOT / "tools" / "valuation_percentile.py"

# 关键观察时点（周样本近似）
MARKS = ["20260102", "20260109", "20260403", "20260430", "20260626", "20260731", "20260814"]

for code in sys.argv[1:]:
    try:
        out = subprocess.run(
            [sys.executable, str(VP), "ashare", code, "--years", "5"],
            capture_output=True, timeout=180, cwd=str(ROOT),
        ).stdout.decode("utf-8", "ignore")
        d = json.loads(out)
    except Exception as e:
        print(f"{code}: 取数失败 {e}")
        continue
    pe, pb = d.get("PE_TTM") or {}, d.get("PB") or {}
    pe = {"当前": pe.get("当前") or {}, "历史分布": pe.get("历史分布") or {}}
    pb = {"当前": pb.get("当前") or {}, "历史分布": pb.get("历史分布") or {}}
    s = d.get("周频历史序列", [])
    peak_pb = max(s, key=lambda r: r.get("pb") or 0) if s else {}
    print(f"\n===== {code} =====")
    print(f"  PE_TTM 当前={pe.get('当前',{}).get('当前值')} 分位={pe.get('当前',{}).get('历史百分位')}% "
          f"区间={pe.get('当前',{}).get('所处区间')} 中位={pe.get('历史分布',{}).get('median')} "
          f"max={pe.get('历史分布',{}).get('max')}")
    print(f"  PB     当前={pb.get('当前',{}).get('当前值')} 分位={pb.get('当前',{}).get('历史百分位')}% "
          f"区间={pb.get('当前',{}).get('所处区间')} 中位={pb.get('历史分布',{}).get('median')} "
          f"max={pb.get('历史分布',{}).get('max')}")
    print(f"  PB峰值周: {peak_pb.get('date')} PB={peak_pb.get('pb')} PE={peak_pb.get('pe_ttm')}")
    # 打印年初 vs 现在的 PB（衡量今年估值扩张幅度）
    picks = {r["date"]: r for r in s if r["date"] in MARKS}
    for m in MARKS:
        if m in picks:
            r = picks[m]
            print(f"    {m}: PB={r['pb']} PE={r['pe_ttm']}")
