#!/usr/bin/env python3
"""Film D1 „Ile kosztuje znudzony kot?”: kociak drapie kanapę, gryzie dłoń, potem walczy z karateką, na końcu karta z ceną 139 zł."""
import subprocess, tempfile, os, re
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
T = tempfile.mkdtemp()
def run(cmd): subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
def dur(f):
    o = subprocess.run([FF, '-i', f], stderr=subprocess.PIPE, text=True).stderr
    h, m, s = re.search(r'Duration: (\d+):(\d+):([\d.]+)', o).groups(); return int(h)*3600+int(m)*60+float(s)
# z kwestii 2 wycinam „Zasłony.” (1,25 do 2,30 s), żeby produkt pojawił się szybciej
run([FF, '-y', '-i', 'd1_l2_p.wav', '-filter_complex', '[0:a]atrim=0:1.25,asetpts=PTS-STARTPTS[a];[0:a]atrim=2.30,asetpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=0:a=1[o]', '-map', '[o]', f'{T}/l2.wav'])
L = ['d1_l1_p.wav', f'{T}/l2.wav', 'd1_l3_p.wav', 'd1_l4_p.wav']
d = [dur(f) for f in L]
st = [0.1]
for i in range(3): st.append(st[i] + d[i] + 0.1)
end = st[3] + d[3] + 0.5
reka = st[1] + 1.25                          # „Twoje ręce” → ujęcie z gryzieniem dłoni
cut = st[2]                                  # walka z karateką od „Jego energia…”
V = 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30'
subprocess.run(['python3', 'karta_ceny.py', f'{T}/karta.png', '-460', 'bez_starej'], check=True)
caps = [('d', 'ILE KOSZTUJE|ZNUDZONY KOT?', 0, st[1]),
        ('t', 'Podrapana kanapa. Twoje ręce.', st[1], cut),
        ('d', 'ENERGIA MUSI|GDZIEŚ PÓJŚĆ', cut, st[3])]
for i, (k, t, a, b) in enumerate(caps):
    if k == 'd': subprocess.run(['python3', 'napis_duzy.py', t, f'{T}/c{i}.png'], check=True, env={**os.environ, 'NAPIS_SIZE': '100', 'NAPIS_Y': '1250'})
    else: subprocess.run(['python3', 'napis_tt.py', t, f'{T}/c{i}.png', '1250'], check=True, env={**os.environ, 'NAPIS_SIZE': '78'})
run([FF, '-y', '-i', 'd1_kanapa.mp4', '-vf', f'trim=0:{reka:.3f},setpts=PTS-STARTPTS,{V},format=yuv420p', '-an', '-c:v', 'libx264', '-crf', '19', f'{T}/a.mp4'])
run([FF, '-y', '-i', 'n1_skok.mp4', '-vf', f'trim=0.6:{0.6 + cut - reka:.3f},setpts=PTS-STARTPTS,{V},format=yuv420p', '-an', '-c:v', 'libx264', '-crf', '19', f'{T}/b.mp4'])
KC = max(1.0, (end - cut) / dur('n1_walka.mp4'))
run([FF, '-y', '-i', 'n1_walka.mp4', '-vf', f'setpts={KC:.4f}*PTS,{V},tpad=stop_mode=clone:stop_duration=1,format=yuv420p', '-t', f'{end - cut:.3f}', '-an', '-c:v', 'libx264', '-crf', '19', f'{T}/c.mp4'])
open(f'{T}/l.txt', 'w').write(f"file '{T}/a.mp4'\nfile '{T}/b.mp4'\nfile '{T}/c.mp4'\n")
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
# dźwięk: lektor, ściszone odgłosy z ujęć, spokojna muzyka pod kartą z ceną
ai, af = [], []
for i, f in enumerate(L):
    ai += ['-i', f]; ms = int(st[i] * 1000); af.append(f'[{i+1}:a]adelay={ms}|{ms},volume=1.4[a{i}]')
subprocess.run(['python3', 'muzyka_spokojna.py', f'{end - st[3]:.2f}', f'{T}/m.wav'], check=True, stdout=subprocess.DEVNULL)
ai += ['-i', 'd1_kanapa.mp4', '-i', 'n1_skok.mp4', '-i', 'n1_walka.mp4', '-i', f'{T}/m.wav']
r, c = int(reka * 1000), int(cut * 1000)
af.append(f'[5:a]atrim=0:{reka:.3f},asetpts=PTS-STARTPTS,volume=0.2[x]')
af.append(f'[6:a]atrim=0.6:{0.6 + cut - reka:.3f},asetpts=PTS-STARTPTS,volume=0.2,adelay={r}|{r}[y]')
af.append(f'[7:a]atempo={max(0.5, 1/KC):.4f},volume=0.2,adelay={c}|{c}[z]')
af.append(f'[8:a]volume=0.4,adelay={int(st[3]*1000)}|{int(st[3]*1000)}[m]')
af.append('[a0][a1][a2][a3][x][y][z][m]amix=inputs=8:duration=longest:normalize=0,alimiter=limit=0.95[a]')
run([FF, '-y', '-i', f'{T}/v.mp4'] + ai + ['-filter_complex', ';'.join(af), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{end:.3f}', '-movflags', '+faststart', 'd1_znudzony_kot.mp4'])
print(f'ręce od {reka:.2f} s, produkt od {cut:.2f} s, karta od {st[3]:.2f} s, razem {end:.2f} s')
