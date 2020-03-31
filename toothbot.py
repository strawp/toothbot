#!/usr/bin/env python

import time, copy
from sys import exit
from decimal import *
from random import shuffle
import usb.core

import scrollphathd as sphd 
from scrollphathd.fonts import font3x5

IMAGE_BRIGHTNESS = 0.5

sphd.flip(True,True)

# http://files.righto.com/files/PanicButton.py
class PanicButton:
  def __init__(self):
    # Device is: ID 1130:0202 Tenx Technology, Inc. 
    self.dev = usb.core.find(idVendor=0x1130, idProduct=0x0202)
    if not self.dev:
      raise ValueError("Panic Button not found")
    
    try:
      self.dev.detach_kernel_driver(0) # Get rid of hidraw
    except Exception, e:
      pass # already unregistered

  def read(self):
    """ Read the USB port.
    Return 1 if pressed and released, 0 otherwise.
    """
    #Magic numbers are from http://search.cpan.org/~bkendi/Device-USB-PanicButton-0.04/lib/Device/USB/PanicButton.pm
    return self.dev.ctrl_transfer(bmRequestType=0xA1, bRequest=1, wValue=0x300, data_or_wLength=8, timeout=500)[0]
    

class Sprite(object):
  top = 0
  left = 0
  matrix = None
 
  def __init__( self, txt='' ):
    self.load_from_ascii( txt )

  def draw( self ):
    y = self.top
    for row in self.matrix:
      x = self.left
      for p in row:
        if p > 0:
          if x > -1 and y > -1:
            sphd.set_pixel(x,y,p)
        x+=1
      y+=1

  def flip( self ):
    rtn = []
    for i in reversed(range(len(self.matrix))):
      row = self.matrix[i]
      rtn.append(row)
    self.matrix = rtn

  def mirror( self ):
    rtn = []
    for row in self.matrix:
      r = []
      for i in reversed(range(len(row))):
        r.append(row[i])
      rtn.append(r)
    self.matrix = rtn

  def load_from_ascii( self, asciitxt ):
    greyscale = " .:-=+*#%@"
    rtn = []
    for line in asciitxt.splitlines():
      if len(line) == 0: continue
      row = []
      for c in line:
        if c in greyscale:
          brightness = Decimal( greyscale.find(c) )
        else:
          brightness = Decimal(c)
        if brightness > 0:
          brightness = brightness / 10
        row.append(brightness)
      rtn.append(row)
    self.matrix = rtn


toothbrush = Sprite('''
=:=:=:=          
=:=:=:=          
=:=:=:=          
@@@@@@@@@@@@@@@@@
''')

teeth = Sprite('''
:   :   :   :   :
:   :   :   :   :
:   :   :   :   :
:::::::::::::::::
''')

def grin():
  top = copy.deepcopy(teeth)
  bottom = copy.deepcopy(teeth)
  bottom.flip()
  top.top = 0
  bottom.top = 3
  top.draw()
  bottom.draw()
  sphd.show()

def open_mouth(row='b'):
  top = copy.deepcopy(teeth)
  bottom = copy.deepcopy(teeth)
  bottom.flip()
  top.top = 0
  bottom.top = 3
  top.draw()
  bottom.draw()
  sphd.show()
  if row == 'b':
    top.top -= 1
    for i in range(4):
      sphd.clear()
      bottom.top+=1
      bottom.draw()
      top.draw()
      sphd.show()
      time.sleep(0.1)
  else:
    bottom.top += 1
    for i in range(4):
      sphd.clear()
      bottom.top-=1
      bottom.draw()
      top.draw()
      sphd.show()
      time.sleep(0.1)
  

def brush_teeth( corner='tl', seconds=30 ):
  t = copy.deepcopy(teeth)
  b = copy.deepcopy(toothbrush)
  print('brush ' + corner + ' for ' + str( seconds ) +' seconds' )
  if corner == 'tl':
    b.top = 3
    t.top = -1
  elif corner == 'bl':
    t.flip()
    t.top = 4
    b.flip()
  elif corner == 'tr':
    b.mirror()
    t.top = -1
    b.top = 3
  else: # br
    b.mirror()
    b.flip()
    t.flip()
    t.top = 4
  sphd.clear_rect(0,0,17,7)
  t.draw()
  
  b.draw()
  sphd.show()
  direction = 'r'
  end = int(time.time()) + seconds
  while int(time.time()) < end:
    if b.left < 5 and direction == 'r':
      b.left += 1
    elif b.left == 5:
      direction = 'l'
      b.left -= 1
    elif b.left > -5 and direction == 'l':
      b.left -= 1
    else:
      direction = 'r'
    sphd.clear_rect(0,b.top,17,4)
    b.draw()
    sphd.show()
    time.sleep(0.01)

def game_loop():
  sphd.clear()
  grin()
  button = PanicButton()
  while True:
    if button.read():
      break
    time.sleep(0.5)

  corners = 'tl,tr,br,bl,tl,tr,br,bl'.split(',')
  # shuffle(corners)
  open_mouth()
  for corner in corners:
    brush_teeth(corner, 15)

  sphd.clear()
  sphd.set_font(font3x5)
  sphd.write_string('Done!')
  sphd.show()
  time.sleep(5)

while True:
  game_loop()
