#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
img2svg.py —— 位图转 SVG 矢量转换器（vtracer 封装）

把 webp / png / jpg / bmp / gif 等位图，用 vtracer 描摹成 SVG 矢量图。
GitHub README 不支持 <style>/<img data:> 内嵌图片，但**本地 SVG 文件**可正常显示，
所以"位图 → 本地 SVG"是给主页插图最稳的办法（图床挂了也不影响）。

特性
----
- 多格式输入：webp/png/jpg/bmp/gif（依赖 Pillow 解码）
- 两种模式：color（彩色）/ bw（黑白）
- 两种形状：spline（平滑曲线，默认）/ polygon（硬边低多边形）
- 四档预设：balance / medium / fine / ultra（清晰度递增、体积递增）
- 任意参数可单独覆盖（精确控制描摹质量）
- 自动下采样到 --width 上限，防止 SVG 过大
- 输出文件名默认 = 输入名替换扩展名为 .svg；可用 -o 指定

用法
----
  python img2svg.py input.webp
  python img2svg.py input.png -o out.svg
  python img2svg.py input.jpg --mode color --quality fine
  python img2svg.py input.png --mode bw
  python img2svg.py input.png --shape polygon
  python img2svg.py input.webp --quality medium --width 1400
  python img2svg.py input.png --color-precision 8 --filter-speckle 4 --splice-threshold 40

依赖
----
  pip install pillow vtracer

说明
----
  - 写实照片转 SVG 会丢失光照/纹理/锐度，且体积随分辨率/精度指数增长；
    想清晰又干净，优先用"扁平插画/线条图"来转。
  - GitHub README 渲染大 SVG（>2MB）会明显变慢，主页插图建议用 balance/medium 档。
