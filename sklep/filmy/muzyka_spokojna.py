#!/usr/bin/env python3
"""Spokojna, własna muzyka w tle (bez praw autorskich innych osób): miękkie akordy i delikatne arpeggio.
użycie: muzyka_spokojna.py długość_s wyjscie.wav"""
import sys, wave, numpy as np
dur, out = float(sys.argv[1]), sys.argv[2]
SR = 48000
t = np.arange(int(dur * SR)) / SR
def note(f, start, length, amp, decay):
    y = np.zeros_like(t); i0 = int(start * SR); i1 = min(len(t), i0 + int(length * SR))
    if i0 >= len(t): return y
    tt = t[: i1 - i0]
    env = np.exp(-tt * decay) * np.minimum(1, tt / 0.01)
    tone = np.sin(2*np.pi*f*tt) + 0.35*np.sin(2*np.pi*2*f*tt) + 0.12*np.sin(2*np.pi*3*f*tt)  # ciepłe „elektryczne pianino”
    y[i0:i1] = amp * env * tone
    return y
m = lambda n: 440 * 2 ** ((n - 69) / 12)
# Cmaj7, Am7, Fmaj7, G6 w spokojnym tempie, 80 BPM
bpm = 80; beat = 60 / bpm; bar = 4 * beat
chords = [[48, 55, 59, 64], [45, 52, 55, 60], [41, 48, 52, 57], [43, 50, 52, 59]]
arp = [[72, 76, 79, 76], [69, 72, 76, 72], [65, 69, 72, 69], [67, 71, 74, 71]]
y = np.zeros_like(t)
for k in range(int(dur / bar) + 1):
    c = chords[k % 4]; s = k * bar
    for n in c: y += note(m(n), s, bar + 0.6, 0.10, 0.9)                 # miękki akord
    for j in range(8):                                                     # arpeggio ósemkami
        y += note(m(arp[k % 4][j % 4]), s + j * beat / 2, 1.2, 0.07, 3.0)
# lekki pogłos: kilka opóźnionych, ściszonych kopii
for d, g in [(0.11, 0.35), (0.23, 0.22), (0.37, 0.12)]:
    sh = int(d * SR); y[sh:] += g * y[:-sh]
fade = np.minimum(1, np.minimum(t / 0.8, (dur - t) / 1.2))
y = y * fade; y = y / np.max(np.abs(y)) * 0.6
st = np.stack([y, np.roll(y, int(0.012 * SR))], axis=1)                    # szerokość stereo
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok', out)
