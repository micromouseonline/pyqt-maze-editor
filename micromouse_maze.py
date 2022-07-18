from vpython import *
#GlowScript 3.0 VPython

##3D Micromouse maze
#Derek Hall 2020 www.micromouse.me.uk   youtube.com/micromouse

#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the
#  "Software"), to deal in the Software without restriction, including
#  without l> imitation the rights to use, copy, modify, merge, publish,
#  distribute, sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so, subject to
#  the following conditions:
# 
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
# 
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

##to change the maze, manipulate the mazemap list then call loadMaze to update the 3D object
##the format used is a standard MicroMouse binary maze file explained here
##https://github.com/micromouseonline/micromouse_maze_tool
##
##Remove walls by clicking on them, add walls by clicking on the darker gray strips on the base
##Press browse button to load maze files
##Press shift and left click to pan

##
##VPYTHON can be downloaded here
##https://vpython.org/index.html


##create maze   Add parameter type to all maze elements
##type= bace
##      post
##      wall
##      center
##      start
##
##wall is index to wall list [wall][0=wall,1=red top]

##from vpython import *
##from playsound import playsound

mazemap=[
 0x0E, 0x0A, 0x08, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x09,
 0x0C, 0x0A, 0x02, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x09, 0x05,
 0x05, 0x0C, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x08, 0x0A, 0x09, 0x05, 0x05,
 0x05, 0x05, 0x0D, 0x0C, 0x0A, 0x09, 0x0E, 0x09, 0x0C, 0x0A, 0x09, 0x05, 0x0C, 0x01, 0x05, 0x05,
 0x05, 0x05, 0x04, 0x01, 0x0E, 0x02, 0x09, 0x04, 0x03, 0x0E, 0x00, 0x01, 0x05, 0x05, 0x05, 0x05,
 0x05, 0x05, 0x05, 0x06, 0x0B, 0x0E, 0x02, 0x02, 0x0A, 0x0B, 0x07, 0x06, 0x03, 0x05, 0x05, 0x05,
 0x05, 0x05, 0x05, 0x0C, 0x08, 0x0B, 0x0C, 0x08, 0x0A, 0x09, 0x0C, 0x09, 0x0C, 0x01, 0x05, 0x05,
 0x05, 0x05, 0x05, 0x05, 0x06, 0x09, 0x05, 0x04, 0x09, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
 0x05, 0x05, 0x05, 0x04, 0x09, 0x06, 0x01, 0x06, 0x03, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05, 0x05,
 0x05, 0x05, 0x05, 0x07, 0x06, 0x09, 0x06, 0x0A, 0x0A, 0x03, 0x05, 0x06, 0x03, 0x05, 0x05, 0x05,
 0x05, 0x05, 0x04, 0x0A, 0x0A, 0x03, 0x0E, 0x08, 0x0A, 0x0A, 0x02, 0x0A, 0x0B, 0x05, 0x05, 0x05,
 0x05, 0x05, 0x06, 0x09, 0x0D, 0x0E, 0x08, 0x02, 0x0A, 0x0A, 0x0A, 0x0A, 0x09, 0x05, 0x05, 0x05,
 0x05, 0x05, 0x0C, 0x03, 0x05, 0x0C, 0x03, 0x0C, 0x0A, 0x0A, 0x0A, 0x0A, 0x03, 0x05, 0x05, 0x05,
 0x05, 0x05, 0x06, 0x09, 0x04, 0x03, 0x0C, 0x03, 0x0C, 0x09, 0x0C, 0x0A, 0x09, 0x05, 0x05, 0x05,
 0x05, 0x06, 0x0A, 0x02, 0x03, 0x0E, 0x02, 0x0A, 0x03, 0x06, 0x03, 0x0E, 0x01, 0x05, 0x05, 0x05,
 0x06, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x02, 0x02, 0x02, 0x03,
]


def createMaze(walls,x,y): ##Create maze with all walls
    walls.clear()
    scene.axis=vector(0,-1,-1)

    mazeBace=box(color=color.gray(.3),length=y*180+150,width=x*180+150,height=20,pos=vector(0,-35,0),type="bace") ##maze bace

    b=-x/2
    while b<x/2+1:
        a=-y/2-1
        while a<y/2:
            if a>-y/2-1:
                wall=(box(pos=vector(a*180+90,0,b*180),length=168,width=12,height=50,type="wall",dire="h",wall=len(walls))) ##horizontal wall
                top=(box(color=color.red,pos=vector(a*180+90,25,b*180),length=168,width=12,height=.5,type="wall",wall=len(walls))) ##horizontal  red top
                walls.append([wall,top])

            if b<x/2:
                wall=(box(pos=vector(a*180+180,0,b*180+90),length=12,width=168,height=50,type="wall",dire="v",wall=len(walls)))  ##vertical wall
                top=(box(color=color.red,pos=vector(a*180+180,25,b*180+90),length=12,width=168,height=.5,type="wall",wall=len(walls)))  ##vertitcal red top
                walls.append([wall,top])

            box(pos=vector(a*180+180,0,b*180),length=11,width=11,height=50,type="post") ##post
            box(color=color.red,pos=vector(a*180+180,25,b*180),length=11,width=11,height=.5,type="post") ##post red top
            a=a+1
        b=b+1

    t=box(color=color.gray(.4),length=347,height=.5,width=347,type="center",pos=walls[int((x*2+1)*(y/2-1)+x)][0].pos) ##add gray center
    
    t.pos.z=t.pos.z+180/2
    t.pos.y=-24

    s=box(color=color.green,length=168,height=.5,width=168,type="start",pos=walls[0][0].pos) ##add green start
    s.pos.x=s.pos.x+180/2
    s.pos.y=-25


