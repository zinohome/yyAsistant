#!/bin/bash
IMGNAME=zinohome/yyassistant
IMGVERSION=v0.4.6
docker build --no-cache -t $IMGNAME:$IMGVERSION .