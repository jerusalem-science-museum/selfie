import cv2
import numpy as np
import imutils

import pygame
from pygame.locals import *

from common.Timer import Timer

import datetime

DELAY_BETWEEN_SOUNDS = 1

WAITING_FOR_START = 0
WAITING_FOR_PHOTO_1 = 1
WAITING_FOR_PHOTO_2 = 2
SUMMARY = 3

pygame.init()
pygame.mouse.set_visible(False)

camera1 = cv2.VideoCapture(0)
camera2 = cv2.VideoCapture(1)

screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)

state = WAITING_FOR_START

language = None
image1 = None
image2 = None
imageSurface1 = None
imageSurface2 = None

timer = None

cameraEffect = pygame.mixer.Sound('assets/camera.ogg')

sounds = { 
	'en': ['assets/E1.ogg', 'assets/E2.ogg', 'assets/E3.ogg'],
	'he': ['assets/H1.ogg', 'assets/H2.ogg', 'assets/H3.ogg'],
	'ar': ['assets/A1.ogg', 'assets/A2.ogg', 'assets/A3.ogg']
}

def moveNext():
	global timer, state

	timer = None

	if state == WAITING_FOR_PHOTO_1:
		# Play second sound
		pygame.mixer.music.load(sounds[language][1])
		pygame.mixer.music.play()
		state = WAITING_FOR_PHOTO_2
	elif state == WAITING_FOR_PHOTO_2:
		# Play summary sound
		pygame.mixer.music.load(sounds[language][2])
		pygame.mixer.music.play()
		state = SUMMARY

def soundDone():
	global state, image1, image2, imageSurface1, imageSurface2, timer

	if state == WAITING_FOR_PHOTO_1:
		# Take picture
		ret, image1 = camera1.read()
		cameraEffect.play()
		timer = Timer(DELAY_BETWEEN_SOUNDS, moveNext)
		
	elif state == WAITING_FOR_PHOTO_2:
		# Take picture
		ret, image2 = camera2.read()
		cameraEffect.play()

		imageSurface1 = getSurfaceFromFrame(imutils.rotate_bound(image1, 90))
		imageSurface2 = getSurfaceFromFrame(imutils.rotate_bound(image2, 90))

		# Save both images with timestamp
		timeString = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
		cv2.imwrite('images/' + timeString + '-image1.png', image1)
		cv2.imwrite('images/' + timeString + '-image2.png', image2)

		timer = Timer(DELAY_BETWEEN_SOUNDS, moveNext)

def getSurfaceFromFrame(frame):
	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	frame = np.fliplr(frame)
	frame = np.rot90(frame)
	return pygame.surfarray.make_surface(frame)

def startGame():
	global state, timer

	timer = None
	state = WAITING_FOR_PHOTO_1
	isGameRunning = False
	pygame.mixer.music.load(sounds[language][0])
	pygame.mixer.music.play()

isGameRunning = True
clock = pygame.time.Clock()

lastTime = pygame.time.get_ticks()

while isGameRunning:
	screen.fill([0,0,0])

	if imageSurface1 is not None and imageSurface2 is not None:
		spaceX = (screen.get_width() - 2 * imageSurface1.get_width()) // 3
		spaceY = (screen.get_height() - imageSurface1.get_height()) // 2
		screen.blit(imageSurface1, (spaceX, spaceY))
		screen.blit(imageSurface2, (spaceX * 2 + imageSurface1.get_width(), spaceY))

	currTime = pygame.time.get_ticks()
	dt = (currTime - lastTime) / 1000
	lastTime = currTime

	if timer is not None:
		timer.tick(dt)
	elif state == WAITING_FOR_PHOTO_1 or state == WAITING_FOR_PHOTO_2:
		if not pygame.mixer.music.get_busy():
			soundDone()

	for event in pygame.event.get():
		if event.type == KEYDOWN:
			if event.key == K_e:
				language = 'en'
				startGame()
			elif event.key == K_h:
				language = 'he'
				startGame()
			elif event.key == K_a:
				language = 'ar'
				startGame()
			elif event.key == K_q:
				isGameRunning = False

	pygame.display.flip()
	clock.tick(60)

pygame.quit()
cv2.destroyAllWindows()