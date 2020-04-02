#!/usr/bin/env python

import time, copy
from sys import exit
from decimal import *
from random import shuffle, randint
import usb.core

import scrollphathd as sphd 
from scrollphathd.fonts import font3x5

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
  name = None
  top = 0
  left = 0
  matrix = None
  flipped = False
  mirrored = False
  width = 0
  height = 0
  asciitxt = None

  def __init__( self, txt='', name=None ):
    self.name = name
    self.load_from_ascii( txt )

  def draw( self ):
    y = self.top
    for row in self.matrix:
      x = self.left
      for p in row:
        if x > -1 and y > -1:
          # 0 is transparent
          if p > 0: sphd.set_pixel(x,y,p)
        x+=1
      y+=1

  def flip( self ):
    rtn = []
    for i in reversed(range(len(self.matrix))):
      row = self.matrix[i]
      rtn.append(row)
    self.matrix = rtn
    self.flipped = not self.flipped

  def mirror( self ):
    rtn = []
    for row in self.matrix:
      r = []
      for i in reversed(range(len(row))):
        r.append(row[i])
      rtn.append(r)
    self.matrix = rtn
    self.mirrored = not self.mirrored

  def load_from_ascii( self, asciitxt ):
    greyscale = " .:-=+*#%@"
    rtn = []
    self.asciitxt = asciitxt
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
    self.set_dimensions()

  def set_dimensions(self):
    self.height = len(self.matrix)
    for row in self.matrix:
      if len(row) > self.width:
        self.width = len(row)

  def clear( self ):
    l = self.left
    w = self.width
    if l < 0: 
      l = 0
      w = self.left + self.width
    if w < 0:
      return
    t = self.top
    h = self.height
    if t < 0: 
      t = 0
      h = self.top + self.height
    if h < 0: 
      return
    sphd.clear_rect( l, t, w, h )

brush = Sprite('''
=:=:=:=          
=:=:=:=          
=:=:=:=          
@@@@@@@@@@@@@@@@@
''','toothbrush')

teeth = Sprite('''
:...:...:...:...:
:...:...:...:...:
:...:...:...:...:
:::::::::::::::::
''')

glint = Sprite('''
  @    
  @    
@@@@@  
  @    
  @    
''')
glint.top = 1
glint.left = 9

toprow = copy.deepcopy(teeth)
toprow.top = -4
toprow.name = 'top row'
bottomrow = copy.deepcopy(teeth)
bottomrow.flip()
bottomrow.top = 8
bottomrow.name = 'bottom row'

def grin():
  toprow.top = 0
  bottomrow.top = 3
  toprow.draw()
  bottomrow.draw()
  sphd.show()


def move_teeth(tfinal=0,bfinal=3):
  if toprow.top > tfinal: 
    tinc = -1 
  else: 
    tinc = 1
  if bottomrow.top > bfinal: 
    binc = -1 
  else: 
    binc = 1
  while toprow.top != tfinal or bottomrow.top != bfinal:
    if toprow.top != tfinal: 
      toprow.clear()
      toprow.top += tinc
      toprow.draw()
    if bottomrow.top != bfinal: 
      bottomrow.clear()
      bottomrow.top += binc
      bottomrow.draw()
    sphd.show()
    time.sleep(0.1)


def close_mouth(visiblerow='b'):
  move_teeth(0,3)

def open_mouth(visiblerow='b'):
  if visiblerow == 't':
    tfinal = -1
    bfinal = 8
  else:
    bfinal = 4
    tfinal = -7
  move_teeth(tfinal,bfinal)
  

def brush_teeth( corner='tl', seconds=30 ):
  print('brush ' + corner + ' for ' + str( seconds ) +' seconds' )
  open_mouth( corner[0] )
  if corner[0] == 'b': 
    if not brush.flipped:
      brush.flip()
    brush.top = 0
  else:
    if brush.flipped:
      brush.flip()
    brush.top = 3
  
  if corner[1] == 'r': 
    if not brush.mirrored:
      brush.mirror()
  else:
    if brush.mirrored:
      brush.mirror()
  brush.draw()
  sphd.show()
  direction = 'r'
  end = int(time.time()) + seconds
  while int(time.time()) < end:
    if brush.left < 5 and direction == 'r':
      brush.left += 1
    elif brush.left == 5:
      direction = 'l'
      brush.left -= 1
    elif brush.left > -5 and direction == 'l':
      brush.left -= 1
    else:
      direction = 'r'
    sphd.clear_rect(0,brush.top,17,4)
    brush.draw()
    sphd.show()
    time.sleep(0.01)
  brush.clear()
  close_mouth()

def shiny():
  sphd.clear()
  mouth = Sprite('')
  mouth.matrix = toprow.matrix + bottomrow.matrix[1:]
  for i in range(25):
    shiny = copy.deepcopy(mouth)
    for row in shiny.matrix:
      if i < len(row): row[i] *= Decimal(2)
      if i > 0 and i-1 < len(row): row[i-1] *= Decimal(2)
    shiny.draw()
    if i % 4 == 0:
      glint.left = i-2
      glint.top = randint(-3,4)
      glint.draw()
    sphd.show()
    time.sleep(0.01)
  time.sleep(0.05)
  sphd.show()


def game_loop():
  sphd.clear()
  close_mouth()
  if button:
    while True:
      if button.read():
        print('Button pushed')
        break
      time.sleep(0.5)

  corners = 'tl,tr,br,bl,tl,tr,br,bl'.split(',')
  shuffle(corners)
  for corner in corners:
    brush_teeth(corner, 15)
  time.sleep(1)
  shiny()
  time.sleep(1)

button = None
try:
  button = PanicButton()
except:
  print('No panic button found')

game_loop()
