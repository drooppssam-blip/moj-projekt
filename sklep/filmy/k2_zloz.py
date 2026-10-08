#!/usr/bin/env python3
"""Film K2 „Kamera w salonie, 3:12 w nocy”: nagranie jak z kamery domowej, kociak atakuje karatekę i patrzy w kamerę."""
import subprocess, tempfile, os, wave
import numpy as np, imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
T = tempfile.mkdtemp()
def run(cmd): subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
V = 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30'
run([FF, '-y', '-i', 'k2_skok.mp4', '-i', 'k2_patrzy.mp4', '-filter_complex',
     f'[0:v]{V}[a];[1:v]{V}[b];[a][b]concat=n=2:v=1:a=0,noise=alls=4:allf=t,format=yuv420p[v]',   # lekkie ziarno jak w kamerze
     '-map', '[v]', '-c:v', 'libx264', '-crf', '19', f'{T}/base.mp4'])
end = 12.0
N = 13
subprocess.run(['python3', 'kamera_hud.py', f'{T}/hud', str(N)], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'napis_tt.py', 'Kamera w salonie, 3:12 w nocy', f'{T}/c.png', '330'], check=True, env={**os.environ, 'NAPIS_SIZE': '64'})
inp = ['-i', f'{T}/base.mp4']; fc = []; prev = '0:v'
for i in range(N):
    inp += ['-i', f'{T}/hud/h{i:02d}.png']; fc.append(f"[{prev}][{i+1}:v]overlay=0:0:enable='gte(t,{i})*lt(t,{i+1})'[o{i}]"); prev = f'o{i}'
inp += ['-i', f'{T}/c.png']; fc.append(f"[{prev}][{N+1}:v]overlay=0:0:enable='between(t,0,3.2)',format=yuv420p[v]")
run([FF, '-y'] + inp + ['-filter_complex', ';'.join(fc), '-map', '[v]', '-t', f'{end}', '-c:v', 'libx264', '-crf', '23', '-maxrate', '8M', '-bufsize', '16M', f'{T}/v.mp4'])
# dźwięk: własna zabawna muzyczka + cichy szum pokoju z mikrofonu kamery i miękkie stuknięcia łapek przy skoku i tarzaniu
SR = 48000; t = np.arange(int(end * SR)) / SR; rng = np.random.default_rng(7)
y = np.cumsum(rng.standard_normal(len(t))); y -= np.convolve(y, np.ones(4800) / 4800, 'same'); y = y / np.max(np.abs(y)) * 0.05
for s in (2.05, 2.35, 3.6, 4.1, 4.6, 5.2, 6.6):
    i0 = int(s * SR); n = int(0.12 * SR); tt = np.arange(n) / SR
    y[i0:i0 + n] += 0.35 * np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 40) + 0.08 * rng.standard_normal(n) * np.exp(-tt * 60)
y = np.clip(y, -1, 1)
with wave.open(f'{T}/a.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype('<i2').tobytes())
subprocess.run(['python3', 'muzyka_skradanie.py', f'{end}', '7.5', f'{T}/mus.wav'], check=True, stdout=subprocess.DEVNULL)   # 7,5 s: kociak patrzy w kamerę
run([FF, '-y', '-i', f'{T}/a.wav', '-i', f'{T}/mus.wav', '-filter_complex', '[0:a]volume=0.8[r];[1:a]volume=0.9[m];[r][m]amix=inputs=2:normalize=0,alimiter=limit=0.95[o]', '-map', '[o]', f'{T}/mix.wav'])
run([FF, '-y', '-i', f'{T}/v.mp4', '-i', f'{T}/mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-ac', '2', '-t', f'{end}', '-movflags', '+faststart', 'k2_kamera_w_nocy.mp4'])
print('ok', end)
