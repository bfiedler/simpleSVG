# simpleSVG.py is a module for generating SVG graphics.
# It is especially useful for constructing nonstandard plots which are
# not offered by a high level function call in the usual plotting packages.
# Recommend that your first learn SVG, such as at http://www.svgbasics.com/index.html
# Put this Python module either in your Python path or in your current working directory.
# A test graphic is output by executing the module, e.g. in Linux: python simpleSVG.py
# Written by Brian Fiedler, after some exploratory motivation by Charlie Pham.
# v0.1  December 25, 2007
# v0.11 February 2, 2008, image command added
# v0.12 October 6, 2008, clipping ability added
# v0.13 January 4, 2010, added arc, and a few other things
# v0.14 May 12, 2010, added radial
# v0.20 June 22, 2011.  Now works with both Python 2.6 and Python 3.1
# v0.21 June 2, 2013. Changed default viewer to eog, rather than inkscape
# v0.22 February 6, 2025.  2to3 simpleSVG.py -w ; reindent simpleSVG.py
####


import os,sys
from math import *
#from __future__ import print_function
display_prog = 'eog' #command to display images, using optional display() method
#display_prog = 'inkview' #command to display images, using optional display() method
pyvers=sys.version_info[0]
if pyvers >=3:
    import fractions
    fractype=type(fractions.Fraction(1,2))

class svg_class:
    def __init__(self,fname="temp.svg",bbx=512,bby=512,whiteback=True):
        self.fname = fname
        self.bbx = int(bbx)
        self.bby = int(bby)
        self.svg=open(self.fname,'w')
        self.group_count=0
        header = """<?xml version="1.0"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg
xmlns:svg="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink"
xmlns="http://www.w3.org/2000/svg"
version="1.0"
height="%d" width="%d">
""" % (self.bby,self.bbx)
        self.svg.write(header)
        if whiteback: self.rect(0,0,self.bbx,self.bby,fill="white")
        self.group(fill_opacity=1., fill="none", stroke="black", stroke_width=1,
font_size="10pt", font_family="Arial, sans-serif")
#               self.scale() # after v.12, scale must be called explicitly, to prevent clipPath from premature definition

    def close(self):
        while self.group_count>=1: self.group()
        endfile = "</svg>\n"
        self.svg.write(endfile)
        sys.stdout.write("The file "+self.fname+" was successfully written and closed by simpleSVG\n")
        self.svg.close()
        return

    def display(self,prog=display_prog):
        os.system("%s %s" % (prog,self.fname))
        return

    def scale(self,xmin=0.,xmax=1.,ymin=0.,ymax=1., #sets the user coordinates
                    leftmarg=50,rightmarg=50,botmarg=50,topmarg=50):
        self.xmin=xmin
        self.xmax=xmax
        self.ymin=ymin
        self.ymax=ymax
        self.leftmarg=leftmarg
        self.rightmarg=rightmarg
        self.botmarg=botmarg
        self.topmarg=topmarg
        self.xscale=float(self.bbx-self.leftmarg-self.rightmarg)/(self.xmax-self.xmin)
        self.yscale=float(self.bby-self.botmarg -self.topmarg  )/(self.ymax-self.ymin)
        clippath="""<defs><clipPath id="marginmask">
<rect x="%d" y="%d" width="%d" height="%d" />
</clipPath></defs>
""" % (
self.leftmarg, self.topmarg, self.bbx-self.leftmarg-self.rightmarg, self.bby-self.topmarg-self.botmarg)
        self.svg.write(clippath)

    def ix(self,x): #svg x coordinate in pts as function of various types of user "x"
        if isinstance(x,float):
            return self.leftmarg+(x-self.xmin)*self.xscale
        elif isinstance(x,complex):
            return x.imag*self.bbx
        elif pyvers<3 and isinstance(x,long):
            return x*.01
        elif pyvers>=3 and type(x)==fractype:
            return float(x)
        else:
            return x

    def jy(self,y): #svg y coordinate in pts as function of various types of user "y"
        if isinstance(y,float):
            return self.bby-(self.botmarg+(y-self.ymin)*self.yscale)
        elif isinstance(y,complex):
            return y.imag*self.bby
        elif pyvers<3 and isinstance(y,long):
            return y*.01
        elif pyvers>=3 and type(y)==fractype:
            return float(y)
        else:
            return y

