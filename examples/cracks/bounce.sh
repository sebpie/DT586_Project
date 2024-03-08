#!/bin/bash

#ffmpeg -loop 1 -i testcard.png  -vf "crop=500:ih:'min((iw/10)*t,9*iw/10)':0" -t 5 -f matroska - | ffplay -

echo "input file: ${1}"

FILE=$1
[ -z "${FILE}"] && FILE="testcard.png"

echo "ffmpeg to use ${FILE}"

ffmpeg -loop 1 -i $FILE  -vf "crop=\
	640:480\
	:'if(eq(mod(floor(st(8,t*100)/(iw - out_w)),2),0), \
		mod(ld(8),iw - out_w), \
		iw - out_w-mod(ld(8), iw - out_w))'\
	:'\
	if(eq(mod(floor(st(9,t*100)/(ih - out_h)),2),0), \
		mod(ld(9),ih - out_h), \
		ih-h-mod(ld(9), ih - out_h))
	'"  -f matroska - | ffplay -
