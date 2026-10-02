import sys, re
from PIL import Image, ImageDraw, ImageFont
# napis w stylu TikToka: biały tekst z czarnym obrysem, w dolnej części kadru
text, out = sys.argv[1], sys.argv[2]
y = int(sys.argv[3]) if len(sys.argv) > 3 else 1180
W, H = 1080, 1920
im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
f = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', 66)
text = re.sub(r'(?<!\S)(\w) ', lambda m: m.group(1) + ' ', text)
words = text.split(' '); lines = []; cur = ''
for w in words:
    t = (cur + ' ' + w).strip()
    if d.textlength(t, font=f) <= 860: cur = t
    else: lines.append(cur); cur = w
lines.append(cur)
for l in lines:
    x = (W - d.textlength(l, font=f)) / 2
    d.text((x, y), l, font=f, fill=(255, 255, 255, 255), stroke_width=5, stroke_fill=(0, 0, 0, 255))
    y += f.size + 14
im.save(out)
