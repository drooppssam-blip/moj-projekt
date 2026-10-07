#!/usr/bin/env python3
"""Film C1 „Masz podrapane ręce?”: kociak gryzie dłoń, potem walczy z karateką, na końcu karta z ceną 169 → 139 zł."""
import subprocess, tempfile, os, re
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
T = tempfile.mkdtemp()
def run(cmd): subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
def dur(f):
    o = subprocess.run([FF, '-i', f], stderr=subprocess.PIPE, text=True).stderr
    h, m, s = re.search(r'Duration: (\d+):(\d+):([\d.]+)', o).groups(); return int(h)*3600+int(m)*60+float(s)
L = ['c1_l1_p.wav', 'c1_l2_p.wav', 'c1_l3_p.wav', 'c1_l4_p.wav']
d = [dur(f) for f in L]
st = [0.1]
for i in range(3): st.append(st[i] + d[i] + 0.1)
end = st[3] + d[3] + 0.5
cut = st[2]                                  # cięcie na walkę razem z „Daj mu sparingpartnera”
V = 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30'
subprocess.run(['python3', 'karta_ceny.py', f'{T}/karta.png', '-460'], check=True)   # karta u góry, nad kotem
caps = [('d', 'MASZ PODRAPANE|RĘCE?', 0, st[1]),
        ('t', 'To nie złość. Twój kot nie ma z kim walczyć.', st[1], cut),
        ('d', 'DAJ MU|SPARINGPARTNERA', cut, st[3])]
for i, (k, t, a, b) in enumerate(caps):
    if k == 'd': subprocess.run(['python3', 'napis_duzy.py', t, f'{T}/c{i}.png'], check=True, env={**os.environ, 'NAPIS_SIZE': '86' if 'SPARING' in t else '110', 'NAPIS_Y': '1250'})
    else: subprocess.run(['python3', 'napis_tt.py', t, f'{T}/c{i}.png', '1200'], check=True, env={**os.environ, 'NAPIS_SIZE': '78'})
# scena 1: czyste pierwsze 2,6 s z N1 (później palce wyglądają na czerwone), zwolnione do długości lektora
KA = cut / 2.6
run([FF, '-y', '-i', 'n1_skok.mp4', '-vf', f'trim=0:2.6,setpts={KA:.4f}*(PTS-STARTPTS),{V},format=yuv420p', '-t', f'{cut:.3f}', '-an', '-c:v', 'libx264', '-crf', '19', f'{T}/a.mp4'])
# scena 2: walka z karateką, zwolniona tak, żeby starczyła do końca
KB = max(1.0, (end - cut) / dur('n1_walka.mp4'))
run([FF, '-y', '-i', 'n1_walka.mp4', '-vf', f'setpts={KB:.4f}*PTS,{V},tpad=stop_mode=clone:stop_duration=1,format=yuv420p', '-t', f'{end - cut:.3f}', '-an', '-c:v', 'libx264', '-crf', '19', f'{T}/b.mp4'])
open(f'{T}/l.txt', 'w').write(f"file '{T}/a.mp4'\nfile '{T}/b.mp4'\n")
run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', f'{T}/l.txt', '-c:v', 'libx264', '-crf', '19', '-r', '30', f'{T}/base.mp4'])
inp = ['-i', f'{T}/base.mp4']; fc = []; prev = '0:v'
for i, (k, t, a, b) in enumerate(caps):
    inp += ['-i', f'{T}/c{i}.png']; fc.append(f"[{prev}][{i+1}:v]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[o{i}]"); prev = f'o{i}'
n = len(caps)
inp += ['-loop', '1', '-i', f'{T}/karta.png']
fc.append(f"[{n+1}:v]format=rgba,fade=t=in:st={st[3]:.3f}:d=0.25:alpha=1[k]")
fc.append(f"[{prev}][k]overlay=0:0:enable='gte(t,{st[3]:.3f})'[ok]")
fc.append('[ok]format=yuv420p[v]')
run([FF, '-y'] + inp + ['-filter_complex', ';'.join(fc), '-map', '[v]', '-t', f'{end:.3f}', '-c:v', 'libx264', '-crf', '20', f'{T}/v.mp4'])
# dźwięk: lektor, ściszony kot, spokojna muzyka pod kartą z ceną
ai, af = [], []
for i, f in enumerate(L):
    ai += ['-i', f]; ms = int(st[i] * 1000); af.append(f'[{i+1}:a]adelay={ms}|{ms},volume=1.4[a{i}]')
subprocess.run(['python3', 'muzyka_spokojna.py', f'{end - st[3]:.2f}', f'{T}/m.wav'], check=True, stdout=subprocess.DEVNULL)
ai += ['-i', 'n1_skok.mp4', '-i', 'n1_walka.mp4', '-i', f'{T}/m.wav']
af.append(f'[5:a]atrim=0:2.6,asetpts=PTS-STARTPTS,atempo={1/KA:.4f},volume=0.2[x]')
af.append(f'[6:a]atempo={max(0.5, 1/KB):.4f},volume=0.2,adelay={int(cut*1000)}|{int(cut*1000)}[y]')
af.append(f'[7:a]volume=0.4,adelay={int(st[3]*1000)}|{int(st[3]*1000)}[m]')
af.append('[a0][a1][a2][a3][x][y][m]amix=inputs=7:duration=longest:normalize=0,alimiter=limit=0.95[a]')
run([FF, '-y', '-i', f'{T}/v.mp4'] + ai + ['-filter_complex', ';'.join(af), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{end:.3f}', '-movflags', '+faststart', 'c1_podrapane_rece.mp4'])
print(f'cięcie {cut:.2f} s, karta od {st[3]:.2f} s, razem {end:.2f} s')
