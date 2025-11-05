#!/bin/bash
IMGNAME=zinohome/yyassistant
IMGVERSION=v0.4.6.2
docker build --no-cache -t $IMGNAME:$IMGVERSION .