#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 PICS3D 后处理产物里提取 L-I，做阈值/斜率效率提取与自洽标定。

做两件事：
  1) 对每个算例目录：读 jplot024.tmp（两列：电流 A，双端面输出功率 W），
     自动挑出"最干净且最长"的线性区，最小二乘拟合 P = a*I + b，
     得到 dP/dI = a、外推阈值 I_th = -b/a、微分效率 eta_d = a / (hc/q/lam)。
  2) 若给了多个算例，且每个算例的端面反射率/腔长不同，则用
         1/eta_d = (1/eta_i) + (alpha_i/eta_i) * (1/alpha_m)
     对 1/alpha_m 做直线拟合，截距倒数 = eta_i，斜率/截距 = alpha_i。

用法：
    python scripts/pics3d_li_fit.py <算例目录> [<算例目录> ...] [--plot-file jplot024.tmp]

依赖：只用标准库（无 numpy）。

背景（2026-09-19 建立）：
  - jplot024.tmp 对应 .plt 里 `plot_scan scan_var=current_1 variable=rtg_2facet_power_allmode`
    （双端面、所有纵模求和的总输出功率）。
  - 高电流段存在轻微 roll-off（斜率下降），所以不能拿整段拟合；
    本脚本用"最长且 r² 达标"的窗口来挑最干净的那一段。
