#!/usr/bin/env python3
"""Wersja „pacynka od 2. sekundy”: hook tylko na pierwsze zdanie, potem od razu scena z pacynką.
użycie: szybki2_p.py hook.png "tekst1" "tekst2" "tekst3" "tekst4" l1.mp3 l2.mp3 l3.mp3 l4.mp3 wyjscie.mp4 [zoom cx cy]
"""
import sys, subprocess, tempfile, os, re
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
D = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
hook, t1, t2, t3, t4, l1, l2, l3, l4, out = a[:10]
Z, CX, CY = (a[10:13] + ['1.18', '0.5', '0.5'][len(a[10:13]):]) if len(a) > 10 else ('1.18', '0.5', '0.5')
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
n1 = int(s1 * 30) + 1
run([FF, '-y', '-loop', '1', '-i', hook, '-i', f'{T}/t0.png', '-filter_complex', f"[0:v]{ZP},zoompan=z='1+({Z}-1)*on/{n1}':x='iw*{CX}-(iw/zoom/2)':y='ih*{CY}-(ih/zoom/2)':d={n1}:s=1080x1920:fps=30[b];[b][1:v]overlay=0:0,format=yuv420p[v]", '-map', '[v]', '-t', f'{s1:.3f}', '-c:v', 'libx264', '-crf', '20', '-r', '30', '-an', f'{T}/s1.mp4'])
# scena z pacynką pod zdaniami 2, 3 i 4; klip lekko zwolniony, żeby nie stał w miejscu
sp = s2 + s3 + s4
clip = dur(f'{D}/test01.mp4')
k = min(1.25, max(1.0, sp / clip))
b2, b3 = s2, s2 + s3
run([FF, '-y', '-i', f'{D}/test01.mp4', '-i', f'{T}/t1.png', '-i', f'{T}/t2.png', '-i', f'{T}/t3.png', '-filter_complex',
     f"[0:v]setpts={k:.4f}*PTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:2[bg];[0:v]setpts={k:.4f}*PTS,scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2:shortest=1,fps=30,tpad=stop_mode=clone:stop_duration=3[v0];"
     f"[v0][1:v]overlay=0:0:enable='lt(t,{b2:.3f})'[v1];[v1][2:v]overlay=0:0:enable='between(t,{b2:.3f},{b3:.3f})'[v2];[v2][3:v]overlay=0:0:enable='gte(t,{b3:.3f})',format=yuv420p[v]",
     '-map', '[v]', '-t', f'{sp:.3f}', '-c:v', 'libx264', '-crf', '20', '-r', '30', '-an', f'{T}/s2.mp4'])
open(f'{T}/l.txt', 'w').write(''.join(f"file '{T}/s{k}.mp4'\n" for k in (1, 2)))
run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', f'{T}/l.txt', '-c', 'copy', f'{T}/v.mp4'])
# 2. dźwięk: lektor + ściszony dźwięk kota od wejścia pacynki
starts = [0.15, s1, s1 + s2, s1 + s2 + s3]
inputs = []; filt = []
for i, (f, d) in enumerate(voc):
    inputs += ['-i', f]; ms = int(starts[i] * 1000); filt.append(f'[{i+1}:a]adelay={ms}|{ms},volume=1.4[a{i}]')
inputs += ['-i', f'{D}/test01.mp4']; ms = int(s1 * 1000)
filt.append(f'[5:a]atempo={1/k:.4f},volume=0.25,adelay={ms}|{ms}[cat]')
filt.append('[a0][a1][a2][a3][cat]amix=inputs=5:duration=longest:normalize=0,alimiter=limit=0.95[a]')
run([FF, '-y', '-i', f'{T}/v.mp4'] + inputs + ['-filter_complex', ';'.join(filt), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{s1+sp:.3f}', '-movflags', '+faststart', out])
print(f'{os.path.basename(out)}: hook {s1:.2f} s, pacynka od {s1:.2f} s, razem {s1+sp:.2f} s (klip x{k:.2f})')