#sizes of things are scaled a bit differently from a position of a thing.
    def sx(self,x): #pt size for fonts, ticks, radius, relative displacement etc., as function of user "x" size
        if isinstance(x,float):
            return x*self.xscale
        elif isinstance(x,complex):
            return x.imag*self.bbx
        elif pyvers<3 and isinstance(x,long):
            return x*.01
        elif pyvers>=3 and type(x)==fractype:
            return float(x)
        else:
            return x

    def sy(self,y): #pt size for fonts, ticks, radius, relative displacement etc., as function of user "y" size
        if isinstance(y,float):
            return -y*self.yscale #note minus sign!!
        elif isinstance(y,complex):
            return y.imag*self.bby
        elif pyvers<3 and isinstance(y,long):
            return y*.01
        elif pyvers>=3 and type(y)==fractype:
            return float(y)
        else:
            return y

    def pathdata(self,*a):
        b=[] #will store all the numbers and sequences of coordinates between the tags
        s="" #a formatted string of all the coordinate pair numbers
        d="" #the pathdata string, for use in <path d=...."
        for q in a: #process items im parameter list
            if isinstance(q,str): #found a tag
                if b: #process stored coordinate pairs in b
                    bf=[x for x in flattn(b)] #flatten the coordinate array and float, flatten is a generator
                    for n in range(0,int(len(bf)/2)):
#                                               if (s): s+=", " #separate coordinate pairs by commas
                        if (s): s+=" " #no comma works in more browsers and software
                        x,y=bf[2*n:2*n+2]
                        if qz in ('l','m'):#add formatted relative coordinate to string
                            s+=" %.2f %.2f" % ( self.sx(x) , self.sy(y) )
                        else:#add formatted absolute coordinate to string
                            s+=" %.2f %.2f" % ( self.ix(x) , self.jy(y) )
                    b=[] #empty the list of coordinate pairs
                d+=s #add formatted coordinate pairs to pathdata
                s="" #clear the string
                d+=" "+q #finally add the tag to the string
                qz=q #store the tag
            else:
                b.append(q) #assume item is coordinate, or list or tuple of coordinates
        if b: #end of the argument list has been reached, process b
            bf=[x for x in flattn(b)]
            for n in range(0,int(len(bf)/2)):
#                               if (s): s+=", " #
                if (s): s+=" " #works better than above
                x,y=bf[2*n:2*n+2]
                if qz in ('l','m'):#add formatted relative coordinate to string
                    s+=" %.2f %.2f" % ( self.sx(x) , self.sy(y) )
                else:#add formatted absolute coordinate to string
                    s+=" %.2f %.2f" % ( self.ix(x) , self.jy(y) )
            d+=s
        return d

    def path(self,*a,**k):
        d=k.pop('d',"")
        style=k.pop('style',"")
        for key in k.keys(): style+=key.replace('_','-')+':'+str(k[key])+';'
        if a: d+=self.pathdata(*a)
        p='<path '
        if style: p+='style="'+style+'" '
        self.svg.write(p+' d="'+d+'"/>\n')

    def group(self,**k):
        if not k and self.group_count>=1:
            self.group_count-=1
            self.svg.write('</g>\n')
        else:
            style=k.pop('style',"")
            transform=k.pop('transform',"")
            clippath=k.pop('clip_path',"")
            for key in k.keys(): style+=key.replace('_','-')+':'+str(k[key])+';'
            self.group_count+=1
            g='<g '
            if style: g+='style="'+style+'" '
            if transform: g+='transform="'+transform+'" '
            if clippath: g+='clip-path="'+clippath+'" '
            self.svg.write(g+'>\n')