"""

import argparse
import os
import sys

from PIL import Image
import vtracer


# ---------------------------------------------------------------------------
# 预设：清晰度 ↑ → 体积 ↑
# ---------------------------------------------------------------------------
PRESETS = {
    "balance": dict(
        color_precision=6, filter_speckle=8, layer_difference=12,
        corner_threshold=60, length_threshold=4.0, splice_threshold=45,
        path_precision=3, max_width=1200,
    ),
    "medium": dict(
        color_precision=7, filter_speckle=6, layer_difference=14,
        corner_threshold=60, length_threshold=4.0, splice_threshold=45,
        path_precision=4, max_width=1400,
    ),
    "fine": dict(
        color_precision=8, filter_speckle=4, layer_difference=16,
        corner_threshold=60, length_threshold=3.0, splice_threshold=45,
        path_precision=4, max_width=1600,
    ),
    "ultra": dict(
        color_precision=8, filter_speckle=2, layer_difference=16,
        corner_threshold=50, length_threshold=2.0, splice_threshold=40,
        path_precision=5, max_width=2000,
    ),
}


def build_parser():
    p = argparse.ArgumentParser(
        description="位图转 SVG 矢量转换器（vtracer 封装）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("input", help="输入位图路径 (webp/png/jpg/bmp/gif)")
    p.add_argument("-o", "--output", help="输出 SVG 路径（默认：输入名.svg）")
    p.add_argument("--mode", choices=["color", "bw"], default="color",
                   help="color=彩色, bw=黑白（默认 color）")
    p.add_argument("--shape", choices=["spline", "polygon"], default="spline",
                   help="spline=平滑曲线, polygon=硬边低多边形（默认 spline）")
    p.add_argument("--quality", choices=list(PRESETS.keys()), default="balance",
                   help="预设档位（默认 balance）")
    p.add_argument("--width", type=int, default=None,
                   help="最大宽度（下采样上限，覆盖预设的 max_width）")
    # ---- 允许单独覆盖的高级参数 ----
    p.add_argument("--color-precision", type=int, default=None,
                   help="颜色量化精度 1-8（越大颜色越多）")
    p.add_argument("--filter-speckle", type=int, default=None,
                   help="噪点过滤阈值（越小保留越多细节）")
    p.add_argument("--layer-difference", type=int, default=None,
                   help="层间差异阈值 1-255")
    p.add_argument("--corner-threshold", type=int, default=None,
                   help="拐角阈值 0-90")
    p.add_argument("--length-threshold", type=float, default=None,
                   help="长度阈值（滤除短路径）")
    p.add_argument("--splice-threshold", type=int, default=None,
                   help="拼接阈值 0-100（合并共线路径）")
    p.add_argument("--path-precision", type=int, default=None,
                   help="路径坐标精度 1-8（越大越精确越占空间）")
    p.add_argument("--bg-color", default=None,
                   help="bw 模式背景色（如 #ffffff，默认黑色）")
    p.add_argument("--fg-color", default=None,
                   help="bw 模式前景色（如 #000000，默认白色）")
    return p


def resolve_params(args):
    """合并预设与命令行覆盖，返回最终 vtracer 参数。"""
    cfg = dict(PRESETS[args.quality])
    # 命令行覆盖
    overrides = {
        "color_precision": args.color_precision,
        "filter_speckle": args.filter_speckle,
        "layer_difference": args.layer_difference,
        "corner_threshold": args.corner_threshold,
        "length_threshold": args.length_threshold,
        "splice_threshold": args.splice_threshold,
        "path_precision": args.path_precision,
    }
    for k, v in overrides.items():
        if v is not None:
            cfg[k] = v
    max_width = args.width if args.width else cfg.pop("max_width")
    return cfg, max_width


def load_and_resize(path, max_width):
    im = Image.open(path)
    w, h = im.size
    if max_width and w > max_width:
        nh = int(h * max_width / w)
        im = im.resize((max_width, nh), Image.LANCZOS)
        print(f"  下采样: {w}x{h} -> {max_width}x{nh}")
    return im


def main():
    args = build_parser().parse_args()

    if not os.path.isfile(args.input):
        print(f"[错误] 找不到输入文件: {args.input}", file=sys.stderr)
        sys.exit(1)

    out_path = args.output or os.path.splitext(args.input)[0] + ".svg"

    cfg, max_width = resolve_params(args)
    print(f"[img2svg] 输入: {args.input}")
    print(f"  模式={args.mode} 形状={args.shape} 预设={args.quality} "
          f"max_width={max_width}")
    print(f"  参数: {cfg}")

    im = load_and_resize(args.input, max_width)

    # 保存中间 PNG（vtracer 走 PNG 路径最稳）
    tmp_png = out_path + ".tmp.png"
    if args.mode == "bw":
        im = im.convert("L")
    else:
        im = im.convert("RGB")
    im.save(tmp_png, "PNG")

    try:
        if args.mode == "bw":
            vtracer.convert_image_to_svg_py(
                tmp_png, out_path, colormode="bw",
                mode=args.shape,
                filter_speckle=cfg["filter_speckle"],
                color_precision=cfg["color_precision"],
                layer_difference=cfg["layer_difference"],
                corner_threshold=cfg["corner_threshold"],
                length_threshold=cfg["length_threshold"],
                splice_threshold=cfg["splice_threshold"],
                path_precision=cfg["path_precision"],
            )
        else:
            vtracer.convert_image_to_svg_py(
                tmp_png, out_path,
                colormode="color",
                hierarchical="stacked",
                mode=args.shape,
                filter_speckle=cfg["filter_speckle"],
                color_precision=cfg["color_precision"],
                layer_difference=cfg["layer_difference"],
                corner_threshold=cfg["corner_threshold"],
                length_threshold=cfg["length_threshold"],
                splice_threshold=cfg["splice_threshold"],
                path_precision=cfg["path_precision"],
            )
    finally:
        if os.path.exists(tmp_png):
            os.remove(tmp_png)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"[完成] 输出: {out_path}  ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
