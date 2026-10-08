#!/usr/bin/env python3
"""Własna kołysanka w stylu pozytywki (bez praw autorskich innych osób), na słodkie filmy bez lektora.
użycie: kolysanka.py długość_s wyjscie.wav"""
import sys, wave, numpy as np
dur, out = float(sys.argv[1]), sys.argv[2]
SR = 48000
t = np.arange(int(dur * SR)) / SR
def bell(f, start, amp):
    y = np.zeros_like(t); i0 = int(start * SR); i1 = min(len(t), i0 + int(2.5 * SR))
    if i0 >= len(t): return y
    tt = t[: i1 - i0]
    env = np.minimum(1, tt / 0.004)
    tone = (np.sin(2*np.pi*f*tt) * np.exp(-tt * 2.2) + 0.4*np.sin(2*np.pi*2.0*f*tt) * np.exp(-tt * 4)
            + 0.25*np.sin(2*np.pi*2.76*f*tt) * np.exp(-tt * 7) + 0.1*np.sin(2*np.pi*5.4*f*tt) * np.exp(-tt * 12))  # metaliczny ząbek pozytywki
    y[i0:i1] = amp * env * tone
    return y
m = lambda n: 440 * 2 ** ((n - 69) / 12)
# metrum 3/4, 66 BPM; prosta, własna melodia w C-dur, wysoko jak w pozytywce
beat = 60 / 66
mel = [(79, 1), (76, 1), (77, 1), (79, 2), (84, 1), (83, 1), (81, 1), (79, 1), (77, 2), (76, 1),
       (74, 1), (76, 1), (77, 1), (79, 2), (76, 1), (74, 1), (72, 2), (0, 1)]
bass = [60, 65, 67, 60, 62, 67, 60, 60]          # jedna nuta basu na takt
y = np.zeros_like(t); s = 0.0
while s < dur:
    pos = s
    for n, l in mel:
        if n: y += bell(m(n), pos, 0.16)
        pos += l * beat
    for k, b in enumerate(bass): y += bell(m(b), s + k * 3 * beat, 0.08)
    s = pos
for d, g in [(0.09, 0.3), (0.19, 0.18), (0.31, 0.1)]:   # lekki pogłos
    sh = int(d * SR); y[sh:] += g * y[:-sh]
fade = np.minimum(1, np.minimum(t / 0.5, (dur - t) / 1.5))
y = y * fade; y = y / np.max(np.abs(y)) * 0.6
st = np.stack([y, np.roll(y, int(0.01 * SR))], axis=1)
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok', out)
