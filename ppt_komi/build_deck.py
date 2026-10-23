# -*- coding: utf-8 -*-
"""Сборка презентации «Моря Республики Коми» (python-pptx).

Одно изображение (img/sea.png) + типографика и фигуры. 16:9, 15 слайдов.
"""
from __future__ import annotations

import os

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
OUT = os.path.join(HERE, "..", "Моря_Республики_Коми.pptx")

SW, SH = 13.333, 7.5
ML, MR = 0.85, 12.483
CW = MR - ML
PANEL = 7.30  # правая граница текстовой колонки на слайдах с фотографией

WHITE = RGBColor(0xF4, 0xFA, 0xFC)
ICE = RGBColor(0xC9, 0xE4, 0xEE)
MUTED = RGBColor(0x93, 0xB3, 0xC3)
MUTED_D = RGBColor(0x5B, 0x7C, 0x8C)
BG = RGBColor(0x05, 0x0F, 0x1B)
BG2 = RGBColor(0x0B, 0x1B, 0x2B)
LIGHT_BG = RGBColor(0xEE, 0xF5, 0xF8)
LIGHT_LINE = RGBColor(0x9A, 0xC2, 0xCC)
CARD = RGBColor(0x10, 0x2C, 0x3E)
AQUA = RGBColor(0x5B, 0xD6, 0xC6)
AQUA_D = RGBColor(0x18, 0x7F, 0x78)
GOLD = RGBColor(0xE7, 0xB6, 0x7A)
GOLD_D = RGBColor(0xA5, 0x6A, 0x2C)
NAVY = RGBColor(0x0B, 0x1F, 0x2E)
NAVY_MID = RGBColor(0x33, 0x5A, 0x6E)

F_LIGHT = "Segoe UI Light"
F_REG = "Segoe UI"

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"


# ------------------------------------------------------------------ xml
def _clean_fill(spPr):
    for tag in ("a:noFill", "a:solidFill", "a:gradFill", "a:blipFill", "a:pattFill", "a:grpFill"):
        for e in spPr.findall(qn(tag)):
            spPr.remove(e)


def _set_fill(shape, hexcol: str | None, alpha: float | None = None):
    spPr = shape.fill._xPr
    _clean_fill(spPr)
    if hexcol is None:
        frag = etree.fromstring(f'<a:noFill xmlns:a="{NS_A}"/>')
    else:
        inner = f'<a:srgbClr val="{hexcol}"/>'
        if alpha is not None:
            inner = f'<a:srgbClr val="{hexcol}"><a:alpha val="{int(alpha * 1000)}"/></a:srgbClr>'
        frag = etree.fromstring(f'<a:solidFill xmlns:a="{NS_A}">{inner}</a:solidFill>')
    ln = spPr.find(qn("a:ln"))
    if ln is not None:
        ln.addprevious(frag)
    else:
        spPr.append(frag)


def _set_grad(shape, hexcol: str, stops, angle_deg: float):
    """Градиентная заливка: stops = [(pos, alpha), ...], pos 0..1, alpha 0..1."""
    spPr = shape.fill._xPr
    _clean_fill(spPr)
    gs = "".join(
        f'<a:gs pos="{int(p * 100000)}"><a:srgbClr val="{hexcol}">'
        f'<a:alpha val="{int(a * 100000)}"/></a:srgbClr></a:gs>'
        for p, a in stops
    )
    frag = etree.fromstring(
        f'<a:gradFill xmlns:a="{NS_A}" rotWithShape="1"><a:gsLst>{gs}</a:gsLst>'
        f'<a:lin ang="{int(angle_deg * 60000)}" scaled="0"/></a:gradFill>'
    )
    ln = spPr.find(qn("a:ln"))
    if ln is not None:
        ln.addprevious(frag)
    else:
        spPr.append(frag)


def _set_line(shape, hexcol=None, width_pt=1.0, alpha=None, dash=None):
    spPr = shape.fill._xPr
    ln = spPr.find(qn("a:ln"))
    if ln is None:
        ln = etree.SubElement(spPr, qn("a:ln"))
    for e in list(ln):
        ln.remove(e)
    if hexcol is None:
        ln.set("w", "0")
        etree.SubElement(ln, qn("a:noFill"))
        return
    ln.set("w", str(int(width_pt * 12700)))
    inner = f'<a:srgbClr val="{hexcol}"/>'
    if alpha is not None:
        inner = f'<a:srgbClr val="{hexcol}"><a:alpha val="{int(alpha * 1000)}"/></a:srgbClr>'
    ln.append(etree.fromstring(f'<a:solidFill xmlns:a="{NS_A}">{inner}</a:solidFill>'))
    if dash:
        ln.append(etree.fromstring(f'<a:prstDash xmlns:a="{NS_A}" val="{dash}"/>'))


def _no_style(s):
    el = s._element
    st = el.find(qn("p:style"))
    if st is not None:
        el.remove(st)


def smooth_pts(pts, n=8):
    """Сглаживание ломаной (Catmull-Rom) — для рек на схеме."""
    if len(pts) < 3:
        return list(pts)
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append((
                0.5 * (2 * p1[0] + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
                0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)))
    out.append(pts[-1])
    return out


def hx(c: RGBColor) -> str:
    return str(c)


