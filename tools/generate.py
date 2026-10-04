#!/usr/bin/env python3
"""Generates watchface.xml plus its small images.

Layout and colors follow Samsung's Health Dashboard+ (its geometry is on a 360px
canvas; everything here is scaled by S to the 450px WFF canvas). Angles are WFF
angles: 0 = 12 o'clock, clockwise.

The gauges need the same drawing repeated for every complication type and for
each gradient layer, so the XML is generated rather than hand-edited.
Run from the repo root:  python3 tools/generate.py
"""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "photodashplus/src/main/res"

C = 225                # canvas center
S = 450 / 360          # Samsung canvas -> ours
PHOTO_ALPHA = 150      # photo dimming: 0 = black, 255 = full brightness
TRACK_ALPHA = 41       # unfilled part of the thick arcs (16%, as in Samsung's dim images)
TRACK_SHADE = "#a0000000"  # dark band under the tracks so they stay dark over a wallpaper
TEXT_SHADOW = '<Shadow color="#e6000000" offsetX="0" offsetY="2" radius="6">'  # soft drop shadow on all text
UV_DIM_ALPHA = 0x50  # Samsung uses 0x99; dimmer so the fill stands out

# Thick arcs (steps, battery): radius 167, 20 thick. Ticked arcs (heart rate, UV): radius 144,
# 10 thick, 1-on/4-off dashes. Each gauge fills one quadrant.
BAND_D, BAND_W = 2 * 167 * S, 20 * S
TICK_D, TICK_W = 2 * 144 * S, 10 * S
TICKS = f"{1 * S} {4 * S}"
NUM_SIZE = 21 * S      # numbers on the thick arcs
SMALL_SIZE = 20        # bpm / UV level text
INSIDE_TEXT = "#ff000000"

STEPS = (-90, 0)       # 9 -> 12 o'clock
BATTERY = (90, 180)    # 3 -> 6 o'clock
HEART = (-90, 0)
UV = (90, 180)
TEXT_INSIDE_AFTER = 62  # degrees of fill after which the number moves inside the fill
TEXT_GAP = 2 + math.degrees(2 * math.asin(5 / 159))  # Samsung: 2 deg + a 10px chord

# Theme colors, indexed into ColorOption.colors:
COLOR_KEYS = ["steps_start", "steps_end", "bat_start", "bat_end", "hr_start", "hr_end", "uv",
              "steps_text", "bat_text", "hr_text", "uv_text", "hr_arrow",
              "steps_icon", "bat_icon", "hr_icon", "uv_icon"]
COL = {k: f"[CONFIGURATION.themeColor.{i}]" for i, k in enumerate(COLOR_KEYS)}

SAMSUNG_THEMES = [  # straight from Health Dashboard+'s color resources
    ("theme_lime", "Lime mint", dict(
        steps_start="#ff2bff8b", steps_end="#ffe6fc68", bat_start="#ff00aeff", bat_end="#ff40ffa9",
        hr_start="#cc24e079", hr_end="#ccc9de52", uv="#ff20d6d3", steps_text="#ffc2fc6f", bat_text="#ff54ffc3",
        hr_text="#b394fc77", uv_text="#ff15d6d3", hr_arrow="#ff289c53", steps_icon="#ff33ff8b",
        bat_icon="#e60cb7f0", hr_icon="#ff1eb05b", uv_icon="#ff20d6d3")),
    ("theme_coral", "Coral pink", dict(
        steps_start="#ffde5474", steps_end="#ffffa1f2", bat_start="#ffc965cf", bat_end="#ffff9191",
        hr_start="#ccde5474", hr_end="#ccd97ccc", uv="#ffeb7ac9", steps_text="#fff280ce", bat_text="#ffff9e9e",
        hr_text="#b3ed6b9f", uv_text="#ffc967ac", hr_arrow="#ff963e58", steps_icon="#fff26896",
        bat_icon="#e6d16dc5", hr_icon="#ffc24c67", uv_icon="#ffad57a8")),
    ("theme_blue", "Blue violet", dict(
        steps_start="#ff00a1ff", steps_end="#ff00ffcc", bat_start="#ff8b59ff", bat_end="#ffc95ecc",
        hr_start="#cc00a1ff", hr_end="#cc00ffcc", uv="#ffc180ff", steps_text="#ff00f2d2", bat_text="#ffcf70ff",
        hr_text="#b300dade", uv_text="#ffb566ff", hr_arrow="#ff0e86a1", steps_icon="#ff00baf2",
        bat_icon="#e68956e8", hr_icon="#ff0088b5", uv_icon="#ff8956e8")),
]
# Extra themes from two stops: (start, end) for steps/heart, (end-ish, start-ish) for battery/UV.
EXTRA_THEMES = [
    ("theme_berry", "Berry", "#ff5ca8", "#a35cff"),
    ("theme_orchid", "Orchid", "#ff9ae6", "#7c4dff"),
    ("theme_sunset", "Sunset", "#ffc04d", "#ff4f7b"),
    ("theme_ocean", "Ocean", "#4fe3ff", "#5468ff"),
    ("theme_ember", "Ember", "#ffd54f", "#ff5a36"),
    ("theme_mono", "Mono", "#ffffff", "#8fa3ad"),
]