#SIMPLE DRAWING

    def rect(self,x,y,width,height,**k): #better than native: negative width and height okay
        style=k.pop('style',"")
        for key in k.keys(): style+=key.replace('_','-')+':'+str(k[key])+';'
        d=self.pathdata('M',x,y,'l',width,0,'l',0,height,'l',-width,0,'Z')
        self.path(d=d,style=style)

    def rect2(self,x1,y1,x2,y2,**k):
        style=k.pop('style',"")
        for key in k.keys(): style+=key.replace('_','-')+':'+str(k[key])+';'
        d=self.pathdata('M',x1,y1,'L',x2,y1,'L',x2,y2,'L',x1,y2,'Z')
        self.path(d=d,style=style)

    def poly(self,*a,**k):
        style=k.pop('style',"")
        for key in k.keys(): style+=key.replace('_','-')+':'+str(k[key])+';'
        b=[x for x in flattn(a)]
        d=self.pathdata('M',b[0:2],'L',b[2:],'Z')
        self.path(d=d,style=style)

    def draw(self,*a,**k):
        style=k.pop('style',"")
        for key in k.keys(): style+=key.replace('_','-')+':'+str(k[key])+';'
        b=[x for x in flattn(a)]
        d=self.pathdata('M',b[0:2],'L',b[2:])
        self.path(d=d,style=style)

    def circle(self,cx,cy,r,**k):
        style=k.pop('style',"")
        for key in k.keys(): style+=key.replace('_','-')+':'+str(k[key])+';'
        p='<circle cx="%.2f" cy="%.2f" r="%.2f" ' % (self.ix(cx),self.jy(cy),self.sx(r))
        if style: p+='style="'+style+'" '
        self.svg.write(p+'/>\n')

    def line(self,x1,y1,x2,y2,**k):
        style=k.pop('style',"")
        for key in k.keys(): style+=key.replace('_','-')+':'+str(k[key])+';'
        p='<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" ' % (self.ix(x1),self.jy(y1),self.ix(x2),self.jy(y2))
        if style: p+='style="'+style+'" '
        self.svg.write(p+'/>\n')

    def text(self,x,y,angle,text,**k):
        style=k.pop('style',"")
        for key in k.keys(): style+=key.replace('_','-')+':'+str(k[key])+';'
        p='<text transform="translate(%8.2f,%8.2f) rotate(%8.2f) "' % (self.ix(x),self.jy(y),-angle)
        if style: p+=' style="'+style+'" '
        p+='>\n'
        p+=text+'\n'
        p+='</text>\n'
        self.svg.write(p)

#sector with center at user (x,y), but radius r1 and r2 are in pts:
    def sector(self,x,y,r1,r2,a1,a2,**k):
        style=k.pop('style',"")
        for key in k.keys(): style+=key.replace('_','-')+':'+str(k[key])+';'
        largecircle='0'
        if (a2<a1): a2,a1=a1,a2
        if abs(a2-a1)>180: largecircle='1'
        a1=pi*a1/180.
        a2=pi*a2/180.
        x11=r1*cos(a1)
        x21=r2*cos(a1)
        x12=r1*cos(a2)
        x22=r2*cos(a2)
        y11=r1*sin(a1)
        y21=r2*sin(a1)
        y12=r1*sin(a2)
        y22=r2*sin(a2)
        d=self.pathdata('M',x,y,'m',hires(x21),hires(-y21),'a',hires(r2),hires(r2),'0',largecircle+',0',hires(x22-x21),hires(-y22+y21),\
'l',hires(x12-x22),hires(-y12+y22),'a',hires(r1),hires(r1),'0',largecircle+',1',hires(x11-x12),hires(-y11+y12),'Z')
        self.path(d=d,style=style)

    def radial(self,x,y,r1,r2,a1,**k):
        style=k.pop('style',"")
        for key in k.keys(): style+=key.replace('_','-')+':'+str(k[key])+';'
        largecircle='0'
        a1=pi*a1/180.
        x11=r1*cos(a1)
        x21=r2*cos(a1)
        y11=r1*sin(a1)
        y21=r2*sin(a1)
        d=self.pathdata('M',x,y,'m',hires(x21),hires(-y21),'l',hires(x11-x21),hires(-y11+y21))
        self.path(d=d,style=style)

    def arc(self,x,y,r,a1,a2,**k):
        style=k.pop('style',"")
        for key in k.keys(): style+=key.replace('_','-')+':'+str(k[key])+';'
        largecircle='0'
        if (a2<a1): a2,a1=a1,a2
        if abs(a2-a1)>180: largecircle='1'
        a1=pi*a1/180.
        a2=pi*a2/180.
        x21=r*cos(a1)
        x22=r*cos(a2)
        y21=r*sin(a1)
        y22=r*sin(a2)
        d=self.pathdata('M',x,y,'m',hires(x21),hires(-y21),'a',hires(r),hires(r),'0',largecircle+',0',hires(x22-x21),hires(-y22+y21))
        self.path(d=d,style=style)