# ------------------------------------------------------------------ примитивы
def text(slide, x, y, w, h, paras, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    first = True
    for p in paras:
        par = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        par.alignment = p.get("align", PP_ALIGN.LEFT)
        if p.get("line"):
            par.line_spacing = p["line"]
        par.space_before = Pt(p.get("before", 0))
        par.space_after = Pt(p.get("after", 0))
        runs = p.get("runs") or [{"t": p.get("t", "")}]
        for r in runs:
            run = par.add_run()
            run.text = r["t"]
            f = run.font
            f.name = r.get("font", p.get("font", F_REG))
            f.size = Pt(r.get("size", p.get("size", 16)))
            f.bold = r.get("bold", p.get("bold", False))
            f.italic = r.get("italic", p.get("italic", False))
            f.color.rgb = r.get("color", p.get("color", WHITE))
            spc = r.get("spc", p.get("spc"))
            if spc:
                f._rPr.set("spc", str(int(spc)))
    return box


def shape(slide, x, y, w, h, kind=MSO_SHAPE.ROUNDED_RECTANGLE, fill=None, alpha=None,
          line=None, line_alpha=None, line_w=1.0, radius=None, dash=None):
    s = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    _no_style(s)
    if radius is not None and kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            s.adjustments[0] = radius
        except Exception:
            pass
    _set_fill(s, hx(fill) if fill is not None else None, alpha)
    _set_line(s, hx(line) if line is not None else None, line_w, line_alpha, dash)
    tf = s.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return s


def grad_rect(slide, x, y, w, h, color, stops, angle):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    _no_style(s)
    _set_grad(s, hx(color), stops, angle)
    _set_line(s, None)
    return s


def hairline(slide, x, y, w, color, alpha=12.0, h=0.008):
    return shape(slide, x, y, w, h, MSO_SHAPE.RECTANGLE, fill=color, alpha=alpha, line=None)


def freeform(slide, pts, close=True, fill=None, alpha=None, line=None, line_alpha=None,
             line_w=1.25, dash=None):
    """pts — в дюймах."""
    E = 914400
    ipts = [(int(round(x * E)), int(round(y * E))) for x, y in pts]
    fb = slide.shapes.build_freeform(ipts[0][0], ipts[0][1], scale=1.0)
    fb.add_line_segments(ipts[1:], close=close)
    s = fb.convert_to_shape()
    _no_style(s)
    _set_fill(s, hx(fill) if fill is not None else None, alpha)
    _set_line(s, hx(line) if line is not None else None, line_w, line_alpha, dash)
    return s


# ------------------------------------------------------------------ каркас
class Deck:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width = Inches(SW)
        self.prs.slide_height = Inches(SH)
        self.blank = self.prs.slide_layouts[6]
        self.n = 0

    def slide(self, bg=BG):
        self.n += 1
        s = self.prs.slides.add_slide(self.blank)
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = bg
        return s

    def photo(self, tint=None, tint_alpha=40, shift=0.0, scrim="left", scrim_alpha=0.94):
        """Слайд с фотографией на весь экран: затемнение слева/снизу + тонировка."""
        s = self.slide()
        w, h = SW * 1.12, SH * 1.12
        s.shapes.add_picture(os.path.join(IMG, "sea.png"),
                             Inches(-0.85 - shift), Inches(-0.45), Inches(w), Inches(h))
        if tint is not None:
            shape(s, 0, 0, SW, SH, MSO_SHAPE.RECTANGLE, fill=tint, alpha=tint_alpha, line=None)
        if scrim == "left":
            grad_rect(s, 0, 0, SW, SH, BG, [(0.0, scrim_alpha), (0.42, scrim_alpha * 0.88),
                                            (0.72, 0.0)], 0)
        elif scrim == "bottom":
            grad_rect(s, 0, 1.4, SW, SH - 1.4, BG, [(0.0, 0.0), (0.55, 0.55), (1.0, 0.96)], 90)
        return s

    def head(self, s, kicker, title, on_light=False, size=38, tw=CW, y=0.62, line=0.98):
        kc = AQUA_D if on_light else AQUA
        tc = NAVY if on_light else WHITE
        text(s, ML, y, tw, 0.24, [{"t": kicker.upper(), "size": 11, "bold": True, "color": kc,
                                   "spc": 240}])
        text(s, ML, y + 0.32, tw, 1.5, [{"t": title, "size": size, "color": tc, "font": F_LIGHT,
                                         "line": line}])

    def footer(self, s, on_light=False):
        col = NAVY if on_light else WHITE
        c1 = MUTED_D if on_light else MUTED
        hairline(s, ML, 6.88, CW, col, 12)
        text(s, ML, 7.03, 8.0, 0.22, [{"t": "МОРЯ РЕСПУБЛИКИ КОМИ · АТЛАС", "size": 9, "color": c1,
                                       "spc": 180}])
        text(s, MR - 1.2, 7.03, 1.2, 0.22, [{"t": f"{self.n:02d} / 15", "size": 9, "color": c1,
                                             "spc": 180, "align": PP_ALIGN.RIGHT}])

    def save(self):
        cp = self.prs.core_properties
        cp.title = "Моря Республики Коми"
        cp.subject = "Атлас-путеводитель по морям Республики Коми"
        cp.author = "Атлас «Моря Республики Коми»"
        cp.keywords = "Коми, моря, озёра, водохранилища, атлас"
        self.prs.save(OUT)


# ------------------------------------------------------------------ слайды
def s01(d: Deck):
    s = d.photo(scrim="bottom")
    text(s, 1.05, 0.92, 9.0, 0.24, [{"t": "АТЛАС-ПУТЕВОДИТЕЛЬ · РЕСПУБЛИКА КОМИ", "size": 11,
                                     "bold": True, "color": AQUA, "spc": 260}])
    text(s, 1.0, 2.20, 11.0, 1.45, [{"t": "МОРЯ", "size": 104, "font": F_LIGHT, "color": WHITE,
                                     "line": 0.9}])
    text(s, 1.05, 3.56, 11.4, 0.9, [{"t": "РЕСПУБЛИКИ КОМИ", "size": 42, "font": F_LIGHT,
                                     "color": WHITE, "spc": 80, "line": 0.95}])
    text(s, 1.05, 4.38, 10.4, 0.45, [{"t": "Девять морей и один океан сухопутного края — и история каждого",
                                      "size": 17, "color": ICE}])
    hairline(s, 1.05, 5.62, 3.2, AQUA, 45, h=0.012)
    text(s, 1.05, 5.84, 9.4, 0.3, [{"t": "416 774 км²  ·  от Тиманского кряжа до Приполярного Урала  ·  2026",
                                    "size": 11.5, "color": MUTED, "spc": 60}])


def s02(d: Deck):
    s = d.slide()
    d.head(s, "01 · Введение", "У Коми нет выхода к морю.\nЗато есть моря.", size=40)
    text(s, ML, 2.62, 6.5, 3.2, [
        {"t": "Республика Коми — 416 774 км² суши между Тиманским кряжем и Приполярным Уралом. "
              "До ближайшего настоящего моря, Баренцева, — больше 700 километров по прямой.",
         "size": 16, "color": ICE, "line": 1.5, "after": 14},
        {"t": "И всё же море здесь повсюду: в названиях озёр, в торфе болот, в чёрной воде стариц "
              "и в памяти геологов, для которых эта суша — дно трёх десятков древних морей.",
         "size": 16, "color": ICE, "line": 1.5}])
    stats = [("416 774", "км² — площадь республики"), ("0", "выходов к морю на карте"),
             ("94 500+", "озёр и водоёмов"), ("9+1", "морей и один океан")]
    x0, y0, cw, ch, g = 7.65, 2.55, 2.4, 1.62, 0.16
    for i, (num, cap) in enumerate(stats):
        cx = x0 + (i % 2) * (cw + g)
        cy = y0 + (i // 2) * (ch + g)
        shape(s, cx, cy, cw, ch, fill=CARD, alpha=55, line=AQUA, line_alpha=16, radius=0.07)
        text(s, cx + 0.26, cy + 0.24, cw - 0.42, 0.7, [{"t": num, "size": 30, "font": F_LIGHT,
                                                        "color": AQUA}])
        text(s, cx + 0.26, cy + 0.92, cw - 0.44, 0.6, [{"t": cap, "size": 11.5, "color": MUTED,
                                                        "line": 1.25}])
    text(s, ML, 6.25, 9.4, 0.3, [{"t": "Море №1 — Печорское — длиной 1809 км. Море №9 — болото, "
                                       "по которому можно пройти пешком.", "size": 12, "color": MUTED}])
    d.footer(s)


def s03(d: Deck):
    s = d.slide(LIGHT_BG)
    shape(s, 10.4, -1.9, 5.4, 5.4, MSO_SHAPE.OVAL, fill=None, line=LIGHT_LINE, line_alpha=45, line_w=1.0)
    d.head(s, "02 · Каталог", "Девять морей Коми", on_light=True, size=40)
    text(s, ML, 1.86, 11.3, 0.3, [{"t": "Порядок — от самого древнего к самому рукотворному.  Кружок: "
                                       "зелёный — природное, золотой — рукотворное, серый — болото.",
                                   "size": 11, "color": NAVY_MID}])
    rows = [
        ("01", "Печорское", "север и северо-восток", "река и древний морской бассейн", "десятки млн лет", "aq"),
        ("02", "Коми море", "бассейн Выми", "приледниковый реликт", "≈ 10 тыс. лет", "aq"),
        ("03", "Ямское", "Тиманский кряж", "лёд выпахал, разломы подправили", "≈ 10 тыс. лет", "aq"),
        ("04", "Косминское", "север Тимана", "ледниковая котловина", "≈ 10 тыс. лет", "aq"),
        ("05", "Донты", "Усть-Куломский район", "старица Вычегды, торф подпрудил", "≈ 10 тыс. лет", "aq"),
        ("06", "Печорское наливное", "у Печорской ГРЭС", "человек: насосы и канал", "1979 год", "gd"),
        ("07", "Нювчимское", "приток Сысолы", "человек: плотина", "XX век", "gd"),
        ("08", "Кажимское", "приток Сысолы", "человек: плотина", "XX век", "gd"),
        ("09", "Океан", "бассейн Печоры", "послеледниковое болото", "≈ 10 тыс. лет", "ic"),
    ]
    cols = [0.5, 2.55, 2.95, 3.45, 1.95]
    xs = [ML]
    for c in cols:
        xs.append(xs[-1] + c)
    hy = 2.34
    text(s, xs[0], hy, 0.5, 0.24, [{"t": "№", "size": 10, "bold": True, "color": AQUA_D, "spc": 160}])
    for i, lab in enumerate(["Море", "Где искать", "Как создано", "Возраст"]):
        text(s, xs[i + 1], hy, cols[i + 1], 0.24, [{"t": lab.upper(), "size": 10, "bold": True,
                                                    "color": AQUA_D, "spc": 160}])
    hairline(s, ML, hy + 0.3, 11.5, NAVY, 22, h=0.012)

    rh = 0.445
    for i, (num, name, where, how, age, kind) in enumerate(rows):
        y = hy + 0.38 + i * rh
        if i % 2 == 0:
            shape(s, ML - 0.12, y - 0.05, 11.75, rh - 0.05, MSO_SHAPE.RECTANGLE,
                  fill=WHITE, alpha=75, line=None)
        dot = {"aq": AQUA_D, "gd": GOLD_D, "ic": MUTED_D}[kind]
        shape(s, xs[0] + 0.03, y + 0.1, 0.085, 0.085, MSO_SHAPE.OVAL, fill=dot, line=None)
        text(s, xs[0] + 0.21, y + 0.05, 0.45, 0.26, [{"t": num, "size": 12, "color": dot, "spc": 40}])
        text(s, xs[1], y + 0.02, cols[1] - 0.1, 0.3, [{"t": name, "size": 14.5, "color": NAVY,
                                                       "bold": True}])
        text(s, xs[2], y + 0.045, cols[2] - 0.1, 0.3, [{"t": where, "size": 12.5, "color": NAVY_MID}])
        text(s, xs[3], y + 0.045, cols[3] - 0.1, 0.3, [{"t": how, "size": 12.5, "color": NAVY_MID}])
        text(s, xs[4], y + 0.045, cols[4], 0.3, [{"t": age, "size": 12.5, "color": NAVY}])
    d.footer(s, on_light=True)


def s04(d: Deck):
    s = d.slide()
    d.head(s, "03 · Атлас", "Где искать моря", size=40)
    text(s, ML, 1.8, 8.0, 0.3, [{"t": "Схема республики: реки, кряж и девять морей атласа",
                                 "size": 12.5, "color": MUTED}])
    MX, MY, MW, MH = 0.9, 2.2, 8.1, 4.35

    def P(nx, ny):
        return (MX + nx * MW, MY + ny * MH)

    region = [(0.30, 0.04), (0.46, 0.02), (0.58, 0.05), (0.66, 0.03), (0.74, 0.08), (0.83, 0.14),
              (0.90, 0.22), (0.97, 0.31), (0.95, 0.40), (0.88, 0.47), (0.83, 0.56), (0.76, 0.62),
              (0.72, 0.72), (0.63, 0.79), (0.56, 0.88), (0.47, 0.94), (0.41, 0.99), (0.36, 0.93),
              (0.34, 0.84), (0.27, 0.77), (0.22, 0.68), (0.15, 0.62), (0.10, 0.52), (0.06, 0.43),
              (0.09, 0.33), (0.14, 0.24), (0.20, 0.15), (0.25, 0.09)]
    freeform(s, [P(*p) for p in region], close=True, fill=RGBColor(0x0F, 0x33, 0x48), alpha=85,
             line=AQUA, line_alpha=38, line_w=1.25)
    freeform(s, [P(*p) for p in [(0.13, 0.50), (0.26, 0.42), (0.40, 0.33), (0.55, 0.24), (0.70, 0.16)]],
             close=False, fill=None, line=MUTED, line_alpha=45, line_w=1.25, dash="dash")
    for river in ([(0.49, 0.90), (0.47, 0.85), (0.50, 0.79), (0.55, 0.71), (0.53, 0.63), (0.57, 0.55),
                   (0.60, 0.47), (0.62, 0.39), (0.66, 0.31), (0.68, 0.23), (0.72, 0.13)],
                  [(0.47, 0.62), (0.40, 0.59), (0.33, 0.61), (0.26, 0.58), (0.19, 0.55), (0.11, 0.50)],
                  [(0.57, 0.55), (0.63, 0.46), (0.69, 0.38)]):
        freeform(s, [P(*p) for p in smooth_pts(river, 10)], close=False, fill=None,
                 line=RGBColor(0x7F, 0xB8, 0xD0), line_alpha=45, line_w=1.6)

    seas = [(1, 0.715, 0.115, AQUA), (2, 0.33, 0.60, AQUA), (3, 0.455, 0.415, AQUA), (4, 0.575, 0.235, AQUA),
            (5, 0.45, 0.85, AQUA), (6, 0.635, 0.40, GOLD), (7, 0.245, 0.715, GOLD),
            (8, 0.315, 0.775, GOLD), (9, 0.615, 0.55, ICE)]
    for num, nx, ny, col in seas:
        cx, cy = P(nx, ny)
        shape(s, cx - 0.17, cy - 0.17, 0.34, 0.34, MSO_SHAPE.OVAL, fill=col, alpha=16, line=None)
        c = shape(s, cx - 0.105, cy - 0.105, 0.21, 0.21, MSO_SHAPE.OVAL, fill=col, line=None)
        c.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        text(s, cx - 0.105, cy - 0.083, 0.21, 0.18, [{"t": str(num), "size": 8.5, "bold": True,
                                                      "color": BG, "align": PP_ALIGN.CENTER}])
    text(s, MX, MY + MH + 0.16, 8.1, 0.25,
         [{"t": "Схема не в масштабе. Пунктир — Тиманский кряж, светлые линии — Печора, Вычегда, Уса.",
           "size": 10, "color": MUTED}])

    IX = 9.6
    text(s, IX, 1.84, 2.9, 0.24, [{"t": "ИНДЕКС МОРЕЙ", "size": 10, "bold": True, "color": AQUA,
                                   "spc": 200}])
    hairline(s, IX, 2.14, 2.9, WHITE, 16)
    index = [("01", "Печорское", AQUA, "1809 км"), ("02", "Коми море", AQUA, "28,5 км²"),
             ("03", "Ямское", AQUA, "31,1 км²"), ("04", "Косминское", AQUA, "12,6 км²"),
             ("05", "Донты", AQUA, "реликт"), ("06", "Печорское наливное", GOLD, "5,74 км²"),
             ("07", "Нювчимское", GOLD, "1,72 км²"), ("08", "Кажимское", GOLD, "1,45 км²"),
             ("09", "Океан", ICE, "болото")]
    for i, (num, name, col, val) in enumerate(index):
        y = 2.3 + i * 0.375
        shape(s, IX + 0.02, y + 0.1, 0.075, 0.075, MSO_SHAPE.OVAL, fill=col, line=None)
        text(s, IX + 0.2, y + 0.02, 0.34, 0.24, [{"t": num, "size": 10, "color": MUTED, "spc": 30}])
        text(s, IX + 0.56, y + 0.01, 1.7, 0.24, [{"t": name, "size": 11.5, "color": WHITE}])
        text(s, IX + 1.55, y + 0.02, 1.35, 0.24, [{"t": val, "size": 10, "color": MUTED,
                                                   "align": PP_ALIGN.RIGHT}])
    text(s, IX, 6.18, 2.9, 0.5, [{"t": "Зелёный — природные озёра.\nЗолотой — созданные человеком.",
                                  "size": 10, "color": MUTED, "line": 1.3}])
    d.footer(s)


def s05(d: Deck):
    s = d.photo(tint=RGBColor(0x0A, 0x3A, 0x63), tint_alpha=34, shift=0.0)
    d.head(s, "04 · Море № 1", "Печорское море", size=44, tw=6.0)
    text(s, ML, 1.82, 6.3, 0.45, [{"t": "1809 км, бассейн 322 000 км² — море с истоком и устьем",
                                   "size": 14.5, "color": AQUA, "line": 1.35}])
    text(s, ML, 2.62, 6.2, 1.7, [{"t": "Печора начинается ручьём на Северном Урале и заканчивается "
                                       "Печорской губой Баренцева моря. Всё, что между, — 1809 километров "
                                       "«моря»: плёсы, песчаные косы, старицы и луга, заливаемые в половодье.",
                                  "size": 14, "color": ICE, "line": 1.5}])
    rows = [("Как создано", "Долина унаследована от древнего морского бассейна: ледник расширил её, "
                            "послеледниковые воды наполнили."),
            ("Почему «море»", "Полторы тысячи километров судоходного пути и ширина, которую не видно "
                              "с берега."),
            ("Факт", "По Печоре ходили до Усть-Цильмы задолго до железных дорог: река была "
                     "единственной дорогой на север.")]
    y = 4.4
    for lab, body in rows:
        text(s, ML, y + 0.02, 1.5, 0.24, [{"t": lab.upper(), "size": 9, "bold": True, "color": GOLD,
                                           "spc": 130}])
        text(s, ML + 1.56, y - 0.03, 4.58, 0.7, [{"t": body, "size": 11, "color": ICE, "line": 1.4}])
        y += 0.8
    d.footer(s)


def s06(d: Deck):
    s = d.photo(tint=RGBColor(0x2A, 0x22, 0x58), tint_alpha=44, shift=0.34)
    d.head(s, "05 · Море № 2", "Коми море", size=44, tw=6.0)
    text(s, ML, 1.82, 6.2, 0.4, [{"t": "Синдорское озеро, 28,5 км² — второе по площади в республике",
                                  "size": 14.5, "color": GOLD, "line": 1.35}])
    text(s, ML, 2.42, 6.2, 1.6, [{"t": "Озеро спрятано в тайге бассейна Выми, в тринадцати километрах "
                                       "от посёлка Синдор. На карте написано «озеро», у местных — "
                                       "«Коми море». Вода тёмная, как чай: торф и сосна по берегам.",
                                  "size": 14, "color": ICE, "line": 1.5}])
    rows = [("Как создано", "Остаток приледникового водоёма: ледник ушёл, торф поднял берега, "
                            "озеро сузилось до 28,5 км²."),
            ("Почему «море»", "Двенадцать километров в длину, низкие берега и волна от ветра: с лодки "
                              "не видно, где кончается вода."),
            ("Факт", "Без проводника и внедорожника к нему не добраться — и это лучшее, "
                     "что с ним случилось.")]
    y = 4.15
    for lab, body in rows:
        text(s, ML, y + 0.02, 1.5, 0.24, [{"t": lab.upper(), "size": 9, "bold": True, "color": AQUA,
                                           "spc": 130}])
        text(s, ML + 1.56, y - 0.03, 4.58, 0.7, [{"t": body, "size": 11, "color": ICE, "line": 1.4}])
        y += 0.85
    d.footer(s)


def s07(d: Deck):
    s = d.slide()
    d.head(s, "06 · Моря № 3–4", "Тиманские моря:\nЯмское и Косминское", size=38, tw=7.3)
    text(s, 8.45, 0.95, 4.0, 1.5, [{"t": "Два самых северных природных моря атласа лежат на кряже, "
                                         "которому больше миллиарда лет.", "size": 14, "color": ICE,
                                    "line": 1.45}])
    cards = [("03", "Ямское", "31,1 км²", "Крупнейший природный водоём Коми. Лежит в понижении "
                                          "Тиманского кряжа между Четласским и Чайцинским камнями — "
                                          "как вода в каменной чаше."),
             ("04", "Косминское", "12,6 км²", "Северный сосед и третий по площади. Котловину выпахал "
                                              "ледник, а разломы древнего кряжа задали ей форму "
                                              "и направление.")]
    x = ML
    for num, name, area, body in cards:
        shape(s, x, 2.6, 5.6, 2.5, fill=CARD, alpha=50, line=AQUA, line_alpha=14, radius=0.055)
        text(s, x + 0.42, 2.86, 0.6, 0.5, [{"t": num, "size": 20, "font": F_LIGHT, "color": AQUA}])
        text(s, x + 1.0, 2.84, 2.9, 0.42, [{"t": name, "size": 24, "font": F_LIGHT, "color": WHITE}])
        text(s, x + 3.9, 2.92, 1.35, 0.35, [{"t": area, "size": 13, "color": GOLD,
                                             "align": PP_ALIGN.RIGHT}])
        hairline(s, x + 0.42, 3.32, 4.76, WHITE, 14)
        text(s, x + 0.42, 3.5, 4.76, 1.3, [{"t": body, "size": 13, "color": ICE, "line": 1.45}])
        x += 5.88
    text(s, ML, 5.52, 6.3, 0.9, [{"t": "Тиман старше Урала. Воды в нём столько же, сколько было "
                                        "всегда, — меняются только берега.",
                                   "size": 18, "font": F_LIGHT, "color": WHITE, "line": 1.3}])
    text(s, 7.35, 5.48, 5.1, 1.1, [{"t": "Оба моря — ледниковые: холодные, прозрачные и очень медленно "
                                         "прогревающиеся. Купаться в них — отдельный вид спорта.",
                                    "size": 12.5, "color": MUTED, "line": 1.45}])
    d.footer(s)


def s08(d: Deck):
    s = d.photo(tint=RGBColor(0x6B, 0x3A, 0x18), tint_alpha=38, shift=0.56)
    d.head(s, "07 · Море № 5", "Донты — море,\nпомнящее мамонтов", size=40, tw=6.0)
    text(s, ML, 2.26, 6.1, 0.4, [{"t": "Реликтовое озеро на юге республики, в пойме Вычегды",
                                  "size": 14.5, "color": GOLD, "line": 1.35}])
    text(s, ML, 2.9, 6.1, 1.4, [{"t": "Донское, Донты, Дон — большое мелководное озеро в "
                                       "Усть-Куломском районе, соединённое протоками с Кадамом. "
                                       "Мелко, тепло, много жизни: рыба, птица и зыбкие сплавины по берегам.",
                                  "size": 14, "color": ICE, "line": 1.5}])
    rows = [("Как создано", "Река бросила старицу, торф подпрудил её, вода осталась. Так рождается "
                            "реликт — водоём, переживший своего создателя."),
            ("Почему «море»", "Плёс уходит за горизонт, а противоположный берег — низкий, как у моря "
                              "в отлив."),
            ("Факт", "По сплавине у берега можно «пройти по морю» — и это худшая идея в этом атласе.")]
    y = 4.62
    for lab, body in rows:
        text(s, ML, y + 0.02, 1.5, 0.24, [{"t": lab.upper(), "size": 9, "bold": True, "color": AQUA,
                                           "spc": 130}])
        text(s, ML + 1.56, y - 0.03, 4.55, 0.7, [{"t": body, "size": 11, "color": ICE, "line": 1.4}])
        y += 0.74
    d.footer(s)


def s09(d: Deck):
    s = d.slide()
    d.head(s, "08 · Моря № 6–8", "Моря, которые построили", size=40)
    text(s, ML, 1.82, 9.6, 0.3, [{"t": "Три моря Коми созданы человеком — и все три моложе "
                                       "шестидесяти лет", "size": 12.5, "color": MUTED}])
    cards = [("06", "Печорское наливное", "5,74 км²",
              "Водоём-охладитель Печорской ГРЭС. Наливное: воду подают насосами из Печоры. "
              "Работает в замкнутом цикле и не замерзает даже в январе.", "1974–1979"),
             ("07", "Нювчимское", "1,72 км²",
              "Плотина на реке Нювчим, правом притоке Сысолы. Малое море с большой историей — "
              "рядом старый заводской посёлок.", "XX век"),
             ("08", "Кажимское", "1,45 км²",
              "Плотина на Кажиме, в том же бассейне. Самое маленькое море атласа и, пожалуй, "
              "самое уютное.", "XX век")]
    x = ML
    for num, name, area, body, when in cards:
        shape(s, x, 2.28, 3.65, 3.3, fill=CARD, alpha=52, line=GOLD, line_alpha=18, radius=0.06)
        text(s, x + 0.34, 2.54, 1.6, 0.24, [{"t": "МОРЕ " + num, "size": 9, "bold": True,
                                             "color": GOLD, "spc": 180}])
        text(s, x + 0.34, 2.86, 3.0, 0.5, [{"t": name, "size": 19, "font": F_LIGHT, "color": WHITE,
                                            "line": 1.0}])
        text(s, x + 0.34, 3.48, 3.0, 0.42, [{"t": area, "size": 26, "font": F_LIGHT, "color": AQUA}])
        text(s, x + 0.34, 4.04, 2.95, 1.2, [{"t": body, "size": 12, "color": ICE, "line": 1.45}])
        hairline(s, x + 0.34, 5.3, 2.95, WHITE, 12)
        text(s, x + 0.34, 5.4, 2.95, 0.24, [{"t": "СОЗДАНО: " + when, "size": 9, "color": MUTED,
                                             "spc": 120}])
        x += 3.99
    text(s, ML, 5.92, 11.2, 0.7, [{"t": "В сумме рукотворные моря Коми — меньше девяти квадратных "
                                         "километров. Человеку здесь море даётся дорого; природе "
                                         "оно досталось вместе с ледником.",
                                    "size": 13, "color": MUTED, "line": 1.45}])
    d.footer(s)


def s10(d: Deck):
    s = d.photo(tint=RGBColor(0x7C, 0x9A, 0xA8), tint_alpha=26, shift=0.74)
    d.head(s, "09 · Океан", "Океан, по которому\nходят пешком", size=40, tw=6.0)
    text(s, ML, 2.26, 6.1, 0.4, [{"t": "Болото Океан — одно из крупнейших в Европе",
                                  "size": 14.5, "color": GOLD, "line": 1.35}])
    text(s, ML, 2.9, 6.2, 1.4, [{"t": "Болота занимают 9,8 % республики — около 40 700 км². Океан "
                                       "и Усинское — две крупнейшие болотные системы Европы. Волн нет, "
                                       "но вода под ногами помнит ледник.",
                                  "size": 14, "color": ICE, "line": 1.5}])
    rows = [("Как создано", "Послеледниковое заболачивание: торф нарастает на миллиметр в год — "
                            "«океан» растёт десять тысяч лет."),
            ("Почему «океан»", "Площадь, через которую не видно края, и вода под ногами. Название "
                               "дали те, кто здесь ходил."),
            ("Факт", "Болото — не суша и не вода. Север придумал третье состояние и живёт в нём "
                     "полгода.")]
    y = 4.2
    for lab, body in rows:
        text(s, ML, y + 0.02, 1.5, 0.24, [{"t": lab.upper(), "size": 9, "bold": True, "color": AQUA,
                                           "spc": 130}])
        text(s, ML + 1.56, y - 0.03, 4.55, 0.7, [{"t": body, "size": 11, "color": ICE, "line": 1.4}])
        y += 0.78
    d.footer(s)


def s11(d: Deck):
    s = d.slide()
    d.head(s, "10 · Механика", "Четыре способа создать море", size=40)
    text(s, ML, 1.82, 9.8, 0.3, [{"t": "Всё, что нужно морю, — вода и место, где ей задержаться",
                                  "size": 12.5, "color": MUTED}])
    items = [("01", "Лёд", "Ледник выпахивает котловины и оставляет морены, которые подпруживают реки. "
                           "Так появились Ямское и Косминское.", "10 000 лет"),
             ("02", "Земля", "Разломы и карст: вода растворяет известняки, уходит вниз и возвращается "
                             "озером. Карстовые озёра — в бассейне Вычегды.", "10 000 лет"),
             ("03", "Река", "Старицы, протоки, пойменные плёсы. Река создаёт моря побочным эффектом: "
                            "бросила русло — получились Донты.", "1 000 лет"),
             ("04", "Человек", "Плотина, насос, канал. Пять лет работы — и 5,74 км² готовы. "
                               "Единственный способ, укладывающийся в человеческую жизнь.", "5 лет")]
    x = ML
    for num, name, body, dur in items:
        text(s, x, 2.45, 2.5, 0.7, [{"t": num, "size": 34, "font": F_LIGHT, "color": AQUA_D}])
        hairline(s, x, 3.24, 2.42, WHITE, 16)
        text(s, x, 3.4, 2.55, 0.4, [{"t": name, "size": 20, "font": F_LIGHT, "color": WHITE}])
        text(s, x, 3.88, 2.5, 1.6, [{"t": body, "size": 12, "color": ICE, "line": 1.45}])
        text(s, x, 5.55, 2.5, 0.24, [{"t": dur.upper(), "size": 9, "color": GOLD, "spc": 140}])
        x += 3.0
    text(s, ML, 6.05, 10.8, 0.6, [{"t": "Первые три способа работают в масштабе геологического времени. "
                                         "Четвёртый — в масштабе человеческой жизни, и потому кажется чудом.",
                                    "size": 12.5, "color": MUTED, "line": 1.45}])
    d.footer(s)


def s12(d: Deck):
    s = d.slide()
    d.head(s, "11 · Палеозой", "Моря, которых уже нет", size=40)
    text(s, ML, 1.8, 10.4, 0.32, [{"t": "Суша Коми — дно древних морей. Каждый раз, когда море "
                                          "уходило, оно оставляло новую породу.",
                                   "size": 12.5, "color": MUTED}])
    nodes = [("470 млн", "Ордовик и силур", "Тёплые мелководья, рифы. Появляются первые рыбы."),
             ("380 млн", "Девон", "«Век рыб»: в ухтинских слоях — панцирные рыбы, в доманиковых "
                                  "сланцах — будущая нефть."),
             ("325 млн", "Карбон", "Каменноугольное море Печорского района: конулярии, лилии, "
                                   "акантоды. Его уже собирают в 3D."),
             ("270 млн", "Пермь", "Море мелеет, рождаются лагуны и красноцветы. Начинается суша."),
             ("150 млн", "Юра", "Последний морской залив на севере. Дальше — только реки.")]
    x0, x1 = 1.4, 11.6
    axis_y = 3.6
    hairline(s, x0, axis_y, x1 - x0, AQUA, 30, h=0.014)
    step = (x1 - x0) / (len(nodes) - 1)
    for i, (year, name, body) in enumerate(nodes):
        cx = x0 + i * step
        shape(s, cx - 0.075, axis_y - 0.06, 0.15, 0.15, MSO_SHAPE.OVAL, fill=AQUA, line=None)
        shape(s, cx - 0.16, axis_y - 0.145, 0.32, 0.32, MSO_SHAPE.OVAL, fill=AQUA, alpha=10, line=None)
        text(s, cx - 1.0, 2.5, 2.0, 0.45, [{"t": year, "size": 24, "font": F_LIGHT, "color": GOLD,
                                             "align": PP_ALIGN.CENTER}])
        hairline(s, cx - 0.005, 3.0, 0.01, GOLD, 40, h=0.52)
        text(s, cx - 1.08, 3.82, 2.16, 0.3, [{"t": name, "size": 13.5, "bold": True, "color": WHITE,
                                              "align": PP_ALIGN.CENTER}])
        text(s, cx - 1.08, 4.14, 2.16, 1.2, [{"t": body, "size": 11, "color": ICE, "line": 1.4,
                                              "align": PP_ALIGN.CENTER}])
    text(s, ML, 5.98, 10.9, 0.5, [{"t": "У каждого моря Коми под водой — ещё одно море. И у нынешних "
                                        "девяти тоже.", "size": 17, "font": F_LIGHT, "color": WHITE,
                                   "line": 1.3}])
    d.footer(s)


def s13(d: Deck):
    s = d.slide()
    d.head(s, "12 · Проект", "Море, которое\nне построили", size=40, tw=6.2)
    text(s, ML, 2.55, 6.0, 2.3, [
        {"t": "С 1960-х годов разрабатывался проект переброски части стока Вычегды и Печоры "
              "в бассейн Волги. Плотины подняли бы уровень северных рек на десятки метров: "
              "под водой оказались бы леса, луга, деревни и пойменные моря-старицы.",
         "size": 13.5, "color": ICE, "line": 1.5, "after": 12},
        {"t": "В 1986 году работы были прекращены. Самое большое море Коми осталось на чертежах — "
              "и это, пожалуй, лучший финал в этом атласе.",
         "size": 13.5, "color": ICE, "line": 1.5}])
    PX, PY, PW, PH = 7.3, 1.85, 5.1, 3.45
    shape(s, PX, PY, PW, PH, fill=BG2, alpha=85, line=AQUA, line_alpha=16, radius=0.03)
    for i in range(1, 6):
        hairline(s, PX + 0.3, PY + i * PH / 6, PW - 0.6, AQUA, 6, h=0.006)
    for i in range(1, 4):
        shape(s, PX + i * PW / 4, PY + 0.26, 0.006, PH - 0.52, MSO_SHAPE.RECTANGLE, fill=AQUA,
              alpha=6, line=None)

    def Q(dx, dy):
        return (PX + dx, PY + dy)

    terrain = [(0.30, 2.25), (0.90, 2.50), (1.50, 2.85), (2.20, 3.00), (3.00, 2.88),
               (3.80, 2.62), (4.60, 2.42), (4.85, 2.34)]
    water = [(0.62, 2.02), (4.85, 2.02), (4.85, 2.34), (3.80, 2.62),
             (3.00, 2.88), (2.20, 3.00), (1.50, 2.85), (0.90, 2.50), (0.62, 2.383)]
    freeform(s, [Q(*p) for p in water], close=True, fill=AQUA, alpha=20, line=None)
    freeform(s, [Q(*p) for p in terrain], close=False, fill=None, line=AQUA, line_alpha=55, line_w=1.5)
    hairline(s, PX + 0.45, PY + 2.02, 4.45, AQUA, 40, h=0.012)
    shape(s, PX + 1.50, PY + 2.02, 0.15, 0.86, MSO_SHAPE.RECTANGLE, fill=GOLD, alpha=60,
          line=GOLD, line_alpha=70, line_w=0.75)
    text(s, PX + 1.18, PY + 2.94, 1.3, 0.24, [{"t": "ПЛОТИНА", "size": 8, "color": GOLD,
                                               "spc": 100, "align": PP_ALIGN.CENTER}])
    text(s, PX + 3.1, PY + 1.76, 1.62, 0.24, [{"t": "проектный уровень", "size": 8, "color": AQUA,
                                               "align": PP_ALIGN.RIGHT}])
    text(s, PX + 0.30, PY + 3.12, 4.4, 0.24, [{"t": "РАЗРЕЗ ПО ДОЛИНЕ · ВОДА ВЫШЕ, ЧЕМ БЫЛА",
                                               "size": 7.5, "color": MUTED, "spc": 60}])
    text(s, PX + 0.30, PY + 0.34, 4.4, 0.26, [{"t": "СХЕМА КВП · 1960–1986", "size": 8.5,
                                               "color": MUTED, "spc": 120}])
    stats = [("десятки", "метров — проектный подъём уровня"),
             ("26 лет", "проектирования, с 1960 по 1986"),
             ("0 км²", "затоплено: проект остановлен")]
    x = ML
    for num, cap in stats:
        text(s, x, 5.5, 3.4, 0.5, [{"t": num, "size": 26, "font": F_LIGHT, "color": AQUA}])
        text(s, x, 6.02, 3.3, 0.5, [{"t": cap, "size": 11, "color": MUTED, "line": 1.3}])
        x += 3.75
    d.footer(s)


def s14(d: Deck):
    s = d.slide(LIGHT_BG)
    d.head(s, "13 · Цифры", "Моря в цифрах", on_light=True, size=40)
    text(s, ML, 1.82, 7.4, 0.3, [{"t": "Площадь водного зеркала, км² — по реальным водоёмам атласа",
                                   "size": 11.5, "color": NAVY_MID}])
    bars = [("Ямское", 31.1, "aq"), ("Коми море", 28.5, "aq"), ("Косминское", 12.6, "aq"),
            ("Печорское наливное", 5.74, "gd"), ("Нювчимское", 1.72, "gd"),
            ("Кажимское", 1.45, "gd")]
    maxv = 31.1
    bar_x, bar_w = 3.7, 3.0
    y = 2.46
    for name, val, kind in bars:
        col = AQUA_D if kind == "aq" else GOLD_D
        text(s, ML, y + 0.02, 2.6, 0.26, [{"t": name, "size": 12.5, "color": NAVY}])
        w = max(bar_w * val / maxv, 0.04)
        shape(s, bar_x, y, bar_w, 0.22, MSO_SHAPE.RECTANGLE, fill=NAVY, alpha=6, line=None)
        shape(s, bar_x, y, w, 0.22, MSO_SHAPE.RECTANGLE, fill=col, line=None)
        text(s, bar_x + w + 0.12, y - 0.01, 0.9, 0.24, [{"t": f"{val:g}".replace(".", ","),
                                                         "size": 11.5, "color": col}])
        y += 0.6
    text(s, bar_x, y + 0.05, 4.3, 0.5, [{"t": "Для сравнения: Печорское море атласа — это 1809 км "
                                              "длины, а не площади.", "size": 10.5, "color": MUTED_D,
                                         "line": 1.35}])
    stats = [("31,1 км²", "крупнейшее природное — Ямское"), ("1979", "год рождения первого рукотворного"),
             ("0,43 %", "озёрность республики"), ("1,8 тыс. км²", "суммарная площадь всех озёр")]
    x0, y0, cw, ch = 8.1, 2.4, 2.05, 1.78
    for i, (num, cap) in enumerate(stats):
        cx = x0 + (i % 2) * (cw + 0.2)
        cy = y0 + (i // 2) * (ch + 0.22)
        shape(s, cx, cy, cw, ch, fill=WHITE, alpha=80, line=NAVY, line_alpha=7, radius=0.06)
        text(s, cx + 0.22, cy + 0.22, cw - 0.4, 0.5, [{"t": num, "size": 21, "font": F_LIGHT,
                                                       "color": NAVY}])
        text(s, cx + 0.22, cy + 0.98, cw - 0.4, 0.7, [{"t": cap, "size": 10, "color": NAVY_MID,
                                                       "line": 1.3}])
    d.footer(s, on_light=True)


def s15(d: Deck):
    s = d.photo(shift=0.2, scrim="left", scrim_alpha=0.93)
    text(s, ML, 2.05, 9.0, 0.24, [{"t": "ВМЕСТО ВЫВОДА", "size": 11, "bold": True, "color": AQUA,
                                   "spc": 260}])
    text(s, ML, 2.38, 7.0, 1.3, [{"t": "Море — это не география.\nЭто согласие.", "size": 38,
                                  "font": F_LIGHT, "color": WHITE, "line": 1.15}])
    text(s, ML, 3.86, 6.2, 1.3, [{"t": "У Республики Коми нет выхода к морю. Но есть девять морей, "
                                       "один океан и три моря, которых уже нет, — и все они на своём "
                                       "месте. Наука называет их озёрами, водохранилищами и болотами. "
                                       "Атлас разрешает называть их морями: на то он и атлас.",
                                  "size": 13.5, "color": ICE, "line": 1.5}])
    hairline(s, ML, 6.02, 2.6, AQUA, 40, h=0.012)
    text(s, ML, 6.18, 6.1, 0.6, [{"t": "Цифры — по открытым гидрологическим справочникам и работам "
                                       "Института геологии Коми НЦ УрО РАН. Названия морей №6–9 — "
                                       "атласные: так их называют здесь.",
                                  "size": 9, "color": MUTED, "line": 1.35}])


def main():
    d = Deck()
    for fn in (s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13, s14, s15):
        fn(d)
    d.save()
    print("saved:", os.path.abspath(OUT), "slides:", len(d.prs.slides._sldIdLst))


if __name__ == "__main__":
    main()
