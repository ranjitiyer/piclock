import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from gpiozero import Button
# display
from waveshare_epd import epd2in7
# imaging
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from signal import pause

import logging
import threading 

# time
import time
from datetime import datetime
import pytz
import calendar

# handle to the display
epd = epd2in7.EPD()

# initialize the display
epd.Init_4Gray()

logging.basicConfig(level=logging.DEBUG)
logging.info("Width %s ",epd2in7.EPD_WIDTH)
logging.info("Height %s",epd2in7.EPD_HEIGHT)

# Declare a font
font24 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 24)
font28 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 28)
font32 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 32)
font40 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 40)
font44 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 44)
font50 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 50)
font52 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 52)
font54 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 54)
font58 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 58)

key1 = Button(5)
key2 = Button(6)
key3 = Button(13)
key4 = Button(19)

epd.init()

def render(key):
    #print('Rendering the clock for %s' % key)
    # Make a blank image to clear the screen
    image = Image.new('1', (epd2in7.EPD_HEIGHT, epd2in7.EPD_WIDTH), 255)    # 255: clear the image with white
    draw = ImageDraw.Draw(image)
    epd.Clear(0xFF)

    now = datetime.utcnow()
    if key == 1:
        draw.text((60, 2), 'London', font = font40, fill = (0))
    elif key == 2:
        now = datetime.now(pytz.timezone('Asia/Kolkata'))
        draw.text((60, 2), 'Mumbai', font = font40, fill = (0))
    elif key == 3:
        now = datetime.now(pytz.timezone('Australia/Sydney'))
        draw.text((60, 2), 'Sydney', font = font40, fill = (0))
    elif key == 4:
        now = datetime.now(pytz.timezone('Singapore'))
        draw.text((30, 2), 'Singapore', font = font40, fill = (0))
                
    # Second section
    draw.line((0,50,264,50), fill=0, width=3)
    draw.text((48,58), now.strftime("%H:%M"), font=font58, fill=0)

    # Third section
    draw.line((0,50*2.5,264,50*2.5), fill=0, width=3)
    draw.rectangle((0,50*2.5,264,200), fill=(0))
    draw.text((34, 135), "%s %s %s" % (calendar.month_abbr[now.month], now.day, now.year), font=font32, fill=(255))

    # render the image
    epd.display(epd.getbuffer(image))

stop_flag = False
def clock_render_thread(key):
    global stop_flag
    logging.debug(f'In the rendering thread {stop_flag}')
    
    # render once
    render(key)

    # render once a min until asked to stop
    start_time = time.time()
    while not stop_flag:
        time.sleep(2)
        if time.time() - start_time >= 55:
            render(key)
            start_time = time.time()
    #print('Stop requested. Shutting down thread') 

import threading 
t1 = threading.Thread(target=clock_render_thread, args=(1,))

font_path = '/home/pi/work/e-Paper/RaspberryPi_JetsonNano/python/examples/Verdana.ttf'
custom_font = ImageFont.truetype(font_path, 14)

def render_separators(draw_context):
    image_width, image_height = 264, 176

    line_color = (0)

    # draw horizontal guidelines
    section1 = 0 + image_height/7
    section2 = section1 + image_height/7
    section3 = section2 + image_height/7
    section4 = section3 + image_height/7
    section5 = section4 + image_height/7
    section6 = section5 + image_height/7

    draw_context.line([(0,section1), (image_width,section1)], fill=line_color, width=1)
    draw_context.line([(0,section2), (image_width,section2)], fill=line_color, width=1)
    draw_context.line([(0,section3), (image_width,section3)], fill=line_color, width=1)
    draw_context.line([(0,section4), (image_width,section4)], fill=line_color, width=1)
    draw_context.line([(0,section5), (image_width,section5)], fill=line_color, width=1)
    draw_context.line([(0,section6), (image_width,section6)], fill=line_color, width=1)

    # draw vertical guidelines
    image_width, image_height = 264, 176
    section1 = 0 + image_width/7
    section2 = section1 + image_width/7
    section3 = section2 + image_width/7
    section4 = section3 + image_width/7
    section5 = section4 + image_width/7
    section6 = section5 + image_width/7

    draw_context.line([(section1,25), (section1,image_height)], fill=line_color, width=1)
    draw_context.line([(section2,25), (section2,image_height)], fill=line_color, width=1)
    draw_context.line([(section3,25), (section3,image_height)], fill=line_color, width=1)
    draw_context.line([(section4,25), (section4,image_height)], fill=line_color, width=1)
    draw_context.line([(section5,25), (section5,image_height)], fill=line_color, width=1)
    draw_context.line([(section6,25), (section6,image_height)], fill=line_color, width=1)