def mix(c1, c2, t):
    a, b = (tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) for c in (c1, c2))
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def derived_theme(a, b):
    light = lambda c: mix(c, "#ffffff", 0.25)
    return dict(steps_start="#ff" + a[1:], steps_end="#ff" + b[1:], bat_start="#ff" + b[1:], bat_end="#ff" + a[1:],
                hr_start="#cc" + a[1:], hr_end="#cc" + b[1:], uv="#ff" + b[1:],
                steps_text="#ff" + light(a)[1:], bat_text="#ff" + light(b)[1:], hr_text="#b3" + light(a)[1:],
                uv_text="#ff" + light(b)[1:], hr_arrow="#ff" + mix(a, "#000000", 0.4)[1:],
                steps_icon="#ff" + a[1:], bat_icon="#e6" + b[1:], hr_icon="#ff" + mix(a, "#000000", 0.2)[1:],
                uv_icon="#ff" + b[1:])


THEMES = SAMSUNG_THEMES + [(k, label, derived_theme(a, b)) for k, label, a, b in EXTRA_THEMES]

# Top-right stats: Samsung's exercise / hourly-moves / calories colors (dot, text).
STAT_COLORS = [("#ff7efa55", "#e692fc6f"), ("#ff00aeff", "#e600aeff"), ("#ffff59de", "#e6ff59de")]

RV = ("(clamp([COMPLICATION.RANGED_VALUE_VALUE],[COMPLICATION.RANGED_VALUE_MIN],[COMPLICATION.RANGED_VALUE_MAX])"
      "-[COMPLICATION.RANGED_VALUE_MIN])/([COMPLICATION.RANGED_VALUE_MAX]-[COMPLICATION.RANGED_VALUE_MIN])")
GP = "clamp([COMPLICATION.GOAL_PROGRESS_VALUE],0,[COMPLICATION.GOAL_PROGRESS_TARGET_VALUE])/[COMPLICATION.GOAL_PROGRESS_TARGET_VALUE]"
HR_P = "clamp(([HEART_RATE] - 40) / 180, 0, 1)"  # Samsung's 40..220 bpm scale
UV_P = "clamp([WEATHER.UV_INDEX] / 11, 0, 1)"

# Weather icon per [WEATHER.CONDITION] value (the runtime's table); NIGHT_ICONS replace them at night.
WEATHER_ICONS = {1: "clear", 2: "cloudy", 3: "fog", 4: "heavy_rain", 5: "heavy_snow", 6: "rain", 7: "snow",
                 8: "clear", 9: "thunder", 10: "sleet", 11: "snow", 12: "rain", 13: "fog", 14: "partly_cloudy",
                 15: "wind"}
NIGHT_ICONS = {1: "night", 8: "night", 14: "partly_cloudy_night"}


def f(v):
    """The runtime parses geometry attributes as integers."""
    return str(round(v))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def polar(angle, r):
    a = math.radians(angle)
    return C + r * math.sin(a), C - r * math.cos(a)


def arc(d, a0, a1, w, color, ticks=False, sweep=None, fade=None):
    """One arc stroke. `sweep` (0..1 expression) fills it from a0. `fade` = ((x0, y0), (x1, y1))
    makes the stroke a white alpha gradient between those points, to be tinted by its part."""
    caps = f'cap="BUTT" dashIntervals="{TICKS}"' if ticks else 'cap="ROUND"'
    grad = ""
    if fade:
        (x0, y0), (x1, y1) = fade
        grad = (f'<LinearGradient startX="{f(x0)}" startY="{f(y0)}" endX="{f(x1)}" endY="{f(y1)}" '
                f'colors="#00ffffff #ffffffff" positions="0 1"/>')
    tf = f'<Transform target="endAngle" value="{esc(f"{a0} + ({sweep}) * {a1 - a0}")}"/>' if sweep else ""
    return (f'<Arc centerX="{C}" centerY="{C}" width="{f(d)}" height="{f(d)}" startAngle="{a0}" endAngle="{a1}">'
            f'<Stroke thickness="{f(w)}" color="{color}" {caps}>{grad}</Stroke>{tf}</Arc>')


def part_draw(content, tint=None, alpha=None):
    attrs = (f' tintColor="{tint}"' if tint else "") + (f' alpha="{alpha}"' if alpha is not None else "")
    return f'<PartDraw x="0" y="0" width="450" height="450"{attrs}>{content}</PartDraw>'


def group(*parts, alpha=255):
    """Full-screen group. Everything but the photo stays visible in always-on mode."""
    return f'<Group x="0" y="0" width="450" height="450" alpha="{alpha}">{"".join(parts)}</Group>'


