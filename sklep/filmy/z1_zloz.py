#!/usr/bin/env python3
"""Film Z1 „Zasnął w trakcie walki”: słodki, bez lektora i reklamy. Walka, zasypianie, sen z karateką, kołysanka."""
import subprocess, tempfile, os
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
T = tempfile.mkdtemp()
def run(cmd): subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
V = 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30'
X = 0.5                                       # długość płynnego przejścia między ujęciami
# (plik, początek, koniec w źródle, spowolnienie)
segs = [('r1_walka.mp4', 0.0, 3.6, 1.0), ('z1_zasypia.mp4', 0.0, 6.0, 1.08), ('s1_spi.mp4', 0.3, 4.0, 1.0)]
lens = []
for j, (f, a, b, k) in enumerate(segs):
    run([FF, '-y', '-i', f, '-vf', f'trim={a}:{b},setpts={k}*(PTS-STARTPTS),{V},format=yuv420p', '-an', '-c:v', 'libx264', '-crf', '19', f'{T}/s{j}.mp4'])
    lens.append((b - a) * k)
o1 = lens[0] - X; o2 = o1 + lens[1] - X; end = o2 + lens[2]
subprocess.run(['python3', 'napis_tt.py', 'Walczył do ostatniej sekundy...', f'{T}/c.png', '330'], check=True, env={**os.environ, 'NAPIS_SIZE': '70'})
fc = [f'[0:v][1:v]xfade=transition=fade:duration={X}:offset={o1:.3f}[v01]',
      f'[v01][2:v]xfade=transition=fade:duration={X}:offset={o2:.3f}[v02]',
      f"[3:v]format=rgba,fade=t=in:st={o1:.3f}:d=0.6:alpha=1[c]",
      f"[v02][c]overlay=0:0:enable='gte(t,{o1:.3f})',format=yuv420p[v]"]
run([FF, '-y', '-i', f'{T}/s0.mp4', '-i', f'{T}/s1.mp4', '-i', f'{T}/s2.mp4', '-loop', '1', '-i', f'{T}/c.png',
     '-filter_complex', ';'.join(fc), '-map', '[v]', '-t', f'{end:.3f}', '-c:v', 'libx264', '-crf', '20', f'{T}/v.mp4'])
# dźwięk: kołysanka przez cały film, odgłosy walki ciche i wyciszane przy zasypianiu
subprocess.run(['python3', 'kolysanka.py', f'{end:.2f}', f'{T}/m.wav'], check=True, stdout=subprocess.DEVNULL)
af = [f'[1:a]atrim=0:{lens[0]:.3f},asetpts=PTS-STARTPTS,volume=0.22,afade=t=out:st={o1:.3f}:d={X}[w]',
      '[2:a]volume=0.55[m]', '[w][m]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[a]']
run([FF, '-y', '-i', f'{T}/v.mp4', '-i', 'r1_walka.mp4', '-i', f'{T}/m.wav', '-filter_complex', ';'.join(af),
     '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{end:.3f}', '-movflags', '+faststart', 'z1_zasnal.mp4'])
print(f'zasypianie od {o1:.2f} s, sen od {o2:.2f} s, razem {end:.2f} s')
