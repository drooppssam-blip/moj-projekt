#!/usr/bin/env python3
"""Własna, zabawna ścieżka do K2 (bez praw autorskich innych osób): skradanie na szarpanych strunach,
szybsza walka, „zatrzymana płyta” w chwili spojrzenia w kamerę, potem cisza i jedno „plink”.
użycie: muzyka_skradanie.py długość_s stop_s wyjscie.wav"""
import sys, wave, numpy as np
dur, stop, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
SR = 48000; N = int(dur * SR); rng = np.random.default_rng(3)
y = np.zeros(N)
m = lambda n: 440 * 2 ** ((n - 69) / 12)
def pluck(f, start, length=0.35, amp=0.5, bright=0.5):
    """struna szarpana (Karplus-Strong), jak pizzicato"""
    i0 = int(start * SR)
    if i0 >= N: return
    n = min(int(length * SR), N - i0); p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p) * bright + (1 - bright) * np.sin(np.linspace(0, 2 * np.pi, p))
    o = np.zeros(n)
    for i in range(n):
        o[i] = buf[i % p]; buf[i % p] = 0.996 * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    o *= np.minimum(1, (n - np.arange(n)) / (0.03 * SR))
    y[i0:i0 + n] += amp * o
# 1) skradanie: wolne, „na palcach”, molowe kroki w dół (0 do 2 s)
beat = 60 / 100
sneak = [45, 0, 48, 0, 47, 0, 46, 0]
for k, n in enumerate(sneak):
    if n: pluck(m(n), k * beat / 2, 0.3, 0.55)
    if k % 2 == 1: pluck(m(69), k * beat / 2, 0.12, 0.12, 0.9)          # ciche „tik” palcami
# 2) skok i walka: szybciej, wyżej, z akcentami (2 s do stop)
t = 2.0; fight = [57, 60, 64, 60, 59, 62, 65, 62, 57, 60, 64, 67, 69, 67, 64, 60]
k = 0
while t < stop - 0.05:
    pluck(m(fight[k % len(fight)]), t, 0.22, 0.45); pluck(m(fight[k % len(fight)] - 12), t, 0.2, 0.25)
    t += 60 / 150 / 2; k += 1
# 3) „zatrzymana płyta”: szum z opadającym tonem, potem cisza
i0 = int(stop * SR); n = int(0.45 * SR); tt = np.arange(n) / SR
f = 900 * np.exp(-tt * 6) + 60
ph = 2 * np.pi * np.cumsum(f) / SR
scr = (0.5 * np.sign(np.sin(ph)) * 0.4 + 0.6 * rng.standard_normal(n) * np.abs(np.sin(ph * 0.5))) * np.exp(-tt * 4)
y[i0:i0 + n] = 0; y[i0:i0 + n] += 0.35 * scr[: max(0, min(n, N - i0))]
y[i0 + n:] = 0
# 4) po chwili ciszy jedno ciche, śmieszne „plink”
pluck(m(84), stop + 1.6, 0.6, 0.35, 0.3)
y = y / np.max(np.abs(y)) * 0.7
fade = np.ones(N); fade[: int(0.05 * SR)] = np.linspace(0, 1, int(0.05 * SR))
y *= fade
with wave.open(out, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype('<i2').tobytes())
print('ok', out)
