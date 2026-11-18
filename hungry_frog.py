#!/usr/bin/env python3
"""
Hungry Frog - a typing game for kids (and grown-ups).

The frog is hungry! Bugs fly over the pond with letters on their bellies.
Type the letter and the frog catches the bug with its tongue.

Levels go from the home row (F and J) all the way to whole words.
"""
import array
import json
import math
import os
import random
import sys

import pygame

W, H = 1280, 800
FPS = 60
FROZEN = getattr(sys, "frozen", False)
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(getattr(sys, "_MEIPASS", HERE), "assets")


def _save_dir():
    """Next to the script while developing; in the user's AppData folder for the .exe."""
    if FROZEN:
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        d = os.path.join(base, "HungryFrog")
        os.makedirs(d, exist_ok=True)
        return d
    return HERE


SAVE_PATH = os.path.join(_save_dir(), "save.json")

# ---------------------------------------------------------------- language
LANG = "km"   # "km" = Khmer, "en" = English


def tr(en, km):
    return km if LANG == "km" else en


def set_lang(lang):
    global LANG
    LANG = lang if lang in ("km", "en") else "km"

# ---------------------------------------------------------------- colors
WHITE = (255, 255, 255)
INK = (45, 45, 70)
CREAM = (255, 249, 232)
SKY_TOP = (110, 195, 255)
SKY_BOT = (205, 240, 255)
WATER_TOP = (95, 190, 225)
WATER_BOT = (45, 125, 185)
PAD = (95, 180, 75)
PAD_DARK = (60, 140, 55)

FROG_G = (120, 205, 85)
FROG_D = (55, 140, 60)
FROG_L = (175, 232, 125)
FROG_BELLY = (232, 248, 188)

# ---------------------------------------------------------------- fingers
FINGERS = [
    ("Left Pinky", (255, 105, 170), "qaz1"),
    ("Left Ring", (255, 155, 50), "wsx2"),
    ("Left Middle", (240, 200, 30), "edc3"),
    ("Left Index", (100, 200, 70), "rfvtgb45"),
    ("Right Index", (40, 195, 200), "yhnujm67"),
    ("Right Middle", (75, 135, 250), "ik,8"),
    ("Right Ring", (160, 105, 240), "ol.9"),
    ("Right Pinky", (240, 75, 85), "p;/0'"),
    ("Thumbs", (150, 160, 185), " "),
]
FINGER_OF = {}
for _i, (_n, _c, _keys) in enumerate(FINGERS):
    for _k in _keys:
        FINGER_OF[_k] = _i


def finger_color(ch):
    return FINGERS[FINGER_OF.get(ch, 8)][1]


FINGER_KM = ["កូនដៃឆ្វេង", "នាងដៃឆ្វេង", "ម្រាមកណ្ដាលឆ្វេង", "ម្រាមចង្អុលឆ្វេង",
             "ម្រាមចង្អុលស្ដាំ", "ម្រាមកណ្ដាលស្ដាំ", "នាងដៃស្ដាំ", "កូនដៃស្ដាំ", "មេដៃ"]


def finger_name(fi):
    return tr(FINGERS[fi][0], FINGER_KM[fi])


# ---------------------------------------------------------------- levels
HOME = "asdfghjkl;"
TOP = "qwertyuiop"
ALL = "abcdefghijklmnopqrstuvwxyz"

LEVELS = [
    dict(name="F and J", letters="fj", new="fj",
         tip="Find the little bumps on F and J. Your pointer fingers live there!"),
    dict(name="D and K", letters="fjdk", new="dk",
         tip="Middle fingers press D and K."),
    dict(name="S and L", letters="fjdksl", new="sl",
         tip="Ring fingers press S and L."),
    dict(name="A and ;", letters="asdfjkl;", new="a;",
         tip="Pinky fingers press A and ;"),
    dict(name="G and H", letters=HOME, new="gh",
         tip="Pointer fingers stretch to G and H, then go back home!"),
    dict(name="Home Row Words", words=[
        "ask", "dad", "sad", "add", "all", "fall", "hall", "lad", "glad", "flag",
        "flash", "salad", "gas", "has", "half", "shall", "dash", "lass", "jag", "alas"],
         tip="Now type whole words! Keep your fingers on the home row."),
    dict(name="E and I", letters=HOME + "ei", new="ei",
         tip="Middle fingers reach UP to E and I."),
    dict(name="R and U", letters=HOME + "eiru", new="ru",
         tip="Pointer fingers reach UP to R and U."),
    dict(name="T and Y", letters=HOME + "eiruty", new="ty",
         tip="Pointer fingers stretch UP to T and Y."),
    dict(name="W and O", letters=HOME + "eirutywo", new="wo",
         tip="Ring fingers reach UP to W and O."),
    dict(name="Q and P", letters=HOME + TOP, new="qp",
         tip="Pinky fingers reach UP to Q and P."),
    dict(name="Top Row Words", words=[
        "tree", "frog", "fly", "water", "pot", "tip", "rope", "house", "road", "story",
        "toad", "leaf", "rest", "quiet", "party", "pie", "yes", "sit", "fish", "day",
        "pool", "star", "wet", "old", "tail", "split", "sweet"],
         tip="Words with the home row AND the top row."),
    dict(name="V and M", letters=HOME + TOP + "vm", new="vm",
         tip="Pointer fingers reach DOWN to V and M."),
    dict(name="C and N", letters=HOME + TOP + "vmcn", new="cn",
         tip="C is the left middle finger. N is the right pointer finger."),
    dict(name="X, Z and B", letters=ALL, new="xzb",
         tip="X: left ring. Z: left pinky. B: left pointer."),
    dict(name="All Letters", letters=ALL, new="",
         tip="Every letter! Always go back to the home row."),
    dict(name="Animal Words", words=[
        "cat", "dog", "cow", "pig", "hen", "fox", "bee", "ant", "owl", "bat", "duck",
        "frog", "fish", "bear", "lion", "zebra", "snake", "mouse", "horse", "sheep",
        "tiger", "panda", "monkey", "rabbit", "turtle"],
         tip="Catch the animal words!"),
    dict(name="Frog Master", words=[
        "jump", "quick", "brown", "lazy", "happy", "pond", "lily", "bubble", "splash",
        "yummy", "buzzing", "flying", "hungry", "green", "catch", "tongue", "rainbow",
        "garden", "sunny", "wiggle", "dragonfly", "butterfly", "ladybug", "keyboard",
        "practice", "amazing"], goal=15,
         tip="The final challenge. Can you become the Frog Master?"),
]

LEVELS_KM = [
    ("F និង J", "រកស្នាមប៉ោងតូចៗនៅលើ F និង J។ ម្រាមចង្អុលរបស់អ្នករស់នៅទីនោះ!"),
    ("D និង K", "ម្រាមកណ្ដាលចុច D និង K។"),
    ("S និង L", "នាងដៃចុច S និង L។"),
    ("A និង ;", "កូនដៃចុច A និង ;"),
    ("G និង H", "ម្រាមចង្អុលលាតទៅ G និង H រួចត្រឡប់មកផ្ទះវិញ!"),
    ("ពាក្យជួរដើម", "ឥឡូវវាយពាក្យទាំងមូល! ទុកម្រាមដៃនៅលើជួរដើម។"),
    ("E និង I", "ម្រាមកណ្ដាលលើកឡើងទៅ E និង I។"),
    ("R និង U", "ម្រាមចង្អុលលើកឡើងទៅ R និង U។"),
    ("T និង Y", "ម្រាមចង្អុលលាតឡើងទៅ T និង Y។"),
    ("W និង O", "នាងដៃលើកឡើងទៅ W និង O។"),
    ("Q និង P", "កូនដៃលើកឡើងទៅ Q និង P។"),
    ("ពាក្យជួរលើ", "ពាក្យដែលប្រើជួរដើម និងជួរលើ។"),
    ("V និង M", "ម្រាមចង្អុលចុះក្រោមទៅ V និង M។"),
    ("C និង N", "C ប្រើម្រាមកណ្ដាលឆ្វេង។ N ប្រើម្រាមចង្អុលស្ដាំ។"),
    ("X, Z និង B", "X ប្រើនាងដៃឆ្វេង។ Z ប្រើកូនដៃឆ្វេង។ B ប្រើម្រាមចង្អុលឆ្វេង។"),
    ("អក្សរទាំងអស់", "អក្សរទាំងអស់! ត្រឡប់មកជួរដើមជានិច្ច។"),
    ("ពាក្យសត្វ", "ចាប់ពាក្យឈ្មោះសត្វ!"),
    ("មេកង្កែប", "ការប្រកួតចុងក្រោយ។ តើអ្នកអាចក្លាយជាមេកង្កែបបានទេ?"),
]
for _lv, (_n, _t) in zip(LEVELS, LEVELS_KM):
    _lv["km"], _lv["tip_km"] = _n, _t


def level_name(lv):
    return tr(lv["name"], lv["km"])


def level_tip(lv):
    return tr(lv.get("tip", ""), lv.get("tip_km", ""))


SPEEDS = [("Slow", "យឺត"), ("Medium", "មធ្យម"), ("Fast", "លឿន")]
SPEED_DESC = [("little kids", "ក្មេងតូច"), ("big kids", "ក្មេងធំ"), ("grown-ups", "មនុស្សធំ")]


def speed_name(i):
    return tr(*SPEEDS[i])


YUM_WORDS = [("Yum!", "ឆ្ងាញ់!"), ("Tasty!", "ឆ្ងាញ់ណាស់!"), ("Gulp!", "អឹក!"),
             ("Nom nom!", "ញ៉ាំៗ!"), ("Crunch!", "ក្រុប!"), ("Yummy!", "ល្អណាស់!")]
COMBO_WORDS = {5: ("Great!", "ពូកែ!"), 10: ("Awesome!", "អស្ចារ្យ!"), 15: ("Super Frog!", "កង្កែបកំពូល!"),
               20: ("Amazing!", "ល្អឥតខ្ចោះ!"), 30: ("Typing Star!", "តារាវាយអក្សរ!"),
               40: ("Unstoppable!", "ឈប់មិនបាន!")}
GOOD_WORDS = [("Yes!", "ត្រូវហើយ!"), ("Good!", "ល្អ!"), ("Great!", "ពូកែ!"), ("Super!", "អស្ចារ្យ!")]