#COMPOSITE DRAWING
    def square(self,x,y,size,**k): #analog to circle, useful for plot symbol
        style=k.pop('style',"")
        for key in k.keys(): style+=key.replace('_','-')+':'+str(k[key])+';'
        self.group(style=style)
        i,j=hires(self.ix(x)),hires(self.jy(y))
        l=size*100
        self.rect2(i-l,j-l,i+l,j+l,style=style)
        self.group()

    def arrow(self,x1,y1,x2,y2,headsize,**k): #headsize is in pts
        style=k.pop('style',"")
        for key in k.keys(): style+=key.replace('_','-')+':'+str(k[key])+';'
        self.group(style=style)
        i1,j1,i2,j2=self.ix(x1),self.jy(y1),self.ix(x2),self.jy(y2)
        headsize=self.sx(headsize)
        r=sqrt((i2-i1)**2+(j2-j1)**2)
        u=(i2-i1)/r
        v=(j2-j1)/r
        ai=-.8*u-.6*v
        aj=.6*u-.8*v
        bi=-.8*u+.6*v
        bj=-.6*u-.8*v
        x2=hires(i2+.5*headsize*(ai+bi))
        y2=hires(j2+.5*headsize*(aj+bj))
        self.line(x1,y1,x2,y2)
        self.path('M',hires(i2),hires(j2),'L',hires(i2+headsize*ai),hires(j2+headsize*aj),\
        'L',hires(i2+headsize*bi),hires(j2+headsize*bj),'Z',stroke='none')
        self.group()

    def fatarrow(self,x1,y1,x2,y2,asize,**k): #asize is the half-width of the fat arrow
        style=k.pop('style',"")
        for key in k.keys(): style+=key.replace('_','-')+':'+str(k[key])+';'
        i1,j1,i2,j2=self.ix(x1),self.jy(y1),self.ix(x2),self.jy(y2)
        asize=self.sx(asize)
        r=sqrt((i2-i1)**2+(j2-j1)**2)
        u=asize*(i2-i1)/r
        v=asize*(j2-j1)/r
        polypoints=[hires(q) for q in [i1+v,j1-u,
        i2+v-u,j2-u-v, i2,j2, i2-v-u,j2+u-v, i1-v,j1+u]]
        self.poly(polypoints,style=style)

    def windbarb(self,x,y,s,a,h,**k):
        style=k.pop('style',"")
        for key in k.keys(): style+=key.replace('_','-')+':'+str(k[key])+';'
        transform= "translate(%8.2f,%8.2f) rotate(%8.2f) " % (self.ix(x),self.jy(y),a-90)
        self.group(style=style,transform=transform)
        i1,j1=self.ix(x),self.jy(y)
        a=0.
        i1=0.
        j1=0.
        d=.13*h
        f=.5*h
        if s>=2.50:
            p=[0,0,-h,0]
            self.draw([hires(z) for z in p ])
        else:
            self.circle(hires(i1),hires(j1),int(abs(d)),fill='none')
        w=-h+d
        if s<47.50 and s>=7.50: w=-h
        while s>=47.50:
#                       p=[w,0,w-d,f,w-d,0]
            p=[w,0,w-d,-f,w-d,0]
            self.poly([hires(z) for z in p])
            s=s-50.
            w=w+d
        while s>=7.50:
#                       p=[w,0,w-d,f]
            p=[w,0,w-d,-f]
            self.draw([hires(z) for z in p])
            s=s-10.
            w=w+d
        while s>=2.50:
#                       p=[w,0,w-.5*d,.5*f]
            p=[w,0,w-.5*d,-.5*f]
            self.draw([hires(z) for z in p])
            s=s-5.
            w=w+d
        self.group()
    def image(self,x,y,file,**k):
        p='<image x="%.2f" y="%.2f" xlink:href="%s" ' % (self.ix(x),self.jy(y),file)
        for key in k.keys(): p+=key.replace('_','-')+'="'+str(k[key])+'" '
        self.svg.write(p+'/>\n')

#AXES DRAWING
#If you don't use the defaults, you should call these using your user coordinates only,
#except for ticklen and pad, which can be passed as an integer
    def xaxis(self, y="", #where to intersect the y-axis
                    x1="", #smallest x
                    dx="", #increment for tick marks
                    x2="", #largest x
                    ticklen=10, #length of ticks, in pts
                    grid=False,
                    xticks=None,
                    pad=10, #padding for tick labels, usually fontsize
                    form='%5.1f'): #format string for numerical labels
