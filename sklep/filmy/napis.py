import sys, os
if os.environ.get('BEZ_TEKSTU'):
    from PIL import Image
    Image.new('RGBA',(1080,1920),(0,0,0,0)).save(sys.argv[2]); sys.exit(0)
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'napis_orig.py')).read())
