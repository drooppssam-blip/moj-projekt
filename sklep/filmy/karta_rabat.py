import sys
from PIL import Image, ImageDraw, ImageFont
# karta bez ceny: tylko obniżka, korzyści i zaproszenie do sprawdzenia ceny na stronie
out = sys.argv[1]
DY = int(sys.argv[2]) if len(sys.argv) > 2 else 0
W, H = 1080, 1920
im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
B = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
f_big, f_url, f_hint = (ImageFont.truetype(B, s) for s in (150, 84, 52))
f_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 54)  # ma znak ✓
d.rounded_rectangle((90, 700 + DY, 990, 1500 + DY), radius=48, fill=(255, 255, 255, 238))
def center(t, f, y, fill):
    w = d.textlength(t, font=f); d.text(((W - w) / 2, y), t, font=f, fill=fill)
center('30 ZŁ', f_big, 735 + DY, (220, 38, 38, 255))
center('TANIEJ', f_big, 885 + DY, (220, 38, 38, 255))
center('✓ darmowa dostawa', f_small, 1070 + DY, (31, 26, 23, 255))
center('✓ 14 dni na zwrot', f_small, 1145 + DY, (31, 26, 23, 255))
center('sprawdź cenę:', f_hint, 1225 + DY, (90, 80, 72, 255))
d.rounded_rectangle((150, 1300 + DY, 930, 1450 + DY), radius=30, fill=(232, 98, 44, 255))
tw = d.textlength('kocisparing.pl', font=f_url)
d.text(((W - tw) / 2, 1328 + DY), 'kocisparing.pl', font=f_url, fill=(255, 255, 255, 255))
im.save(out)
