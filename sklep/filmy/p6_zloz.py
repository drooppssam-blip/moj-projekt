#!/usr/bin/env python3
"""Film P6 „POV: kupiłeś prezent dla kociarza”: bez lektora i bez reklamy, napisy POV, wesoła własna muzyka,
dyskretny znak kocisparing.pl w rogu. Z nowej sceny tylko czyste 0 do 4,8 s (potem AI otwiera karatece buzię)."""
import subprocess, tempfile, os
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
FF = imageio_ffmpeg.get_ffmpeg_exe()
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
T = tempfile.mkdtemp()
def run(cmd): subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
V = 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30'
X = 0.4
segs = [('p6_prezent.mp4', 0.3, 4.8, 1.0), ('n1_walka.mp4', 0.0, 4.4, 1.0), ('s1_spi.mp4', 0.3, 4.6, 1.0)]
lens = []
for j, (f, a, b, k) in enumerate(segs):
    run([FF, '-y', '-i', f, '-vf', f'trim={a}:{b},setpts={k}*(PTS-STARTPTS),{V},format=yuv420p', '-an', '-c:v', 'libx264', '-crf', '19', f'{T}/s{j}.mp4'])
    lens.append((b - a) * k)
o1 = lens[0] - X; o2 = o1 + lens[1] - X; end = o2 + lens[2]
caps = [('POV: kupiłeś prezent|dla kociarza 🎁', 0, 2.6), ('Kot: najlepszy dzień w życiu', 2.6, o2 + X / 2), ('Ty: od dziś ulubiony gość|w tym domu', o2 + X / 2, end)]
# napisy POV: biały tekst z czarnym obrysem, emoji osobną czcionką
TXT = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
def napis(t, out, y=300, size=68):
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(TXT, size); t = t.replace(' 🎁', '')
    lines = [l.strip() for l in t.split('|')]   # | wymusza nową linię
    for i, l in enumerate(lines):
        x = (1080 - d.textlength(l, font=f)) / 2
        d.text((x, y + i * int(size * 1.2)), l, font=f, fill='white', stroke_width=6, stroke_fill='black')
    im.save(out)
for i, (t, a, b) in enumerate(caps): napis(t, f'{T}/c{i}.png')
wm = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); dw = ImageDraw.Draw(wm)
dw.text((40, 1850), 'kocisparing.pl', font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 34), fill=(255, 255, 255, 150), stroke_width=2, stroke_fill=(0, 0, 0, 90))
wm.save(f'{T}/wm.png')
inp = ['-i', f'{T}/s0.mp4', '-i', f'{T}/s1.mp4', '-i', f'{T}/s2.mp4']
fc = [f'[0:v][1:v]xfade=transition=fade:duration={X}:offset={o1:.3f}[v01]', f'[v01][2:v]xfade=transition=fade:duration={X}:offset={o2:.3f}[b]']
prev = 'b'
for i, (t, a, b) in enumerate(caps):
    inp += ['-i', f'{T}/c{i}.png']; fc.append(f"[{prev}][{3+i}:v]overlay=0:0:enable='gte(t,{a:.3f})*lt(t,{b:.3f})'[o{i}]"); prev = f'o{i}'
inp += ['-i', f'{T}/wm.png']; fc.append(f'[{prev}][6:v]overlay=0:0,format=yuv420p[v]')
run([FF, '-y'] + inp + ['-filter_complex', ';'.join(fc), '-map', '[v]', '-t', f'{end:.3f}', '-c:v', 'libx264', '-crf', '21', f'{T}/v.mp4'])
subprocess.run(['python3', 'muzyka_wesola.py', f'{end:.2f}', f'{T}/m.wav'], check=True, stdout=subprocess.DEVNULL)
run([FF, '-y', '-i', f'{T}/v.mp4', '-i', f'{T}/m.wav', '-i', 'n1_walka.mp4', '-filter_complex',
     f'[1:a]volume=0.75[m];[2:a]atrim=0:{lens[1]:.3f},asetpts=PTS-STARTPTS,volume=0.25,adelay={int(o1*1000)}|{int(o1*1000)}[w];[m][w]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]',
     '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-t', f'{end:.3f}', '-movflags', '+faststart', 'p6_prezent_pov.mp4'])
print(f'walka od {o1:.2f} s, sen od {o2:.2f} s, razem {end:.2f} s')
