#!/bin/bash
IMGNAME=zinohome/yyassistant
IMGVERSION=v0.4.6.1
docker build --no-cache -t $IMGNAME:$IMGVERSION .