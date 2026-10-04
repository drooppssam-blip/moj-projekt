#!/usr/bin/env python3
"""Film K1 „Odliczanie”: kobieta odlicza 3, 2, 1 i rozrywa folię, osobne ujęcie rozpakowania z prawdziwym wyglądem produktu,
potem kot walczy z karateką. Bez lektora i bez dźwięku (muzykę dodaje się w aplikacji)."""
import subprocess, tempfile, os
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
T = tempfile.mkdtemp()
def run(cmd): subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
V = 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30'
A0, A1 = 0.5, 3.55         # od 0,5 s palce są już w górze; ucinamy po chwyceniu paczki, zanim AI pokaże inną zabawkę
dA = A1 - A0
# duże cyfry odliczania, zgrane z palcami kobiety
for i, n in enumerate(['3', '2', '1']):
    subprocess.run(['python3', 'napis_duzy.py', n, f'{T}/n{i}.png'], check=True, env={**os.environ, 'NAPIS_SIZE': '320', 'NAPIS_Y': '1400'})
num = [(0, 0.75), (0.75, 1.78), (1.78, 2.4)]   # sprawdzone klatka po klatce z palcami kobiety
ov = ';'.join(f"[o{i}][{i+1}:v]overlay=0:0:enable='between(t,{a},{b})'[o{i+1}]" for i, (a, b) in enumerate(num))
run([FF, '-y', '-ss', f'{A0}', '-t', f'{dA:.3f}', '-i', 'k1_odliczanie.mp4'] + sum([['-i', f'{T}/n{i}.png'] for i in range(3)], []) +
    ['-filter_complex', f'[0:v]{V}[o0];{ov};[o3]format=yuv420p[v]', '-map', '[v]', '-an', '-c:v', 'libx264', '-crf', '19', f'{T}/a.mp4'])
# rozpakowanie: osobne ujęcie wygenerowane od klatki z prawdziwym wyglądem produktu
run([FF, '-y', '-t', '5.5', '-i', 'k1_wyjmuje.mp4', '-vf', f'{V},format=yuv420p', '-an', '-c:v', 'libx264', '-crf', '19', f'{T}/b.mp4'])
# kot z karateką
run([FF, '-y', '-t', '5.8', '-i', 'k1_kot.mp4', '-vf', f'{V},format=yuv420p', '-an', '-c:v', 'libx264', '-crf', '19', f'{T}/c.mp4'])
open(f'{T}/l.txt', 'w').write(''.join(f"file '{T}/{k}.mp4'\n" for k in 'abc'))
run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', f'{T}/l.txt', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
     '-map', '0:v', '-map', '1:a', '-shortest', '-c:v', 'libx264', '-crf', '20', '-c:a', 'aac', '-movflags', '+faststart', 'k1_odliczanie_final.mp4'])
print('gotowe')
