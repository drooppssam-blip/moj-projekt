#!/usr/bin/env python3
"""Film N1 „Nigdy tego nie rób”: skok na gołą rękę, potem walka z karateką w salonie."""
import subprocess, tempfile, os, re
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
T = tempfile.mkdtemp()
def run(cmd): subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
def dur(f):
    o = subprocess.run([FF, '-i', f], stderr=subprocess.PIPE, text=True).stderr
    h, m, s = re.search(r'Duration: (\d+):(\d+):([\d.]+)', o).groups(); return int(h)*3600+int(m)*60+float(s)
# lektor (pauzy już skrócone w r1_l*_p.wav)
L = ['n1_l1_p.wav', 'n1_l2_p.wav', 'n1_l3_p.wav']
d = [dur(f) for f in L]
st = [0.1]; st.append(st[0] + d[0] + 0.12); st.append(st[1] + d[1] + 0.12)
end = st[2] + d[2] + 0.4
cut = st[1] - 0.06            # cięcie po całym pierwszym zdaniu lektora
# napisy: (tekst, od, do), granice fraz zmierzone w lektorze
caps = [("NIGDY TEGO|NIE RÓB", 0, st[0] + 1.93),
        ("Uczysz go, że ręka to zabawka.", st[0] + 1.93, st[1]),
        ("Ręka ma być ręką.", st[1], st[1] + 1.55),
        ("Do walki jest sparingpartner.", st[1] + 1.55, st[2]),
        ("Drugi sparingpartner −50 zł", st[2], st[2] + 1.86),
        ("kocisparing.pl", st[2] + 1.86, end + 1)]
for i, (t, a, b) in enumerate(caps):
    if i == 0: run(['python3', 'napis_duzy.py', t, f'{T}/c{i}.png'])
    else: subprocess.run(['python3', 'napis_tt.py', t, f'{T}/c{i}.png'], check=True, env={**os.environ, 'NAPIS_SIZE': '82'})
V = 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1'
# scena A: skok na rękę
KA = 1.6  # tylko czyste pierwsze 2,6 s sceny, zwolnione (dalej palce wyglądają na czerwone)
run([FF, '-y', '-i', 'n1_skok.mp4', '-vf', f'trim=0:{cut/KA:.3f},setpts={KA}*(PTS-STARTPTS),{V},fps=30,format=yuv420p', '-t', f'{cut:.3f}', '-an', '-c:v', 'libx264', '-crf', '19', f'{T}/a.mp4'])
# scena B: walka zwolniona x1.5, potem ostatnia klatka z lekkim najazdem
k = 1.3; wd = dur('n1_walka.mp4') * k; bd = end - cut
run([FF, '-y', '-i', 'n1_walka.mp4', '-vf', f'setpts={k}*PTS,{V},fps=30,format=yuv420p', '-an', '-c:v', 'libx264', '-crf', '19', f'{T}/b1.mp4'])
rest = max(0.0, bd - wd)
parts = [f'{T}/b1.mp4']
if rest > 0.05:
    run([FF, '-y', '-sseof', '-0.1', '-i', 'n1_walka.mp4', '-frames:v', '1', '-update', '1', f'{T}/last.png'])
    n = int(rest * 30) + 1
    run([FF, '-y', '-loop', '1', '-i', f'{T}/last.png', '-vf', f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,scale=2160:3840,zoompan=z='1+0.12*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1080x1920:fps=30,format=yuv420p", '-t', f'{rest:.3f}', '-c:v', 'libx264', '-crf', '19', f'{T}/b2.mp4'])
    parts.append(f'{T}/b2.mp4')
open(f'{T}/l.txt', 'w').write(''.join(f"file '{p}'\n" for p in [f'{T}/a.mp4'] + parts))
run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', f'{T}/l.txt', '-c:v', 'libx264', '-crf', '19', '-r', '30', f'{T}/base.mp4'])
# napisy
inp = ['-i', f'{T}/base.mp4']; fc = []; prev = '0:v'
for i, (t, a, b) in enumerate(caps):
    inp += ['-i', f'{T}/c{i}.png']; fc.append(f"[{prev}][{i+1}:v]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[o{i}]"); prev = f'o{i}'
fc.append(f'[{prev}]format=yuv420p[v]')
run([FF, '-y'] + inp + ['-filter_complex', ';'.join(fc), '-map', '[v]', '-t', f'{end:.3f}', '-c:v', 'libx264', '-crf', '20', f'{T}/v.mp4'])
# dźwięk: lektor + ściszone odgłosy z obu scen
ai = []; af = []
for i, f in enumerate(L):
    ai += ['-i', f]; ms = int(st[i] * 1000); af.append(f'[{i+1}:a]adelay={ms}|{ms},volume=1.4[a{i}]')
ai += ['-i', 'n1_skok.mp4', '-i', 'n1_walka.mp4']; ms = int(cut * 1000)
af.append(f'[4:a]atrim=0:{cut/KA:.3f},asetpts=PTS-STARTPTS,atempo={1/KA:.4f},volume=0.25[s]')
af.append(f'[5:a]atempo={1/k:.4f},volume=0.25,adelay={ms}|{ms}[w]')
af.append('[a0][a1][a2][s][w]amix=inputs=5:duration=longest:normalize=0,alimiter=limit=0.95[a]')
run([FF, '-y', '-i', f'{T}/v.mp4'] + ai + ['-filter_complex', ';'.join(af), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{end:.3f}', '-movflags', '+faststart', 'n1_nigdy_tego_nie_rob.mp4'])
print(f'cięcie {cut:.2f} s, walka {wd:.2f} s, najazd {rest:.2f} s, razem {end:.2f} s')
