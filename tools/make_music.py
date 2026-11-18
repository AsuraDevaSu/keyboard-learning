#!/usr/bin/env python3
"""Generate the background music for Hungry Frog (original tunes, made from code).

Writes assets/music_menu.wav and assets/music_play.wav. Each file loops seamlessly.
Run:  python3 tools/make_music.py
"""
import math
import os
import random
import struct
import wave

SR = 22050
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")


def freq(m):
    return 440.0 * 2 ** ((m - 69) / 12)


CHORDS = {  # root (MIDI, bass octave) and chord tones
    "C": (48, [60, 64, 67]), "Am": (45, [57, 60, 64]), "F": (41, [53, 57, 60]),
    "G": (43, [55, 59, 62]), "Dm": (50, [62, 65, 69]), "Em": (52, [64, 67, 71]),
}


class Track:
    def __init__(self, bpm, bars):
        self.beat = 60.0 / bpm
        self.n = int(SR * self.beat * 4 * bars)
        self.buf = [0.0] * self.n

    def add(self, start_beat, samples):
        i0 = int(start_beat * self.beat * SR)
        n = self.n
        buf = self.buf
        for i, v in enumerate(samples):
            buf[(i0 + i) % n] += v      # wrap around so the loop is seamless

    def note(self, start, beats, midi, vol, wave_kind="lead", release=0.08):
        dur = beats * self.beat
        n = int(SR * (dur + release))
        f = freq(midi)
        out = []
        ph = 0.0
        for i in range(n):
            t = i / SR
            vib = 1 + (0.004 * math.sin(2 * math.pi * 5.5 * t) if wave_kind == "lead" and t > 0.12 else 0)
            ph += 2 * math.pi * f * vib / SR
            if wave_kind == "lead":      # soft square-ish (odd harmonics)
                v = math.sin(ph) + 0.28 * math.sin(3 * ph) + 0.12 * math.sin(5 * ph)
            elif wave_kind == "bell":    # bright bell / marimba
                v = math.sin(ph) + 0.35 * math.sin(2 * ph) * math.exp(-t * 12) + 0.2 * math.sin(4 * ph) * math.exp(-t * 20)
            elif wave_kind == "bass":
                v = math.sin(ph) + 0.25 * math.sin(2 * ph)
            else:                        # triangle pad
                x = (ph / (2 * math.pi)) % 1.0
                v = 4 * abs(x - 0.5) - 1
            # envelope
            a = min(1.0, t / 0.01)
            if wave_kind == "bell":
                env = a * math.exp(-t * 4.5)
            else:
                env = a * (0.85 + 0.15 * math.exp(-t * 8))
            if t > dur:
                env *= max(0.0, 1 - (t - dur) / release)
            out.append(v * env * vol)
        self.add(start, out)

    def kick(self, start, vol=0.9):
        n = int(SR * 0.16)
        ph, out = 0.0, []
        for i in range(n):
            t = i / SR
            ph += 2 * math.pi * (50 + 110 * math.exp(-t * 30)) / SR
            out.append(math.sin(ph) * math.exp(-t * 22) * vol)
        self.add(start, out)

    def noise(self, start, length, decay, vol, bright=True, seed=0):
        rnd = random.Random(seed)
        n = int(SR * length)
        prev, out = 0.0, []
        for i in range(n):
            x = rnd.uniform(-1, 1)
            v = (x - prev) if bright else (x + prev) * 0.5
            prev = x
            out.append(v * math.exp(-i / SR * decay) * vol)
        self.add(start, out)

    def save(self, path, peak=0.75):
        m = max(1e-6, max(abs(v) for v in self.buf))
        k = peak / m
        with wave.open(path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(b"".join(struct.pack("<h", int(v * k * 32767)) for v in self.buf))
        print("wrote", os.path.relpath(path), f"{self.n / SR:.1f}s")


def lay_melody(tr, bars, vol, kind="lead"):
    beat = 0.0
    for bar in bars:
        for midi, length in bar:
            if midi is not None:
                tr.note(beat, length * 0.9, midi, vol, kind)
            beat += length


def menu_tune():
    """Calm, happy pond song (104 bpm)."""
    chords = ["C", "Am", "F", "G", "C", "Am", "F", "G", "C", "Am", "Dm", "G", "C", "F", "G", "C"]
    tr = Track(104, len(chords))
    melody = [
        [(76, 1), (79, 1), (76, .5), (74, .5), (72, 1)],
        [(72, .5), (74, .5), (76, 1), (72, 1), (69, 1)],
        [(69, 1), (72, 1), (77, 1), (76, .5), (74, .5)],
        [(74, 1.5), (71, .5), (74, 1), (79, 1)],
        [(79, .5), (77, .5), (76, 1), (79, 1), (84, 1)],
        [(81, 1), (79, .5), (76, .5), (72, 1), (76, 1)],
        [(77, 1), (76, .5), (74, .5), (72, 1), (71, 1)],
        [(74, 2), (None, 1), (67, 1)],
        [(72, 1), (76, .5), (79, .5), (84, 1), (79, 1)],
        [(81, 1), (76, 1), (72, 1), (76, 1)],
        [(77, 1), (74, .5), (77, .5), (81, 1), (77, 1)],
        [(79, 1.5), (77, .5), (76, 1), (74, 1)],
        [(76, 1), (79, 1), (84, 1), (83, .5), (81, .5)],
        [(81, 1), (77, 1), (72, 1), (77, 1)],
        [(79, 1), (77, .5), (76, .5), (74, 1), (71, 1)],
        [(72, 3), (None, 1)],
    ]
    lay_melody(tr, melody, 0.30, "bell")
    for b, ch in enumerate(chords):
        root, tones = CHORDS[ch]
        base = b * 4
        tr.note(base, 1.8, root, 0.42, "bass")
        tr.note(base + 2, 1.8, root + 7, 0.36, "bass")
        for k in range(8):                       # soft arpeggio
            tr.note(base + k * 0.5, 0.45, tones[[0, 1, 2, 1][k % 4]], 0.07, "pad")
        tr.kick(base, 0.35)
        for k in range(8):
            tr.noise(base + k * 0.5, 0.05, 70, 0.05 if k % 2 else 0.08, seed=b * 8 + k)
    return tr


def play_tune():
    """Bouncy bug-catching song (128 bpm)."""
    chords = ["C", "F", "G", "C", "Am", "F", "G", "C", "F", "C", "Dm", "G", "Am", "F", "G", "C"]
    tr = Track(128, len(chords))
    melody = [
        [(72, .5), (72, .5), (76, .5), (79, .5), (84, 1), (79, 1)],
        [(81, .5), (79, .5), (77, .5), (76, .5), (77, 1), (72, 1)],
        [(74, .5), (76, .5), (77, .5), (79, .5), (83, 1), (79, 1)],
        [(84, 1), (79, .5), (76, .5), (72, 1), (None, 1)],
        [(76, .5), (76, .5), (81, .5), (76, .5), (84, 1), (81, 1)],
        [(77, .5), (81, .5), (84, .5), (81, .5), (77, 1), (72, 1)],
        [(79, .5), (77, .5), (76, .5), (74, .5), (71, 1), (74, 1)],
        [(72, 1.5), (67, .5), (72, 1), (None, 1)],
        [(77, .5), (77, .5), (81, .5), (84, .5), (86, 1), (84, 1)],
        [(84, .5), (79, .5), (76, .5), (79, .5), (84, 1), (None, 1)],
        [(74, .5), (77, .5), (81, .5), (77, .5), (86, 1), (81, 1)],
        [(79, .5), (83, .5), (86, .5), (83, .5), (79, 1), (74, 1)],
        [(81, .5), (84, .5), (88, .5), (84, .5), (81, 1), (76, 1)],
        [(77, .5), (81, .5), (84, .5), (81, .5), (77, 1), (81, 1)],
        [(79, .5), (79, .5), (81, .5), (83, .5), (86, 1), (83, 1)],
        [(84, 1.5), (79, .5), (84, 1), (None, 1)],
    ]
    lay_melody(tr, melody, 0.26, "lead")
    lay_melody(tr, [[(m - 12 if m else None, l) for m, l in bar] for bar in melody], 0.10, "bell")
    for b, ch in enumerate(chords):
        root, tones = CHORDS[ch]
        base = b * 4
        for k, off in enumerate((0, 1, 2, 3)):     # walking bass: root, 5th, octave, 5th
            tr.note(base + off, 0.8, root + (0, 7, 12, 7)[k], 0.40, "bass")
        for k in range(4):                          # off-beat chord stabs
            for tn in tones:
                tr.note(base + k + 0.5, 0.25, tn, 0.05, "pad")
        tr.kick(base, 0.8)
        tr.kick(base + 2, 0.8)
        tr.noise(base + 1, 0.12, 25, 0.22, bright=False, seed=b)      # snare-ish
        tr.noise(base + 3, 0.12, 25, 0.22, bright=False, seed=b + 99)
        for k in range(8):
            tr.noise(base + k * 0.5, 0.04, 90, 0.07 if k % 2 else 0.11, seed=b * 8 + k + 500)
    return tr


if __name__ == "__main__":
    menu_tune().save(os.path.join(OUT, "music_menu.wav"))
    play_tune().save(os.path.join(OUT, "music_play.wav"))
