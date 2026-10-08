import sys
from PIL import Image, ImageDraw
# zielone kółko z białym ptaszkiem („TAK” w teście), na przezroczystym tle 1080x1920
out = sys.argv[1]; cy = int(sys.argv[2]) if len(sys.argv) > 2 else 950
im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
r = 95; cx = int(sys.argv[3]) if len(sys.argv) > 3 else 540
d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(34, 160, 70, 250), outline=(255, 255, 255, 255), width=8)
d.line([(cx - 48, cy + 2), (cx - 12, cy + 40), (cx + 52, cy - 38)], fill=(255, 255, 255, 255), width=24, joint='curve')
im.save(out)
