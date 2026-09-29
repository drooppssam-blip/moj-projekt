#!/bin/bash
# użycie: ./zrob.sh wejscie.mp4 "Tekst na ekranie" wyjscie.mp4
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
python3 "$(dirname "$0")/napis.py" "$2" /tmp/napis.png
$FF -loglevel error -y -i "$1" -i /tmp/napis.png -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:2[bg];[0:v]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2[v];[v][1:v]overlay=0:0,format=yuv420p[out]" -map "[out]" -map 0:a? -c:v libx264 -crf 20 -preset medium -c:a aac -movflags +faststart "$3"