## called on mouse click
def mouseCallback(cb):

    obj=scene.mouse.pick
    if obj!=None:
        print ("You clicked on a",obj.type)
        if obj.type=="wall":
            print(obj.wall)
            #playsound('doortrek2.wav',False)
            if wall[obj.wall][0].visible==True:
                for t in range(25,-26,-5):
                    rate(50)
                    wall[obj.wall][1].pos.y=t
                    wall[obj.wall][0].pos.y=t-25
                wall[obj.wall][1].color=color.gray(.4)
                wall[obj.wall][0].visible=False
            else:
                wall[obj.wall][1].color=color.red
                wall[obj.wall][0].pos.y=-50
                wall[obj.wall][0].visible=True
                for t in range(-25,26,5):
                    rate(50)
                    wall[obj.wall][1].pos.y=t
                    wall[obj.wall][0].pos.y=t-25

def keyboardCallback(cb):
    ##if(cb.key=="L" | cb.key=="l"):
    print(cb.key)


def loadMaze(walls,mazemap): ##load maze from mazemap, create maze must be called first as this will just lower walls
    #print("loadMaze")
    cell=0
    for i in range(len(walls)):

        if i%33>0 and cell<256:
            ##print(i,cell,mod,hex(mazemap[cell]),wall[i][0].width)
            
            if (wall[i][0].dire=="v" and not(mazemap[cell] & 4) or (wall[i][0].dire=="h" and not(mazemap[cell] & 8))):     ##Wall missing             
                wall[i][1].pos.y=-25
                wall[i][0].pos.y=1
                wall[i][1].color=color.gray(.4)
                wall[i][0].visible=False
            else:                                             ##wall present       
                wall[i][1].pos.y=25
                wall[i][0].pos.y=0
                wall[i][1].color=color.red
                wall[i][0].visible=True
                
            if wall[i][0].width==12:
                cell=cell+1


def listMaze(walls):
    print(len(walls))
    for i in range(len(walls)):
        print ("cell=% mod=%",int(walls[i][0].wall/2)-int(walls[i][0].wall/32),walls[i][0].wall%32)


##start of program
wall=[] #[index to wall object][0=wall,1=top]

createMaze(wall,16,16)
##listMaze(wall)
loadMaze(wall,mazemap)

scene.bind('click',mouseCallback)
scene.bind('keyup',keyboardCallback)

##create mouse object
m1=box(color=color.blue,height=.8,length=100,width=75,axis=vector(0,0,1),pos=vector(0,-7,0))                   ##mouse bace
m2=cylinder(color=color.black,radius=12.5,length=10,pos=vector(28,0,0))                     ##left wheel
m3=cylinder(color=color.black,radius=12.5,length=10,pos=vector(-28,0,0),axis=vector(-1,0,0))##right wheel
m4=cone(color=color.red,radius=12,length=122,pos=vector(-150,8,-15),axis=vector(1,0,0),opacity=.3)  ##ls
m5=cone(color=color.red,radius=12,length=122,pos=vector(150,8,-15),axis=vector(-1,0,0),opacity=.2)  ##rs
m6=cone(color=color.red,radius=12,length=122,pos=vector(-40,8,-145),axis=vector(.1,0,1),opacity=.2)  ##lf
m7=cone(color=color.red,radius=12,length=122,pos=vector(40,8,-145),axis=vector(-.1,0,1),opacity=.2)   ##rf
m8=cone(color=color.red,radius=12,length=122,pos=vector(-100,8,-120),axis=vector(1,0,.8),opacity=.2)  ##ld
m9=cone(color=color.red,radius=12,length=122,pos=vector(100,8,-120),axis=vector(-1,0,.8),opacity=.2)  ##rd
m10=cone(color=color.gray(.3),radius=12,length=122,pos=vector(0,8,145),axis=vector(0,0,-1),opacity=0)  ##fake back
m=compound([m1,m2,m3,m4,m5,m6,m7,m8,m9,m10],type="mouse",texture="https://i.imgur.com/OtPL2KO.jpg")
m.axis=vector(1,0,0)
m.pos.x=-180/2
m.pos.z=180/2
m.pos.y=-8.5

print ("To load Micromouse Maze file (.MAZ format)press the button below")
print ("get .MAZ files here https://github.com/micromouseonline/micromouse_maze_tool/tree/master/mazefiles/binary")
print ("youtube.com/micromouse")
while True:
    f = read_local_file()
    print(f.name) # The file name
    #print(f.size) # File size in bytes
    #print(f.type) # What kind of file
    #print(f.date) # Creation date if available
    if (f.size == 256):         ##maze files are always 256 bytes
        for cell in range(0,255):
            ##print(hex(ord(f.text[cell])))
            mazemap[cell]=ord(f.text[cell])
        loadMaze(wall,mazemap)


#while True:
#    sleep(.03)
#    m.rotate(angle=radians(1),axis=vector(0,1,0))