def gradient_arc(d, a0, a1, w, start, end, fade, ticks=False, sweep=None):
    """Arc going from color `start` to `end` along the `fade` line. The runtime can't build a
    gradient from configuration colors, so: solid start underneath, plus a white alpha ramp tinted end."""
    return (part_draw(arc(d, a0, a1, w, start, ticks, sweep))
            + part_draw(arc(d, a0, a1, w, "#ffffffff", ticks, sweep, fade=fade), tint=end))


# Bundled Quicksand (res/font), one resource per weight. Quicksand has a Reserved Font Name and
# these are modified (static instances of the variable font), so they're renamed "BU Rounded".
FONTS = {"NORMAL": "rounded_medium", "MEDIUM": "rounded_medium",  # regular is too faint at watch size "SEMI_BOLD": "rounded_semibold",
         "BOLD": "rounded_bold", "STATS": "rounded_medium_bigdot", "CLOCK": "rounded_semibold",
         # Inter (OFL, no Reserved Font Name) for the bpm / UV text, where Quicksand reads poorly.
         "LABEL": "inter_medium", "LABEL_BOLD": "inter_bold"}
CLOCK_FONT = "rounded_semibold"
BULLET_SCALE = 1.6  # the stats' "•", enlarged in a copy of the medium weight (see make_stats_font)


def font(size, color, weight="BOLD"):
    return f'<Font family="{FONTS[weight]}" size="{f(size)}" color="{color}">'


def template(fmt, *exprs, shadow=True):
    params = "".join(f'<Parameter expression="{esc(e)}"/>' for e in exprs)
    tpl = f"<Template>{fmt}{params}</Template>"
    return f"{TEXT_SHADOW}{tpl}</Shadow>" if shadow else tpl


def curved(d, a0, a1, size, color, fmt, *exprs, ccw=False, align="CENTER", weight="BOLD", rotate=None, alpha=None):
    """Text along a circle of diameter d between angles a0 < a1. The circle is the baseline:
    clockwise text grows outward, ccw (upright at the bottom) grows inward. align START/END refer
    to a0/a1 either way. `rotate` is an expression (degrees) turning the text around the center."""
    direction = "CLOCKWISE"
    if ccw:  # the runtime sweeps counter-clockwise from startAngle, so start must be the larger angle
        direction, a0, a1 = "COUNTER_CLOCKWISE", a1, a0
        align = {"START": "END", "END": "START"}.get(align, align)
    tf = f'<Transform target="angle" value="{esc(rotate)}"/>' if rotate else ""
    tf += f'<Transform target="alpha" value="{esc(alpha)}"/>' if alpha else ""
    return (f'<PartText x="0" y="0" width="450" height="450">{tf}'
            f'<TextCircular centerX="{C}" centerY="{C}" width="{f(d)}" height="{f(d)}" startAngle="{f(a0)}" '
            f'endAngle="{f(a1)}" align="{align}" direction="{direction}" ellipsis="TRUE">'
            f'{font(size, color, weight)}{template(fmt, *exprs, shadow=color != INSIDE_TEXT)}</Font></TextCircular></PartText>')


def text(x, y, w, h, size, color, fmt, *exprs, align="START", weight="NORMAL"):
    return (f'<PartText x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}">'
            f'<Text align="{align}" ellipsis="TRUE">{font(size, color, weight)}{template(fmt, *exprs, shadow=color != INSIDE_TEXT)}</Font></Text></PartText>')


def image(x, y, w, h, resource, tint=None):
    tint = f' tintColor="{tint}"' if tint else ""
    return (f'<PartImage x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"{tint}>'
            f'<Image resource="{resource}"/></PartImage>')


def condition(cases, default=""):
    """cases: [(expression, xml)] - the first true one is drawn, else default."""
    exprs = "".join(f'<Expression name="c{i}">{esc(e)}</Expression>' for i, (e, _) in enumerate(cases))
    cmps = "".join(f'<Compare expression="c{i}">{x}</Compare>' for i, (_, x) in enumerate(cases))
    default = f"<Default>{default}</Default>" if default else ""
    return f"<Condition><Expressions>{exprs}</Expressions>{cmps}{default}</Condition>"


def s(*v):
    """Samsung 360px coordinates -> ours."""
    return [x * S for x in v]


