#!/usr/bin/env python3
"""Format W z lektorem: kot pyta (hook), odsłona pacynki, końcówka kocisparing.pl.
użycie: w_lektor.py kot.mp4 "pytanie" "odpowiedź" l1.mp3 l2.mp3 l3.mp3 wyjscie.mp4
"""
import sys, subprocess, tempfile, os, re
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
D = os.path.dirname(os.path.abspath(__file__))
kot, t1, t2, l1, l2, l3, out = sys.argv[1:8]
T = tempfile.mkdtemp()
def run(cmd): subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
def dur(f):
    o = subprocess.run([FF, '-i', f], stderr=subprocess.PIPE, text=True).stderr
    h, m, s = re.search(r'Duration: (\d+):(\d+):([\d.]+)', o).groups(); return int(h)*3600+int(m)*60+float(s)
voc = []
for i, f in enumerate([l1, l2, l3]):
    o = f'{T}/v{i}.wav'
    run([FF, '-y', '-i', f, '-af', 'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo=1.08', '-ar', '48000', '-ac', '2', o])
    voc.append((o, dur(o)))
s1 = voc[0][1] + 0.15 + 0.25
b3 = voc[1][1] + 0.12
s2 = b3 + voc[2][1] + 0.45
run(['python3', f'{D}/napis_tt.py', t1, f'{T}/t1.png']); run(['python3', f'{D}/napis_tt.py', t2, f'{T}/t2.png'])
run(['python3', f'{D}/napis_tt.py', 'kocisparing.pl', f'{T}/t3.png', '1290'])
run([FF, '-y', '-i', kot, '-i', f'{T}/t1.png', '-filter_complex', "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1[b];[b][1:v]overlay=0:0,format=yuv420p[v]", '-map', '[v]', '-t', f'{s1:.3f}', '-c:v', 'libx264', '-crf', '19', '-r', '30', '-an', f'{T}/s1.mp4'])
run([FF, '-y', '-i', f'{D}/test01.mp4', '-i', f'{T}/t2.png', '-i', f'{T}/t3.png', '-filter_complex', f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:2[bg];[0:v]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,fps=30,setsar=1,tpad=stop_mode=clone:stop_duration=3[v0];[v0][1:v]overlay=0:0[v1];[v1][2:v]overlay=0:0:enable='gte(t,{b3:.3f})',format=yuv420p[v]", '-map', '[v]', '-t', f'{s2:.3f}', '-c:v', 'libx264', '-crf', '19', '-r', '30', '-an', f'{T}/s2.mp4'])
open(f'{T}/l.txt', 'w').write(f"file '{T}/s1.mp4'\nfile '{T}/s2.mp4'\n")
run([FF, '-y', '-f', 'concat', '-safe', '0', '-i', f'{T}/l.txt', '-c', 'copy', f'{T}/v.mp4'])
starts = [0.15, s1, s1 + b3]
inputs, filt = [], []
for i, (f, d) in enumerate(voc):
    inputs += ['-i', f]; ms = int(starts[i] * 1000); filt.append(f'[{i+1}:a]adelay={ms}|{ms},volume=1.4[a{i}]')
inputs += ['-i', kot, '-i', f'{D}/test01.mp4']; ms = int(s1 * 1000)
filt.append(f'[4:a]atrim=0:{s1:.3f},volume=0.25[k]')
filt.append(f'[5:a]volume=0.25,adelay={ms}|{ms}[cat]')
filt.append('[a0][a1][a2][k][cat]amix=inputs=5:duration=longest:normalize=0,alimiter=limit=0.95[a]')
run([FF, '-y', '-i', f'{T}/v.mp4'] + inputs + ['-filter_complex', ';'.join(filt), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{s1+s2:.3f}', '-movflags', '+faststart', out])
print(f'kot {s1:.2f} s, odsłona {s2:.2f} s, razem {s1+s2:.2f} s')
