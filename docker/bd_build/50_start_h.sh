#!/bin/bash
cd /opt/yyAsistant && \
source .venv/bin/activate
nohup python app.py >> /tmp/yyAsistant.log 2>&1 &
