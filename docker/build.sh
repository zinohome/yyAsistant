#!/bin/bash
IMGNAME=zinohome/yyassistant
IMGVERSION=v0.3.7.2
docker build --no-cache -t $IMGNAME:$IMGVERSION .