#!/bin/bash
IMGNAME=zinohome/yyAssistant
IMGVERSION=v0.3.8
docker build --no-cache -t $IMGNAME:$IMGVERSION .