# NeoPixel library strandtest example
# Author: Tony DiCola (tonlllllllllllllllly@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

import random
import math

import numpy
from scipy import fft, arange

import alsaaudio

import numpy as np

from neopixel import *
import pylab
import hyperion

hyp = hyperion.server()

# LED strip configuration:
LED_COUNT   = 46*9       # Number of LED pixels.
LED_PIN    = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 900000  # LED signal frequency in hertz (usually 800khz)
LED_DMA     = 5       # DMA channel to use for generating signal (try 5)
LED_INVERT  = True   # True to invert the signal (when using NPN transistor level shift)

redwalker = True	# put False here for EQ
redwalker_rgb = [255,0,0]


def clip(sample):
	"""Clips a value greater then 255"""
	if(sample > 255):
		return 255
	elif sample < 0:
		return 0
	else:
		return sample
		
def scaleLine(tgtPixelsSize , srcPixels):
	tgtPixels = [0 for x in range(tgtPixelsSize)]

	#print "tgtPixelsSize: ", tgtPixelsSize
	#print "srcPixels: ", len(srcPixels)
	
	epsilon = 0.000001
	scale = (1.0*(len(srcPixels)-1)/(len(tgtPixels)-1+epsilon))


	for tgtIndex in range(len(tgtPixels)):
		estSrcIndex = tgtIndex * scale
		srcIndex = int(estSrcIndex)
		delta = estSrcIndex - srcIndex

		#print srcIndex, tgtIndex, estSrcIndex
		tgtPixels[tgtIndex] = (1-delta)*srcPixels[srcIndex]+delta*srcPixels[srcIndex+1]
		tgtPixels[tgtIndex] = tgtPixels[tgtIndex] * tgtPixels[tgtIndex] * 0.0000001

	return tgtPixels

def fftToPixelsHue(length, data, sizefft):

	a = numpy.fromstring(data,'int16')/32768.0
	#print np.mean(a)	
	#a = [math.sin(25*2*math.pi*(x/180.0)) for x in range(180)]

	#print a
	
	ft = (abs(fft(a)))[15:87]/90
	#print len(ft)

	#drawGraph(len(ft),ft)
	
	#print ft
	lenDivisor = 8

	eq = [0 for x in range(9)]
	for i in range(9):
		#print ft[j+lenDivisor*(i)]
		eq[i] = np.mean(ft[i*lenDivisor:(i+1)*lenDivisor])

	#print eq
	
	return eq

# power = 0-1.0
def toBar(striplength, power, bgCol):
	bar = [bgCol for x in range(striplength)]
	#for i in range(striplength):
	#	Col = Color(int(255.0*math.log(power)*i/striplength),0,0)
	#	bar[i] = Col

	if(math.isnan(power) | math.isinf(power)):
		power = 1.0;
	
	#print power

	power = power * 16.0

	for i in range(striplength):
		if( int(power*48) > i):
			Col = Color(clip(int(5.0*power)),clip(int(127.0*power)),clip(int(255.0*power)))
			bar[i] = Col

	return bar

def drawGraph(lenght, yData):
    xAxis = range(lenght)
    pylab.figure(1)
    pylab.plot(xAxis, yData)
    pylab.show()

def redstd(striplength, strip,j,rgb):
	
	r,g,b=rgb
	for i in range(striplength):
		Col = Color(r/3,g/3,b/3)
		strip.setPixelColor(i,Col)
	
	strip.setPixelColor(j,Color(r,g,b))
	if j > 1:
		strip.setPixelColor(j-1,Color(r,g,b))
		strip.setPixelColor(j-2,Color(r,g,b))

	strip.show()
	
		
		

# Main program logic follows:
if __name__ == '__main__':
	# Create NeoPixel object with appropriate configuration.
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT)
	# Intialize the library (must be called once before other functions).
	strip.begin()

	#print alsaaudio.cards()

	card = 'front:CARD=Device,DEV=0'
        inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL,card)
        inp.setchannels(1)
	inp.setrate(32000)
        inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
	inp.setperiodsize(90)

	#for n in range(1, 16385):
	#	if inp.setperiodsize(n) == n:
	#		print n	

	print 'Press Ctrl-C to quit.'
	walker_pos = 0
	walker_dir = 1
	fg_bg_toggle = 0	# start with bgCol

        hyp_color = redwalker_rgb

	bar = []
	lastEQ = [0,0,0,0,0,0,0,0,0]

	counter = 0
	bgCol = Color(hyp_color[0], hyp_color[1], hyp_color[2])
	fgCol = Color(255,0,0)

	while True:
		
		if (hyp.poll()):
                        new = hyp.color()
                        if new:
                        	hyp_color = new
                        	print new
                	else: 
				hyp_color = redwalker_rgb
				fg_bg_toggle = 1 - fg_bg_toggle
			
		if redwalker:
			redstd(LED_COUNT, strip, walker_pos, hyp_color)
			if walker_pos >= LED_COUNT: walker_dir = -1
			if walker_pos <= 0:         walker_dir = 1
			walker_pos += walker_dir
		else:			
			length,data = inp.read()
			r,g,b = hyp_color
			if fg_bg_toggle:
				fgCol = Color(r,g,b)			
			else:
				bgCol = Color(r,g,b)

			while (length != 90):
				length,data = inp.read()

			if (length == 90):
					
				eq = fftToPixelsHue(len(data), data, strip.numPixels())

				if(eq[5] != 0):
					lastEQ = eq
				else:
					for i in range(9):
						lastEQ[i] = lastEQ[i]/1.5
				iEQ = 0
				for ledNum in range(LED_COUNT):
					if (ledNum % 46) == 0:
						bar = toBar(46,lastEQ[iEQ],bgCol)
						#print bar
						iEQ += 1

					strip.setPixelColor(ledNum,bar[(ledNum%46)])

					#for i in range(LED_COUNT):
					#	strip.setPixelColor(i,fgCol)
			
				strip.show()
##46 per Strip
