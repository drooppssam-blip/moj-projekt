#!/bin/bash
# użycie: ./zloz_p.sh hook.png "tekst hook" emocja.png "tekst emocja" "tekst produkt" wyjscie.mp4 [zoom_hook] [cx] [cy]
set -e
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
D=$(dirname "$0"); S=$(mktemp -d)
Z=${7:-1.18}; CX=${8:-0.5}; CY=${9:-0.5}
python3 $D/napis.py "$2" $S/t1.png; python3 $D/napis.py "$4" $S/t2.png
python3 $D/napis.py "$5" $S/t3.png; python3 $D/napis.py "KociSparing · link w bio" $S/t4.png
ZP="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,scale=2160:3840"
$FF -loglevel error -y -loop 1 -i "$1" -i $S/t1.png -f lavfi -i anullsrc=r=48000:cl=stereo -filter_complex "[0:v]$ZP,zoompan=z='1+($Z-1)*on/75':x='iw*$CX-(iw/zoom/2)':y='ih*$CY-(ih/zoom/2)':d=75:s=1080x1920:fps=30[b];[b][1:v]overlay=0:0,format=yuv420p[v]" -map "[v]" -map 2:a -t 2.5 -c:v libx264 -crf 20 -r 30 -c:a aac $S/s1.mp4
$FF -loglevel error -y -loop 1 -i "$3" -i $S/t2.png -f lavfi -i anullsrc=r=48000:cl=stereo -filter_complex "[0:v]$ZP,zoompan=z='min(zoom+0.0012,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=150:s=1080x1920:fps=30[b];[b][1:v]overlay=0:0,format=yuv420p[v]" -map "[v]" -map 2:a -t 5 -c:v libx264 -crf 20 -r 30 -c:a aac $S/s2.mp4
$FF -loglevel error -y -i $D/test01.mp4 -i $S/t3.png -i $S/t4.png -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:2[bg];[0:v]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,fps=30[v0];[v0][1:v]overlay=0:0:enable='lt(t,4.2)'[v1];[v1][2:v]overlay=0:0:enable='gte(t,4.2)',format=yuv420p[v]" -map "[v]" -map 0:a -c:v libx264 -crf 20 -r 30 -c:a aac -ar 48000 -ac 2 $S/s3.mp4
printf "file '$S/s1.mp4'\nfile '$S/s2.mp4'\nfile '$S/s3.mp4'\n" > $S/list.txt
$FF -loglevel error -y -f concat -safe 0 -i $S/list.txt -c:v libx264 -crf 20 -c:a aac -movflags +faststart "$6"
rm -rf $S