def band_slot(slot_id, name, span, colors, fade, icon_rect, ccw, default):
    """Thick arc complication (steps / battery). The number rides just past the fill tip, or
    moves inside the fill (in black) once the fill passes TEXT_INSIDE_AFTER degrees."""
    a0, a1 = span
    start, end, text_color, icon_color = colors
    # Slot content is clipped to the BoundingArc region, so it has to cover the icon as well.
    ix, iy, iw, ih = icon_rect
    icon_angle = math.degrees(math.atan2(ix + iw / 2 - C, C - iy - ih / 2))
    lo, hi = min(a0, icon_angle) - 6, max(a1, icon_angle) + 6
    text_d = BAND_D  # curved text is centered on its circle, so this centers it in the band
    out = [f'<ComplicationSlot slotId="{slot_id}" displayName="{name}" x="0" y="0" width="450" height="450" '
           f'supportedTypes="RANGED_VALUE GOAL_PROGRESS SHORT_TEXT EMPTY">',
           f'<BoundingArc centerX="{C}" centerY="{C}" width="450" height="450" startAngle="{f(lo)}" endAngle="{f(hi)}" thickness="60"/>',
           default]
    icon = image(*icon_rect, "[COMPLICATION.MONOCHROMATIC_IMAGE]", tint=icon_color)
    track = (part_draw(arc(BAND_D, a0, a1, BAND_W, TRACK_SHADE))
             + group(gradient_arc(BAND_D, a0, a1, BAND_W, start, end, fade), alpha=TRACK_ALPHA))
    for kind, p in (("RANGED_VALUE", RV), ("GOAL_PROGRESS", GP), ("SHORT_TEXT", "0")):
        fill = gradient_arc(BAND_D, a0, a1, BAND_W, start, end, fade, sweep=p) if p != "0" else ""
        tip = f"({p}) * {a1 - a0}"
        # Past the tip the number takes the gradient's color at its position: start color, with
        # the end color faded in by how far along the arc the text sits.
        at = f"clamp(({tip} + {f(TEXT_GAP + 8)}) / {a1 - a0}, 0, 1)"
        outside = "".join(
            curved(text_d, a0, a0 + 80, NUM_SIZE, color, "%s", "[COMPLICATION.TEXT]", ccw=ccw, align="START",
                   rotate=f"{tip} + {f(TEXT_GAP)}", alpha=alpha)
            for color, alpha in ((start, None), (end, f"255 * {at}")))
        inside = curved(text_d, a0 - 80, a0, NUM_SIZE, INSIDE_TEXT, "%s", "[COMPLICATION.TEXT]",
                        ccw=ccw, align="END", rotate=f"{tip} + {2 if ccw else 0}")
        label = condition([(f"{tip} > {TEXT_INSIDE_AFTER}", inside)], outside) if p != "0" else outside
        out.append(f'<Complication type="{kind}">{group(track, fill, label, icon)}</Complication>')
    out.append("</ComplicationSlot>")
    return "\n".join(out)


