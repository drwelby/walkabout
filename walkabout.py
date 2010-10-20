#!/usr/bin/python
import os
import cgi
import sys
import Image
import ImageDraw
import ImageFont
import ImageOps
import cStringIO

# image size restrictions
MAX_WIDTH = 2000
MIN_WIDTH = 640
MAX_HEIGHT = 1200
MIN_HEIGHT = 400

# frame parameters
BORDER_W =3 
FRAME_W = 1
BAR_W_PER = .25
BAR_H = 30 
TEXT_BUFF = 6

bar_h = BAR_H + BORDER_W


# target parameters
T_OFFSET = BAR_H/2 + BORDER_W
BAR_OFFSET = 0
CIRCLE_OFFSET = 4 
CROSS_OFFSET = 5 

# some colors for convenience
BLACK = (0,0,0,255)
TRANS = (255,255,255,0)
WHITE = (255,255,255,255)
#test color, uncomment
#WHITE = (255,255,25,255)

# set up font, need one local in the package
font = ImageFont.truetype('/Library/Fonts/Andale Mono.ttf', BAR_H - (2*TEXT_BUFF))

def drawTarget(x,y,bar_h,draw):

    ''' Draws a target into a bar given an ImageDraw'''

    radius = int(bar_h/2) - BAR_OFFSET
    draw.ellipse( [x-radius, y-radius, x+radius, y+radius], fill=WHITE, outline=BLACK)
    radius = radius- CIRCLE_OFFSET 
    draw.ellipse( [x-radius, y-radius, x+radius, y+radius], fill=WHITE, outline=BLACK)
    radius = radius - CROSS_OFFSET 
    draw.line( [x-radius,y,x+radius,y], fill=BLACK)
    draw.line( [x,y-radius,x,y+radius], fill=BLACK)

   

def drawTextImage(text,pos,bar_w):

    '''draws an aligned image to be pasted into the frame'''

    text = str(text)
    text_w, text_h = font.getsize(text)
    t_img = Image.new('RGBA', (bar_w, bar_h),WHITE)
    t_draw = ImageDraw.Draw(t_img)
    if pos == "N":
        t_draw.text((bar_h +BORDER_W+ TEXT_BUFF, TEXT_BUFF+BORDER_W), text, font=font, fill=BLACK)
        return t_img
    elif pos == "W":
        t_draw.text((bar_w-text_w-TEXT_BUFF-bar_h, TEXT_BUFF), text, font=font, fill=BLACK)
        return t_img.rotate(90, expand=1)
    elif pos == 'S':
        t_draw.text((bar_w-text_w-TEXT_BUFF-bar_h, TEXT_BUFF),text, font=font, fill=BLACK)
        return t_img
    else: 
        t_draw.text((bar_w-text_w-TEXT_BUFF-bar_h, TEXT_BUFF),text, font=font, fill=BLACK)
        return t_img.rotate(-90, expand=1)


def drawFrame(bbox, height, width):

    '''Draws the frame and outputs it as a PNG'''

    if height > MAX_HEIGHT or height < MIN_HEIGHT:
        returnError("Height parameter must be between %s and %s" % (MIN_HEIGHT, MAX_HEIGHT))
    if width > MAX_WIDTH or width < MIN_WIDTH:
        returnError("Width parameter must be between %s and %s" % (MIN_WIDTH, MAX_WIDTH))
    #try:
    east,south,west,north = (float(x)  for x in bbox.split(','))
    #except:
        #returnError("Invalid BBOX")

    # get the pixel resolutino and change the bounds to the targets 
    res = abs((east-west)/width)
    north = north - res*T_OFFSET
    south = south + res*T_OFFSET
    west = west + res*T_OFFSET
    east = east - res*T_OFFSET


    bar_w = width * BAR_W_PER + BORDER_W
        #initialize to white
    img = Image.new("RGBA", (width,height),WHITE)
    draw = ImageDraw.Draw(img)
    f = cStringIO.StringIO()

    #transparent center
    draw.rectangle( [BORDER_W,BORDER_W,width-BORDER_W, height-BORDER_W], fill=TRANS, outline=BLACK)

    #coordinate boxes
    draw.rectangle( [0,0,bar_w, bar_h], fill=WHITE )
    draw.rectangle( [0,0,bar_h, bar_w], fill=WHITE )
    draw.rectangle( [width,height,width-bar_w, height-bar_h], fill=WHITE )
    draw.rectangle( [width,height, width-bar_h, height-bar_w], fill=WHITE )

    #add text
    img.paste(drawTextImage(north,'N', bar_w), (0,0))
    img.paste(drawTextImage(west,'W', bar_w), (0,0))
    img.paste(drawTextImage(south,'S', bar_w), (width-bar_w, height-bar_h))
    img.paste(drawTextImage(east,'E', bar_w), (width-bar_h, height-bar_w))
    #add targets
    drawTarget(20,20,10,draw)
    drawTarget(T_OFFSET, T_OFFSET,BAR_H,draw)
    drawTarget(width-T_OFFSET, height-T_OFFSET, BAR_H,draw)

    #finish frame
    draw.line( [bar_h,bar_h,bar_w,bar_h], fill=BLACK)
    draw.line( [bar_h,bar_h,bar_h,bar_w], fill=BLACK)
    draw.line( [bar_w,BORDER_W,bar_w,bar_h], fill=BLACK)
    draw.line( [BORDER_W,bar_w, bar_h,bar_w], fill=BLACK)
    draw.line( [width-bar_h, height-bar_h, width-bar_w, height-bar_h], fill=BLACK)
    draw.line( [width-bar_h, height-bar_h, width-bar_h, height-bar_w], fill=BLACK)
    draw.line( [width-bar_w, height-bar_h, width-bar_w, height-BORDER_W], fill=BLACK)
    draw.line( [width-bar_h, height-bar_w, width-BORDER_W, height-bar_w], fill=BLACK)


    img.save(f, 'PNG')

    print "Content-Type: image/png\n"
    
    f.seek(0)
    print f.read()
    
def returnError(msg):
    print "Content-type: text/html"
    print
    print msg
    sys.exit()

def returnCapabilities():
    server = os.environ['SERVER_NAME']
    port = os.environ['SERVER_PORT']
    if port == '80':
        port = ''
    else:
        port = ':' + port
    templatevars = {'uri':"http://" + server + port + "/walkabout.py?"}
    
    f = open('capabilities.xml', 'r')
    print "Content-Type: text/xml\n"
    f.seek(0)
    print f.read() % templatevars
    sys.exit()

def returnServer():
    print "Content-Type: text/html\n"
    print "http://" + os.environ['SERVER_NAME'] +":"+ os.environ['SERVER_PORT']
    sys.exit()

if __name__ == "__main__":
    form = cgi.FieldStorage()
    form = dict((key.lower(), form[key]) for key in form.keys())
    if "request" in form:
        if form['request'].value.lower() == 'getcapabilities':
                returnCapabilities()
        if form['request'].value.lower() == 'getserver':
            returnServer()
    if "width" in form and "height" in form and "bbox" in form:
        srs = "srs" in form and form["srs"].value  
        drawFrame(form["bbox"].value,int(form["height"].value),int(form["width"].value))
    else:
        returnError("Insufficient parameters: WIDTH, HEIGHT, and BBOX required")
