import sys
from PIL import Image, ImageDraw, ImageFont
# karta z ceną na przezroczystym tle: stara cena przekreślona, nowa duża, korzyści i adres
out = sys.argv[1]
DY = int(sys.argv[2]) if len(sys.argv) > 2 else 0   # przesunięcie karty w pionie
STARA = len(sys.argv) <= 3 or sys.argv[3] != 'bez_starej'   # 'bez_starej' = sama cena 139 zł, bez przekreślenia
W, H = 1080, 1920
im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
B = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
f_old, f_new, f_url = (ImageFont.truetype(B, s) for s in (86, 190, 84))
f_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 54)  # ma znak ✓
x0, y0, x1, y1 = 90, (700 if STARA else 800) + DY, 990, 1500 + DY
d.rounded_rectangle((x0, y0, x1, y1), radius=48, fill=(255, 255, 255, 238))
def center(t, f, y, fill):
    w = d.textlength(t, font=f); x = (W - w) / 2; d.text((x, y), t, font=f, fill=fill); return x, w
if STARA:
    x, w = center('169 zł', f_old, 740 + DY, (140, 128, 120, 255))
    d.line((x - 10, 740 + DY + 52, x + w + 10, 740 + DY + 40), fill=(220, 38, 38, 255), width=10)   # przekreślenie
center('139 zł', f_new, 840 + DY, (220, 38, 38, 255))
center('✓ darmowa dostawa', f_small, 1080 + DY, (31, 26, 23, 255))
center('✓ 14 dni na zwrot', f_small, 1160 + DY, (31, 26, 23, 255))
bx0, by0, bx1, by1 = 150, 1290 + DY, 930, 1440 + DY
d.rounded_rectangle((bx0, by0, bx1, by1), radius=30, fill=(232, 98, 44, 255))
tw = d.textlength('kocisparing.pl', font=f_url)
d.text(((W - tw) / 2, by0 + 28), 'kocisparing.pl', font=f_url, fill=(255, 255, 255, 255))
im.save(out)