def build():
    T = COL
    steps = band_slot(
        0, "slot_steps", STEPS, (T["steps_start"], T["steps_end"], T["steps_text"], T["steps_icon"]),
        ((C - BAND_D / 2, C), (C, C)), (5, 240, 22, 22), False,  # Samsung: s(4, 182, 20, 20), nudged clear of the round cap
        '<DefaultProviderPolicy defaultSystemProvider="STEP_COUNT" defaultSystemProviderType="GOAL_PROGRESS"/>')
    battery = band_slot(
        2, "slot_battery", BATTERY, (T["bat_start"], T["bat_end"], T["bat_text"], T["bat_icon"]),
        ((C, C), (C, C + BAND_D / 2)), (C + BAND_D / 2 - 11, 184, 22, 24), True,  # Samsung: s(340, 156, 11, 19); centered on the bar, wider
        '<DefaultProviderPolicy defaultSystemProvider="WATCH_BATTERY" defaultSystemProviderType="RANGED_VALUE"/>')

    # Heart rate: a fixed gradient scale (40..220 bpm) with an arrow marking the current rate and
    # the reading centered on the arrow.
    h0, h1 = HEART
    hr_angle = f"{h0} + {HR_P} * {h1 - h0}"
    arrow = part_draw(f'<RoundRectangle x="{f(C - 3 * S)}" y="{f(29 * S)}" width="{f(6 * S)}" height="{f(15 * S)}" '
                      f'cornerRadiusX="{f(3 * S)}" cornerRadiusY="{f(3 * S)}"><Fill color="{T["hr_arrow"]}"/></RoundRectangle>'
                      f'<Transform target="angle" value="{esc(hr_angle)}"/>')
    half = 19  # about half the width of "100 bpm", so the text stays inside the quadrant
    hr_text = curved(2 * 150, -half, half, SMALL_SIZE, T["hr_text"], "%d bpm", "[HEART_RATE]",
                     weight="LABEL", rotate=f"clamp({hr_angle}, {h0}, {h1})")
    heart = group(
        gradient_arc(TICK_D, h0, h1, TICK_W, T["hr_start"], T["hr_end"], ((C - TICK_D / 2, C), (C, C)), ticks=True),
        image(C - TICK_D / 2 - 15 * S / 2, 186 * S, 15 * S, 13 * S, "hr_icon", tint=T["hr_icon"]),  # centered under the ticks
        condition([("[HEART_RATE] > 0", arrow + hr_text)]))

    # UV: dim ticks with the index filled over them; the level word is centered on the fill tip.
    u0, u1 = UV
    uv_tip = f"{u0} + {UV_P} * {u1 - u0}"
    half = 24  # wide enough for "moderate" / "very high"
    uv_word = lambda word: curved(2 * 148, -half, half, SMALL_SIZE, T["uv_text"], word, ccw=True,
                                  weight="LABEL", rotate=f"clamp({uv_tip}, {u0}, {u1})")
    levels = [("[WEATHER.UV_INDEX] < 3", "low"), ("[WEATHER.UV_INDEX] < 6", "moderate"),
              ("[WEATHER.UV_INDEX] < 8", "high"), ("[WEATHER.UV_INDEX] < 11", "very high")]
    uv = group(condition([("[WEATHER.IS_AVAILABLE]", "".join([
        part_draw(arc(TICK_D, u0, u1, TICK_W, T["uv"], ticks=True), alpha=UV_DIM_ALPHA),
        part_draw(arc(TICK_D, u0, u1, TICK_W, T["uv"], ticks=True, sweep=UV_P)),
        text(312 * S - 8, 156 * S - 4, 22 * S + 16, 19 * S + 8, 17, T["uv_icon"], "UV", align="CENTER", weight="LABEL_BOLD"),
        condition([(e, uv_word(w)) for e, w in levels], uv_word("extreme"))]))]))

    # Date, weather icon and temperature on one curved line in the lower left (9 -> 6 o'clock).
    date_d, date_size, date_color = 2 * 204, 22 * S, "#b3ffffff"
    icon_at, icon_sz = -136, 30
    ix, iy = polar(icon_at, date_d / 2)
    weather_icon = condition(
        [(f"[WEATHER.CONDITION] == {c}" + (" && ![WEATHER.IS_DAY]" if night else ""),
          f'<PartImage x="{f(ix - icon_sz / 2)}" y="{f(iy - icon_sz / 2)}" width="{icon_sz}" height="{icon_sz}" '
          f'angle="{icon_at + 180}" tintColor="{date_color}"><Image resource="weather_{name}"/></PartImage>')
         for c, name, night in [(c, n, True) for c, n in NIGHT_ICONS.items()]
         + [(c, n, False) for c, n in sorted(WEATHER_ICONS.items())]])
    date = group(condition(
        [("[WEATHER.IS_AVAILABLE]", "".join([
            curved(date_d, icon_at + 8, -90, date_size, date_color, "%s, %s", "[DAY_OF_WEEK_S]", "[DAY]",
                   ccw=True, align="START", weight="NORMAL"),
            weather_icon,
            curved(date_d, -178, icon_at - 8, date_size, date_color, "%d°", "[WEATHER.TEMPERATURE]",
                   ccw=True, align="END", weight="NORMAL")]))],
        curved(date_d, -180, -90, date_size, date_color, "%s, %s", "[DAY_OF_WEEK_S]", "[DAY]", ccw=True, weight="NORMAL")))

    # Button under the clock (Samsung's "Work out" pill).
    bx, by, bw, bh = s(108, 226, 144, 42)
    pill = (f'<PartDraw x="0" y="0" width="{f(bw)}" height="{f(bh)}"><RoundRectangle x="0" y="0" width="{f(bw)}" '
            f'height="{f(bh)}" cornerRadiusX="{f(bh / 2)}" cornerRadiusY="{f(bh / 2)}"><Fill color="#38ffffff"/></RoundRectangle></PartDraw>')
    pill_text = text(8, (bh - 36) / 2, bw - 16, 36, 21, "#e6ffffff", "%s", "[COMPLICATION.TEXT]", align="CENTER", weight="MEDIUM")
    icon_sz = bh - 18
    pill_icon = image((bw - icon_sz) / 2, 9, icon_sz, icon_sz, "[COMPLICATION.MONOCHROMATIC_IMAGE]", tint="#e6ffffff")
    action = "\n".join([
        f'<ComplicationSlot slotId="5" displayName="slot_action" x="{f(bx)}" y="{f(by)}" width="{f(bw)}" height="{f(bh)}" '
        'supportedTypes="SHORT_TEXT LONG_TEXT MONOCHROMATIC_IMAGE EMPTY">',
        f'<BoundingBox x="0" y="0" width="{f(bw)}" height="{f(bh)}"/>',
        f'<Complication type="SHORT_TEXT">{pill}{pill_text}</Complication>',
        f'<Complication type="LONG_TEXT">{pill}{pill_text}</Complication>',
        f'<Complication type="MONOCHROMATIC_IMAGE">{pill}{pill_icon}</Complication>',
        "</ComplicationSlot>"])

    # Top-right stats: three slots side by side along r156 (12 -> 3 o'clock), each a dot + value.
    stat_d = 2 * 156 * S
    stats = []
    for n, (slot_id, (dot, color)) in enumerate(zip((6, 8, 9), STAT_COLORS)):
        # Between the steps arc's end cap and the battery icon; each "• value" centered in its third.
        a0 = 8 + n * 25.5
        a1 = a0 + 25.5
        body = group(curved(stat_d, a0, a1, 24, color, "• %s", "[COMPLICATION.TEXT]", weight="STATS"))
        stats.append("\n".join([
            f'<ComplicationSlot slotId="{slot_id}" displayName="slot_stats{n + 1}" x="0" y="0" width="450" height="450" '
            'supportedTypes="SHORT_TEXT RANGED_VALUE GOAL_PROGRESS EMPTY">',
            f'<BoundingArc centerX="{C}" centerY="{C}" width="450" height="450" startAngle="{a0 - 1}" endAngle="{a1 + 1}" thickness="56"/>',
            *(f'<Complication type="{k}">{body}</Complication>' for k in ("SHORT_TEXT", "RANGED_VALUE", "GOAL_PROGRESS")),
            "</ComplicationSlot>"]))

    # Round complication where Samsung has its activity heart: ring progress, icon over value.
    d = 70
    ox, oy = 309 - d / 2, 150 - d / 2
    ring_d, ring_w = d - 6, 5
    disc = part_draw(f'<Ellipse x="{f(ox)}" y="{f(oy)}" width="{d}" height="{d}"><Fill color="#1fffffff"/></Ellipse>')
    ring = lambda a1, color: (f'<Arc centerX="{f(ox + d / 2)}" centerY="{f(oy + d / 2)}" width="{ring_d}" height="{ring_d}" '
                              f'startAngle="0" endAngle="{a1}"><Stroke thickness="{ring_w}" color="{color}" cap="ROUND"/>')
    track = part_draw(ring(360, "#33ffffff") + "</Arc>")
    progress = lambda p: part_draw(ring(360, T["bat_start"])
                                   + f'<Transform target="endAngle" value="{esc(f"360 * ({p})")}"/></Arc>')
    small_icon = image(ox + d / 2 - 11, oy + 11, 22, 22, "[COMPLICATION.MONOCHROMATIC_IMAGE]", tint="#ffffffff")
    value = text(ox + 8, oy + 33, d - 16, 26, 20, "#ffffffff", "%s", "[COMPLICATION.TEXT]", align="CENTER", weight="BOLD")
    circle = lambda *parts: f"{group(disc, track, *parts)}"
    activity = "\n".join([
        f'<ComplicationSlot slotId="7" displayName="slot_circle" x="0" y="0" width="450" height="450" '
        'supportedTypes="RANGED_VALUE GOAL_PROGRESS SHORT_TEXT MONOCHROMATIC_IMAGE EMPTY">',
        f'<BoundingOval x="{f(ox)}" y="{f(oy)}" width="{d}" height="{d}"/>',
        f'<Complication type="RANGED_VALUE">{circle(progress(RV), small_icon, value)}</Complication>',
        f'<Complication type="GOAL_PROGRESS">{circle(progress(GP), small_icon, value)}</Complication>',
        f'<Complication type="SHORT_TEXT">{circle(small_icon, value)}</Complication>',
        f'<Complication type="MONOCHROMATIC_IMAGE">{circle(image(ox + d / 2 - 16, oy + d / 2 - 16, 32, 32, "[COMPLICATION.MONOCHROMATIC_IMAGE]", tint="#ffffffff"))}</Complication>',
        "</ComplicationSlot>"])

    options = "\n".join(f'<ColorOption id="{i}" displayName="{key}" colors="{" ".join(c[k] for k in COLOR_KEYS)}"/>'
                        for i, (key, _, c) in enumerate(THEMES))

    ampm = text(*s(81, 113, 114, 36), 28 * S, "#d4ffffff", "%s", "[AMPM_STRING]", weight="BOLD")
    # Clock: hours and minutes either side of a separate colon. Like Samsung's, the colon is white for
    # the first 500ms of each second and 50% white for the rest (steady white in always-on mode).
    cy, ch, size, colon_w = 168, 124, 106, 26
    # Plain text rather than DigitalClock/TimeText: the runtime ignores Shadow on TimeText.
    digits = lambda expr, x, w, align: text(x, cy, w, ch, size, "#ffffffff", "%02d", expr, align=align, weight="CLOCK")
    hours = condition([("[IS_24_HOUR_MODE]", digits("[HOUR_0_23]", 0, C - colon_w / 2, "END"))],
                      digits("[HOUR_1_12]", 0, C - colon_w / 2, "END"))
    colon = lambda color: text(C - colon_w / 2, cy, colon_w, ch, size, color, ":", align="CENTER", weight="CLOCK")
    clock = "\n".join([
        hours + digits("[MINUTE]", C + colon_w / 2, C - colon_w / 2, "START"),
        # Only one colon is drawn at a time (a white one underneath would fringe the gray one).
        condition([("[MILLISECOND] >= 500",
                    '<Group x="0" y="0" width="450" height="450"><Variant mode="AMBIENT" target="alpha" value="0"/>'
                    + colon("#80ffffff") + "</Group>"
                    + '<Group x="0" y="0" width="450" height="450" alpha="0"><Variant mode="AMBIENT" target="alpha" value="255"/>'
                    + colon("#ffffffff") + "</Group>")],
                  colon("#ffffffff")),
        # The runtime only redraws about once a second unless something animates, so loop an
        # invisible animation (interactive mode only) to get frames at the 500ms mark.
        '<Group x="0" y="0" width="450" height="450"><Variant mode="AMBIENT" target="alpha" value="0"/>'
        '<PartDraw x="0" y="0" width="2" height="2" alpha="0"><Rectangle x="0" y="0" width="1" height="1">'
        '<Fill color="#00000000"/></Rectangle><Transform target="x" value="1">'
        '<Animation interpolation="LINEAR" controls="ON_VISIBLE" duration="1" fps="4" repeat="-1"/>'
        '</Transform></PartDraw></Group>'])
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!-- GENERATED by tools/generate.py - edit that instead. -->
<!-- Photo Dash Plus: Health Dashboard+ style. Steps/heart rate on the left, battery/UV on the right. -->
<WatchFace width="450" height="450">
<Metadata key="CLOCK_TYPE" value="DIGITAL"/>
<Metadata key="PREVIEW_TIME" value="10:08:32"/>
<UserConfigurations>
<PhotosConfiguration id="photoConfig" configType="SINGLE"/>
<ColorConfiguration id="themeColor" defaultValue="0" displayName="colors_label" screenReaderText="colors_label">
{options}
</ColorConfiguration>
<!-- A list rather than two BooleanConfigurations: the system editor clips boolean switches. -->
<ListConfiguration id="arcs" displayName="arcs_label" screenReaderText="arcs_label" defaultValue="0">
<ListOption id="0" displayName="arcs_both" screenReaderText="arcs_both"/>
<ListOption id="1" displayName="arcs_heart" screenReaderText="arcs_heart"/>
<ListOption id="2" displayName="arcs_uv" screenReaderText="arcs_uv"/>
<ListOption id="3" displayName="arcs_none" screenReaderText="arcs_none"/>
</ListConfiguration>
</UserConfigurations>
<Scene backgroundColor="#ff000000">
<!-- Dimmed photo: alpha 0-255 (0 black, 255 full). Hidden in ambient. -->
<Group x="0" y="0" width="450" height="450" name="photo" alpha="{PHOTO_ALPHA}">
<Variant mode="AMBIENT" target="alpha" value="0"/>
<PartImage x="0" y="0" width="450" height="450"><Photos source="[CONFIGURATION.photoConfig]" defaultImageResource="default_image"/></PartImage>
</Group>
{steps}

