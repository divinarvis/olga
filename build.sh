#!/bin/bash
apt-get update -y
apt-get install -y ffmpeg curl
curl -fsSL https://deno.land/install.sh | sh
export DENO_INSTALL="/opt/render/.deno"
export PATH="$DENO_INSTALL/bin:$PATH"
pip install -U yt-dlp
pip install -r requirements.txt
mkdir -p downloads