#               self.rect2(self.leftmarg,self.topmarg,self.bbx-self.rightmarg,self.bby-self.botmarg,fill="yellow") #for testing
        if y=="": y=self.ymin
        if x1=="": x1=self.xmin
        if x2=="": x2=self.xmax
        if dx=="": dx=(self.xmax-self.xmin)*.1
        if xticks==None: xticks=[]
        y,x1,x2,dx=map(float,[y,x1,x2,dx])
        if grid:
            y2=float(self.ymax)
            self.line(x1,y2,x2,y2)
            ticklen=self.jy(y2)-self.jy(y)
        else:
            ticklen=self.sy(ticklen)
        self.line(x1,y,x2,y)
        if not xticks:
            x=x1
            while x < x2*1.00001: #make tick marks
                xticks.append(x)
                x=x+dx
        for x in xticks: #make tick marks
            if form: str=form % x
            self.path('M',x,y,'l',0,-ticklen)
            if form: self.text(x,y-1.5*pad/self.yscale,0,str,stroke_width=".3pt",text_anchor='middle')

    def yaxis(self, x="", #where to intersect the x-axis
                    y1="", #smallest y
                    dy="", #increment for tick marks
                    y2="", #largest y
                    ticklen=10, #length of ticks, in pts
                    grid=False,
                    yticks=None,
                    pad=10, #padding for tick labels, usually fontsize
                    form='%5.1f'): #format for numerical labels
        if x=="": x=self.xmin
        if y1=="": y1=self.ymin
        if y2=="": y2=self.ymax
        if dy=="": dy=(self.ymax-self.ymin)*.1
        if yticks==None: yticks=[]
        x,y1,y2,dy=map(float,[x,y1,y2,dy])
        self.line(x,y1,x,y2)
        if grid:
            x2=float(self.xmax)
            self.line(x2,y1,x2,y2)
            ticklen=self.ix(x2)-self.ix(x)
        else:
            ticklen=self.sx(ticklen)
        if not yticks:
            y=y1
            while y < y2*1.00001:
                yticks.append(y)
                y=y+dy
        for y in yticks: #render tick marks and labels
            if form: str=form % y
            self.path('M',x,y,'l',ticklen,0)
            if form: self.text(x-.5*pad/self.xscale,y-.5*pad/self.yscale,0,str,stroke_width=".3pt",text_anchor='end')


### some functions independent of svg_class

if pyvers<3: #long integers are hi-res svg coordinates
    def hires(x): #converts svg (pts) coordinates to hi-res coordinate type
        return long(100*x)
else: #Python version 3.0 no longer supports long integers
    def hires(x): #converts svg (pts) coordinates to hi-res coordinate type
        return(fractions.Fraction(int(x*100),100))

#following is from
# http://www.ubookcase.com/book/Oreilly/Python.Cookbook.2nd.edition/0596007973/pythoncook2-chp-4-sect-6.html
# changed name flatten -> flatten to avoid namespace conflicts
#-----
def list_or_tuple(x):
    return isinstance(x, (list, tuple))
def flattn(sequence, to_expand=list_or_tuple):
    for item in sequence:
        if to_expand(item):
            for subitem in flattn(item, to_expand):
                yield subitem
        else:
            yield item
#-----

def rgbstring(*colors):
    if colors:
        f=colors[0]
        if isinstance(f,list) or isinstance(f,tuple):
            r,g,b=f
        elif len(colors)==3: r,g,b=colors
        else: r,g,b=colors[0],colors[0],colors[0]
    else:
        r,g,b=0,0,0
    if isinstance(r,float): r=255.*r
    if isinstance(g,float): g=255.*g
    if isinstance(b,float): b=255.*b
    return "rgb(%d,%d,%d)" % (r,g,b)

def stylestring(**k):
    s=""
    for key in k.keys():
        s+=key.replace('_','-')+':'+str(k[key])+';'
    return s