"""

import math
import os
import re
import sys

HC_OVER_Q = 1.2398424  # hc/q, 单位 eV*um；lam 用 um，则 hc/q/lam 得到伏特


def read_text(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    # PowerShell 的 `>` 重定向会写出 UTF-16LE+BOM 的日志文件，必须先认出来，
    # 否则所有正则都会静默失配（2026-09-19 踩过这个坑）。
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    for enc in ("utf-8-sig", "gbk", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def parse_case(path, plot_name):
    """读一个算例目录，返回 dict。"""
    info = {"dir": path, "name": os.path.basename(path.rstrip("\\/"))}

    sol = os.path.join(path, "s2.sol")
    if os.path.exists(sol):
        txt = read_text(sol)
        m = re.search(r"uniform_length\s*=\s*([0-9.eE+-]+)", txt)
        info["L_um"] = float(m.group(1)) if m else None
        m = re.search(r"left_f_refl\s*=\s*([0-9.eE+-]+)", txt)
        info["R1"] = float(m.group(1)) if m else None
        m = re.search(r"right_f_refl\s*=\s*([0-9.eE+-]+)", txt)
        info["R2"] = float(m.group(1)) if m else None

    # 激射波长：日志里最后一个 wavel= （材料增益峰所在波长）
    log = os.path.join(path, "s2_run.log")
    info["lam_um"] = None
    if os.path.exists(log):
        wavels = re.findall(r"wavel=\s*([0-9.]+)", read_text(log))
        if wavels:
            info["lam_um"] = float(wavels[-1])

    # L-I 数据
    plot = os.path.join(path, plot_name)
    pts = []
    if os.path.exists(plot):
        for line in read_text(plot).splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            try:
                pts.append((float(parts[0]) * 1000.0, float(parts[1]) * 1000.0))  # mA, mW
            except ValueError:
                continue
    pts.sort()
    info["points"] = pts
    return info


def linreg(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None  # 所有 x 相同（例如各算例的 alpha_m 一样）无法拟合
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    a = sxy / sxx
    b = my - a * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (a * x + b)) ** 2 for x, y in zip(xs, ys))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    # 斜率/截距的标准误
    dof = n - 2
    if dof > 0 and sxx > 0:
        s2 = ss_res / dof
        se_a = math.sqrt(s2 / sxx)
        se_b = math.sqrt(s2 * (1.0 / n + mx * mx / sxx))
    else:
        se_a = se_b = float("nan")
    return {"a": a, "b": b, "r2": r2, "n": n, "se_a": se_a, "se_b": se_b,
            "x0": xs[0], "x1": xs[-1]}


def pick_window(pts, knee_mA, min_span=10.0, r2_levels=(0.9995, 0.999, 0.995, 0.99)):
    """在阈值以上挑"最长且足够直"的窗口。"""
    above = [p for p in pts if p[0] > knee_mA + 0.5]
    best = None
    for level in r2_levels:
        for i in range(len(above)):
            for j in range(len(above) - 1, i, -1):
                span = above[j][0] - above[i][0]
                if span < min_span:
                    break
                if best is not None and span <= best["span"]:
                    break
                xs = [p[0] for p in above[i:j + 1]]
                ys = [p[1] for p in above[i:j + 1]]
                fit = linreg(xs, ys)
                if fit["r2"] >= level:
                    best = dict(fit)
                    best["span"] = span
                    best["level"] = level
                    break
        if best is not None:
            break
    return best


def window_fit(pts, lo, hi):
    """对 [lo, hi] mA 之内的点做直线拟合；点太少返回 None。"""
    sel = [p for p in pts if lo <= p[0] <= hi]
    if len(sel) < 4:
        return None
    fit = linreg([p[0] for p in sel], [p[1] for p in sel])
    fit["span"] = sel[-1][0] - sel[0][0]
    return fit


def analyse(info, pad=5.0, span=30.0, verbose=True):
    pts = info["points"]
    if len(pts) < 6:
        info["error"] = "too few L-I points (check that jplot024.tmp exists and is not 0 bytes)"
        return info

    knee = next((p[0] for p in pts if p[1] > 1e-9), None)
    info["knee_mA"] = knee
    if knee is None:
        info["error"] = "the whole L-I is zero: no lasing was reached"
        return info

    # 主判据：紧贴阈值上方开一段固定相对窗口（物理上"刚出光时的斜率效率"）
    fit = window_fit(pts, knee + pad, min(knee + pad + span, pts[-1][0]))
    # 敏感性对照：自动挑"最长且 r² 达标"的窗口（会含入高电流 roll-off）
    alt = pick_window(pts, knee)
    if fit is None:
        fit = alt
        alt = None
    if fit is None:
        info["error"] = "no usable linear region found"
        return info

    info["fit"] = fit
    info["fit_alt"] = alt
    info["dP_dI"] = fit["a"]                    # mW/mA 数值上就是 W/A
    info["I_th"] = -fit["b"] / fit["a"]         # mA
    if info.get("lam_um"):
        info["hv_q"] = HC_OVER_Q / info["lam_um"]
        info["eta_d"] = info["dP_dI"] / info["hv_q"]
    if alt:
        info["dP_dI_alt"] = alt["a"]
        info["I_th_alt"] = -alt["b"] / alt["a"]
        if info.get("hv_q"):
            info["eta_d_alt"] = info["dP_dI_alt"] / info["hv_q"]
    if info.get("L_um") and info.get("R1") and info.get("R2"):
        L_cm = info["L_um"] * 1e-4
        info["alpha_m"] = math.log(1.0 / (info["R1"] * info["R2"])) / (2.0 * L_cm)
    info["P_at_Imax"] = pts[-1][1]
    return info


def main(argv):
    plot_name = "jplot024.tmp"
    pad, span = 5.0, 30.0
    for opt, conv in (("--plot-file", str), ("--pad", float), ("--span", float)):
        if opt in argv:
            k = argv.index(opt)
            val = conv(argv[k + 1])
            del argv[k:k + 2]
            if opt == "--plot-file":
                plot_name = val
            elif opt == "--pad":
                pad = val
            else:
                span = val
    dirs = [a for a in argv[1:] if not a.startswith("--")]
    if not dirs:
        print(__doc__)
        return 1

    cases = []
    for d in dirs:
        info = analyse(parse_case(d, plot_name), pad=pad, span=span)
        cases.append(info)

    print("=" * 96)
    print("[1] L-I extraction per case   (window = knee+%.0f .. knee+%.0f mA, clipped at Imax)"
          % (pad, pad + span))
    print("=" * 96)
    print("%-22s %8s %9s %9s %9s %9s %8s" %
          ("case", "R", "I_th/mA", "dP/dI", "eta_d", "lambda", "r2"))
    print("%-22s %8s %9s %9s %9s %9s %8s" %
          ("", "", "", "W/A", "%", "um", ""))
    for c in cases:
        if "error" in c:
            print("%-22s  !! %s" % (c["name"], c["error"]))
            continue
        print("%-22s %8s %9.2f %9.4f %9.2f %9.4f %8.4f" %
              (c["name"], ("%.2f" % c["R1"]) if c.get("R1") else "-",
               c["I_th"], c["dP_dI"], 100 * c["eta_d"], c["lam_um"], c["fit"]["r2"]))
    print()
    print("%-22s %-28s %10s %10s" % ("case", "fit window (mA)", "span", "knee"))
    for c in cases:
        if "error" in c:
            continue
        f = c["fit"]
        print("%-22s %-28s %10.2f %10.2f" %
              (c["name"], "%.1f ~ %.1f" % (f["x0"], f["x1"]), f["span"], c["knee_mA"]))
    print()
    print("sensitivity: longest high-r2 window (includes high-current roll-off):")
    print("%-22s %-28s %10s %10s %10s" % ("case", "window (mA)", "span", "dP/dI W/A", "eta_d %"))
    for c in cases:
        a = c.get("fit_alt")
        if not a:
            continue
        print("%-22s %-28s %10.2f %10.4f %10.2f" %
              (c["name"], "%.1f ~ %.1f" % (a["x0"], a["x1"]), a["span"],
               a["a"], 100 * c["eta_d_alt"]))

    ok = [c for c in cases if "eta_d" in c and "alpha_m" in c]
    if len(ok) < 2:
        print("\n(need >=2 usable cases; calibration fit skipped)")
        return 0

    print()
    print("=" * 96)
    print("[2] calibration:  1/eta_d = (1/eta_i) + (alpha_i/eta_i) * (1/alpha_m)")
    print("=" * 96)
    print("%-22s %10s %10s %12s %12s" % ("case", "alpha_m", "1/alpha_m", "eta_d", "1/eta_d"))
    print("%-22s %10s %10s %12s %12s" % ("", "/cm", "cm", "%", ""))
    xs, ys = [], []
    for c in sorted(ok, key=lambda z: z["alpha_m"]):
        x = 1.0 / c["alpha_m"]
        y = 1.0 / c["eta_d"]
        xs.append(x)
        ys.append(y)
        print("%-22s %10.2f %10.5f %12.2f %12.4f" %
              (c["name"], c["alpha_m"], x, 100 * c["eta_d"], y))

    fit = linreg(xs, ys)
    if fit is None:
        print("\n(所有算例的 alpha_m 相同，无法做直线拟合——至少需要两种不同的端面反射率或腔长)")
        return 0
    eta_i = 1.0 / fit["b"]
    alpha_i = fit["a"] / fit["b"]
    print()
    print("  intercept 1/eta_i = %.4f +/- %.4f   -> eta_i = %.1f %% +/- %.1f %%" %
          (fit["b"], fit["se_b"], 100 * eta_i,
           100 * eta_i * fit["se_b"] / fit["b"] if fit["b"] else float("nan")))
    print("  slope alpha_i/eta_i = %.3f +/- %.3f /cm -> alpha_i = %.2f +/- %.2f /cm" %
          (fit["a"], fit["se_a"], alpha_i,
           alpha_i * math.sqrt((fit["se_a"] / fit["a"]) ** 2 + (fit["se_b"] / fit["b"]) ** 2)))
    print("  linearity r2 = %.5f" % fit["r2"])
    print()
    print("  cross-check: compare with alpha_i from the Int._loss column of s2.sol.msg (60 mA dataset).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
