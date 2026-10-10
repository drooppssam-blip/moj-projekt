#!/usr/bin/env python3
"""Własna, wesoła muzyczka (bez praw autorskich innych osób): skoczny ukulelowy rytm z dzwoneczkami, do filmów POV.
użycie: muzyka_wesola.py długość_s wyjscie.wav"""
import sys, wave, numpy as np
dur, out = float(sys.argv[1]), sys.argv[2]
SR = 48000; N = int(dur * SR); rng = np.random.default_rng(5)
y = np.zeros(N)
m = lambda n: 440 * 2 ** ((n - 69) / 12)
def pluck(f, start, length, amp, bright=0.6):
    i0 = int(start * SR)
    if i0 >= N: return
    n = min(int(length * SR), N - i0); p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p) * bright + (1 - bright) * np.sin(np.linspace(0, 2 * np.pi, p))
    o = np.zeros(n)
    for i in range(n):
        o[i] = buf[i % p]; buf[i % p] = 0.995 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    y[i0:i0 + n] += amp * o
def bell(f, start, amp):
    i0 = int(start * SR)
    if i0 >= N: return
    n = min(int(1.2 * SR), N - i0); tt = np.arange(n) / SR
    y[i0:i0 + n] += amp * (np.sin(2*np.pi*f*tt) * np.exp(-tt * 3) + 0.3 * np.sin(2*np.pi*2.76*f*tt) * np.exp(-tt * 8))
beat = 60 / 118
chords = [[60, 64, 67, 72], [57, 60, 64, 69], [53, 57, 60, 65], [55, 59, 62, 67]]   # C, Am, F, G
melody = [76, 79, 81, 79, 76, 74, 72, 74, 76, 77, 79, 77, 76, 74, 72, 71]
t = 0.0; k = 0
while t < dur:
    c = chords[(k // 4) % 4]
    for j, s in enumerate([0, 0.5, 0.75]):                     # rytm „bum, cyk-cyk” jak ukulele
        for q, n in enumerate(c): pluck(m(n), t + s * beat + q * 0.012, 0.4, 0.09 if j == 0 else 0.06)
    if k % 2 == 0: bell(m(melody[(k // 2) % len(melody)]), t, 0.12)
    t += beat; k += 1
for d, g in [(0.12, 0.25), (0.25, 0.12)]:
    sh = int(d * SR); y[sh:] += g * y[:-sh]
tt = np.arange(N) / SR
y *= np.minimum(1, np.minimum(tt / 0.2, (dur - tt) / 1.0))
y = y / np.max(np.abs(y)) * 0.7
st = np.stack([y, np.roll(y, int(0.01 * SR))], axis=1)
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok', out)