def SVGtest():
    import simpleSVG
    sys.stdout.write("A sample plot will be output as testSVG.svg\n")
    a=simpleSVG.svg_class(fname='testSVG.svg',bbx=600,bby=600) #override defaults for bbx and bby
    a.scale() #uses default scaling of coordinates (x=0. to x=1.0, y=0. to y=1.0)
    a.group(fill='black')#otherwise fonts are hollow
    a.yaxis()
    a.xaxis(dx=.2,form='%9.2e')
    a.group()
    mypath=a.pathdata('M',[150,400],'l',(50,50),'l',-50,50,'l',-50,-50,'l',50,-50,'Z') #optional use of [] and ()
    mystyle=stylestring(stroke="olive",fill="#49bab6",stroke_width=10) #two ways to specify colors; note '_' replaces '-' in SVG parameters
    a.path(d=mypath,style=mystyle) # render the path
    color1='rgb(100,150,200)' #third way to define color
    color2=rgbstring(.6,.7,200) #fourth way, real numbers will be multiplied by 255
    a.path('M',200,300,'l',50,50,'l',-50,50,'l',-50,-50,'l',50,-50,'Z',
            fill=color1,stroke=color2,stroke_width=5) # make path from positional arguements, make a style string from keyword arguments
    # if style= is passed, it will prepend  the style string made from keyword arguments:
    a.circle(.5,.3,20,style=mystyle,stroke='none')
    a.line(.5,.5,.4,.5)
    a.group(stroke_width=5) #apply this style to all items in the group
    a.line(.5,.5,.4,.6)
    a.line(300,simpleSVG.hires(300.23),.5,.6,stroke="lime") #demonstates using a hi-res coordinate
#       a.line(300,30023L,.5,.6,stroke="lime") # long integers (*100)  for hi-res coordinate are deprecated
    a.line(300,300,.5,.6,stroke="lime") #same central starting point, specified two ways in SVG coords
    a.path('M',300,300,'l',.1,.1,stroke="red",stroke_dasharray='3,2') #a line is easily made from path too
    a.fatarrow(.5,.5,.7,.5,10,fill='green',stroke='none') #arrow is like line, but with a headsize
    a.arrow(.5,.5,.7,.4,10,stroke_width=3,stroke='maroon',fill='black') #fill is for the head
    a.group()
    a.path('M',.7,.1,'l',.1,.1,.0,.1,-.1,.1,'Z',fill='gray',stroke='none') #path closed with 'Z ' makes polygon
    a.poly(.9,.1,1.,.2,1.,.3,.9,.4,fill='silver',stroke='none') #same poly as above, shifted.  Must use abs. coords.
    a.draw(.9,.1,1.,.2,1.,.3,.9,.4,stroke_width=3) #draw is similar to poly, but not closed
    a.arc(.8,.65,30,20,180,stroke='brown',stroke_width=10) #arc has radius 30, spans angle 20 to 180
    a.arc(.8,.65,60,20,245,stroke='purple',stroke_width=15) #arc had radius 60, spans angle 20 to 245
    a.radial(.8,.65,60,80,132.5,stroke='purple',stroke_width=15) #draw radial from radius of 60 to 80, at angle 132.5
    a.sector(.7,.85,30,100,10,45,fill='red',stroke='black') #sector has radii 30 and 100, spans angle 10 to 45
    a.rect(.7,.8,.35,.25,fill='none',stroke='aqua',stroke_width=3) #specify with width and height
    a.rect2(.72,.82,1.03,1.03,fill='none',stroke='yellow',stroke_width=5) #specify with two opposite vertices
    a.text(.2,.1,0,'hello',font_size="60pt",fill="lime")
    a.text(.5,.3,60,'again',font_size="48pt",text_anchor='middle') #rotate text by 60 degrees, place middle of text at x,y
    a.group(fill='black')
    a.windbarb(.05,.95,0,40,50,stroke_width=1) #x,y,speed,dir,size
    a.windbarb(.10,.90,7,30,50,stroke_width=1)
    a.windbarb(.15,.85,47,20,50,stroke_width=1)
    a.windbarb(.20,.80,107,10,80,stroke_width=1)
    a.group()
    a.group(clip_path=r'url(#marginmask)')
    a.text(.5,.85,60,'clipped',font_size="24pt",text_anchor='left') #demonstrates clipping
    a.group()
    a.text(.35,.80,60,' not clipped',font_size="24pt",text_anchor='left')
    a.close()
    a.display()

if __name__=='__main__':
    SVGtest()
