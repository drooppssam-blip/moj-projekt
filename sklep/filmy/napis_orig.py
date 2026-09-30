import sys
from PIL import Image, ImageDraw, ImageFont
text, out = sys.argv[1], sys.argv[2]
W,H=1080,1920
im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
f=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',72)
# zawijanie do szerokości 900 px
import re
text=re.sub(r'(?<!\S)(\w) ', lambda m: m.group(1)+'\u00a0', text)
words=text.split(' '); lines=[]; cur=''
for w in words:
    t=(cur+' '+w).strip()
    if d.textlength(t,font=f)<=900: cur=t
    else: lines.append(cur); cur=w
lines.append(cur)
y=250
for l in lines:
    tw=d.textlength(l,font=f); x=(W-tw)/2
    # białe tło pod tekstem jak w TikToku
    bb=d.textbbox((x,y),l,font=f)
    d.rounded_rectangle((bb[0]-22,bb[1]-14,bb[2]+22,bb[3]+14),radius=18,fill=(255,255,255,245))
    d.text((x,y),l,font=f,fill=(20,20,20,255))
    y+=f.size+34
im.save(out)
