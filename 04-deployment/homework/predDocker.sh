#!/bin/bash
year=$1
month=$2

docker build -t homework-week4:latest .

docker run -it --rm homework-week4:latest  -y $year -m $month