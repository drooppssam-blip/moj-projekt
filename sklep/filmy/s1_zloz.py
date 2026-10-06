#!/usr/bin/env python3
"""Film S1 „Bez zabawy / po zabawie”: kociak szaleje, walczy z karateką, potem śpi. Końcówka: 14 dni na zwrot i adres."""
import subprocess, tempfile, os, re
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
T = tempfile.mkdtemp()
def run(cmd): subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
def dur(f):
    o = subprocess.run([FF, '-i', f], stderr=subprocess.PIPE, text=True).stderr
    h, m, s = re.search(r'Duration: (\d+):(\d+):([\d.]+)', o).groups(); return int(h)*3600+int(m)*60+float(s)
L = ['s1_l1_p.wav', 's1_l2_p.wav', 's1_l3_p.wav', 's1_l4_p.wav']
d = [dur(f) for f in L]
st = [0.1]
st.append(st[0] + d[0] + 0.1)            # „A po dziesięciu minutach zabawy…” razem z cięciem na walkę
st.append(st[1] + d[1] + 0.6)            # chwila walki bez głosu, potem cięcie na śpiącego kota
st.append(st[2] + d[2] + 0.12)           # „Wpisz: kocisparing kropka pe el.”
end = st[3] + d[3] + 0.6
c1, c2 = st[1], st[2]                    # cięcia: szaleje → walczy → śpi
V = 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30'
# napisy: duże (czerwony pasek) i zwykłe (biały z obrysem)
caps = [('d', 'BEZ ZABAWY', 0, st[0] + 1.0),
        ('t', 'gryzie ręce i szaleje do nocy', st[0] + 1.0, c1),
        ('d', 'PO 10 MINUTACH|ZABAWY', c1, c2),
        ('t', '…śpi jak dziecko.', c2, st[2] + 1.3),
        ('d', '14 DNI|NA ZWROT', st[2] + 1.3, st[3]),
        ('d', 'KOCISPARING.PL', st[3], end + 1)]
for i, (k, t, a, b) in enumerate(caps):
    if k == 'd': subprocess.run(['python3', 'napis_duzy.py', t, f'{T}/c{i}.png'], check=True, env={**os.environ, 'NAPIS_SIZE': '100' if t == 'KOCISPARING.PL' else '120', 'NAPIS_Y': '1250'})
    else: subprocess.run(['python3', 'napis_tt.py', t, f'{T}/c{i}.png', '1200'], check=True, env={**os.environ, 'NAPIS_SIZE': '82'})
# sceny
run([FF, '-y', '-i', 'b1_ucieka.mp4', '-vf', f'{V},format=yuv420p', '-t', f'{c1:.3f}', '-an', '-c:v', 'libx264', '-crf', '19', f'{T}/a.mp4'])
run([FF, '-y', '-i', 'r1_walka.mp4', '-vf', f'{V},format=yuv420p', '-t', f'{c2 - c1:.3f}', '-an', '-c:v', 'libx264', '-crf', '19', f'{T}/b.mp4'])
SPI = dur('s1_spi.mp4')
k = max(1.0, (end - c2) / SPI)
run([FF, '-y', '-i', 's1_spi.mp4', '-vf', f'trim=0:{SPI},setpts={k:.4f}*(PTS-STARTPTS),{V},tpad=stop_mode=clone:stop_duration=2,format=yuv420p', '-t', f'{end - c2:.3f}', '-an', '-c:v', 'libx264', '-crf', '19', f'{T}/c.mp4'])
open(f'{T}/l.txt', 'w').write(''.join(f"file '{T}/{x}.mp4'\n" for x in 'abc'))
run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', f'{T}/l.txt', '-c:v', 'libx264', '-crf', '19', '-r', '30', f'{T}/base.mp4'])
inp = ['-i', f'{T}/base.mp4']; fc = []; prev = '0:v'
for i, (kk, t, a, b) in enumerate(caps):
    inp += ['-i', f'{T}/c{i}.png']; fc.append(f"[{prev}][{i+1}:v]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[o{i}]"); prev = f'o{i}'
fc.append(f'[{prev}]format=yuv420p[v]')
run([FF, '-y'] + inp + ['-filter_complex', ';'.join(fc), '-map', '[v]', '-t', f'{end:.3f}', '-c:v', 'libx264', '-crf', '20', f'{T}/v.mp4'])
# dźwięk: lektor, ściszone odgłosy kota w dwóch pierwszych scenach, spokojna muzyka przy śpiącym kocie
ai = []; af = []
for i, f in enumerate(L):
    ai += ['-i', f]; ms = int(st[i] * 1000); af.append(f'[{i+1}:a]adelay={ms}|{ms},volume=1.4[a{i}]')
subprocess.run(['python3', 'muzyka_spokojna.py', f'{end - c2:.2f}', f'{T}/m.wav'], check=True, stdout=subprocess.DEVNULL)
ai += ['-i', 'b1_ucieka.mp4', '-i', 'r1_walka.mp4', '-i', f'{T}/m.wav']
af.append(f'[5:a]atrim=0:{c1:.3f},volume=0.25[x]')
af.append(f'[6:a]atrim=0:{c2 - c1:.3f},asetpts=PTS-STARTPTS,volume=0.25,adelay={int(c1*1000)}|{int(c1*1000)}[y]')
af.append(f'[7:a]volume=0.45,adelay={int(c2*1000)}|{int(c2*1000)}[m]')
af.append('[a0][a1][a2][a3][x][y][m]amix=inputs=7:duration=longest:normalize=0,alimiter=limit=0.95[a]')
run([FF, '-y', '-i', f'{T}/v.mp4'] + ai + ['-filter_complex', ';'.join(af), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{end:.3f}', '-movflags', '+faststart', 's1_bez_zabawy.mp4'])
print(f'cięcia {c1:.2f} i {c2:.2f} s, razem {end:.2f} s, sen zwolniony x{k:.2f}')