# ---------------------------------------------------------------- helpers


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_col(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def pastel(c, k=0.6):
    return lerp_col(c, WHITE, k)


def darker(c, k=0.3):
    return lerp_col(c, (0, 0, 0), k)


def ell(surf, color, cx, cy, w, h, width=0):
    if w < 1 or h < 1:
        return
    pygame.draw.ellipse(surf, color, pygame.Rect(round(cx - w / 2), round(cy - h / 2),
                                                 round(w), round(h)), width)


def circ(surf, color, cx, cy, r, width=0):
    pygame.draw.circle(surf, color, (round(cx), round(cy)), max(1, round(r)), width)


def rrect(surf, color, rect, radius, width=0):
    pygame.draw.rect(surf, color, rect, width, border_radius=int(radius))


def alpha_fill(surf, color, alpha, rect=None):
    rect = rect or surf.get_rect()
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    s.fill((*color, alpha))
    surf.blit(s, rect.topleft)


def vgradient(surf, rect, c1, c2):
    x, y, w, h = rect
    for i in range(h):
        pygame.draw.line(surf, lerp_col(c1, c2, i / max(1, h - 1)), (x, y + i), (x + w - 1, y + i))


def star_points(cx, cy, R, r=None, rot=-math.pi / 2):
    r = r if r is not None else R * 0.47
    pts = []
    for i in range(10):
        a = rot + i * math.pi / 5
        rad = R if i % 2 == 0 else r
        pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
    return pts


def draw_star(surf, cx, cy, R, color=(255, 215, 50), outline=(205, 135, 20)):
    pygame.draw.polygon(surf, outline, star_points(cx, cy, R + 4))
    pygame.draw.polygon(surf, color, star_points(cx, cy, R))
    pygame.draw.polygon(surf, lerp_col(color, WHITE, 0.5),
                        star_points(cx - R * 0.15, cy - R * 0.15, R * 0.35))


def draw_heart(surf, cx, cy, size, color=(255, 80, 110), outline=(160, 30, 70)):
    r = size * 0.55
    for col, g in ((outline, 2.5), (color, 0)):
        rr = r + g
        circ(surf, col, cx - r * 0.9, cy - r * 0.3, rr)
        circ(surf, col, cx + r * 0.9, cy - r * 0.3, rr)
        pygame.draw.polygon(surf, col, [(cx - r * 1.85 - g, cy), (cx + r * 1.85 + g, cy),
                                        (cx, cy + r * 2.1 + g * 1.6)])
    circ(surf, lerp_col(color, WHITE, 0.6), cx - r * 1.0, cy - r * 0.55, r * 0.3)


# ---------------------------------------------------------------- fonts / text
_fonts = {}
_text_cache = {}


def is_khmer(ch):
    return "\u1780" <= ch <= "\u17ff" or "\u19e0" <= ch <= "\u19ff"


def font(size, title=False, khmer=False):
    key = (size, title, khmer)
    f = _fonts.get(key)
    if f:
        return f
    try:
        if khmer:
            f = pygame.font.Font(os.path.join(ASSETS, "NotoSansKhmer-Black.ttf" if title else
                                              "NotoSansKhmer-Bold.ttf"), max(8, int(size * 0.9)))
            try:
                f.set_script("Khmr")
            except Exception:
                pass
        else:
            f = pygame.font.Font(os.path.join(ASSETS, "LuckiestGuy-Regular.ttf" if title else "Fredoka.ttf"), size)
            if not title:
                f.set_bold(True)
    except Exception:
        f = pygame.font.SysFont("dejavusans", size, bold=True)
    _fonts[key] = f
    return f


def text_runs(text):
    """Split text into runs of Khmer / non-Khmer characters (spaces join the current run)."""
    runs = []
    for ch in text:
        k = is_khmer(ch) if ch != " " else (runs[-1][0] if runs else False)
        if runs and runs[-1][0] == k:
            runs[-1][1] += ch
        else:
            runs.append([k, ch])
    return runs


def render_mixed(text, size, color, title=False):
    if not any(is_khmer(c) for c in text):
        return font(size, title).render(text, True, color)
    parts = []
    for k, run in text_runs(text):
        f = font(size, title, k)
        parts.append((f, f.render(run, True, color)))
    asc = max(f.get_ascent() for f, _ in parts)
    h = max(asc - f.get_ascent() + p.get_height() for f, p in parts)
    w = sum(p.get_width() for _, p in parts)
    surf = pygame.Surface((max(1, w), max(1, h)), pygame.SRCALPHA)
    x = 0
    for f, p in parts:
        surf.blit(p, (x, asc - f.get_ascent()))
        x += p.get_width()
    return surf


def text_width(text, size, title=False):
    return sum(font(size, title, k).size(run)[0] for k, run in text_runs(text))


def text_surf(text, size, color, outline=None, ow=3, title=False):
    key = (text, size, color, outline, ow, title)
    s = _text_cache.get(key)
    if s is not None:
        return s
    base = render_mixed(text, size, color, title)
    if outline:
        o = render_mixed(text, size, outline, title)
        s = pygame.Surface((base.get_width() + ow * 2, base.get_height() + ow * 2), pygame.SRCALPHA)
        for dx in range(-ow, ow + 1):
            for dy in range(-ow, ow + 1):
                if dx * dx + dy * dy <= ow * ow + 1:
                    s.blit(o, (dx + ow, dy + ow))
        s.blit(base, (ow, ow))
    else:
        s = base
    if len(_text_cache) > 800:
        _text_cache.clear()
    _text_cache[key] = s
    return s


def draw_text(surf, text, size, color, pos, anchor="center", outline=None, ow=3, title=False,
              scale=1.0, max_w=None):
    s = text_surf(text, size, color, outline, ow, title)
    if max_w and s.get_width() > max_w:
        scale = scale * max_w / s.get_width()
    if scale != 1.0:
        s = pygame.transform.smoothscale_by(s, max(0.05, scale))
    r = s.get_rect()
    setattr(r, anchor, (round(pos[0]), round(pos[1])))
    surf.blit(s, r)
    return r


def wrap(text, size, maxw):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if text_width(test, size) <= maxw:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- sound
class Sfx:
    def __init__(self):
        self.sounds = {}
        try:
            init = pygame.mixer.get_init()
            if not init:
                pygame.mixer.init(44100, -16, 1, 512)
                init = pygame.mixer.get_init()
        except Exception:
            return
        if not init or init[1] != -16:
            return
        self.sr, _, self.ch = init
        mk = self.make
        self.sounds = {
            "slurp": mk([(320, 1250, 0.09)], 0.22),
            "gulp": mk([(260, 90, 0.16)], 0.45),
            "wrong": mk([(190, 150, 0.16)], 0.12, square=True),
            "escape": mk([(700, 280, 0.32)], 0.18),
            "click": mk([(880, 880, 0.04)], 0.15),
            "step": mk([(660, 990, 0.08)], 0.22),
            "star": mk([(880, 880, 0.07), (1320, 1320, 0.18)], 0.25),
            "combo": mk([(784, 784, 0.07), (1047, 1568, 0.16)], 0.22),
            "win": mk([(523, 523, 0.1), (659, 659, 0.1), (784, 784, 0.1), (1047, 1047, 0.32)], 0.28),
            "lose": mk([(440, 420, 0.18), (370, 350, 0.18), (300, 220, 0.4)], 0.22),
            "go": mk([(523, 523, 0.08), (1047, 1047, 0.2)], 0.22),
        }

    def make(self, parts, vol=0.3, square=False):
        buf = array.array("h")
        sr = self.sr
        for f0, f1, dur in parts:
            n = int(sr * dur)
            ph = 0.0
            for i in range(n):
                k = i / n
                ph += 2 * math.pi * (f0 + (f1 - f0) * k) / sr
                v = math.sin(ph)
                if square:
                    v = 0.6 if v > 0 else -0.6
                env = min(1.0, i / (sr * 0.005)) * (1 - k) ** 1.3
                s = int(v * env * vol * 32767)
                for _ in range(self.ch):
                    buf.append(s)
        return pygame.mixer.Sound(buffer=buf.tobytes())

    def play(self, name):
        s = self.sounds.get(name)
        if s:
            s.play()


# ---------------------------------------------------------------- save
def new_student():
    return {"stars": {}, "speed": 0, "missed": {}, "lesson_done": False}


_DATA = {"students": {}, "order": [], "last": None, "lang": "km"}


def load_data():
    d = {"students": {}, "order": [], "last": None, "lang": "km"}
    raw = None
    try:
        with open(SAVE_PATH, encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        pass
    if isinstance(raw, dict):
        if "students" in raw:
            d.update(raw)
        elif raw.get("stars") or raw.get("lesson_done"):   # old one-player save file
            st = new_student()
            st.update({k: raw[k] for k in st if k in raw})
            d["students"]["Player 1"] = st
            d["order"] = ["Player 1"]
            d["last"] = "Player 1"
    for name, st in list(d["students"].items()):
        for k, v in new_student().items():
            st.setdefault(k, v)
        if name not in d["order"]:
            d["order"].append(name)
    d["order"] = [n for n in d["order"] if n in d["students"]]
    return d


def write_save(_=None):
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(_DATA, f, indent=1, ensure_ascii=False)
    except Exception:
        pass


def total_stars(st):
    return sum(st["stars"].values())


def first_letter(name):
    """First letter of a name, keeping Khmer vowel signs / subscripts attached."""
    if not name:
        return "?"
    out = name[0]
    for ch in name[1:]:
        if out.endswith("\u17d2") or "\u17b6" <= ch <= "\u17d3" or ch == "\u17dd":
            out += ch
        else:
            break
    return out.upper()


def level_unlocked(save, i):
    return i == 0 or save["stars"].get(str(i - 1), 0) >= 1


# ---------------------------------------------------------------- bugs
BUG_KINDS = ["fly", "bee", "lady", "bfly_pink", "bfly_blue"]
_bug_frames = {}
BUG_AX, BUG_AY = 60, 58  # anchor (body centre) inside the sprite


def make_bug_frames(kind):
    frames = []
    for i in range(6):
        f = i / 5
        s = pygame.Surface((120, 110), pygame.SRCALPHA)
        cx, cy = BUG_AX, BUG_AY
        wing = pygame.Surface((120, 110), pygame.SRCALPHA)
        if kind.startswith("bfly"):
            c1, c2 = ((255, 120, 190), (255, 225, 90)) if kind == "bfly_pink" else \
                ((90, 165, 255), (255, 255, 255))
            ww = 0.3 + 0.7 * f
            for side in (-1, 1):
                ell(s, darker(c1, 0.35), cx + side * 24 * ww, cy - 18, 50 * ww + 5, 58)
                ell(s, c1, cx + side * 24 * ww, cy - 18, 46 * ww, 53)
                ell(s, c2, cx + side * 28 * ww, cy - 24, 18 * ww, 18)
                ell(s, darker(c1, 0.35), cx + side * 18 * ww, cy + 16, 36 * ww + 5, 40)
                ell(s, lerp_col(c1, c2, 0.4), cx + side * 18 * ww, cy + 16, 32 * ww, 35)
            ell(s, (70, 50, 70), cx, cy, 16, 46)
            circ(s, (70, 50, 70), cx, cy - 24, 10)
            for side in (-1, 1):
                pygame.draw.line(s, (70, 50, 70), (cx + side * 4, cy - 30), (cx + side * 14, cy - 46), 3)
                circ(s, (70, 50, 70), cx + side * 14, cy - 46, 4)
                circ(s, WHITE, cx + side * 4, cy - 26, 4)
                circ(s, INK, cx + side * 4, cy - 25, 2)
            frames.append(s)
            continue
        # see-through flapping wings
        for side in (-1, 1):
            wy = cy - 6 - 22 * f
            ell(wing, (180, 225, 255, 210), cx + side * 31, wy, 42, 26 + 6 * f)
            ell(wing, (235, 248, 255, 170), cx + side * 31, wy, 36, 20 + 6 * f)
        s.blit(wing, (0, 0))
        if kind == "fly":
            body, outline = (100, 115, 150), (60, 70, 100)
            circ(s, outline, cx, cy, 27)
            circ(s, body, cx, cy, 25)
            circ(s, lerp_col(body, WHITE, 0.35), cx - 9, cy - 10, 7)
            eye_c = (225, 70, 80)
            for side in (-1, 1):
                circ(s, darker(eye_c, 0.3), cx + side * 13, cy - 22, 12)
                circ(s, eye_c, cx + side * 13, cy - 22, 10)
                circ(s, WHITE, cx + side * 13 - 3, cy - 26, 3)
        elif kind == "bee":
            body, outline = (255, 205, 45), (190, 130, 20)
            pygame.draw.polygon(s, INK, [(cx - 6, cy + 24), (cx + 6, cy + 24), (cx, cy + 36)])
            circ(s, outline, cx, cy, 28)
            circ(s, body, cx, cy, 26)
            for dy in (-12, 12):
                hw = math.sqrt(max(0, 26 * 26 - dy * dy))
                pygame.draw.rect(s, (60, 45, 40), (cx - hw, cy + dy - 4, hw * 2, 8))
            for side in (-1, 1):
                pygame.draw.line(s, INK, (cx + side * 6, cy - 24), (cx + side * 14, cy - 40), 3)
                circ(s, INK, cx + side * 14, cy - 40, 4)
                circ(s, WHITE, cx + side * 10, cy - 20, 8)
                circ(s, INK, cx + side * 10, cy - 19, 4)
        else:  # ladybug
            circ(s, (30, 30, 40), cx, cy - 20, 16)
            circ(s, (150, 25, 30), cx, cy + 3, 27)
            circ(s, (232, 55, 50), cx, cy + 3, 25)
            pygame.draw.line(s, (30, 30, 40), (cx, cy - 18), (cx, cy + 27), 3)
            for ox, oy, r in ((-16, -6, 5), (16, -6, 5), (-18, 12, 5), (18, 12, 5), (-7, 22, 4), (7, 22, 4)):
                circ(s, (30, 30, 40), cx + ox, cy + oy, r)
            for side in (-1, 1):
                pygame.draw.line(s, (30, 30, 40), (cx + side * 5, cy - 32), (cx + side * 12, cy - 44), 3)
                circ(s, (30, 30, 40), cx + side * 12, cy - 44, 4)
                circ(s, WHITE, cx + side * 7, cy - 24, 6)
                circ(s, INK, cx + side * 7, cy - 23, 3)
        frames.append(s)
    return frames


def bug_frames(kind):
    if kind not in _bug_frames:
        _bug_frames[kind] = make_bug_frames(kind)
    return _bug_frames[kind]


class Bug:
    def __init__(self, text, x, y, vx, kind=None):
        self.text = text
        self.typed = 0
        self.kind = kind or random.choice(BUG_KINDS)
        self.x, self.y, self.base_y, self.vx = x, y, y, vx
        self.phase = random.uniform(0, 6.28)
        self.age = 0.0
        self.state = "fly"  # fly, targeted, grabbed, dead, leaving
        self.grab_k = 0.0
        self.wobble = 0.0

    @property
    def next_char(self):
        return self.text[self.typed] if self.typed < len(self.text) else None

    def remaining(self):
        return (W + 70 - self.x) if self.vx > 0 else (self.x + 70)

    def update(self, dt):
        self.age += dt
        self.wobble = max(0.0, self.wobble - dt)
        if self.state in ("fly", "targeted"):
            self.x += self.vx * dt
            self.y = self.base_y + 22 * math.sin(self.age * 2.0 + self.phase)
        elif self.state == "leaving":
            self.x += self.vx * 2.5 * dt
            self.y -= 260 * dt

    def draw(self, surf, t, words=False, target=False, locked=False):
        frames = bug_frames(self.kind)
        f = abs(math.sin(t * 13 + self.phase))
        img = frames[min(5, int(f * 6))]
        scale = 1.0
        if self.state == "grabbed":
            scale = max(0.3, 1 - 0.65 * self.grab_k)
            img = pygame.transform.smoothscale_by(img, scale)
        surf.blit(img, (self.x - BUG_AX * scale, self.y - BUG_AY * scale))
        if self.state == "grabbed":
            return
        dx = math.sin(self.wobble * 40) * 5 if self.wobble > 0 else 0
        if not words:
            ch = self.text
            col = finger_color(ch)
            pulse = 1 + (0.08 * math.sin(t * 8) if target else 0)
            r = 21 * pulse
            if target:
                circ(surf, WHITE, self.x + dx, self.y + 3, r + 7)
            circ(surf, col, self.x + dx, self.y + 3, r + 4)
            circ(surf, WHITE, self.x + dx, self.y + 3, r)
            draw_text(surf, ch, 32, INK, (self.x + dx, self.y + 1), scale=pulse)
        else:
            done, rest = self.text[:self.typed], self.text[self.typed:]
            s_done = text_surf(done, 30, (40, 160, 60)) if done else None
            s_rest = text_surf(rest, 30, INK) if rest else None
            wd = s_done.get_width() if s_done else 0
            wr = s_rest.get_width() if s_rest else 0
            pw, ph = wd + wr + 26, 44
            px, py = self.x + dx - pw / 2, self.y + 34
            nc = self.next_char
            border = (255, 150, 30) if locked else (finger_color(nc) if nc else WHITE)
            rrect(surf, darker(border, 0.25), pygame.Rect(px - 3, py - 3 + 3, pw + 6, ph + 6), 16)
            rrect(surf, border, pygame.Rect(px - 3, py - 3, pw + 6, ph + 6), 16)
            rrect(surf, WHITE, pygame.Rect(px, py, pw, ph), 13)
            if target and not locked:
                rrect(surf, WHITE, pygame.Rect(px - 6, py - 6, pw + 12, ph + 12), 18, 2)
            x = px + 13
            if s_done:
                surf.blit(s_done, (x, py + ph / 2 - s_done.get_height() / 2))
                x += wd
            if s_rest:
                surf.blit(s_rest, (x, py + ph / 2 - s_rest.get_height() / 2))
                cw = font(30).size(rest[0])[0]
                pygame.draw.line(surf, finger_color(rest[0]), (x, py + ph - 7), (x + cw, py + ph - 7), 4)


# ---------------------------------------------------------------- frog
TONGUE_OUT, TONGUE_IN, CHEW, JUMP = 0.10, 0.16, 0.45, 0.45


class Frog:
    def __init__(self, x, y, s=1.0):
        self.x, self.y, self.s = x, y, s
        self.tongue = None
        self.tip = (x, y)
        self.blink = 0.0
        self.blink_timer = random.uniform(1.5, 4)
        self.chew = self.shake = self.sad = self.jump = self.happy = 0.0
        self.look = (x, y - 300)

    def anchor(self):
        s = self.s
        jy = 0.0
        if self.jump > 0:
            jy = -math.sin((1 - self.jump / JUMP) * math.pi) * 45 * s
        dx = math.sin(self.shake * 55) * 8 * s if self.shake > 0 else 0
        return self.x + dx, self.y + jy

    def mouth(self):
        cx, cy = self.anchor()
        return cx, cy - 58 * self.s

    def catch(self, bug, on_eat=None):
        if self.tongue:
            self.finish(on_eat)
        bug.state = "targeted"
        self.tongue = {"bug": bug, "t": 0.0, "grabbed": False, "gx": 0, "gy": 0}
        self.tip = self.mouth()

    def finish(self, on_eat):
        b = self.tongue["bug"]
        b.state = "dead"
        self.tongue = None
        self.chew = CHEW
        if on_eat:
            on_eat(b)

    def update(self, dt, on_eat=None):
        self.blink_timer -= dt
        if self.blink_timer <= 0:
            self.blink = 0.16
            self.blink_timer = random.uniform(2, 5)
        self.blink = max(0.0, self.blink - dt)
        for a in ("chew", "shake", "sad", "jump", "happy"):
            setattr(self, a, max(0.0, getattr(self, a) - dt))
        if self.tongue:
            tg = self.tongue
            tg["t"] += dt
            mx, my = self.mouth()
            b = tg["bug"]
            self.look = (b.x, b.y)
            if tg["t"] < TONGUE_OUT:
                k = tg["t"] / TONGUE_OUT
                self.tip = (lerp(mx, b.x, k), lerp(my, b.y, k))
            else:
                if not tg["grabbed"]:
                    tg["grabbed"] = True
                    b.state = "grabbed"
                    tg["gx"], tg["gy"] = b.x, b.y
                k = min(1.0, (tg["t"] - TONGUE_OUT) / TONGUE_IN)
                k2 = k * k
                self.tip = (lerp(tg["gx"], mx, k2), lerp(tg["gy"], my, k2))
                b.x, b.y = self.tip
                b.grab_k = k
                if k >= 1:
                    self.finish(on_eat)

    def draw_tongue(self, surf):
        if not self.tongue:
            return
        s = self.s
        mx, my = self.mouth()
        tx, ty = self.tip
        pygame.draw.line(surf, (175, 45, 85), (mx, my), (tx, ty), max(3, int(18 * s)))
        pygame.draw.line(surf, (240, 95, 130), (mx, my), (tx, ty), max(2, int(12 * s)))
        circ(surf, (175, 45, 85), tx, ty, 13 * s)
        circ(surf, (240, 95, 130), tx, ty, 10 * s)

    def draw(self, surf, t):
        s = self.s
        cx, cy = self.anchor()
        br = 1 + 0.03 * math.sin(t * 2.6)
        lift = self.y - cy
        # shadow on the lily pad
        ell(surf, PAD_DARK, self.x, self.y + 18 * s, 200 * s * (1 - min(0.35, lift / 150)), 34 * s)

        body_y = cy - 45 * s
        bw, bh = 200 * s, 150 * s * br
        eye_y = cy - 108 * s - (br - 1) * 50 * s
        eyes = [(cx - 52 * s, eye_y), (cx + 52 * s, eye_y)]

        # back legs
        for side in (-1, 1):
            ell(surf, FROG_D, cx + side * 82 * s, cy - 2 * s, 98 * s, 62 * s)
            ell(surf, FROG_G, cx + side * 82 * s, cy - 2 * s, 88 * s, 52 * s)
        # silhouette outline, then fill
        ell(surf, FROG_D, cx, body_y, bw + 9 * s, bh + 9 * s)
        for ex, ey in eyes:
            circ(surf, FROG_D, ex, ey, 39 * s)
        ell(surf, FROG_G, cx, body_y, bw, bh)
        for ex, ey in eyes:
            circ(surf, FROG_G, ex, ey, 34.5 * s)
        ell(surf, FROG_L, cx, cy - 98 * s, 96 * s, 30 * s)
        for ox, oy, r in ((-72, -40, 9), (74, -52, 7), (82, -22, 5), (-64, -78, 5), (60, -88, 4)):
            circ(surf, (98, 182, 72), cx + ox * s, cy + oy * s, r * s)
        ell(surf, FROG_BELLY, cx, cy - 16 * s, 132 * s, 86 * s * br)
        # front feet
        for side in (-1, 1):
            fx = cx + side * 50 * s
            ell(surf, FROG_D, fx, cy + 22 * s, 60 * s, 28 * s)
            ell(surf, FROG_G, fx, cy + 21 * s, 53 * s, 21 * s)
            for k in (-1, 0, 1):
                circ(surf, FROG_D, fx + k * 17 * s, cy + 31 * s, 8 * s)
                circ(surf, FROG_G, fx + k * 17 * s, cy + 30 * s, 6.5 * s)
        # cheeks
        puff = abs(math.sin((self.chew / CHEW) * math.pi * 3)) if self.chew > 0 else 0
        for side in (-1, 1):
            if puff:
                circ(surf, FROG_D, cx + side * 70 * s, cy - 58 * s, (16 + 12 * puff) * s + 2)
                circ(surf, FROG_L, cx + side * 70 * s, cy - 58 * s, (16 + 12 * puff) * s)
            ell(surf, (255, 165, 175), cx + side * 66 * s, cy - 62 * s, 30 * s, 15 * s)
        # eyes
        lx, ly = self.look
        lid = 1.0 if self.blink > 0 else 0.0
        if self.sad > 0:
            lid = max(lid, 0.45)
        for ex, ey in eyes:
            circ(surf, WHITE, ex, ey, 25 * s)
            if self.happy > 0:
                circ(surf, FROG_G, ex, ey, 26 * s)
                pygame.draw.arc(surf, INK, pygame.Rect(ex - 15 * s, ey - 8 * s, 30 * s, 26 * s),
                                0.25, math.pi - 0.25, max(2, int(5 * s)))
                continue
            ang = math.atan2(ly - ey, lx - ex)
            d = min(9 * s, math.hypot(lx - ex, ly - ey) / 25)
            px, py = ex + math.cos(ang) * d, ey + math.sin(ang) * d
            circ(surf, (30, 35, 50), px, py, 13 * s)
            circ(surf, WHITE, px - 4 * s, py - 5 * s, 4.5 * s)
            circ(surf, WHITE, px + 4 * s, py + 4 * s, 2 * s)
            circ(surf, FROG_D, ex, ey, 25 * s, max(1, int(2.5 * s)))
            if lid > 0:
                clip = pygame.Rect(ex - 28 * s, ey - 28 * s, 56 * s, 56 * s * lid)
                surf.set_clip(clip)
                circ(surf, FROG_G, ex, ey, 27 * s)
                surf.set_clip(None)
                pygame.draw.line(surf, FROG_D, (ex - 24 * s, ey - 28 * s + 56 * s * lid),
                                 (ex + 24 * s, ey - 28 * s + 56 * s * lid), max(1, int(3 * s)))
        # mouth
        mx, my = cx, cy - 62 * s
        lw = max(2, int(5 * s))
        if self.tongue:
            ell(surf, FROG_D, mx, my + 4 * s, 72 * s, 44 * s)
            ell(surf, (125, 25, 55), mx, my + 4 * s, 64 * s, 36 * s)
            ell(surf, (240, 105, 135), mx, my + 13 * s, 38 * s, 13 * s)
        elif self.sad > 0:
            pygame.draw.arc(surf, FROG_D, pygame.Rect(mx - 30 * s, my - 2 * s, 60 * s, 34 * s),
                            0.35, math.pi - 0.35, lw)
        else:
            pygame.draw.arc(surf, FROG_D, pygame.Rect(mx - 58 * s, my - 34 * s, 116 * s, 52 * s),
                            math.pi + 0.3, 2 * math.pi - 0.3, lw)
        # nostrils
        for side in (-1, 1):
            circ(surf, FROG_D, cx + side * 11 * s, cy - 82 * s, 2.5 * s)


def draw_pad(surf, cx, cy, w, h, color=PAD, notch_col=None, flower=False):
    ell(surf, darker(color, 0.3), cx, cy + 4, w + 6, h + 6)
    ell(surf, color, cx, cy, w, h)
    ell(surf, lerp_col(color, WHITE, 0.15), cx - w * 0.06, cy - h * 0.1, w * 0.75, h * 0.6)
    for a in (0.6, 1.4, 2.2, 3.0, 3.8, 4.6):
        pygame.draw.line(surf, darker(color, 0.12), (cx, cy),
                         (cx + math.cos(a) * w * 0.42, cy + math.sin(a) * h * 0.42), 2)
    if notch_col:
        pygame.draw.polygon(surf, notch_col, [(cx + w * 0.05, cy),
                                              (cx + w * 0.52, cy - h * 0.18),
                                              (cx + w * 0.52, cy + h * 0.22)])
    if flower:
        fx, fy = cx - w * 0.28, cy - h * 0.2
        for i in range(6):
            a = i * math.pi / 3
            ell(surf, (255, 170, 205), fx + math.cos(a) * 9, fy + math.sin(a) * 5, 16, 11)
        circ(surf, (255, 225, 80), fx, fy, 6)


# ---------------------------------------------------------------- keyboard + hands
ROWS = ["qwertyuiop", "asdfghjkl;", "zxcvbnm,./"]
ROW_OFF = [0.0, 0.3, 0.8]
_layouts = {}


def key_layout(cx, top, ks):
    key = (cx, top, ks)
    if key in _layouts:
        return _layouts[key]
    p = ks + max(4, ks // 9)
    x0 = cx - (10.8 * p) / 2
    rects = {}
    for r, row in enumerate(ROWS):
        for i, ch in enumerate(row):
            rects[ch] = pygame.Rect(round(x0 + (ROW_OFF[r] + i) * p), round(top + r * p), ks, ks)
    rects[" "] = pygame.Rect(round(x0 + 2.8 * p), round(top + 3 * p), round(5 * p - (p - ks)),
                             round(ks * 0.6))
    _layouts[key] = rects
    return rects


def draw_keyboard(surf, cx, top, ks, t, target=None, pressed=None):
    rects = key_layout(cx, top, ks)
    fsize = int(ks * 0.5)
    for ch, r in rects.items():
        col = finger_color(ch)
        is_t = bool(target) and ch in target
        face = col if is_t else pastel(col, 0.62)
        rr = r.copy()
        if is_t:
            rr.y -= 3 + int(2 * math.sin(t * 9))
        if pressed and pressed[0] == ch and t - pressed[1] < 0.18:
            face = (120, 220, 110) if pressed[2] else (255, 90, 90)
            rr.y = r.y + 2
        rrect(surf, darker(col, 0.35) if is_t else darker(pastel(col, 0.62), 0.22),
              r.move(0, 5), ks * 0.2)
        rrect(surf, face, rr, ks * 0.2)
        if is_t:
            rrect(surf, WHITE, rr.inflate(6, 6), ks * 0.25, 3)
        label = "space" if ch == " " else ch.upper()
        draw_text(surf, label, int(fsize * (0.7 if ch == " " else 1)),
                  WHITE if is_t else darker(col, 0.45), rr.center,
                  outline=darker(col, 0.4) if is_t else None, ow=2)
        if ch in "fj":
            pygame.draw.line(surf, darker(col, 0.45) if not is_t else WHITE,
                             (rr.centerx - ks * 0.14, rr.bottom - ks * 0.14),
                             (rr.centerx + ks * 0.14, rr.bottom - ks * 0.14), 3)
    return rects


SKIN = (255, 222, 190)
SKIN_D = (215, 165, 130)


SKIN_SHADE = (240, 195, 160)
HOME_KEYS = {0: "a", 1: "s", 2: "d", 3: "f", 4: "j", 5: "k", 6: "l", 7: ";"}


def capsule(surf, color, a, b, w):
    """A thick line with round ends (used for fingers)."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy) or 1e-6
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    pygame.draw.polygon(surf, color, [(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)])
    circ(surf, color, ax, ay, w / 2)
    circ(surf, color, bx, by, w / 2)


class KeyboardHands:
    """Two cartoon hands resting on the keyboard, seen from above.

    Every fingertip sits on its HOME key. The finger that must press the
    target key glows and slides over to it, then slides back home.
    """

    def __init__(self, cx, top, ks, alpha=235):
        self.rects = key_layout(cx, top, ks)
        self.p = self.rects["s"].x - self.rects["a"].x
        self.alpha = alpha
        self.active = None
        self.tips = {fi: list(xy) for fi, xy in self.home_tips().items()}
        self.layer = pygame.Surface((W, H), pygame.SRCALPHA)

    def key_tip(self, ch):
        r = self.rects[ch]
        if ch == " ":
            return r.centerx, r.centery
        return r.centerx, r.bottom - r.h * 0.1

    def home_tips(self):
        tips = {fi: self.key_tip(k) for fi, k in HOME_KEYS.items()}
        sp = self.rects[" "]
        tips[8] = (sp.centerx - self.p * 1.0, sp.centery + 2)   # left thumb
        tips[9] = (sp.centerx + self.p * 1.0, sp.centery + 2)   # right thumb
        return tips

    def update(self, dt, target_key):
        goal = self.home_tips()
        active = FINGER_OF.get(target_key) if target_key else None
        if target_key and len(target_key) == 1 and active is not None and active != 8:
            goal[active] = self.key_tip(target_key)
        self.active = active
        k = 1 - math.exp(-dt * 12)
        for fi, (gx, gy) in goal.items():
            cur = self.tips[fi]
            cur[0] += (gx - cur[0]) * k
            cur[1] += (gy - cur[1]) * k

    def draw(self, surf, t, glow_all=False):
        lay = self.layer
        lay.fill((0, 0, 0, 0))
        home = self.home_tips()
        for left in (True, False):
            self.draw_hand(lay, left, home, t, glow_all)
        lay.set_alpha(self.alpha)
        surf.blit(lay, (0, 0))

    def draw_hand(self, surf, left, home, t, glow_all):
        p = self.p
        fingers = [0, 1, 2, 3] if left else [7, 6, 5, 4]      # pinky ... index (left to right on screen)
        out = -1 if left else 1                               # direction of the pinky side
        # how far each knuckle sits below the home key, and how much it leans to the hand centre
        drop = {0: 1.05, 1: 1.35, 2: 1.45, 3: 1.3}
        lean = {0: 0.45, 1: 0.2, 2: 0.0, 3: -0.12}
        width = {0: 0.40, 1: 0.44, 2: 0.47, 3: 0.48}
        order_of = {fi: (fi if left else 7 - fi) for fi in fingers}   # 0 pinky .. 3 index
        # the whole hand follows a reaching finger a little
        shift = [0.0, 0.0]
        for fi in fingers + [8 if left else 9]:
            hx, hy = home[fi]
            shift[0] += (self.tips[fi][0] - hx) * 0.25
            shift[1] += (self.tips[fi][1] - hy) * 0.25
        knuckles = {}
        for fi in fingers:
            o = order_of[fi]
            hx, hy = home[fi]
            knuckles[fi] = (hx - out * lean[o] * p + shift[0], hy + drop[o] * p + shift[1])
        kx = sum(k[0] for k in knuckles.values()) / 4
        ky = sum(k[1] for k in knuckles.values()) / 4
        thumb_side = -out
        palm_c = (kx + thumb_side * 0.12 * p, ky + 0.85 * p)
        wrist = pygame.Rect(0, 0, 1.75 * p, 1.8 * p)
        wrist.midtop = (palm_c[0] + thumb_side * 0.05 * p, palm_c[1])
        thumb_tip = self.tips[8 if left else 9]
        thumb_base = (palm_c[0] + thumb_side * 0.95 * p, palm_c[1] + 0.35 * p)

        def parts(grow):
            ell(surf, col_now, palm_c[0], palm_c[1], 2.75 * p + grow, 2.05 * p + grow)
            rrect(surf, col_now, wrist.inflate(grow, grow), p * 0.6)
            capsule(surf, col_now, thumb_base, thumb_tip, 0.55 * p + grow)
            for fi in fingers:
                capsule(surf, col_now, knuckles[fi], self.tips[fi], width[order_of[fi]] * p + grow)

        # glow behind the active finger
        for fi in fingers + [8 if left else 9]:
            on = glow_all or fi == self.active or (fi in (8, 9) and self.active == 8)
            if on:
                a = knuckles[fi] if fi in knuckles else thumb_base
                w = (width[order_of[fi]] if fi in knuckles else 0.55) * p
                capsule(surf, (255, 255, 255, 255), a, self.tips[fi], w + 12 + 3 * math.sin(t * 8))
        col_now = SKIN_D
        parts(6)
        col_now = SKIN
        parts(0)
        # soft shading on the palm side
        ell(surf, SKIN_SHADE, palm_c[0] - out * 0.55 * p, palm_c[1] + 0.25 * p, 1.1 * p, 1.4 * p)
        ell(surf, SKIN, palm_c[0] - out * 0.4 * p, palm_c[1] + 0.05 * p, 1.2 * p, 1.4 * p)
        # coloured fingertips, nails and knuckle lines
        tip_list = [(fi, knuckles[fi], width[order_of[fi]] * p) for fi in fingers]
        tip_list.append((8, thumb_base, 0.55 * p))
        for fi, base, w in tip_list:
            tip = self.tips[fi if fi != 8 else (8 if left else 9)]
            col = FINGERS[fi][1]
            on = glow_all or fi == self.active
            c = col if on else pastel(col, 0.25)
            dx, dy = tip[0] - base[0], tip[1] - base[1]
            L = math.hypot(dx, dy) or 1
            ux, uy = dx / L, dy / L
            cap_start = (tip[0] - ux * min(L * 0.3, 0.42 * p), tip[1] - uy * min(L * 0.3, 0.42 * p))
            capsule(surf, c, cap_start, tip, w - 2)
            # finger nail
            nx, ny = tip[0] - ux * w * 0.12, tip[1] - uy * w * 0.12
            circ(surf, lerp_col(c, WHITE, 0.55), nx, ny, w * 0.26)
            circ(surf, lerp_col(c, WHITE, 0.85), nx - w * 0.07, ny - w * 0.07, w * 0.1)
            # knuckle crease
            if fi != 8:
                mx, my = base[0] + dx * 0.45, base[1] + dy * 0.45
                px, py = -uy * w * 0.22, ux * w * 0.22
                pygame.draw.line(surf, SKIN_D, (mx - px, my - py), (mx + px, my + py), 2)


def draw_finger_hint(surf, cx, cy, ch, t):
    """Big 'use this finger' badge shown beside the keyboard."""
    if ch is None:
        draw_text(surf, tr("Fingers on", "ម្រាមដៃនៅលើ"), 22, (170, 140, 100), (cx, cy - 26))
        draw_text(surf, tr("HOME ROW", "ជួរដើម"), 30, (110, 190, 80), (cx, cy + 6), outline=WHITE, ow=2)
        draw_text(surf, "A S D F   J K L ;", 20, (170, 140, 100), (cx, cy + 40))
        return
    fi = FINGER_OF.get(ch, 8)
    col = FINGERS[fi][1]
    draw_text(surf, tr("USE YOUR", "ប្រើ"), 20, (170, 140, 100), (cx, cy - 42))
    if LANG == "km":
        draw_text(surf, FINGER_KM[fi], 34, col, (cx, cy + 6), outline=darker(col, 0.45), ow=2, max_w=270)
        return
    words = FINGERS[fi][0].upper().split()
    if len(words) == 2:
        draw_text(surf, words[0], 24, col, (cx, cy - 12), outline=darker(col, 0.45), ow=2)
        draw_text(surf, words[1], 36, col, (cx, cy + 22), outline=darker(col, 0.45), ow=3)
    else:
        draw_text(surf, words[0], 36, col, (cx, cy + 4), outline=darker(col, 0.45), ow=3)
    draw_text(surf, "FINGER" if fi != 8 else "", 20, (170, 140, 100), (cx, cy + 54))


# ---------------------------------------------------------------- particles
class Particles:
    def __init__(self):
        self.items = []
        self.texts = []

    def burst(self, x, y, colors, n=14, speed=260, kind="dot"):
        for _ in range(n):
            a = random.uniform(0, math.tau)
            v = random.uniform(0.35, 1) * speed
            life = random.uniform(0.5, 0.9)
            self.items.append([x, y, math.cos(a) * v, math.sin(a) * v - 80, life, life,
                               random.choice(colors), random.uniform(4, 9), kind])

    def text(self, x, y, msg, color, size=34, life=1.0, vy=-70):
        self.texts.append([x, y, msg, color, size, life, life, vy])

    def update(self, dt):
        for p in self.items:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[3] += 420 * dt
            p[4] -= dt
        self.items = [p for p in self.items if p[4] > 0]
        for tx in self.texts:
            tx[1] += tx[7] * dt
            tx[5] -= dt
        self.texts = [tx for tx in self.texts if tx[5] > 0]

    def draw(self, surf):
        for x, y, _, _, life, ml, col, size, kind in self.items:
            r = size * (life / ml)
            if kind == "star":
                pygame.draw.polygon(surf, col, star_points(x, y, r * 1.6))
            else:
                circ(surf, col, x, y, r)
        for x, y, msg, col, size, life, ml, _ in self.texts:
            k = life / ml
            sc = 1.0 + 0.35 * max(0, (k - 0.85) / 0.15)
            draw_text(surf, msg, size, col, (x, y), outline=WHITE, ow=4, scale=sc)


# ---------------------------------------------------------------- world (shared scenery)
def water_col(y):
    return lerp_col(WATER_TOP, WATER_BOT, (y - 385) / (H - 385))


def make_cloud(scale):
    w, h = int(260 * scale), int(120 * scale)
    s = pygame.Surface((w, int(h * 1.5)), pygame.SRCALPHA)
    puffs = [(0.25, 0.62, 0.22), (0.45, 0.45, 0.28), (0.68, 0.55, 0.24), (0.82, 0.68, 0.16),
             (0.15, 0.75, 0.14)]
    for px, py, pr in puffs:
        circ(s, (215, 232, 250), px * w, py * h + 6 * scale, pr * w)
    for px, py, pr in puffs:
        circ(s, WHITE, px * w, py * h, pr * w)
    return s


def make_background():
    bg = pygame.Surface((W, H))
    vgradient(bg, (0, 0, W, 420), SKY_TOP, SKY_BOT)
    # far hills
    rnd = random.Random(7)
    for layer, (base, amp, col, f1, f2) in enumerate([
            (322, 30, (160, 215, 140), 0.006, 0.017),
            (352, 22, (118, 195, 100), 0.009, 0.021)]):
        pts = [(0, 420)]
        for x in range(0, W + 21, 20):
            pts.append((x, base + amp * math.sin(x * f1 + layer * 2) + amp * 0.5 * math.sin(x * f2)))
        pts.append((W, 420))
        pygame.draw.polygon(bg, col, pts)
        for _ in range(16 if layer else 10):
            x = rnd.uniform(0, W)
            y = base + amp * math.sin(x * f1 + layer * 2) + amp * 0.5 * math.sin(x * f2)
            r = rnd.uniform(14, 28)
            circ(bg, darker(col, 0.08), x, y + 4, r)
            circ(bg, lerp_col(col, (90, 170, 80), 0.3), x, y, r * 0.92)
    # pond
    vgradient(bg, (0, 385, W, H - 385), WATER_TOP, WATER_BOT)
    # grassy shore line
    pts = [(0, 370)]
    for x in range(0, W + 11, 10):
        pts.append((x, 392 + 5 * math.sin(x * 0.045) + 3 * math.sin(x * 0.13)))
    pts.append((W, 370))
    pygame.draw.polygon(bg, (95, 180, 80), pts)
    for x in range(0, W + 11, 10):
        y = 392 + 5 * math.sin(x * 0.045) + 3 * math.sin(x * 0.13)
        pygame.draw.line(bg, (75, 155, 70), (x, y), (x + 5, y + 3), 3)
    # light bands on water
    for i in range(14):
        y = rnd.uniform(410, 580)
        x = rnd.uniform(60, W - 120)
        ell(bg, lerp_col(water_col(y), WHITE, 0.25), x, y, rnd.uniform(40, 110), 4)
    # decoration lily pads
    for x, y, w, fl in ((175, 455, 120, True), (1090, 440, 110, False), (330, 545, 90, False),
                        (960, 548, 130, True), (1180, 520, 80, False), (60, 520, 70, False)):
        draw_pad(bg, x, y, w, w * 0.32, PAD, water_col(y), flower=fl)
    return bg


class World:
    def __init__(self):
        self.bg = make_background()
        self.t = 0.0
        self.cloud_imgs = [make_cloud(s) for s in (0.8, 1.0, 0.65)]
        self.clouds = [[random.uniform(0, W), random.uniform(40, 210), random.uniform(8, 18), i % 3]
                       for i in range(5)]
        self.ripples = []
        self.ripple_t = 0.5
        rnd = random.Random(3)
        self.reeds = []
        for _ in range(9):
            self.reeds.append((rnd.uniform(5, 110), rnd.uniform(150, 250), rnd.uniform(0, 6)))
            self.reeds.append((rnd.uniform(W - 110, W - 5), rnd.uniform(150, 250), rnd.uniform(0, 6)))
        self.sun = self.make_sun()

    def make_sun(self):
        s = pygame.Surface((240, 240), pygame.SRCALPHA)
        for r, a in ((110, 30), (90, 45), (72, 70)):
            circ(s, (255, 240, 150, a), 120, 120, r)
        circ(s, (255, 200, 60), 120, 120, 52)
        circ(s, (255, 222, 90), 120, 120, 48)
        for side in (-1, 1):
            circ(s, INK, 120 + side * 16, 112, 5)
            ell(s, (255, 160, 120), 120 + side * 28, 128, 16, 9)
        pygame.draw.arc(s, INK, (100, 108, 40, 30), math.pi + 0.4, 2 * math.pi - 0.4, 4)
        return s

    def update(self, dt):
        self.t += dt
        for c in self.clouds:
            c[0] += c[2] * dt
            if c[0] > W + 50:
                c[0] = -300
                c[1] = random.uniform(40, 210)
        self.ripple_t -= dt
        if self.ripple_t <= 0:
            self.ripple_t = random.uniform(0.6, 1.6)
            self.ripples.append([random.uniform(80, W - 80), random.uniform(410, 575), 0.0])
        for r in self.ripples:
            r[2] += dt
        self.ripples = [r for r in self.ripples if r[2] < 2.2]

    def draw(self, surf):
        t = self.t
        surf.blit(self.bg, (0, 0))
        sx, sy = 1150, 150
        for i in range(12):
            a = t * 0.3 + i * math.tau / 12
            p1 = (sx + math.cos(a - 0.12) * 62, sy + math.sin(a - 0.12) * 62)
            p2 = (sx + math.cos(a + 0.12) * 62, sy + math.sin(a + 0.12) * 62)
            p3 = (sx + math.cos(a) * (88 + 6 * math.sin(t * 3 + i)), sy + math.sin(a) * (88 + 6 * math.sin(t * 3 + i)))
            pygame.draw.polygon(surf, (255, 215, 80), [p1, p2, p3])
        surf.blit(self.sun, (sx - 120, sy - 120))
        for x, y, _, i in self.clouds:
            surf.blit(self.cloud_imgs[i], (x, y))
        for x, y, age in self.ripples:
            k = age / 2.2
            col = lerp_col((225, 245, 255), water_col(y), k)
            ell(surf, col, x, y, 20 + 120 * k, 6 + 30 * k, 2)
            if k < 0.7:
                ell(surf, col, x, y, 10 + 60 * k, 3 + 15 * k, 2)
        for x, hgt, ph in self.reeds:
            sway = math.sin(t * 1.4 + ph) * 8
            base = 595
            top = (x + sway, base - hgt)
            pygame.draw.line(surf, (60, 125, 55), (x, base), top, 5)
            pygame.draw.line(surf, (85, 160, 70), (x + 6, base), (x + 6 + sway * 0.6 + 14, base - hgt * 0.55), 4)
            ell(surf, (120, 72, 40), top[0], top[1] + 22, 13, 36)
            ell(surf, (150, 95, 55), top[0] - 2, top[1] + 18, 5, 22)


# ---------------------------------------------------------------- UI widgets
class Button:
    def __init__(self, rect, text, color, size=30):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.size = size

    def hover(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def draw(self, surf, t, selected=False):
        on = selected or self.hover()
        r = self.rect.copy()
        lift = -4 if on else 0
        rrect(surf, darker(self.color, 0.35), r.move(0, 7), 22)
        face = r.move(0, lift)
        rrect(surf, lerp_col(self.color, WHITE, 0.15) if on else self.color, face, 22)
        rrect(surf, lerp_col(self.color, WHITE, 0.35), pygame.Rect(face.x + 10, face.y + 6, face.w - 20, face.h * 0.35), 14)
        if on:
            rrect(surf, WHITE, face.inflate(8, 8), 26, 4)
        draw_text(surf, self.text, self.size, WHITE, face.center, outline=darker(self.color, 0.45), ow=3,
                  max_w=face.w - 24)


def draw_panel(surf):
    """Wooden board at the bottom of the screen with bushes on top."""
    pygame.draw.rect(surf, (150, 105, 65), (0, 590, W, H - 590))
    rrect(surf, CREAM, pygame.Rect(14, 600, W - 28, H - 610), 24)
    rrect(surf, (225, 200, 160), pygame.Rect(14, 600, W - 28, H - 610), 24, 4)
    for i, x in enumerate(range(-10, W + 30, 34)):
        r = 20 if i % 2 else 16
        circ(surf, (80, 160, 65), x, 592, r + 2)
        circ(surf, (110, 190, 80) if i % 2 else (95, 178, 72), x, 590, r)


def draw_overlay(surf, alpha=140):
    alpha_fill(surf, (20, 30, 50), alpha)


def draw_card(surf, rect):
    rrect(surf, (110, 80, 50), pygame.Rect(rect).move(0, 10), 34)
    rrect(surf, CREAM, rect, 34)
    rrect(surf, (240, 200, 120), rect, 34, 6)


# ---------------------------------------------------------------- scenes
class Scene:
    def __init__(self, app):
        self.app = app

    def handle(self, e):
        pass

    def update(self, dt):
        pass

    def draw(self, surf):
        pass


MUSIC_BTN_R = 28


def draw_music_button(surf, center, on, t):
    cx, cy = center
    hover = math.hypot(pygame.mouse.get_pos()[0] - cx, pygame.mouse.get_pos()[1] - cy) < MUSIC_BTN_R
    col = (80, 195, 70) if on else (160, 165, 175)
    r = MUSIC_BTN_R + (2 if hover else 0)
    circ(surf, darker(col, 0.35), cx, cy + 5, r)
    circ(surf, col, cx, cy, r)
    circ(surf, WHITE, cx, cy, r, 3)
    bob = math.sin(t * 6) * 2 if on else 0
    # eighth note
    ell(surf, WHITE, cx - 5, cy + 9 + bob, 15, 11)
    pygame.draw.line(surf, WHITE, (cx + 2, cy + 8 + bob), (cx + 2, cy - 13 + bob), 4)
    pygame.draw.line(surf, WHITE, (cx + 2, cy - 13 + bob), (cx + 11, cy - 6 + bob), 4)
    if not on:
        pygame.draw.line(surf, (235, 70, 80), (cx - 17, cy - 17), (cx + 17, cy + 17), 5)


def music_button_hit(pos, center):
    return math.hypot(pos[0] - center[0], pos[1] - center[1]) <= MUSIC_BTN_R + 4


TILE_COLS = [(110, 200, 80), (70, 150, 240), (255, 155, 40), (240, 95, 140), (160, 105, 240), (40, 185, 190)]


def draw_avatar(surf, cx, cy, r, name, col):
    circ(surf, darker(col, 0.3), cx, cy + 3, r + 3)
    circ(surf, col, cx, cy, r)
    circ(surf, lerp_col(col, WHITE, 0.35), cx - r * 0.35, cy - r * 0.4, r * 0.25)
    draw_text(surf, first_letter(name), int(r * 1.15), WHITE, (cx, cy), outline=darker(col, 0.4), ow=2,
              max_w=r * 1.6)


def draw_student_chip(surf, rect, name, t):
    hover = rect.collidepoint(pygame.mouse.get_pos())
    rrect(surf, (40, 110, 160), rect.move(0, 4), 30)
    rrect(surf, (255, 255, 240) if hover else WHITE, rect, 30)
    draw_avatar(surf, rect.x + 34, rect.centery, 24, name or "?", (110, 200, 80))
    draw_text(surf, name or "", 24, INK, (rect.x + 68, rect.centery - 9), anchor="midleft", max_w=rect.w - 80)
    draw_text(surf, tr("change student", "ប្ដូរសិស្ស"), 16, (120, 150, 190), (rect.x + 68, rect.centery + 17),
              anchor="midleft")


class StudentScene(Scene):
    """'Who is playing?' - every student keeps their own stars, speed and tricky keys."""
    MAX = 11

    def __init__(self, app):
        super().__init__(app)
        self.mode = "pick"   # pick, name, delete
        self.entry = ""
        self.msg = ""
        self.names = list(app.data["order"])
        last = app.data.get("last")
        self.sel = self.names.index(last) if last in self.names else (0 if self.names else 0)
        self.frog = Frog(640, 690, 0.55)
        self.btn_quit = Button((20, 16, 170, 56), "", (240, 95, 140), 24)
        self.btn_lang = Button((W - 250, 16, 230, 56), "", (160, 105, 240), 24)
        self.btn_yes = Button((W / 2 - 200, 400, 180, 64), "", (240, 95, 140), 26)
        self.btn_no = Button((W / 2 + 20, 400, 180, 64), "", (80, 195, 70), 26)

    def count(self):
        return len(self.names) + (1 if len(self.names) < self.MAX else 0)

    def tile_rect(self, i):
        col, row = i % 4, i // 4
        return pygame.Rect(104 + col * 274, 150 + row * 136, 250, 116)

    def activate(self, i):
        self.app.sfx.play("click")
        if i < len(self.names):
            self.app.use_student(self.names[i])
            self.app.goto(TitleScene(self.app))
        else:
            self.mode = "name"
            self.entry = ""
            self.msg = ""

    def confirm_name(self):
        name = " ".join(self.entry.split())
        if not name:
            return
        if name in self.app.data["students"]:
            self.msg = tr("That name is already here!", "ឈ្មោះនេះមានរួចហើយ!")
            self.app.sfx.play("wrong")
            return
        self.app.add_student(name)
        self.app.use_student(name)
        self.app.sfx.play("win")
        self.app.goto(TitleScene(self.app))

    def handle(self, e):
        if self.mode == "name":
            if e.type == pygame.TEXTINPUT:
                for ch in e.text:
                    if ch.isprintable() and len(self.entry) < 20:
                        self.entry += ch
                self.msg = ""
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_BACKSPACE:
                    self.entry = self.entry[:-1]
                elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.confirm_name()
                elif e.key == pygame.K_ESCAPE:
                    self.mode = "pick"
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.btn_yes.hover():
                    self.mode = "pick"
                elif self.btn_no.hover():
                    self.confirm_name()
            return
        if self.mode == "delete":
            if (e.type == pygame.KEYDOWN and e.key == pygame.K_y) or \
                    (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.btn_yes.hover()):
                self.app.remove_student(self.names[self.sel])
                self.names = list(self.app.data["order"])
                self.sel = max(0, min(self.sel, self.count() - 1))
                self.mode = "pick"
                self.app.sfx.play("escape")
            elif (e.type == pygame.KEYDOWN and e.key in (pygame.K_n, pygame.K_ESCAPE)) or \
                    (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.btn_no.hover()):
                self.mode = "pick"
            return
        n = self.count()
        if e.type == pygame.KEYDOWN:
            moves = {pygame.K_LEFT: -1, pygame.K_RIGHT: 1, pygame.K_UP: -4, pygame.K_DOWN: 4}
            if e.key in moves:
                self.sel = max(0, min(n - 1, self.sel + moves[e.key]))
                self.app.sfx.play("click")
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.activate(self.sel)
            elif e.key == pygame.K_DELETE and self.sel < len(self.names):
                self.mode = "delete"
            elif e.key == pygame.K_ESCAPE:
                self.app.quit()
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button in (1, 3):
            if e.button == 1 and music_button_hit(e.pos, (W - 290, 44)):
                self.app.toggle_music()
                return
            if e.button == 1 and self.btn_quit.hover():
                self.app.quit()
                return
            if e.button == 1 and self.btn_lang.hover():
                self.app.toggle_lang()
                self.app.sfx.play("click")
                return
            for i in range(n):
                if self.tile_rect(i).collidepoint(e.pos):
                    self.sel = i
                    if e.button == 1:
                        self.activate(i)
                    elif i < len(self.names):
                        self.mode = "delete"
        elif e.type == pygame.MOUSEMOTION:
            for i in range(n):
                if self.tile_rect(i).collidepoint(e.pos):
                    self.sel = i

    def update(self, dt):
        r = self.tile_rect(self.sel)
        self.frog.look = r.center
        self.frog.update(dt)

    def draw(self, surf):
        t = self.app.world.t
        self.app.world.draw(surf)
        alpha_fill(surf, (255, 255, 255), 70)
        draw_text(surf, tr("WHO IS PLAYING?", "តើនរណាកំពុងលេង?"), 56, (255, 210, 60), (W / 2, 92),
                  outline=(40, 90, 120), ow=5, title=True)
        students = self.app.data["students"]
        for i in range(self.count()):
            r = self.tile_rect(i)
            sel = i == self.sel and self.mode == "pick"
            face = r.move(0, -5 if sel else 0)
            if i < len(self.names):
                name = self.names[i]
                st = students[name]
                col = TILE_COLS[i % len(TILE_COLS)]
                rrect(surf, darker(col, 0.35), r.move(0, 7), 24)
                rrect(surf, WHITE, face, 24)
                rrect(surf, col, face, 24, 6)
                if sel:
                    rrect(surf, WHITE, face.inflate(12, 12), 30, 5)
                draw_avatar(surf, face.x + 52, face.centery, 34, name, col)
                draw_text(surf, name, 28, INK, (face.x + 98, face.centery - 18), anchor="midleft", max_w=140)
                draw_star(surf, face.x + 110, face.centery + 22, 10)
                draw_text(surf, str(total_stars(st)), 22, (200, 140, 30), (face.x + 128, face.centery + 22),
                          anchor="midleft")
                lvl = max([i2 + 1 for i2 in range(len(LEVELS)) if level_unlocked(st, i2)] or [1])
                draw_text(surf, tr("Level", "កម្រិត") + f" {lvl}", 20, (130, 120, 110),
                          (face.right - 18, face.centery + 22), anchor="midright")
            else:
                col = (150, 200, 140)
                rrect(surf, darker(col, 0.3), r.move(0, 7), 24)
                rrect(surf, (240, 252, 235), face, 24)
                rrect(surf, col, face, 24, 4)
                if sel:
                    rrect(surf, WHITE, face.inflate(12, 12), 30, 5)
                draw_text(surf, "+", 64, (110, 190, 80), (face.x + 52, face.centery - 4), outline=WHITE, ow=2)
                draw_text(surf, tr("NEW STUDENT", "សិស្សថ្មី"), 26, (90, 160, 70), (face.x + 98, face.centery),
                          anchor="midleft", max_w=140)
        draw_pad(surf, 640, 710, 200, 56, PAD, water_col(710))
        self.frog.draw(surf, t)
        if not self.names:
            draw_text(surf, tr("Click NEW STUDENT to start!", "ចុច សិស្សថ្មី ដើម្បីចាប់ផ្ដើម!"), 28, WHITE,
                      (W / 2, 590), outline=(40, 90, 120), ow=3)
        draw_text(surf, tr("Arrows + Enter to choose.  Delete = remove a student.  F8 = music  F11 = full screen",
                           "ប្រើព្រួញ + Enter ដើម្បីជ្រើស។  Delete = លុបសិស្ស។  F8 = តន្ត្រី  F11 = ពេញអេក្រង់"),
                  20, WHITE, (W / 2, 775), outline=(40, 90, 120), ow=2)
        self.btn_quit.text = tr("QUIT", "ចាកចេញ")
        self.btn_lang.text = tr("LANGUAGE: ENGLISH", "ភាសា: ខ្មែរ")
        self.btn_quit.draw(surf, t)
        self.btn_lang.draw(surf, t)
        draw_music_button(surf, (W - 290, 44), self.app.music_on, t)

        if self.mode == "name":
            draw_overlay(surf, 150)
            card = pygame.Rect(W / 2 - 380, 150, 760, 360)
            draw_card(surf, card)
            draw_text(surf, tr("What is your name?", "តើអ្នកឈ្មោះអ្វី?"), 44, (110, 190, 80), (W / 2, 210),
                      outline=(50, 100, 40), ow=4, title=True)
            box = pygame.Rect(W / 2 - 300, 255, 600, 76)
            rrect(surf, (230, 210, 170), box.move(0, 4), 18)
            rrect(surf, WHITE, box, 18)
            rrect(surf, (110, 190, 80), box, 18, 4)
            tr_ = draw_text(surf, self.entry or " ", 40, INK, (box.x + 24, box.centery), anchor="midleft",
                            max_w=box.w - 50)
            if int(t * 2.5) % 2 == 0:
                x = tr_.right + 4 if self.entry else box.x + 26
                pygame.draw.line(surf, INK, (x, box.y + 16), (x, box.bottom - 16), 3)
            draw_text(surf, tr("Type your name, then press Enter", "វាយឈ្មោះរបស់អ្នក រួចចុច Enter"), 24,
                      (130, 110, 90), (W / 2, 362))
            if self.msg:
                draw_text(surf, self.msg, 24, (230, 80, 80), (W / 2, 392))
            self.btn_yes.rect.y = self.btn_no.rect.y = 420
            self.btn_yes.text = tr("CANCEL", "បោះបង់")
            self.btn_no.text = tr("OK", "យល់ព្រម")
            self.btn_yes.draw(surf, t)
            self.btn_no.draw(surf, t)
        elif self.mode == "delete":
            draw_overlay(surf, 150)
            card = pygame.Rect(W / 2 - 340, 200, 680, 300)
            draw_card(surf, card)
            name = self.names[self.sel]
            draw_text(surf, tr("Remove this student?", "លុបសិស្សនេះ?"), 40, (240, 95, 140), (W / 2, 262),
                      outline=darker((240, 95, 140), 0.5), ow=3, title=True)
            draw_text(surf, name, 36, INK, (W / 2, 322), max_w=600)
            draw_text(surf, tr("All stars will be lost.  Y = yes,  N = no",
                               "ផ្កាយទាំងអស់នឹងបាត់។  Y = បាទ/ចាស,  N = ទេ"), 22, (130, 110, 90), (W / 2, 368))
            self.btn_yes.rect.y = self.btn_no.rect.y = 405
            self.btn_yes.text = tr("REMOVE", "លុប")
            self.btn_no.text = tr("KEEP", "ទុក")
            self.btn_yes.draw(surf, t)
            self.btn_no.draw(surf, t)


class TitleScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.frog = Frog(640, 500, 1.15)
        self.bugs = []
        self.spawn_t = 0.2
        self.eat_t = 2.5
        self.parts = Particles()
        self.sel = 0
        bw, gap, y = 220, 18, 640
        x0 = (W - (5 * bw + 4 * gap)) // 2
        cols = [(80, 195, 70), (70, 150, 240), (255, 155, 40), (160, 105, 240), (240, 95, 140)]
        self.buttons = [Button((x0 + i * (bw + gap), y, bw, 84), "", cols[i], 28) for i in range(5)]
        self.chip = pygame.Rect(16, 14, 280, 64)
        self.refresh_labels()

    def refresh_labels(self):
        labels = [tr("PLAY", "លេង"), tr("HAND LESSON", "មេរៀនដាក់ដៃ"),
                  tr("SPEED: ", "ល្បឿន: ") + speed_name(self.app.save["speed"]).upper(),
                  tr("LANGUAGE: ENGLISH", "ភាសា: ខ្មែរ"),
                  tr("QUIT", "ចាកចេញ")]
        for b, l in zip(self.buttons, labels):
            b.text = l

    def activate(self, i):
        app = self.app
        app.sfx.play("click")
        if i == 0:
            app.goto(MapScene(app) if app.save["lesson_done"] else LessonScene(app, then_map=True))
        elif i == 1:
            app.goto(LessonScene(app))
        elif i == 2:
            app.save["speed"] = (app.save["speed"] + 1) % 3
            write_save(app.save)
            self.refresh_labels()
        elif i == 3:
            app.toggle_lang()
            self.refresh_labels()
        else:
            app.quit()

    def handle(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_LEFT, pygame.K_UP):
                self.sel = (self.sel - 1) % 5
                self.app.sfx.play("click")
            elif e.key in (pygame.K_RIGHT, pygame.K_DOWN, pygame.K_TAB):
                self.sel = (self.sel + 1) % 5
                self.app.sfx.play("click")
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.activate(self.sel)
            elif e.key == pygame.K_ESCAPE:
                self.app.goto(StudentScene(self.app))
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if music_button_hit(e.pos, (W - 50, 46)):
                self.app.toggle_music()
                return
            if self.chip.collidepoint(e.pos):
                self.app.sfx.play("click")
                self.app.goto(StudentScene(self.app))
                return
            for i, b in enumerate(self.buttons):
                if b.hover():
                    self.sel = i
                    self.activate(i)
        elif e.type == pygame.MOUSEMOTION:
            for i, b in enumerate(self.buttons):
                if b.hover():
                    self.sel = i

    def on_eat(self, bug):
        self.app.sfx.play("gulp")
        mx, my = self.frog.mouth()
        self.parts.burst(mx, my - 20, [(255, 230, 80), (255, 140, 180), WHITE], 10, kind="star")

    def update(self, dt):
        self.spawn_t -= dt
        if self.spawn_t <= 0 and len(self.bugs) < 4:
            self.spawn_t = random.uniform(0.8, 1.8)
            side = random.choice((-1, 1))
            self.bugs.append(Bug(random.choice(ALL), -60 if side > 0 else W + 60,
                                 random.uniform(250, 340), side * random.uniform(70, 120)))
        for b in self.bugs:
            b.update(dt)
        self.bugs = [b for b in self.bugs if b.state != "dead" and -90 < b.x < W + 90]
        self.eat_t -= dt
        if self.eat_t <= 0:
            near = [b for b in self.bugs if b.state == "fly" and 380 < b.x < 900]
            if near:
                self.frog.catch(random.choice(near), self.on_eat)
                self.app.sfx.play("slurp")
                self.eat_t = random.uniform(1.6, 3.2)
        if not self.frog.tongue:
            fl = [b for b in self.bugs if b.state == "fly"]
            if fl:
                b = min(fl, key=lambda b: abs(b.x - 640))
                self.frog.look = (b.x, b.y)
        self.frog.update(dt, self.on_eat)
        self.parts.update(dt)

    def draw(self, surf):
        t = self.app.world.t
        self.app.world.draw(surf)
        draw_pad(surf, 640, 528, 330, 90, PAD, water_col(528))
        for b in self.bugs:
            if b.state != "grabbed":
                b.draw(surf, t)
        self.frog.draw(surf, t)
        self.frog.draw_tongue(surf)
        for b in self.bugs:
            if b.state == "grabbed":
                b.draw(surf, t)
        self.parts.draw(surf)
        # title
        title = "HUNGRY FROG"
        colors = [(120, 210, 80), (255, 200, 40), (255, 120, 170), (80, 170, 255), (255, 150, 50)]
        f = font(104, True)
        total = sum(f.size(c)[0] for c in title) + 4 * (len(title) - 1)
        x = W / 2 - total / 2
        for i, c in enumerate(title):
            cw = f.size(c)[0]
            y = 118 + math.sin(t * 3 + i * 0.5) * 9
            if c != " ":
                draw_text(surf, c, 104, colors[i % len(colors)], (x + cw / 2, y + 6), outline=(40, 70, 40),
                          ow=7, title=True)
            x += cw + 4
        draw_text(surf, tr("Type the letters. Catch the bugs!", "កង្កែបឃ្លាន - វាយអក្សរ ចាប់សត្វល្អិត!"),
                  34, WHITE, (W / 2, 205), outline=(50, 110, 160), ow=4)
        draw_student_chip(surf, self.chip, self.app.student_name, t)
        draw_music_button(surf, (W - 50, 46), self.app.music_on, t)
        draw_panel(surf)
        for i, b in enumerate(self.buttons):
            b.draw(surf, t, i == self.sel)
        sp = self.app.save["speed"]
        draw_text(surf, tr(f"Speed {speed_name(sp)} is for {SPEED_DESC[sp][0]}.  Arrows + Enter, or click!",
                           f"ល្បឿន{speed_name(sp)} សម្រាប់{SPEED_DESC[sp][1]}។  ប្រើព្រួញ + Enter ឬចុចកណ្ដុរ!"),
                  20, (150, 120, 85), (W / 2, 765))


LESSON_STEPS = [
    ("talk", "", "Hi! I'm Froggy. Before we catch bugs, let's learn where your fingers go on the keyboard!",
     "សួស្ដី! ខ្ញុំជាកង្កែប។ មុនចាប់សត្វល្អិត តោះរៀនដាក់ម្រាមដៃលើក្ដារចុច!"),
    ("talk", "", "Sit up tall. Feet flat on the floor. Keep your wrists up a little. Don't lean them on the desk!",
     "អង្គុយត្រង់ ជើងដាក់លើឥដ្ឋ។ លើកកដៃឡើងបន្តិច។ កុំផ្អែកកដៃលើតុ!"),
    ("talk", "asdfjkl; ", "Look at the hands! This is the HOME POSITION. Left fingers on A S D F. "
                          "Right fingers on J K L ;  Both thumbs on SPACE.",
     "មើលដៃ! នេះជាទីតាំងដើម។ ម្រាមដៃឆ្វេងនៅលើ A S D F។ ម្រាមដៃស្ដាំនៅលើ J K L ;  មេដៃទាំងពីរនៅលើ SPACE។"),
    ("talk", "fj", "Feel the little BUMPS on F and J? Your pointer fingers go there. "
                   "Now you can find home without looking!",
     "មានស្នាមប៉ោងតូចៗនៅលើ F និង J ទេ? ម្រាមចង្អុលដាក់នៅទីនោះ។ ឥឡូវអ្នករកផ្ទះឃើញ ដោយមិនបាច់មើល!"),
    ("talk", "", "Curve your fingers like you are holding a little ball. Tap the keys softly with your fingertips.",
     "កោងម្រាមដៃ ដូចកំពុងកាន់បាល់តូចមួយ។ ចុចគ្រាប់ចុចថ្នមៗ ដោយចុងម្រាមដៃ។"),
    ("talk", "", "Every finger has its own COLOR. A finger only presses the keys with its color. "
                 "Look at the screen, not at your hands!",
     "ម្រាមដៃនីមួយៗមានពណ៌រៀងៗខ្លួន។ ម្រាមដៃចុចតែគ្រាប់ចុចដែលមានពណ៌ដូចខ្លួន។ មើលអេក្រង់ កុំមើលដៃ!"),
    ("key", "f", "Put your LEFT POINTER finger on F. Can you feel the little bump? Press F!",
     "ដាក់ម្រាមចង្អុលឆ្វេងលើ F។ មានស្នាមប៉ោងទេ? ចុច F!"),
    ("key", "j", "Put your RIGHT POINTER finger on J. It has a bump too! Press J!",
     "ដាក់ម្រាមចង្អុលស្ដាំលើ J។ វាក៏មានស្នាមប៉ោងដែរ! ចុច J!"),
    ("key", "d", "Your LEFT MIDDLE finger sits on D. Press D!", "ម្រាមកណ្ដាលឆ្វេងនៅលើ D។ ចុច D!"),
    ("key", "k", "Your RIGHT MIDDLE finger sits on K. Press K!", "ម្រាមកណ្ដាលស្ដាំនៅលើ K។ ចុច K!"),
    ("key", "s", "Your LEFT RING finger sits on S. Press S!", "នាងដៃឆ្វេងនៅលើ S។ ចុច S!"),
    ("key", "l", "Your RIGHT RING finger sits on L. Press L!", "នាងដៃស្ដាំនៅលើ L។ ចុច L!"),
    ("key", "a", "Your LEFT PINKY sits on A. Press A!", "កូនដៃឆ្វេងនៅលើ A។ ចុច A!"),
    ("key", ";", "Your RIGHT PINKY sits on ;  Press it!", "កូនដៃស្ដាំនៅលើ ;  ចុចវា!"),
    ("key", " ", "Your THUMBS rest on the SPACE bar. Press SPACE!", "មេដៃសម្រាកនៅលើ SPACE។ ចុច SPACE!"),
    ("key", "g", "Stretch your LEFT POINTER from F over to G. Press G, then go back to F!",
     "លាតម្រាមចង្អុលឆ្វេងពី F ទៅ G។ ចុច G រួចត្រឡប់ទៅ F វិញ!"),
    ("key", "h", "Stretch your RIGHT POINTER from J over to H. Press H, then go back to J!",
     "លាតម្រាមចង្អុលស្ដាំពី J ទៅ H។ ចុច H រួចត្រឡប់ទៅ J វិញ!"),
    ("talk", "asdfjkl;", "You did it! Your HOME ROW is A S D F and J K L ;  "
                         "After every key, go back home. Now let's catch some bugs!",
     "អ្នកធ្វើបានហើយ! ជួរដើមគឺ A S D F និង J K L ;  ចុចរួច ត្រឡប់មកផ្ទះវិញ។ តោះចាប់សត្វល្អិត!"),
]

LESSON_KB = (640, 300, 58)   # keyboard centre x, top y, key size


class LessonScene(Scene):
    def __init__(self, app, then_map=True):
        super().__init__(app)
        self.step = 0
        self.frog = Frog(165, 210, 0.55)
        self.parts = Particles()
        self.pressed = None
        self.step_t = 0.0
        self.hands = KeyboardHands(*LESSON_KB, alpha=240)

    def cur(self):
        return LESSON_STEPS[self.step]

    def advance(self):
        self.step += 1
        self.step_t = 0.0
        if self.step >= len(LESSON_STEPS):
            self.app.save["lesson_done"] = True
            write_save(self.app.save)
            self.app.goto(MapScene(self.app))

    def handle(self, e):
        st = self.cur()
        t = self.app.world.t
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.app.goto(TitleScene(self.app))
            elif st[0] == "talk" and e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.app.sfx.play("step")
                self.advance()
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and st[0] == "talk":
            self.app.sfx.play("step")
            self.advance()
        elif e.type == pygame.TEXTINPUT and st[0] == "key":
            for ch in e.text.lower():
                ok = ch == st[1]
                self.pressed = (ch, t, ok)
                if ok:
                    self.app.sfx.play("step")
                    r = key_layout(*LESSON_KB)[ch]
                    self.parts.burst(r.centerx, r.centery, [finger_color(ch), (255, 230, 80), WHITE], 16,
                                     kind="star")
                    self.parts.text(r.centerx, r.top - 20, tr(*random.choice(GOOD_WORDS)),
                                    finger_color(ch), 34)
                    self.frog.happy = 0.6
                    self.frog.jump = JUMP
                    self.advance()
                    break
                else:
                    self.app.sfx.play("wrong")
                    self.frog.shake = 0.3

    def update(self, dt):
        self.step_t += dt
        self.frog.look = (640, 420)
        self.frog.update(dt)
        self.parts.update(dt)
        if self.step < len(LESSON_STEPS):
            st = self.cur()
            self.hands.update(dt, st[1] if st[0] == "key" else None)

    def draw(self, surf):
        t = self.app.world.t
        self.app.world.draw(surf)
        alpha_fill(surf, CREAM, 222, pygame.Rect(0, 0, W, H))
        draw_text(surf, tr("HAND LESSON", "មេរៀនដាក់ដៃ"), 52, (255, 190, 40), (W / 2, 42), outline=(120, 80, 20),
                  ow=5, title=True)
        draw_pad(surf, 165, 236, 170, 48, PAD)
        self.frog.draw(surf, t)
        if self.step >= len(LESSON_STEPS):
            return
        st = self.cur()
        msg = tr(st[2], st[3])
        # speech bubble
        bub = pygame.Rect(300, 82, 930, 168)
        tail = [(bub.x + 6, bub.y + 92), (bub.x - 46, bub.y + 120), (bub.x + 6, bub.y + 124)]
        pygame.draw.polygon(surf, (225, 200, 150), [(x - 4, y) for x, y in tail])
        rrect(surf, (225, 200, 150), bub.inflate(8, 8), 34)
        rrect(surf, WHITE, bub, 30)
        pygame.draw.polygon(surf, WHITE, tail)
        lines = wrap(msg, 29, bub.w - 60)
        y0 = bub.centery - (len(lines) - 1) * 19
        for i, ln in enumerate(lines):
            draw_text(surf, ln, 29, INK, (bub.centerx, y0 + i * 38))
        target = st[1] if st[0] == "key" else None
        glow = st[1] if st[0] == "talk" else target
        active = FINGER_OF.get(target) if target is not None else None
        draw_keyboard(surf, *LESSON_KB, t, glow, self.pressed)
        self.hands.draw(surf, t, glow_all=(st[0] == "talk" and len(st[1]) > 2))
        # side badges
        draw_finger_hint(surf, 150, 420, target, t)
        if target is not None:
            r = key_layout(*LESSON_KB)[target]
            draw_text(surf, "SPACE" if target == " " else target.upper(), 80, finger_color(target), (1130, 420),
                      outline=darker(finger_color(target), 0.45), ow=5)
        if st[0] == "talk":
            if int(t * 2) % 2 == 0:
                draw_text(surf, tr("Press ENTER to go on", "ចុច Enter ដើម្បីបន្ត"), 30, (80, 170, 70),
                          (W / 2, 728), outline=WHITE, ow=3)
        else:
            nm = "SPACE" if target == " " else target.upper()
            draw_text(surf, tr(f"Press  {nm}  with your {FINGERS[active][0].upper()} finger",
                               f"ចុច  {nm}  ដោយប្រើ{FINGER_KM[active]}"), 30,
                      finger_color(target), (W / 2, 728), outline=darker(finger_color(target), 0.5), ow=2)
        # progress dots
        n = len(LESSON_STEPS)
        for i in range(n):
            x = W / 2 + (i - (n - 1) / 2) * 26
            circ(surf, (110, 195, 80) if i < self.step else ((255, 190, 40) if i == self.step else (215, 205, 185)),
                 x, 772, 8 if i == self.step else 6)
        self.parts.draw(surf)


def pad_positions():
    pts = []
    for i in range(len(LEVELS)):
        row, col = divmod(i, 6)
        if row % 2 == 1:
            col = 5 - col
        pts.append((170 + col * 188, 225 + row * 185))
    return pts


class MapScene(Scene):
    def __init__(self, app, select=None):
        super().__init__(app)
        self.pos = pad_positions()
        save = app.save
        if select is None:
            select = 0
            for i in range(len(LEVELS)):
                if level_unlocked(save, i):
                    select = i
        self.sel = select
        self.hop = None  # (from, to, t)
        x, y = self.pos[self.sel]
        self.frog = Frog(x, y - 12, 0.42)
        self.bg = self.make_bg()
        rnd = random.Random(11)
        self.twinkles = [(rnd.uniform(0, W), rnd.uniform(120, H), rnd.uniform(0, 6)) for _ in range(40)]
        self.btn_back = Button((20, 18, 150, 56), tr("BACK", "ត្រឡប់"), (240, 95, 140), 24)
        self.btn_lesson = Button((W - 400, 18, 190, 56), tr("HAND LESSON", "មេរៀនដាក់ដៃ"), (70, 150, 240), 22)
        self.btn_speed = Button((W - 195, 18, 175, 56), "", (255, 155, 40), 22)

    def make_bg(self):
        bg = pygame.Surface((W, H))
        vgradient(bg, (0, 0, W, H), (100, 200, 230), (40, 120, 180))
        rnd = random.Random(5)
        for _ in range(30):
            y = rnd.uniform(100, H)
            ell(bg, lerp_col((100, 200, 230), WHITE, 0.2), rnd.uniform(0, W), y, rnd.uniform(40, 120), 4)
        pts = self.pos
        for i in range(len(pts) - 1):
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            d = math.hypot(x2 - x1, y2 - y1)
            n = int(d / 24)
            for k in range(1, n):
                u = k / n
                bend = math.sin(u * math.pi) * (30 if y1 == y2 else 0)
                circ(bg, (215, 240, 255), lerp(x1, x2, u), lerp(y1, y2, u) + 10 + bend, 4)
        for x, y in ((40, 140), (1240, 760), (30, 700), (1250, 330), (640, 770)):
            draw_pad(bg, x, y, 90, 30, (80, 160, 70))
        return bg

    def play(self):
        if level_unlocked(self.app.save, self.sel):
            self.app.sfx.play("go")
            self.app.goto(PlayScene(self.app, self.sel))

    def select(self, i):
        if i == self.sel or not (0 <= i < len(LEVELS)):
            return
        if not level_unlocked(self.app.save, i):
            self.app.sfx.play("wrong")
            return
        self.hop = (self.pos[self.sel], self.pos[i], 0.0)
        self.sel = i
        self.app.sfx.play("step")

    def handle(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_LEFT, pygame.K_UP):
                self.select(self.sel - 1)
            elif e.key in (pygame.K_RIGHT, pygame.K_DOWN):
                self.select(self.sel + 1)
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.play()
            elif e.key == pygame.K_ESCAPE:
                self.app.goto(TitleScene(self.app))
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if music_button_hit(e.pos, (W - 448, 46)):
                self.app.toggle_music()
                return
            if self.btn_back.hover():
                self.app.goto(TitleScene(self.app))
                return
            if self.btn_lesson.hover():
                self.app.goto(LessonScene(self.app))
                return
            if self.btn_speed.hover():
                self.app.save["speed"] = (self.app.save["speed"] + 1) % 3
                write_save(self.app.save)
                self.app.sfx.play("click")
                return
            mx, my = e.pos
            for i, (x, y) in enumerate(self.pos):
                if abs(mx - x) < 75 and abs(my - y) < 50:
                    if i == self.sel:
                        self.play()
                    else:
                        self.select(i)

    def update(self, dt):
        if self.hop:
            a, b, k = self.hop
            k += dt / 0.4
            if k >= 1:
                self.hop = None
                self.frog.x, self.frog.y = b[0], b[1] - 12
            else:
                self.hop = (a, b, k)
                self.frog.x = lerp(a[0], b[0], k)
                self.frog.y = lerp(a[1], b[1], k) - 12 - math.sin(k * math.pi) * 70
        nxt = self.pos[min(self.sel + 1, len(LEVELS) - 1)]
        self.frog.look = nxt if not self.hop else self.hop[1]
        self.frog.update(dt)

    def draw(self, surf):
        t = self.app.world.t
        save = self.app.save
        surf.blit(self.bg, (0, 0))
        for x, y, ph in self.twinkles:
            k = (math.sin(t * 2 + ph) + 1) / 2
            if k > 0.6:
                ell(surf, WHITE, x, y, 16 * k, 3)
        draw_text(surf, tr("PICK A LILY PAD", "ជ្រើសរើសស្លឹកឈូក"), 50, (255, 225, 80), (W / 2, 50),
                  outline=(40, 90, 120), ow=5, title=True)
        for i, (x, y) in enumerate(self.pos):
            unlocked = level_unlocked(save, i)
            stars = save["stars"].get(str(i), 0)
            col = PAD if unlocked else (150, 165, 160)
            if i == self.sel:
                ell(surf, (255, 240, 150), x, y, 162 + 6 * math.sin(t * 5), 82)
            draw_pad(surf, x, y, 146, 70, col, lerp_col((100, 200, 230), (40, 120, 180), y / H),
                     flower=(stars == 3))
            if unlocked:
                if not (i == self.sel):
                    draw_text(surf, str(i + 1), 34, WHITE, (x, y), outline=darker(col, 0.45), ow=3)
                for k in range(3):
                    sx = x + (k - 1) * 28
                    if k < stars:
                        draw_star(surf, sx, y + 50, 11)
                    else:
                        pygame.draw.polygon(surf, (40, 110, 150), star_points(sx, y + 50, 11))
            else:
                # padlock
                rrect(surf, (110, 110, 120), pygame.Rect(x - 15, y - 8, 30, 24), 6)
                pygame.draw.arc(surf, (110, 110, 120), pygame.Rect(x - 11, y - 24, 22, 30), 0, math.pi, 5)
                circ(surf, (60, 60, 70), x, y + 4, 4)
        fx, fy = self.frog.x, self.frog.y
        self.frog.draw(surf, t)
        if not self.hop:
            draw_text(surf, str(self.sel + 1), 22, WHITE, (fx, fy + 30), outline=FROG_D, ow=2)
        # info banner
        lv = LEVELS[self.sel]
        ban = pygame.Rect(W / 2 - 330, 690, 660, 92)
        draw_card(surf, ban)
        draw_text(surf, tr("Level", "កម្រិត") + f" {self.sel + 1}: {level_name(lv)}", 34, INK,
                  (ban.centerx, ban.y + 30), max_w=ban.w - 30)
        if int(t * 2) % 2 == 0:
            draw_text(surf, tr("Press ENTER to play!", "ចុច Enter ដើម្បីលេង!"), 24, (80, 170, 70),
                      (ban.centerx, ban.y + 66))
        self.btn_back.draw(surf, t)
        self.btn_lesson.draw(surf, t)
        self.btn_speed.text = tr("SPEED: ", "ល្បឿន: ") + speed_name(save["speed"]).upper()
        self.btn_speed.draw(surf, t)
        draw_music_button(surf, (W - 448, 46), self.app.music_on, t)


class PlayScene(Scene):
    KB_TOP = 612

    def __init__(self, app, idx):
        super().__init__(app)
        self.idx = idx
        self.lv = LEVELS[idx]
        self.words = "words" in self.lv
        self.goal = self.lv.get("goal", 10 if self.words else 15)
        sp = app.save["speed"]
        self.speed = [42, 66, 98][sp] * (1 + idx * 0.025) * (0.8 if self.words else 1.0)
        self.max_bugs = ([1, 2, 3] if self.words else [2, 3, 4])[sp]
        self.interval = [3.0, 2.2, 1.5][sp] * (1.4 if self.words else 1.0)
        self.bugs = []
        self.frog = Frog(640, 512, 1.0)
        self.parts = Particles()
        self.hearts = 5
        self.eaten = 0
        self.correct = 0
        self.keys = 0
        self.missed = {}
        self.combo = 0
        self.best_combo = 0
        self.spawn_t = 0.3
        self.play_time = 0.0
        self.locked = None
        self.state = "ready"  # ready, play, done, result
        self.state_t = 0.0
        self.paused = False
        self.pressed = None
        self.result = None
        self.stars_shown = 0
        self.res_buttons = []
        self.home_pressed = set()
        self.hands = KeyboardHands(640, self.KB_TOP, 46, alpha=205)

    # ---- game logic
    def spawn(self):
        on_screen = [b.text for b in self.bugs if b.state in ("fly", "targeted")]
        if self.words:
            pool = [w for w in self.lv["words"] if w not in on_screen and
                    not any(o[0] == w[0] for o in on_screen)] or self.lv["words"]
            text = random.choice(pool)
        else:
            letters, new = self.lv["letters"], self.lv.get("new", "")
            text = None
            for _ in range(12):
                c = random.choice(new) if (new and random.random() < 0.5) else random.choice(letters)
                if c not in on_screen:
                    text = c
                    break
            text = text or random.choice(letters)
        side = random.choice((-1, 1))
        x = -60 if side > 0 else W + 60
        lanes = [150, 200, 250, 300, 345] if not self.words else [150, 220, 290]
        def clearance(y):
            near = [abs(b.base_y - y) for b in self.bugs if abs(b.x - x) < 300]
            return min(near) if near else 999
        y = max(lanes, key=lambda yy: clearance(yy) + random.uniform(0, 30))
        vx = side * self.speed * random.uniform(0.85, 1.15)
        self.bugs.append(Bug(text, x, y, vx))

    def live_bugs(self):
        return [b for b in self.bugs if b.state == "fly"]

    def target_bug(self):
        if self.locked and self.locked.state == "fly":
            return self.locked
        live = self.live_bugs()
        return min(live, key=lambda b: b.remaining()) if live else None

    def on_eat(self, bug):
        self.app.sfx.play("gulp")
        mx, my = self.frog.mouth()
        self.parts.burst(mx, my - 10, [(255, 230, 80), (255, 140, 180), (140, 230, 120), WHITE], 14,
                         kind="star")
        self.parts.text(mx + random.uniform(-60, 60), my - 70, tr(*random.choice(YUM_WORDS)),
                        (255, 120, 60), 34)

    def type_char(self, ch):
        if self.state == "ready" and not self.paused:
            if ch in "fj" and ch not in self.home_pressed:
                self.home_pressed.add(ch)
                self.pressed = (ch, self.app.world.t, True)
                self.app.sfx.play("step")
                r = key_layout(640, self.KB_TOP, 46)[ch]
                self.parts.burst(r.centerx, r.top, [finger_color(ch), WHITE, (255, 230, 80)], 12, kind="star")
                if len(self.home_pressed) == 2:
                    self.state = "go"
                    self.state_t = 0.0
                    self.app.sfx.play("go")
            return
        if self.state != "play" or self.paused:
            return
        if ch == " " and not self.words:
            return
        t = self.app.world.t
        tgt = self.locked if (self.locked and self.locked.state == "fly") else None
        hit = None
        if tgt:
            if tgt.next_char == ch:
                hit = tgt
        else:
            cands = [b for b in self.live_bugs() if b.next_char == ch]
            if cands:
                hit = min(cands, key=lambda b: b.remaining())
        self.keys += 1
        if hit:
            self.correct += 1
            self.pressed = (ch, t, True)
            hit.typed += 1
            if hit.typed >= len(hit.text):
                self.locked = None
                self.eaten += 1
                self.combo += 1
                self.best_combo = max(self.best_combo, self.combo)
                self.frog.catch(hit, self.on_eat)
                self.app.sfx.play("slurp")
                if self.combo in COMBO_WORDS:
                    self.app.sfx.play("combo")
                    self.parts.text(W / 2, 300, tr(*COMBO_WORDS[self.combo]), (255, 170, 30), 60, 1.4, -40)
                    self.frog.happy = 0.8
                    self.frog.jump = JUMP
                if self.eaten >= self.goal:
                    self.finish(True)
            else:
                self.locked = hit
                self.app.sfx.play("click")
        else:
            self.pressed = (ch, t, False)
            self.combo = 0
            expect = tgt.next_char if tgt else (self.target_bug().next_char if self.target_bug() else None)
            if expect:
                self.missed[expect] = self.missed.get(expect, 0) + 1
            if tgt:
                tgt.wobble = 0.3
            self.frog.shake = 0.3
            self.app.sfx.play("wrong")
            mx, my = self.frog.mouth()
            self.parts.text(mx, my - 120, ch if ch.strip() else "space", (240, 70, 80), 30, 0.6, -60)

    def finish(self, win):
        self.state = "done"
        self.state_t = 0.0
        self.won = win
        for b in self.bugs:
            if b.state == "fly":
                b.state = "leaving"
        acc = 100.0 * self.correct / self.keys if self.keys else 100.0
        minutes = max(self.play_time, 1) / 60
        wpm = (self.correct / 5) / minutes
        stars = 0
        if win:
            stars = 3 if acc >= 95 else 2 if acc >= 85 else 1
        save = self.app.save
        key = str(self.idx)
        save["stars"][key] = max(save["stars"].get(key, 0), stars)
        for k, v in self.missed.items():
            save["missed"][k] = save["missed"].get(k, 0) + v
        write_save(save)
        tricky = sorted(self.missed.items(), key=lambda kv: -kv[1])[:4]
        self.result = dict(win=win, acc=acc, wpm=wpm, stars=stars, tricky=[k for k, v in tricky if v >= 2])
        self.app.sfx.play("win" if win else "lose")
        if win:
            self.frog.happy = 2.0
            self.frog.jump = JUMP
        else:
            self.frog.sad = 3.0

    def make_result_buttons(self):
        cy = 560
        has_next = self.result["win"] and self.idx + 1 < len(LEVELS)
        bs = [(tr("AGAIN", "ម្ដងទៀត"), (255, 155, 40), "again"), (tr("MAP", "ផែនទី"), (70, 150, 240), "map")]
        if has_next:
            bs.append((tr("NEXT", "បន្ទាប់"), (80, 195, 70), "next"))
        bw, gap = 170, 22
        x0 = W / 2 - (len(bs) * bw + (len(bs) - 1) * gap) / 2
        self.res_buttons = [(Button((x0 + i * (bw + gap), cy, bw, 66), l, c, 28), a)
                            for i, (l, c, a) in enumerate(bs)]

    def do(self, action):
        app = self.app
        app.sfx.play("click")
        if action == "again":
            app.goto(PlayScene(app, self.idx))
        elif action == "next":
            app.goto(PlayScene(app, self.idx + 1))
        else:
            app.goto(MapScene(app, self.idx + 1 if (self.result and self.result["win"]
                                                     and self.idx + 1 < len(LEVELS)) else self.idx))

    def handle(self, e):
        if e.type == pygame.TEXTINPUT:
            for ch in e.text:
                self.type_char(ch.lower())
        elif e.type == pygame.KEYDOWN:
            if self.state == "result":
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self.do("next" if any(a == "next" for _, a in self.res_buttons) else "again")
                elif e.key == pygame.K_ESCAPE:
                    self.do("map")
                elif e.key == pygame.K_r:
                    self.do("again")
                return
            if e.key == pygame.K_ESCAPE:
                if self.paused:
                    self.paused = False
                elif self.state in ("ready", "go", "play"):
                    self.paused = True
            elif self.paused and e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.paused = False
            elif self.paused and e.key == pygame.K_m:
                self.app.goto(MapScene(self.app, self.idx))
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.state == "result":
                for b, a in self.res_buttons:
                    if b.hover():
                        self.do(a)
            elif self.paused and music_button_hit(e.pos, (W / 2 + 215, 262)):
                self.app.toggle_music()
            elif self.paused:
                for b, a in self.pause_buttons():
                    if b.hover():
                        if a == "map":
                            self.app.goto(MapScene(self.app, self.idx))
                        else:
                            self.paused = False

    def pause_buttons(self):
        return [(Button((W / 2 - 200, 400, 190, 66), tr("MAP (M)", "ផែនទី (M)"), (70, 150, 240), 26), "map"),
                (Button((W / 2 + 10, 400, 190, 66), tr("PLAY", "លេងបន្ត"), (80, 195, 70), 28), "play")]

    def update(self, dt):
        if self.paused:
            return
        self.state_t += dt
        if self.state == "go" and self.state_t > 0.9:
            self.state = "play"
            self.state_t = 0
        elif self.state == "play":
            self.play_time += dt
            self.spawn_t -= dt
            alive = len(self.live_bugs())
            if (self.spawn_t <= 0 and alive < self.max_bugs) or alive == 0 and self.spawn_t < self.interval - 0.7:
                self.spawn()
                self.spawn_t = self.interval * random.uniform(0.8, 1.2)
        elif self.state == "done" and self.state_t > 1.6:
            self.state = "result"
            self.state_t = 0
            self.make_result_buttons()
        elif self.state == "result":
            n = self.result["stars"]
            should = sum(1 for i in range(n) if self.state_t > 0.5 + i * 0.4)
            if should > self.stars_shown:
                self.stars_shown = should
                self.app.sfx.play("star")
                x = W / 2 + (self.stars_shown - 2) * 110
                self.parts.burst(x, 255, [(255, 225, 60), WHITE, (255, 170, 40)], 18, kind="star")

        for b in self.bugs:
            b.update(dt)
        for b in self.bugs:
            if b.state == "fly" and b.remaining() < 0:
                b.state = "dead"
                if b is self.locked:
                    self.locked = None
                if self.state == "play":
                    self.hearts -= 1
                    self.combo = 0
                    self.frog.sad = 1.0
                    self.app.sfx.play("escape")
                    self.parts.text(max(110, min(W - 110, b.x)), b.y, tr("Bye bye!", "លាហើយ!"), (90, 110, 160), 28, 1.0, -40)
                    if self.hearts <= 0:
                        self.finish(False)
        self.bugs = [b for b in self.bugs if b.state != "dead" and -400 < b.y]
        if not self.frog.tongue:
            tb = self.target_bug()
            if tb:
                self.frog.look = (tb.x, tb.y)
        self.frog.update(dt, self.on_eat)
        self.parts.update(dt)
        self.hands.update(dt, self.next_key())

    def next_key(self):
        if self.state != "play":
            return None
        tb = self.target_bug()
        return tb.next_char if tb else None

    # ---- drawing
    def draw_hud(self, surf, t):
        name = tr("Level", "កម្រិត") + f" {self.idx + 1}: {level_name(self.lv)}"
        tw = text_width(name, 24)
        r = pygame.Rect(16, 14, tw + 36, 48)
        rrect(surf, (40, 110, 160), r.move(0, 4), 22)
        rrect(surf, WHITE, r, 22)
        draw_text(surf, name, 24, INK, r.center)
        # progress bar
        bar = pygame.Rect(W / 2 - 190, 18, 380, 40)
        rrect(surf, (40, 110, 160), bar.move(0, 4), 20)
        rrect(surf, WHITE, bar, 20)
        k = min(1.0, self.eaten / self.goal)
        if k > 0:
            fill = pygame.Rect(bar.x + 5, bar.y + 5, max(30, (bar.w - 10) * k), bar.h - 10)
            rrect(surf, (110, 205, 80), fill, 15)
            rrect(surf, (160, 230, 120), pygame.Rect(fill.x + 6, fill.y + 3, fill.w - 12, 8), 4)
        draw_text(surf, f"{self.eaten} / {self.goal} " + tr("bugs", "សត្វល្អិត"), 22, INK, bar.center,
                  outline=WHITE, ow=2)
        icon = pygame.transform.smoothscale_by(bug_frames("lady")[int(t * 10) % 6], 0.5)
        surf.blit(icon, (bar.x - 50, bar.y - 10))
        # hearts
        for i in range(5):
            x = W - 40 - i * 46
            if i < self.hearts:
                draw_heart(surf, x, 34, 22)
            else:
                draw_heart(surf, x, 34, 22, (200, 210, 220), (150, 160, 175))
        if self.combo >= 3:
            draw_text(surf, tr("Combo", "ជាប់គ្នា") + f" x{self.combo}", 26, (255, 170, 30), (W / 2, 82), outline=WHITE, ow=3)

    def draw(self, surf):
        t = self.app.world.t
        self.app.world.draw(surf)
        draw_pad(surf, 640, 540, 320, 86, PAD, water_col(540))
        tb = self.target_bug()
        for b in self.bugs:
            if b.state != "grabbed":
                b.draw(surf, t, self.words, target=(b is tb), locked=(b is self.locked))
        self.frog.draw(surf, t)
        self.frog.draw_tongue(surf)
        for b in self.bugs:
            if b.state == "grabbed":
                b.draw(surf, t, self.words)
        self.draw_hud(surf, t)
        # bottom panel with keyboard + hands
        draw_panel(surf)
        nc = self.next_key()
        if self.state == "ready":
            glow = "".join(c for c in "fj" if c not in self.home_pressed)
        else:
            glow = nc
        draw_keyboard(surf, 640, self.KB_TOP, 46, t, glow, self.pressed)
        self.hands.draw(surf, t, glow_all=(self.state == "ready"))
        draw_finger_hint(surf, 175, 700, nc, t)
        if nc is not None:
            draw_text(surf, tr("PRESS", "ចុច"), 20, (170, 140, 100), (1105, 650))
            draw_text(surf, "SPACE" if nc == " " else nc.upper(), 64, finger_color(nc), (1105, 712),
                      outline=darker(finger_color(nc), 0.45), ow=4)

        if self.state == "ready":
            alpha_fill(surf, (20, 30, 50), 110, pygame.Rect(0, 0, W, 585))
            card = pygame.Rect(W / 2 - 400, 90, 800, 450)
            draw_card(surf, card)
            sc = min(1.0, self.state_t * 4)
            draw_text(surf, tr("GET READY!", "ត្រៀមខ្លួន!"), 64, (255, 200, 50), (W / 2, 148),
                      outline=(120, 80, 20), ow=5, title=True, scale=0.3 + 0.7 * sc)
            tip = level_tip(self.lv)
            for i, ln in enumerate(wrap(tip, 27, 700)[:2]):
                draw_text(surf, ln, 27, INK, (W / 2, 210 + i * 36))
            if self.words:
                hint = tr("Type the WORD on each bug!", "វាយពាក្យនៅលើសត្វល្អិតនីមួយៗ!")
            else:
                hint = tr("Type the LETTER on each bug!", "វាយអក្សរនៅលើសត្វល្អិតនីមួយៗ!")
            draw_text(surf, hint, 24, (90, 140, 200), (W / 2, 290))
            pygame.draw.line(surf, (235, 215, 175), (card.x + 40, 322), (card.right - 40, 322), 3)
            draw_text(surf, tr("Put your fingers on the HOME ROW", "ដាក់ម្រាមដៃនៅលើជួរដើម"), 30, (80, 170, 70),
                      (W / 2, 358))
            for i, ch in enumerate("fj"):
                done = ch in self.home_pressed
                kx = W / 2 + (i - 0.5) * 150
                col = (110, 205, 80) if done else finger_color(ch)
                bounce = 0 if done else 4 * math.sin(t * 7 + i)
                kr = pygame.Rect(0, 0, 84, 84)
                kr.center = (kx, 450 - bounce)
                rrect(surf, darker(col, 0.35), kr.move(0, 7), 18)
                rrect(surf, col, kr, 18)
                draw_text(surf, ch.upper(), 48, WHITE, kr.center, outline=darker(col, 0.4), ow=3)
                pygame.draw.line(surf, WHITE, (kx - 12, kr.bottom - 13), (kx + 12, kr.bottom - 13), 4)
                if done:
                    draw_text(surf, "OK!", 22, (80, 170, 70), (kx + 62, kr.centery))
            if int(t * 2) % 2 == 0:
                draw_text(surf, tr("Press F and J to start!", "ចុច F និង J ដើម្បីចាប់ផ្ដើម!"), 28,
                          (230, 120, 40), (W / 2, 516))
        elif self.state == "go":
            k = self.state_t
            draw_text(surf, tr("GO!", "ទៅ!"), 120, (120, 230, 90), (W / 2, 260), outline=(40, 90, 40), ow=7,
                      title=True, scale=1 + k * 0.6)
        self.parts.draw(surf)
        if self.paused:
            draw_overlay(surf, 150)
            card = pygame.Rect(W / 2 - 260, 220, 520, 290)
            draw_card(surf, card)
            draw_text(surf, tr("PAUSED", "ផ្អាក"), 64, (255, 190, 40), (W / 2, 290), outline=(120, 80, 20), ow=5,
                      title=True)
            draw_text(surf, tr("Take a little break!", "សម្រាកបន្តិចសិន!"), 28, INK, (W / 2, 355))
            draw_music_button(surf, (W / 2 + 215, 262), self.app.music_on, t)
            for b, _ in self.pause_buttons():
                b.draw(surf, t)
        if self.state == "result":
            self.draw_result(surf, t)

    def draw_result(self, surf, t):
        r = self.result
        draw_overlay(surf, 150)
        card = pygame.Rect(W / 2 - 330, 110, 660, 560)
        draw_card(surf, card)
        if r["win"]:
            title, col = tr("YUMMY! LEVEL CLEAR!", "ឆ្ងាញ់! ជាប់កម្រិតហើយ!"), (120, 210, 80)
        else:
            title, col = tr("OH NO! THE BUGS GOT AWAY", "អូ! សត្វល្អិតហោះបាត់ហើយ"), (255, 130, 90)
        draw_text(surf, title, 48, col, (W / 2, 172), outline=darker(col, 0.55), ow=5, title=True, max_w=620)
        for i in range(3):
            x = W / 2 + (i - 1) * 110
            y = 260 - (12 if i == 1 else 0)
            if i < self.stars_shown:
                age = self.state_t - (0.5 + i * 0.4)
                sc = 1 + 0.5 * max(0, 1 - age * 4)
                draw_star(surf, x, y, 44 * sc)
            else:
                pygame.draw.polygon(surf, (220, 210, 190), star_points(x, y, 44))
        lines = [
            (tr("Bugs eaten", "ចាប់បាន"), f"{self.eaten}"),
            (tr("Accuracy", "ភាពត្រឹមត្រូវ"), f"{r['acc']:.0f}%"),
            (tr("Speed", "ល្បឿន"), f"{r['wpm']:.0f} WPM"),
            (tr("Best combo", "ជាប់គ្នាច្រើនបំផុត"), f"{self.best_combo}"),
        ]
        for i, (a, b) in enumerate(lines):
            y = 340 + i * 40
            draw_text(surf, a, 28, (130, 110, 90), (W / 2 - 20, y), anchor="midright")
            draw_text(surf, b, 30, INK, (W / 2 + 20, y), anchor="midleft")
        if r["tricky"]:
            ks = "  ".join(k.upper() if k != " " else "SPACE" for k in r["tricky"])
            draw_text(surf, tr("Practice these keys:", "ហាត់គ្រាប់ចុចទាំងនេះ:") + f"  {ks}", 24, (230, 90, 90),
                      (W / 2, 515))
        elif r["win"] and r["acc"] < 85:
            draw_text(surf, tr("Tip: go slow and use the right finger!", "យឺតៗ ហើយប្រើម្រាមដៃឱ្យត្រូវ!"), 24,
                      (230, 120, 60), (W / 2, 515))
        elif r["win"]:
            draw_text(surf, tr("Wonderful typing!", "វាយបានល្អណាស់!"), 24, (80, 170, 70), (W / 2, 515))
        for b, a in self.res_buttons:
            b.draw(surf, t, selected=(a == ("next" if any(x == "next" for _, x in self.res_buttons) else "again")))


# ---------------------------------------------------------------- app
class App:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        os.environ.setdefault("SDL_RENDER_SCALE_QUALITY", "linear")   # smooth scaling on big screens
        pygame.init()
        global _DATA
        self.data = _DATA = load_data()
        full = self.data.get("fullscreen", True) and os.environ.get("SDL_VIDEODRIVER") != "dummy"
        flags = pygame.SCALED | (pygame.FULLSCREEN if full else pygame.RESIZABLE)
        self.screen = pygame.display.set_mode((W, H), flags)
        pygame.display.set_caption("Hungry Frog - Typing Game")
        icon = pygame.Surface((64, 64), pygame.SRCALPHA)
        Frog(32, 50, 0.22).draw(icon, 0)
        pygame.display.set_icon(icon)
        pygame.key.start_text_input()
        pygame.key.set_repeat()
        self.clock = pygame.time.Clock()
        self.sfx = Sfx()
        set_lang(self.data.get("lang", "km"))
        self.save = new_student()   # replaced when a student is chosen
        self.student_name = None
        self.world = World()
        self.music_on = self.data.get("music", True)
        self.music_now = None
        self.scene = None
        self.goto(StudentScene(self))
        self.running = True

    def use_student(self, name):
        self.student_name = name
        self.save = self.data["students"][name]
        self.data["last"] = name
        write_save()

    def add_student(self, name):
        self.data["students"][name] = new_student()
        self.data["order"].append(name)
        write_save()

    def remove_student(self, name):
        self.data["students"].pop(name, None)
        if name in self.data["order"]:
            self.data["order"].remove(name)
        if self.data.get("last") == name:
            self.data["last"] = None
        write_save()

    def toggle_lang(self):
        self.data["lang"] = "en" if LANG == "km" else "km"
        set_lang(self.data["lang"])
        write_save()

    def toggle_fullscreen(self):
        try:
            pygame.display.toggle_fullscreen()
        except Exception:
            return
        self.data["fullscreen"] = bool(pygame.display.is_fullscreen())
        write_save()

    def goto(self, scene):
        self.scene = scene
        self.play_music("play" if isinstance(scene, PlayScene) else "menu")

    def play_music(self, name):
        """Loop assets/music_<name>.wav (menu or play). Quietly does nothing without audio."""
        if not self.music_on or not self.sfx.sounds:
            return
        if name == self.music_now:
            return
        path = os.path.join(ASSETS, f"music_{name}.wav")
        try:
            pygame.mixer.music.fadeout(300)
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1, fade_ms=600)
            self.music_now = name
        except Exception:
            self.music_now = None

    def toggle_music(self):
        self.music_on = not self.music_on
        self.data["music"] = self.music_on
        write_save()
        self.sfx.play("click")
        if self.music_on:
            self.play_music("play" if isinstance(self.scene, PlayScene) else "menu")
        else:
            try:
                pygame.mixer.music.fadeout(300)
            except Exception:
                pass
            self.music_now = None

    def quit(self):
        write_save(self.save)
        self.running = False

    def step(self, dt, events):
        for e in events:
            if e.type == pygame.QUIT:
                self.quit()
                return
            if e.type == pygame.KEYDOWN and (e.key == pygame.K_F11 or
                                             (e.key == pygame.K_RETURN and e.mod & pygame.KMOD_ALT)):
                self.toggle_fullscreen()
                continue
            if e.type == pygame.KEYDOWN and e.key == pygame.K_F8:
                self.toggle_music()
                continue
            self.scene.handle(e)
        self.world.update(dt)
        self.scene.update(dt)
        self.scene.draw(self.screen)

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            self.step(dt, pygame.event.get())
            pygame.display.flip()
        pygame.quit()


def selftest(out_dir):
    """Drive every screen without a window and save screenshots (used to check the .exe)."""
    global SAVE_PATH
    os.makedirs(out_dir, exist_ok=True)
    SAVE_PATH = os.path.join(out_dir, "selftest_save.json")
    if os.path.exists(SAVE_PATH):
        os.remove(SAVE_PATH)
    app = App()

    def run(sec, events=()):
        for i in range(int(sec * 60)):
            app.step(1 / 60, list(events) if i == 0 else [])

    def txt(c):
        return pygame.event.Event(pygame.TEXTINPUT, text=c)

    def key(k):
        return pygame.event.Event(pygame.KEYDOWN, key=k, mod=0, unicode="")

    shots = []

    def shot(name):
        p = os.path.join(out_dir, name + ".png")
        pygame.image.save(app.screen, p)
        shots.append(p)

    run(0.5)
    shot("1_students")
    run(0.1, [key(pygame.K_RETURN)])
    for ch in "សុខា":
        run(0.05, [txt(ch)])
    shot("2_name")
    run(0.1, [key(pygame.K_RETURN)])
    run(0.5)
    shot("3_title")
    app.goto(LessonScene(app))
    for _ in range(2):
        run(0.1, [key(pygame.K_RETURN)])
    run(0.5)
    shot("4_lesson")
    app.goto(PlayScene(app, 0))
    run(0.5)
    shot("5_ready")
    run(0.1, [txt("f")])
    run(0.1, [txt("j")])
    run(5)
    sc = app.scene
    for step in range(900):
        tb = sc.target_bug()
        app.step(1 / 60, [txt(tb.next_char)] if (tb and step % 20 == 0 and 100 < tb.x < W - 100) else [])
    shot("6_play")
    print("SELFTEST OK", app.scene.eaten, "bugs;", len(shots), "screenshots in", out_dir)
    pygame.quit()


def main():
    if "--selftest" in sys.argv:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        i = sys.argv.index("--selftest")
        selftest(sys.argv[i + 1] if len(sys.argv) > i + 1 else "selftest_out")
        return
    App().run()


if __name__ == "__main__":
    main()
