#!/usr/bin/env python3
"""Szybka wersja filmu P: tempo dyktuje lektor, bez przerw.
użycie: szybki_p.py hook.png emocja.png "tekst1" "tekst2" "tekst3" "tekst4" l1.mp3 l2.mp3 l3.mp3 l4.mp3 wyjscie.mp4 [zoom cx cy]
"""
import sys, subprocess, tempfile, os, re
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
D = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
hook, emo, t1, t2, t3, t4, l1, l2, l3, l4, out = a[:11]
Z, CX, CY = (a[11:14] + ['1.18', '0.5', '0.5'][len(a[11:14]):]) if len(a) > 11 else ('1.18', '0.5', '0.5')
T = tempfile.mkdtemp()
TEMPO = '1.08'
def run(cmd): subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
def dur(f):
    o = subprocess.run([FF, '-i', f], stderr=subprocess.PIPE, text=True).stderr
    h, m, s = re.search(r'Duration: (\d+):(\d+):([\d.]+)', o).groups(); return int(h)*3600+int(m)*60+float(s)
# 1. lektor: obcięcie ciszy i lekkie przyspieszenie
voc = []
for i, f in enumerate([l1, l2, l3, l4]):
    o = f'{T}/v{i}.wav'
    run([FF, '-y', '-i', f, '-af', f'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo={TEMPO}', '-ar', '48000', '-ac', '2', o])
    voc.append((o, dur(o)))
gap = 0.12
s1 = voc[0][1] + gap + 0.15; s2 = voc[1][1] + gap; s3 = voc[2][1] + gap; s4 = voc[3][1] + 0.45
for i, t in enumerate([t1, t2, t3, t4]):
    run(['python3', f'{D}/napis.py', t, f'{T}/t{i}.png'])
ZP = 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,scale=2160:3840'
n1 = int(s1 * 30) + 1; n2 = int(s2 * 30) + 1
run([FF, '-y', '-loop', '1', '-i', hook, '-i', f'{T}/t0.png', '-filter_complex', f"[0:v]{ZP},zoompan=z='1+({Z}-1)*on/{n1}':x='iw*{CX}-(iw/zoom/2)':y='ih*{CY}-(ih/zoom/2)':d={n1}:s=1080x1920:fps=30[b];[b][1:v]overlay=0:0,format=yuv420p[v]", '-map', '[v]', '-t', f'{s1:.3f}', '-c:v', 'libx264', '-crf', '20', '-r', '30', '-an', f'{T}/s1.mp4'])
run([FF, '-y', '-loop', '1', '-i', emo, '-i', f'{T}/t1.png', '-filter_complex', f"[0:v]{ZP},zoompan=z='1+0.12*on/{n2}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n2}:s=1080x1920:fps=30[b];[b][1:v]overlay=0:0,format=yuv420p[v]", '-map', '[v]', '-t', f'{s2:.3f}', '-c:v', 'libx264', '-crf', '20', '-r', '30', '-an', f'{T}/s2.mp4'])
s34 = s3 + s4
run([FF, '-y', '-i', f'{D}/test01.mp4', '-i', f'{T}/t2.png', '-i', f'{T}/t3.png', '-filter_complex', f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:2[bg];[0:v]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,fps=30[v0];[v0][1:v]overlay=0:0:enable='lt(t,{s3:.3f})'[v1];[v1][2:v]overlay=0:0:enable='gte(t,{s3:.3f})',tpad=stop_mode=clone:stop_duration=3,format=yuv420p[v]", '-map', '[v]', '-t', f'{s34:.3f}', '-c:v', 'libx264', '-crf', '20', '-r', '30', '-an', f'{T}/s3.mp4'])
open(f'{T}/l.txt', 'w').write(''.join(f"file '{T}/s{k}.mp4'\n" for k in (1, 2, 3)))
run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', f'{T}/l.txt', '-c', 'copy', f'{T}/v.mp4'])
# 2. ścieżka dźwiękowa: lektor + ściszony dźwięk kota w scenie z produktem
starts = [0.15, s1, s1 + s2, s1 + s2 + s3]
inputs = []; filt = []
for i, (f, d) in enumerate(voc):
    inputs += ['-i', f]; ms = int(starts[i] * 1000); filt.append(f'[{i+1}:a]adelay={ms}|{ms},volume=1.4[a{i}]')
inputs += ['-i', f'{D}/test01.mp4']; ms = int((s1 + s2) * 1000)
filt.append(f'[5:a]volume=0.25,adelay={ms}|{ms}[cat]')
filt.append('[a0][a1][a2][a3][cat]amix=inputs=5:duration=longest:normalize=0,alimiter=limit=0.95[a]')
run([FF, '-y', '-i', f'{T}/v.mp4'] + inputs + ['-filter_complex', ';'.join(filt), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', out])
print(f'sceny: {s1:.2f} + {s2:.2f} + {s3:.2f} + {s4:.2f} = {s1+s2+s34:.2f} s')
