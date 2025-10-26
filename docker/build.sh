#!/bin/bash
IMGNAME=zinohome/yyassistant
IMGVERSION=v0.3.7.3
docker build --no-cache -t $IMGNAME:$IMGVERSION .