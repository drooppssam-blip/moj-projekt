#!/usr/bin/env python3
"""Film T1 „Test: czy Twój kot tego potrzebuje?”: 3 pytania z ptaszkami, na końcu karta z ceną 139 zł."""
import subprocess, tempfile, os, re
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
T = tempfile.mkdtemp()
def run(cmd): subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
def dur(f):
    o = subprocess.run([FF, '-i', f], stderr=subprocess.PIPE, text=True).stderr
    h, m, s = re.search(r'Duration: (\d+):(\d+):([\d.]+)', o).groups(); return int(h)*3600+int(m)*60+float(s)
# kwestia 1 i 5 dodatkowo przyspieszone, żeby film zmieścił się w ~13 s
for i in (1, 5): run([FF, '-y', '-i', f't1_l{i}_p.wav', '-af', 'atempo=1.08', f'{T}/l{i}.wav'])
L = [f'{T}/l1.wav', 't1_l2_p.wav', 't1_l3_p.wav', 't1_l4_p.wav', f'{T}/l5.wav']
d = [dur(f) for f in L]
st = [0.1, d[0] + 0.25]                      # po haczyku od razu pytanie 1
for i in (1, 2, 3): st.append(st[i] + d[i] + 0.55)   # 0,55 s na ptaszek po każdym pytaniu
end = st[4] + d[4] + 0.5
tick = [st[i] + d[i] for i in (1, 2, 3)]     # ptaszek pojawia się po wypowiedzeniu pytania
karta = st[4] + 0.85                          # po „Dwa razy tak?”
V = 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30'
def big(t, out, size, y): subprocess.run(['python3', 'napis_duzy.py', t, out], check=True, env={**os.environ, 'NAPIS_SIZE': str(size), 'NAPIS_Y': str(y)})
caps = [('TEST: CZY TWÓJ KOT|TEGO POTRZEBUJE?', 0, st[1], 86),
        ('1. GRYZIE CIĘ|PO RĘKACH?', st[1], st[2], 100),
        ('2. POLUJE NA RĘCE|POD KOCEM?', st[2], st[3], 92),
        ('3. DRAPIE KANAPĘ?', st[3], st[4], 100),
        ('DWA RAZY TAK?', st[4], end, 110)]
for i, (t, a, b, s) in enumerate(caps): big(t, f'{T}/c{i}.png', s, 1300)
subprocess.run(['python3', 'ptaszek.py', f'{T}/tick.png', '1580', '880'], check=True)
subprocess.run(['python3', 'karta_ceny.py', f'{T}/karta.png', '-460', 'bez_starej'], check=True)
# ujęcia: (plik, początek w źródle, długość w filmie)
segs = [('n1_walka.mp4', 0.0, st[1]),
        ('n1_skok.mp4', 0.5, st[2] - st[1]),
        ('r1_skok.mp4', 1.6, st[3] - st[2]),
        ('d1_kanapa.mp4', 0.0, st[4] - st[3])]
for j, (f, a, n) in enumerate(segs):
    run([FF, '-y', '-i', f, '-vf', f'trim={a}:{a + n:.3f},setpts=PTS-STARTPTS,{V},format=yuv420p', '-an', '-c:v', 'libx264', '-crf', '19', f'{T}/s{j}.mp4'])
rest = end - st[4]; src = dur('n1_walka.mp4') - st[1]
KE = max(1.0, rest / src)
run([FF, '-y', '-i', 'n1_walka.mp4', '-vf', f'trim={st[1]:.3f},setpts={KE:.4f}*(PTS-STARTPTS),{V},tpad=stop_mode=clone:stop_duration=1,format=yuv420p', '-t', f'{rest:.3f}', '-an', '-c:v', 'libx264', '-crf', '19', f'{T}/s4.mp4'])
open(f'{T}/l.txt', 'w').write(''.join(f"file '{T}/s{j}.mp4'\n" for j in range(5)))
run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', f'{T}/l.txt', '-c:v', 'libx264', '-crf', '19', '-r', '30', f'{T}/base.mp4'])
inp = ['-i', f'{T}/base.mp4']; fc = []; prev = '0:v'; k = 1
for i, (t, a, b, s) in enumerate(caps):
    inp += ['-i', f'{T}/c{i}.png']; fc.append(f"[{prev}][{k}:v]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[o{k}]"); prev = f'o{k}'; k += 1
for i, a in enumerate(tick):
    inp += ['-i', f'{T}/tick.png']; fc.append(f"[{prev}][{k}:v]overlay=0:0:enable='between(t,{a:.3f},{st[i+2]:.3f})'[o{k}]"); prev = f'o{k}'; k += 1
inp += ['-loop', '1', '-i', f'{T}/karta.png']
fc.append(f"[{k}:v]format=rgba,fade=t=in:st={karta:.3f}:d=0.25:alpha=1[kk]")
fc.append(f"[{prev}][kk]overlay=0:0:enable='gte(t,{karta:.3f})'[ok]")
fc.append('[ok]format=yuv420p[v]')
run([FF, '-y'] + inp + ['-filter_complex', ';'.join(fc), '-map', '[v]', '-t', f'{end:.3f}', '-c:v', 'libx264', '-crf', '20', f'{T}/v.mp4'])
# dźwięk: lektor, ściszone odgłosy z ujęć, spokojna muzyka pod kartą
ai, af = [], []
for i, f in enumerate(L):
    ai += ['-i', f]; ms = int(st[i] * 1000); af.append(f'[{i+1}:a]adelay={ms}|{ms},volume=1.4[a{i}]')
n = len(L) + 1
pos = [0.0, st[1], st[2], st[3]]
for j, (f, a, ln) in enumerate(segs):
    ai += ['-i', f]; ms = int(pos[j] * 1000)
    af.append(f'[{n+j}:a]atrim={a}:{a + ln:.3f},asetpts=PTS-STARTPTS,volume=0.2,adelay={ms}|{ms}[x{j}]')
subprocess.run(['python3', 'muzyka_spokojna.py', f'{end - st[4]:.2f}', f'{T}/m.wav'], check=True, stdout=subprocess.DEVNULL)
ai += ['-i', f'{T}/m.wav']; ms = int(st[4] * 1000)
af.append(f'[{n+4}:a]volume=0.4,adelay={ms}|{ms}[m]')
af.append(''.join(f'[a{i}]' for i in range(5)) + ''.join(f'[x{j}]' for j in range(4)) + '[m]amix=inputs=10:duration=longest:normalize=0,alimiter=limit=0.95[a]')
run([FF, '-y', '-i', f'{T}/v.mp4'] + ai + ['-filter_complex', ';'.join(af), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{end:.3f}', '-movflags', '+faststart', 't1_test.mp4'])
print('pytania od', [round(x, 2) for x in st], 'ptaszki', [round(x, 2) for x in tick], f'karta {karta:.2f}, razem {end:.2f} s')