# todo: render month in bigger font
def render_month_year(draw):
    text = f'{calendar.month_name[datetime.utcnow().month]} {datetime.utcnow().year}'
    text_position = (15,2)
    left, top, right, bottom = draw.textbbox(text_position, text, custom_font)
    #print(left, top, right, bottom)

    width = 264
    start_x = width/2 - (right-left)/2 - 10 # padding
    draw.text((start_x, 5), text, font=custom_font, fill='black')

def render_days(draw):
    image_width = 264
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    sections = [ i*image_width/7 for i in range(1,8) ]
    text_color = (0)

    # make an exception for Wed?
    for (day, right_x) in zip(days, sections):
        padding, y_pos = 10, 30
        if day == 'Wed':
            text_position = (right_x - draw.textlength(day) - padding - 3,y_pos)
        else:
            text_position = (right_x - draw.textlength(day) - padding,y_pos)
        draw.text(text_position, day, font=custom_font, fill=text_color)

def render_dates(draw, row):
    dates = calendar.monthcalendar(year=datetime.now().year, month=datetime.now().month)
    text_color = (0)

    # draw vertical guidelines
    image_width = 264
    sections = [ i*image_width/7 for i in range(1,8) ]
    #print(sections)
    
    for (date_text,right_x) in zip(dates[row], sections):
        padding = 15 + draw.textlength(str(date_text))
        #print(f"Padding for {date_text} is {padding}")
        text_position = (right_x - padding, 55+(row * 25))
        if date_text != 0:
            if datetime.utcnow().day == date_text:
                #print('print today differently ', date_text)
                
                x1,y1 = text_position
                left, top, right, bottom = draw.textbbox(text_position, str(date_text), custom_font)
                #print('text position ',text_position)
                #print('text bbox is ',(left,top,right,bottom)) 
                draw.rectangle((x1-2,y1,right+2,bottom+3),outline='black', width=1)
                #print('text position is ',text_position)
                draw.text(text_position, str(date_text), font=custom_font, fill=text_color)
            else:
                draw.text(text_position, str(date_text), font=custom_font, fill=text_color)


def render_calendar():
    # make a blank image
    image = Image.new('1', (epd2in7.EPD_HEIGHT, epd2in7.EPD_WIDTH), 255)    # 255: clear the image with white
    draw = ImageDraw.Draw(image)
    
    # clear the screen
    epd.Clear(0xFF)

    # draw separator lines
    # render_separators(draw)

    # month and year
    render_month_year(draw)

    # days of week
    render_days(draw)

    # draw vertical guidelines

    # # dates
    render_dates(draw,0)
    render_dates(draw,1)
    render_dates(draw,2)
    render_dates(draw,3)
    render_dates(draw,4)

    logging.debug('rendering the calendar')

    # render the image
    epd.display(epd.getbuffer(image))

def start_render_thread(key, calendar=False):
    print(f'Render thread called for key {key}')
    global stop_flag
    global t1

    print('Render thread called ')
    stop_flag = True
    t1.join()
    stop_flag = False
    if calendar == True:
        t1 = threading.Thread(target=calendar_render_thread)
    else:    
        t1 = threading.Thread(target=clock_render_thread, args=(key,))
    t1.start()

def calendar_render_thread():
    global stop_flag
    logging.debug(f'In the calendar rendering thread {stop_flag}')
    
    # render once
    render_calendar()

    # render once a day
    start_time = time.time()
    while not stop_flag:
        time.sleep(2)
        if time.time() - start_time >= 60*60*24:
            render_calendar()
            start_time = time.time()

    #print('Value of stop_flag ', stop_flag)
    print('Stop requested on the calendar thread. Shutting down thread')

mode = 'clock'
key = 1
def handleBtnPress1(btn):
    global key, mode
    if key != 1 or mode == 'calendar':
        print('rendering clock')
        mode = 'clock'
        key = 1
        start_render_thread(1)
    else:
        mode = 'calendar'
        key = 1
        print('rendering calendar')
        start_render_thread(1, True)
    
def handleBtnPress2(btn):
    global key, mode
    key = 2
    start_render_thread(2)
    
def handleBtnPress3(btn):
    global key, mode
    key = 3
    start_render_thread(3)
    
def handleBtnPress4(btn):
    global key, mode
    key = 4
    start_render_thread(4)

# tell the button what to do when pressed
key1.when_pressed = handleBtnPress1
key2.when_pressed = handleBtnPress2
key3.when_pressed = handleBtnPress3
key4.when_pressed = handleBtnPress4

# start the default render thread
t1.start()
#render_calendar()

pause()