{battery}

{action}

{stats[0]}

{activity}

{stats[1]}

{stats[2]}

<ListConfiguration id="arcs"><ListOption id="0">{heart}</ListOption><ListOption id="1">{heart}</ListOption></ListConfiguration>

<ListConfiguration id="arcs"><ListOption id="0">{uv}</ListOption><ListOption id="2">{uv}</ListOption></ListConfiguration>

{date}
<!-- AM/PM only in 12-hour mode. -->
{condition([("![IS_24_HOUR_MODE]", ampm)])}
{clock}
</Scene>
</WatchFace>
'''


def heart_points(n=720):
    pts = []
    for i in range(n + 1):
        t = 2 * math.pi * i / n
        pts.append((16 * math.sin(t) ** 3,
                    -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))))
    return pts


def weather_icons(size=30, ss=8):
    """Simple white weather glyphs, drawn on a 32-unit grid."""
    from PIL import Image, ImageDraw

    def canvas():
        img = Image.new("L", (32 * ss, 32 * ss), 0)
        return img, ImageDraw.Draw(img)

    u = lambda *v: [x * ss for x in v]

    def cloud(d, dy=0, fill=255):
        for x, y, r in ((11, 17, 6), (18, 13, 8), (24, 18, 5)):
            d.ellipse(u(x - r, y - r + dy, x + r, y + r + dy), fill=fill)
        d.rounded_rectangle(u(5, 17 + dy, 29, 23 + dy), radius=3 * ss, fill=fill)

    def sun(d, cx=16, cy=16, r=6):
        d.ellipse(u(cx - r, cy - r, cx + r, cy + r), fill=255)
        for k in range(8):
            a = math.radians(k * 45)
            d.line(u(cx + (r + 3) * math.cos(a), cy + (r + 3) * math.sin(a),
                     cx + (r + 7) * math.cos(a), cy + (r + 7) * math.sin(a)), fill=255, width=round(2.2 * ss))

    def drops(d, xs, length):
        for x in xs:
            d.line(u(x, 25, x - 2, 25 + length), fill=255, width=round(2.2 * ss))

    def flakes(d, pts):
        for x, y in pts:
            d.ellipse(u(x - 1.6, y - 1.6, x + 1.6, y + 1.6), fill=255)

    icons = {}
    img, d = canvas(); sun(d); icons["clear"] = img
    img, d = canvas()
    d.ellipse(u(6, 6, 26, 26), fill=255); d.ellipse(u(12, 2, 32, 22), fill=0); icons["night"] = img
    img, d = canvas(); cloud(d, 2); icons["cloudy"] = img
    img, d = canvas(); sun(d, 12, 11, 5); cloud(d, 6, 0); cloud(d, 7); icons["partly_cloudy"] = img
    img, d = canvas()
    d.ellipse(u(3, 2, 19, 18), fill=255); d.ellipse(u(8, -1, 24, 15), fill=0); cloud(d, 6, 0); cloud(d, 7)
    icons["partly_cloudy_night"] = img
    img, d = canvas(); cloud(d, -4); drops(d, (10, 22), 4); flakes(d, ((16, 27), (16, 32))); icons["sleet"] = img
    img, d = canvas()
    for y, x0, x1 in ((9, 5, 27), (15, 3, 29), (21, 5, 27), (27, 8, 24)):
        d.line(u(x0, y, x1, y), fill=255, width=round(2.4 * ss))
    icons["fog"] = img
    img, d = canvas(); cloud(d, -4); drops(d, (11, 17, 23), 4); icons["rain"] = img
    img, d = canvas(); cloud(d, -4); drops(d, (8, 13, 18, 23, 28), 6); icons["heavy_rain"] = img
    img, d = canvas(); cloud(d, -4); flakes(d, ((11, 26), (17, 29), (23, 26))); icons["snow"] = img
    img, d = canvas(); cloud(d, -4); flakes(d, ((8, 25), (14, 28), (20, 25), (26, 28), (11, 31), (23, 31))); icons["heavy_snow"] = img
    img, d = canvas(); cloud(d, -4)
    d.polygon(u(17, 21, 11, 28, 15, 28, 13, 32, 20, 24, 16, 24, 18, 21), fill=255); icons["thunder"] = img
    img, d = canvas()
    for y, x1 in ((10, 22), (16, 27), (22, 19)):
        d.line(u(3, y, x1, y), fill=255, width=round(2.4 * ss))
        d.arc(u(x1 - 4, y - 8, x1 + 4, y), 270, 90 + 90, fill=255, width=round(2.4 * ss))
    icons["wind"] = img
    out = {}
    for name, img in icons.items():
        rgba = Image.new("RGBA", img.size, (255, 255, 255, 0))
        rgba.putalpha(img)
        out[name] = rgba.resize((size, size), Image.LANCZOS)
    return out


def write_images():
    from PIL import Image, ImageDraw

    drawable = RES / "drawable"
    w, h = round(15 * S), round(13 * S)
    ss = 8
    xs, ys = zip(*heart_points())
    img = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(img).polygon([((x - min(xs)) * w * ss / (max(xs) - min(xs)), (y - min(ys)) * h * ss / (max(ys) - min(ys)))
                                 for x, y in heart_points()], fill=255)
    icon = Image.new("RGBA", img.size, (255, 255, 255, 0))
    icon.putalpha(img)
    icon.resize((w, h), Image.LANCZOS).save(drawable / "hr_icon.png")
    # Shown when no background photo is picked.
    Image.new("RGB", (450, 450), (0, 0, 0)).save(drawable / "default_image.png")
    for name, im in weather_icons().items():
        im.save(drawable / f"weather_{name}.png")
    for old in drawable.glob("heart_*.png"):
        old.unlink()


def make_stats_font():
    """The medium weight with a bigger bullet, so the stats' dot stays part of the centered text."""
    from fontTools.pens.transformPen import TransformPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.ttLib import TTFont

    font_dir = RES / "font"
    font = TTFont(font_dir / f"{FONTS['MEDIUM']}.ttf")
    name = font.getBestCmap()[0x2022]
    glyf, hmtx = font["glyf"], font["hmtx"]
    glyph = glyf[name]
    glyph.recalcBounds(glyf)
    cx, cy = (glyph.xMin + glyph.xMax) / 2, (glyph.yMin + glyph.yMax) / 2
    advance, lsb = hmtx[name]
    extra = (glyph.xMax - glyph.xMin) * (BULLET_SCALE - 1)
    dx = cx + extra / 2 - cx * BULLET_SCALE
    pen = TTGlyphPen(glyf)
    glyph.draw(TransformPen(pen, (BULLET_SCALE, 0, 0, BULLET_SCALE, dx, cy - cy * BULLET_SCALE)), glyf)
    glyf[name] = pen.glyph()
    glyf[name].recalcBounds(glyf)
    hmtx[name] = (round(advance + extra), glyf[name].xMin)
    for rec in font["name"].names:  # a modified copy gets its own name
        if rec.nameID in (1, 3, 4, 6, 16):
            rec.string = str(rec).replace("BU Rounded", "BU Rounded BigDot")
    font.save(font_dir / f"{FONTS['STATS']}.ttf")


if __name__ == "__main__":
    (RES / "raw/watchface.xml").write_text(build())
    write_images()
    make_stats_font()
    print("wrote", RES / "raw/watchface.xml")
