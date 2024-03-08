#!/bin/bash

#ffmpeg -loop 1 -i testcard.png  -vf "crop=500:ih:'min((iw/10)*t,9*iw/10)':0" -t 5 -f matroska - | ffplay -

ffmpeg -loop 1 -i testcard.png  -vf "crop=\
	1280:720\
	:'min((iw/50)*t,iw-500)'\
	:\
	0"  -f matroska - | ffplay -

