#! /usr/bin/python
#
# (c) 2014 jnweiger@gmail.com, distribute under GPL-2.0
# 
# Usage: 
#  '-'           zoom out
#  '+'           zoom in
#  LMB           drag the graphics around
#  'p'           save 'output.pdf'
#
# Reference Manual:
# http://people.gnome.org/~gianmt/pygoocanvas/
# https://developer.gnome.org/goocanvas/unstable/
#
# Examples:
# http://nullege.com/codes/search/goocanvas.Ellipse

import sys
import gtk
from goocanvas import *
import cairo

def print_pdf(c):
  # (x1,y1,x2,y2) = c.get_bounds()
  scale= 72/25.4 # PDF is at 72DPI, so this is 12 inch wide.
  width=300     # mm
  height=400    # mm
  width *= scale
  height *= scale
  surface = cairo.PDFSurface("output.pdf", width, height)
  ctx = cairo.Context(surface)
  ctx.scale(scale,scale)
  # ctx.set_source_rgb(1,1,1)
  # ctx.rectangle(0,0,width,height)
  # ctx.fill()
  # ctx.set_source_rgb(1,0,0)
  # ctx.move_to(width/2,height/2)
  # ctx.arc(width/2,height/2,512*0.25,0, 6)     # math.pi*2)
  # ctx.fill()
  c.render(ctx)
  ctx.show_page()
  print "output.pdf written"

def key_press(win, ev, c):
  new_idx = None
  s = c.get_scale()  
  key = chr(ev.keyval & 0xff)
  if   key == '+':  c.set_scale(s*1.2)
  elif key == '-':  c.set_scale(s*.8)
  elif key == 'p':  print_pdf(c)
  elif ev.keyval <= 255: gtk.main_quit()

def button_press(win, ev):
  win.click_x = ev.x
  win.click_y = ev.y

def button_release(win, ev):
  win.click_x = None
  win.click_y = None

def motion_notify(win, ev, c):
  try:
    # 3.79 is the right factor for units='mm'
    dx = (ev.x-win.click_x) / c.get_scale() / 3.79
    dy = (ev.y-win.click_y) / c.get_scale() / 3.79
    win.click_x = ev.x
    win.click_y = ev.y
    (x1,y1,x2,y2) = c.get_bounds()
    c.set_bounds(x1-dx,y1-dy,x2-dx,y2-dy)
  except:
    pass


def main ():
    win = gtk.Window()

    canvas = Canvas(units='mm', scale=1)
    canvas.set_size_request(800, 600)
    # canvas.set_bounds(0, 0, 120., 90.)
    root = canvas.get_root_item()

    win.connect("destroy", gtk.main_quit)
    win.connect("key-press-event", key_press, canvas)
    win.connect("motion-notify-event", motion_notify, canvas)
    win.connect("button-press-event", button_press)
    win.connect("button-release-event", button_release)

    new_cut = [ [ (10,10), (30,10), (20, 20), (10,10) ],
                [ (10,30), (20, 40), (30, 30) ] ]

    for i in range(5):
        for path in new_cut:
          for C in path:
            Ellipse(parent=root, center_x=C[0]+35*i, center_y=C[1], radius_x=5, radius_y=5, line_width = 0.003+0.005*i, stroke_color="black")

          p = Points(path)
          poly = Polyline(parent=root, points=p, line_width=0.031+0.005*i, stroke_color="black")
	  poly.translate(35*i, 0)

    win.add(canvas)
    win.show_all()
                                
    gtk.main()

if __name__ == "__main__":
    main ()
