import pygame
import csv
import random
import os.path
from collections import deque

pygame.init()
pygame.font.init()

clock = pygame.time.Clock()
FPS = 60
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800

tile_size = SCREEN_HEIGHT/16

ROWS = 16
MAX_COLS = 300
SCREENMOVEMARGIN = 3

#Controlls
C_LEFT = pygame.K_a
C_RIGHT = pygame.K_d
C_JUMP  = pygame.K_w
C_DASH1 = pygame.K_SPACE
C_DASH2 = pygame.K_LSHIFT
C_SNEAK = pygame.K_s

INT_SIZE = 60
SPEED = 1
DASH_SPEED = 30
DASH_LOSS = 2
JUMP_HEIGHT = 15
DOUBLEJUMP_LOSS = 1
GRAVITY = 1
FRICTION = 1.1
MIN_SIZE = 200
RESPAWN_TIME = 2

#(Texture_Pack,Max_Colums,)
Level_Dat = [
    (0,270,1,'WHITE',0.05,pygame.mixer.Sound(r'assets\sounds\music\polar.mp3')),
    (0,370,1,'WHITE',0.05,pygame.mixer.Sound(r'assets\sounds\music\polar.mp3')),
    (0,300,1,'WHITE',0.07,pygame.mixer.Sound(r'assets\sounds\music\polar.mp3')),
    (1,300,2,'forestgreen',0.02,pygame.mixer.Sound(r'assets\sounds\music\woods.mp3')),
    (1,380,2,'forestgreen',0.02,pygame.mixer.Sound(r'assets\sounds\music\woods.mp3')),
    (1,350,2,'forestgreen',0.02,pygame.mixer.Sound(r'assets\sounds\music\woods.mp3')),
    (2,320,3,(228,210,175),0.1,pygame.mixer.Sound(r'assets\sounds\music\beach.mp3')),
    (2,362,3,(228,210,175),0.1,pygame.mixer.Sound(r'assets\sounds\music\beach.mp3')),
    (2,300,3,(228,210,175),0.1,pygame.mixer.Sound(r'assets\sounds\music\beach.mp3')),
    (3,350,4,'GREY30',0.02,pygame.mixer.Sound(r'assets\sounds\music\lava.mp3'))
]

Damage_Dat = [
{
    47:(1/30,(0.2,4,'RED',3,0,-2,2,1,2))
},
{
    40:(1/2,(0.4,4,'White',5,0,-2,2,1,2))
},
{
    69:(1,(0.5,8,'RED',5,0,-2,2,1,2)),
    73:(1,(0.4,4,'GREY30',3,0,-3,2,1,1))
},
{
    0:(1/2,(0.1,10,'ORANGERED',8,0,-2,2,1,2)),
    2:(2,(0.1,4,'ORANGERED',8,0,-2,2,1,2)),
    3:(2,(0.1,4,'ORANGERED',8,0,-2,2,1,2)),
    4:(2,(0.1,4,'ORANGERED',8,0,-2,2,1,2))
},
]

Gif_Dat = [
    'Arctic',
    'Woods',
    'Beach',
    'This is not an error'
]

pygame.display.set_icon(pygame.image.load(r'assets/img/cup.png')) 
pygame.display.set_caption("The Perfect Drink")
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

font = pygame.font.Font(r'assets/img/Font.ttf',int(SCREEN_WIDTH/50))

path = 'Data.txt'

if not os.path.isfile(path):
    with open(path,'w') as file:
        file.write('0')

class World():
    def __init__(self,dat,Texturepack,Id):
        self.Id = Id
        self.dat = dat
        self.Texturepack = Texturepack
        
        self.tiles_img = []
        self.Water_List = []

        try:
            for x in range(100):
                img = pygame.image.load(f'assets/img/tiles{self.Texturepack}/{x}.png')
                self.tiles_img.append(img)
                
        except FileNotFoundError:
            TILE_TYPES = len(self.tiles_img)
            self.tiles_img = []
            for x in range(TILE_TYPES):
                img = pygame.image.load(f'assets/img/tiles{self.Texturepack}/{x}.png').convert_alpha()
                img = pygame.transform.scale(img, (tile_size, tile_size))
                self.tiles_img.append(img)

        self.extra_list = []
        try:
            for x in range(100):
                img = pygame.image.load(f'assets/img/extras{self.Texturepack}/{x}.png')
                self.extra_list.append(img)
				
        except FileNotFoundError:
            ExtraTYPES = len(self.extra_list)
            self.extra_list = []
            for x in range(ExtraTYPES):
                img = pygame.image.load(f'assets/img/extras{self.Texturepack}/{x}.png').convert_alpha()
                self.extra_list.append(img)

        self.Scroll = 100
        self.Spawnpoint = (500,100,self.Scroll)
        self.active_Spawnpoint = pygame.Rect(0,0,0,0)

        self.Tile_List = []
        self.Shade_List = []
        self.Spawnpoint_List = []
        self.Damage_List = []

        for ir,row in enumerate(self.dat):
            for it,tile in enumerate(row):
                if str(tile)[len(str(tile))-1][0][0] == 's':
                    self.Shade_List.append(get_shade(it,ir,self.Scroll))
                elif str(tile[0])[0] == 's':
                    self.Shade_List.append(get_shade(it,ir,self.Scroll))

        for ir, row in enumerate(self.dat):
            for it, tile in enumerate(row):
                deg = 0
                if str(tile)[len(str(tile))-1] == '&':
                    if str(tile)[len(str(tile))-2] == '%':
                        tile = str(tile).split('&')[0]
                    
                    else:tile = str(tile).split('&')[0]
                
                if str(tile)[len(str(tile))-1] == '.':
                    tile = str(tile)[:-1]
                    deg += 90
                    
                    if str(tile)[len(str(tile))-1] == '.':
                        tile = str(tile)[:-1]
                        deg += 90
                        if str(tile)[len(str(tile))-1] == '.':
                            tile = str(tile)[:-1]
                            deg += 90

                if str(tile)[0] == 's':
                    self.Tile_List.append((pygame.Rect(it*tile_size-self.Scroll,ir*tile_size,tile_size,tile_size),(pygame.mask.from_surface(pygame.transform.rotate(self.tiles_img[int(tile[1:])],deg))),tile,it))
                
                elif int(tile) > -1:
                    if int(tile) in Damage_Dat[self.Texturepack]:
                        self.Damage_List.append((pygame.Rect(it*tile_size-self.Scroll,ir*tile_size,tile_size,tile_size),(pygame.mask.from_surface(pygame.transform.rotate(self.tiles_img[int(tile)],deg))),tile,it))
                    self.Tile_List.append((pygame.Rect(it*tile_size-self.Scroll,ir*tile_size,tile_size,tile_size),(pygame.mask.from_surface(pygame.transform.rotate(self.tiles_img[int(tile)],deg))),tile,it))

        for ir,row in enumerate(self.dat):
            for it,tile in enumerate(row):
                if str(tile)[len(str(tile))-1] == '&':
                    if str(tile)[len(str(tile))-2] == '%':
                        tile = str(tile).split('&')
                        tile[1] = str(tile[1][:1])

                        self.Spawnpoint_List.append((pygame.Rect(it*tile_size-self.Scroll+20,ir*tile_size,self.extra_list[int(tile[1])].get_width(),self.extra_list[int(tile[1])].get_height()),it))
				
                    else:tile = str(tile).split('&')

                    if str(tile[0])[0] == 's':
                        self.Tile_List.append((pygame.Rect(it*tile_size-self.Scroll,ir*tile_size,tile_size,tile_size),(pygame.mask.from_surface(pygame.transform.rotate(self.tiles_img[int(tile[1:])],deg))),tile,it))

                    elif int(tile[0]) > -1:
                        self.Tile_List.append((pygame.Rect(it*tile_size-self.Scroll,ir*tile_size,tile_size,tile_size),(pygame.mask.from_surface(pygame.transform.rotate(self.tiles_img[int(tile)],deg))),tile,it))

    def update(self):
        for Shade in self.Shade_List:
            Shade[0].x = Shade[2]*tile_size-self.Scroll+tile_size-150
                    
        for Tile in self.Tile_List:
            Tile[0].x = Tile[3]*tile_size-self.Scroll
        
        for Spawnpoint in self.Spawnpoint_List:
            Spawnpoint[0].x = Spawnpoint[1]*tile_size-self.Scroll+20

        for Tile in self.Damage_List:
            Tile[0].x = Tile[3]*tile_size-self.Scroll

    def draw(self,surface):
        for ir,row in enumerate(self.dat):
            for it,tile in enumerate(row):
                if str(tile[0])[0] == 's' or str(tile)[len(str(tile))-1][0][0] == 's':
                    if self.Scroll+SCREEN_WIDTH+200 > it*tile_size and self.Scroll-(SCREEN_WIDTH+200) < it*tile_size:
                        draw_shade(surface,it,ir,self.Scroll)
        
        for tile in self.Damage_List:
            
            dat = Damage_Dat[self.Texturepack][int(tile[2])][1]
            spawn_Particle(tile[0].x+tile[0].width/2+self.Scroll,tile[0].y+tile[0].height,dat[0],dat[1],dat[2],dat[3],dat[4],dat[5],dat[6],dat[7],dat[8])

        update_Particle2(Playscreen,player.Level.Scroll)

        for ir, row in enumerate(self.dat):
            for it, tile in enumerate(row):
                deg = 0
                if str(tile)[len(str(tile))-1] == '&':
                    if str(tile)[len(str(tile))-2] == '%':
                        tile = str(tile).split('&')[0]
                
                    else:tile = str(tile).split('&')[0]
                
                if str(tile)[len(str(tile))-1] == '.':
                    tile = str(tile)[:-1]
                    deg += 90
                    if str(tile)[len(str(tile))-1] == '.':
                        tile = str(tile)[:-1]
                        deg += 90
                        if str(tile)[len(str(tile))-1] == '.':
                            tile = str(tile)[:-1]
                            deg += 90
                
                if str(tile)[0] == 's':
                    if self.Scroll+SCREEN_WIDTH+200 > it*tile_size and self.Scroll-(SCREEN_WIDTH+200) < it*tile_size:
                        surface.blit(pygame.transform.rotate(self.tiles_img[int(tile[1:])],deg), (it * tile_size - self.Scroll, ir * tile_size))
                
                elif int(tile) > -1:
                        
                    if self.Scroll+SCREEN_WIDTH+200 > it*tile_size and self.Scroll-(SCREEN_WIDTH+200) < it*tile_size:
                        surface.blit(pygame.transform.rotate(self.tiles_img[int(tile)],deg), (it * tile_size - self.Scroll, ir * tile_size))

        for ir,row in enumerate(self.dat):
            for it,tile in enumerate(row):
                if str(tile)[len(str(tile))-1] == '&':
                    if str(tile)[len(str(tile))-2] == '%':
                        tile = str(tile).split('&')
                        tile[1] = str(tile[1][:1])
				
                    else:tile = str(tile).split('&')
 
                    if str(tile[0])[0] == 's':
                        if self.Scroll+SCREEN_WIDTH+200 > it*tile_size and self.Scroll-(SCREEN_WIDTH+200) < it*tile_size:
                            surface.blit(pygame.transform.rotate(self.tiles_img[int(tile[1:])],deg), (it * tile_size - self.Scroll, ir * tile_size))

                    elif int(tile[0]) > -1:
                        if self.Scroll+SCREEN_WIDTH+200 > it*tile_size and self.Scroll-(SCREEN_WIDTH+200) < it*tile_size:
                            surface.blit(pygame.transform.rotate(self.tiles_img[int(tile)],deg), (it * tile_size - self.Scroll, ir * tile_size))

                    if self.Spawnpoint[0]+self.Spawnpoint[2] == it * tile_size+20:
                        surface.blit(self.extra_list[int(tile[1])+1], (it * tile_size - self.Scroll, ir * tile_size))
                        self.active_Spawnpoint = pygame.Rect((it * tile_size - self.Scroll, ir * tile_size,self.extra_list[int(tile[1])+1].get_width(),self.extra_list[int(tile[1])+1].get_height()))
                        spawn_Particle(it * tile_size+self.extra_list[int(tile[1])+1].get_width()/6,ir * tile_size+self.extra_list[int(tile[1])+1].get_height()/3,0.4,1,random.choice(['Snow1','Lightblue1']),4,1.5,0,1,3,1)
                        spawn_Particle(it * tile_size+self.extra_list[int(tile[1])+1].get_width()/6,ir * tile_size+self.extra_list[int(tile[1])+1].get_height()/3*2,0.4,1,random.choice(['Snow1','Lightblue1']),4,1.5,0,1,3,1)

                    else:
                        if self.Scroll+SCREEN_WIDTH+200 > it*tile_size and self.Scroll-(SCREEN_WIDTH+200) < it*tile_size:
                            surface.blit(self.extra_list[int(tile[1])], (it * tile_size - self.Scroll, ir * tile_size))

        for i,Water in enumerate(self.Water_List):
            if Water.update(self.Scroll):
                self.Water_List.pop(i)
            Water.draw(surface,self.Scroll)



class Player():
    def __init__(self,x,y,Scroll,Level):
        self.width = INT_SIZE
        self.height = INT_SIZE

        resize_Cube(self)

        self.Level = Level
        self.img = self.Faces['Idle']
        
        self.Spawnpoint = x,y,Scroll
        self.rect = self.img.get_rect(topleft=(self.Spawnpoint[0],self.Spawnpoint[1]))
        self.vely = 0
        self.velx = 0
        self.onfloor = False
        self.Jumped = False
        self.Dashed = False
        self.Doublejumped = False
        self.meltram = 0
        self.Respawntime = -1
        self.oldSneak = False
        
        self.sneaking = False
        self.sleeptimer = 10
        self.temperature = -2

    def update(self):
        
        keys = pygame.key.get_pressed()
        if keys[C_LEFT]:
            if keys[C_SNEAK]:
                self.velx += -SPEED/3
            else:
                self.velx += -SPEED

        if keys[C_RIGHT]:
            if keys[C_SNEAK]:
                self.velx += SPEED/3
            else:
                self.velx += SPEED

        if keys[C_JUMP] and not self.Jumped:
            if self.onfloor:
                if keys[C_SNEAK]:
                    self.vely = -JUMP_HEIGHT/2
                    self.Jumped = True
                    sound = pygame.mixer.Sound(r'assets/sounds/sfx/jump_1.wav')
                    sound.set_volume(0.3)
                    pygame.mixer.Channel(1).play(sound)
                else:
                    self.vely = -JUMP_HEIGHT
                    self.Jumped = True
                    sound = pygame.mixer.Sound(r'assets/sounds/sfx/jump_1.wav')
                    sound.set_volume(0.5)
                    pygame.mixer.Channel(1).play(sound)

            elif not self.onfloor and not self.Doublejumped:
                if keys[C_SNEAK]:
                    pass
                else:
                    self.vely = -JUMP_HEIGHT*1.2
                    self.melt(DOUBLEJUMP_LOSS)
                    self.Doublejumped = True
                    sound = pygame.mixer.Sound(r'assets/sounds/sfx/jump_1.wav')
                    sound.set_volume(0.5)
                    pygame.mixer.Channel(1).play(sound)

        elif not keys[C_JUMP]:
            self.Jumped = False

        if (keys[C_DASH1] or keys[C_DASH2]) and self.velx != 0 and not self.Dashed:
            if keys[C_SNEAK]:
                pass
            else:
                self.Dashed = True
                self.melt(DASH_LOSS)
                sound = pygame.mixer.Sound(r'assets/sounds/sfx/woosh.wav')
                sound.set_volume(0.5)
                pygame.mixer.Channel(1).play(sound)
                if self.velx > 0:
                    self.velx += DASH_SPEED
                    
                else:
                    self.velx -= DASH_SPEED

        elif (not keys[C_DASH1]) and (not keys[C_DASH2]):
            self.Dashed = False


        if self.velx > 0:
            self.velx /= FRICTION
        elif self.velx < 0:
            self.velx /= FRICTION
        if self.velx < 0.1 and self.velx > -0.1:
            self.velx = 0
        dx = round(self.velx)

    	#Gravity - I guess...
        if self.vely < JUMP_HEIGHT:
            self.vely += GRAVITY
        dy = self.vely

        self.onfloor = False
        
        for tile in self.Level.Tile_List:
            if tile[0].colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                if tile[1].overlap(pygame.mask.Mask((self.rect.width,self.rect.height),True),(self.rect.x+dx-tile[0].x,self.rect.y-tile[0].y)):

                    stepupheight = 0
                    for i in range(2):
                        stepupheight += 5
                        if not tile[1].overlap(pygame.mask.Mask((self.rect.width,self.rect.height),True),(self.rect.x+dx-tile[0].x,self.rect.y-stepupheight-tile[0].y)):
                            dy = -stepupheight
                            self.velx /= FRICTION*1.3
                            break

                    else:
                        if dx < 0:
                            dx = 0

                        elif dx > 0:
                            dx = 0
                        self.velx = 0

            if tile[0].colliderect(self.rect.x +dx, self.rect.y + dy, self.rect.width, self.rect.height):
                if tile[1].overlap(pygame.mask.Mask((self.rect.width,self.rect.height),True),(self.rect.x+dx-tile[0].x,self.rect.y+dy-tile[0].y)):

                    if self.vely < 0:
                        dy = 0

                    elif self.vely > 0:
                        dy = 0
                        self.onfloor = True
                        self.Doublejumped = False
                    
                    self.vely = 0

        for tile in self.Level.Damage_List:
            if tile[0].colliderect(self.rect.x +dx, self.rect.y + dy, self.rect.width, self.rect.height):
                    self.melt(Damage_Dat[self.Level.Texturepack][int(tile[2])][0])
                    self.temperature += Damage_Dat[self.Level.Texturepack][int(tile[2])][0]


        for Spawnpoint in self.Level.Spawnpoint_List:
             if Spawnpoint[0].colliderect(self.rect):
                self.Level.Spawnpoint = Spawnpoint[0].x,Spawnpoint[0].y,self.Level.Scroll
                self.Spawnpoint = Spawnpoint[0].x,Spawnpoint[0].y,self.Level.Scroll

        overwrite = False
        if self.sneaking:
            for tile in self.Level.Tile_List:
                if tile[0].colliderect(self.rect.x, self.rect.y-self.height*3/20, self.rect.width, self.height):
                    if tile[1].overlap(pygame.mask.Mask((self.rect.width,self.height),True),(self.rect.x-tile[0].x,(self.rect.y-self.height*3/20)-tile[0].y)):
                        overwrite = True

        if not overwrite:
            if keys[C_SNEAK] and not self.oldSneak:
                dy += self.height*3/20
                self.sneaking = True

            if not keys[C_SNEAK] and self.oldSneak:
                dy -= self.height*3/20
                self.sneaking = False

            self.oldSneak = keys[C_SNEAK]
        
        sleep = False
        if keys[C_LEFT]:
            if  self.sneaking:
                self.img = self.Faces['SneakL']
            else:
                if abs(self.velx) > 11:
                    self.img = self.Faces['DashL']
                elif self.vely < 0:
                    if self.Doublejumped:
                        self.img = self.Faces['Jump2L']
                    else:self.img = self.Faces['Jump1L']
                else:
                    self.img = self.Faces['WalkL']

        elif keys[C_RIGHT]:
            if  self.sneaking:
                self.img = self.Faces['SneakR']
            else:
                if abs(self.velx) > 11:
                    self.img = self.Faces['DashR']
                elif self.vely < 0:
                    if self.Doublejumped:
                        self.img = self.Faces['Jump2R']
                    else:self.img = self.Faces['Jump1R']
                else:
                    self.img = self.Faces['WalkR']

        else:
            if  self.sneaking:
                self.img = self.Faces['Sneak']
            else:
                if self.vely < 0:
                    if self.Doublejumped:
                        self.img = self.Faces['Jump2']
                    else:self.img = self.Faces['Jump1']
                else: 
                    if self.sleeptimer < time:
                        self.img = self.Faces['Sleep']
                        spawn_Particle(self.rect.x+self.rect.width/2,self.rect.y+self.rect.height/3*2,0.02,1,'Pink',8,-0.5,-0.5,0.08,0.08,3)
                    else: 
                        self.img = self.Faces['Idle']
                    sleep = True

        if sleep == False:
            self.sleeptimer = time + 5

        if self.Level.Scroll < Level_Dat[self.Level.Id][1]*44:
            if SCREEN_WIDTH/SCREENMOVEMARGIN > self.rect.x + dx or self.rect.x + dx > SCREEN_WIDTH/SCREENMOVEMARGIN*(SCREENMOVEMARGIN-1):
                self.Level.Scroll += dx
                dx = 0

            if (SCREEN_WIDTH/SCREENMOVEMARGIN)-10 > self.rect.x + dx:
                dx +=10
            
            if self.rect.x + dx > (SCREEN_WIDTH/SCREENMOVEMARGIN*(SCREENMOVEMARGIN-1))+10:
                dx -=10

        if self.sneaking:
            height = self.height*17/20
        else: height = self.height


        self.temperature += self.should_melt()

        crits = [2, 1, 0.02, 0.015, 0.01, 0.005]
        global thermoindex
        if self.temperature < 0:
            thermoindex = 5
        else:
            for i,crit in enumerate(crits):
                if self.temperature >= crit:
                    thermoindex = i
                    break
        self.temperature = 0

        self.rect = pygame.Rect(self.rect.x + dx,self.rect.y + dy,self.rect.width,height)

    def should_melt(self):
        if not self.Level.active_Spawnpoint.colliderect(self.rect):
            
            overlap = 0
            for shade in self.Level.Shade_List:
                if shade[0].colliderect(self.rect):
                    overlap += shade[1].overlap_area(pygame.mask.Mask((self.rect.width,self.rect.height),True),(self.rect.x-shade[0].x,self.rect.y-shade[0].y))

            if not self.rect.height*self.rect.width <= overlap*1.1:
                self.melt(SUNMELT)
                return SUNMELT
            else: return SUNMELT-SUNMELT/10
        
        else:
            x = self.rect.x - (INT_SIZE-self.rect.width)
            y = self.rect.y - (INT_SIZE-self.rect.height)
            self.width = INT_SIZE
            self.height = INT_SIZE

            resize_Cube(self)
            self.rect = self.img.get_rect(topleft=(x,y))
            return -1000

    def melt(self,amount):

        if amount+self.meltram >= 1 :
            amount += self.meltram
            self.meltram = 0
            self.width -= amount
            self.height -= amount
            x = self.rect.x + amount/4
            y = self.rect.y + amount/4
            
            resize_Cube(self)
            self.rect = self.img.get_rect(topleft=(x,y))

        else: self.meltram += amount

        if self.meltram % 0.02 == 0:
            self.Level.Water_List.append(Water(random.randint(self.rect.x,self.rect.x+self.rect.width),self.rect.y+self.rect.height,self.Level,self.Level.Scroll))

    def Deathcheck(self):
        if self.Respawntime == -1:
            if self.width*self.height <= MIN_SIZE :
                self.Respawntime = time + RESPAWN_TIME
                spawn_Particle(self.rect.x+self.Level.Scroll+self.width/2,self.rect.y+self.height/2,50,1,(random.randint(30,50),170,200),4,0,-0.5,5,5,1)
                sound = pygame.mixer.Sound(r'assets/sounds/sfx/explosion.wav')
                sound.set_volume(0.5)
                pygame.mixer.Channel(1).play(sound)
                return True
            
            if self.rect.y > SCREEN_HEIGHT:
                self.Respawntime = time + RESPAWN_TIME
                spawn_Particle(self.rect.x+self.Level.Scroll+self.width/2,self.rect.y+self.height/2,50,1,(random.randint(30,50),170,200),4,0,-1,5,5,1)
                sound = pygame.mixer.Sound(r'assets/sounds/sfx/explosion.wav')
                sound.set_volume(0.5)
                pygame.mixer.Channel(1).play(sound)
                return True

    def Respawn(self):
        self.Level.Scroll = self.Spawnpoint[2]
        self.__init__(self.Spawnpoint[0],self.Spawnpoint[1],self.Spawnpoint[2],self.Level)

    def Wincheck(self):
        if self.rect.x > SCREEN_WIDTH:
            gif = Gif(position=(0, 0), images=load_images(path=f'assets/img/{Gif_Dat[self.Level.Texturepack]}') )
            return True,gif
        else: return False,False
        
    def draw(self,surface):
        surface.blit(self.img,self.rect)

class Water():
    def __init__(self,x,y,Level,Scroll):
        self.img = pygame.surface.Surface((5,5))
        self.col = (random.randint(30,50),170,200)
        self.img.fill(self.col)
        self.rect = pygame.rect.Rect(x+Scroll,y,3,3)
        self.vely = 0
        self.Level = Level
        self.onfloor = False
        self.opacity = 255

    def update(self,Scroll):
        self.img.set_alpha(int(self.opacity))
        self.opacity -= 0.5
        if not self.onfloor:
            self.vely += GRAVITY/4
            dy = self.vely

            for tile in self.Level.Tile_List:
                if tile[0].colliderect(self.rect.x-Scroll, self.rect.y + dy, self.rect.width, self.rect.height):
                    area = tile[1].overlap_area(pygame.mask.Mask((self.rect.width,self.rect.height),True),(self.rect.x-tile[0].x-Scroll,self.rect.y-tile[0].y))
                    if area > 0:
                        
                        dy = self.rect.height+30-area
                        dy = 0
                        self.onfloor = True
                        break
                        
            self.rect.y += dy
            
            if self.rect.y > SCREEN_HEIGHT:
                return True
        if self.opacity < 10:
            return True

    def draw(self,surface,Scroll):
        surface.blit(self.img,(self.rect.x-Scroll,self.rect.y,self.rect.width,self.rect.height))

class Particle():
    def __init__(self,x,y,fade,col,size,speedx,speedy,devx,devy,despawn):
        self.x = x
        self.y = y

        self.fade = fade
        self.opacity = 255

        self.speedx = speedx
        self.speedy = speedy
        self.devx = devx
        self.devy = devy
        if despawn == False:
            self.despawn = 1000
        else: self.despawn = despawn

        self.img = pygame.Surface((size,size))
        self.img.fill(col)
        self.rect= self.img.get_rect(center=(self.x,self.y))

    def update(self):
        self.img.set_alpha(int(self.opacity))
        self.opacity -= self.fade
        self.despawn -= 1

        speedx_ = random.gauss(self.speedx,self.devx)
        speedy_ = random.gauss(self.speedy,self.devy)

        if abs(speedx_)>abs(speedy_):
            self.rect.x += speedx_
        if abs(speedx_)<abs(speedy_):
            self.rect.y += speedy_

        if self.opacity < 10 or self.despawn <= 0:
            return True
        
    def draw(self,surface,Scroll):
        surface.blit(self.img,(self.rect.x-Scroll,self.rect.y,self.rect.width,self.rect.height))

class Button():
    def __init__(self,cords, size, Text, col):
        self.width = size[0]
        self.height = size[1]
        self.col = col
        self.img = pygame.Surface((self.width,self.height))
        self.img.fill(col)
        try:
            self.Id = int(Text)
        except ValueError:pass
        self.Text = font.render(Text,False,'White')
        self.img.blit(self.Text,self.Text.get_rect(center=(self.width/2,self.height/2)))
        self.rect = self.img.get_rect(topleft = cords)
        self.clicked = False
        self.Hoverrect = (self.rect.x-5,self.rect.y-5,self.rect.width+10,self.rect.height+10)

    def draw(self, surface):
        global clicked
        action = False

        pos = pygame.mouse.get_pos()

        mouseclicks = pygame.mouse.get_pressed()
        if self.rect.collidepoint(pos):
            if mouseclicks[0] == True and clicked == False:
                pygame.draw.rect(surface,'GREEN',self.Hoverrect)
            else: pygame.draw.rect(surface,'WHITE',self.Hoverrect)

        else: pygame.draw.rect(surface,(50,50,50),self.Hoverrect)

        if self.rect.collidepoint(pos):
            if mouseclicks[0] == 1 and clicked == False:
                action = True
                clicked = True
                sound = pygame.mixer.Sound(r'assets/sounds/sfx/blipSelect_1.wav')
                sound.set_volume(0.5)
                pygame.mixer.Channel(1).play(sound)

            if mouseclicks[0] == 0:
                clicked = False

        surface.blit(self.img, self.rect)

        return action
    
class LevelButton(Button):
    def draw(self, surface,Latest_Level):
        global clicked
        action = False

        pos = pygame.mouse.get_pos()

        mouseclicks = pygame.mouse.get_pressed()
        if self.rect.collidepoint(pos):
            if mouseclicks[0] == True and Latest_Level >= self.Id and clicked == False:
                pygame.draw.rect(surface,'GREEN',self.Hoverrect)
            else: pygame.draw.rect(surface,'WHITE',self.Hoverrect)

        else: pygame.draw.rect(surface,(50,50,50),self.Hoverrect)

        surface.blit(self.img, self.rect)

        if Latest_Level >= self.Id:
            if self.rect.collidepoint(pos):
                if mouseclicks[0] == 1 and clicked == False:
                    action = True
                    clicked = True
                    sound = pygame.mixer.Sound(r'assets/sounds/sfx/blipSelect_1.wav')
                    sound.set_volume(0.5)
                    pygame.mixer.Channel(1).play(sound)

            if mouseclicks[0] == 0 and clicked == True:
                clicked = False
        else:
            surface.blit(pygame.transform.scale(pygame.image.load(r'assets/img/lock.png'),(self.rect.width/3,self.rect.height/2)),(self.rect.x+self.rect.width/4+self.rect.width/12,self.rect.y+self.rect.height/4.5))

        return action

class CreditText():
    def __init__(self,y,speed,size,Text,col):
        font = pygame.font.Font(r'assets/img/Font.ttf',int(SCREEN_WIDTH/size))
        self.speed = speed
        self.img = font.render(Text,False,col)
        self.rect = self.img.get_rect(center=(SCREEN_WIDTH/2,y+SCREEN_HEIGHT))

    def draw(self,surface):
        self.rect.y -= self.speed
        surface.blit(self.img, self.rect)

class Gif():

    def __init__(self, position, images):
        size = (135, 80)

        self.rect = pygame.Rect(position, size)
        self.images = images
        self.images_right = images
        self.images_left = [pygame.transform.flip(image, True, False) for image in images]
        self.index = 0
        self.image = images[self.index]

        self.animation_time = 0.1
        self.current_time = 0

        self.animation_frames = 6
        self.current_frame = 0

    def update(self, dt):

        self.current_time += dt
        if self.current_time >= self.animation_time:
            self.current_time = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]
            if self.index+1 == len(self.images):
                return True,self.image
            else:
                return False,False
        else: return False,False

class Tutorial_Banner():
    def __init__(self):
        self.img = pygame.image.load(r'assets/img/tutorial.png')
        
    def draw(self,surface,Scroll):
        opacity = -Scroll+355
        if opacity < 0:
            opacity = 0
        elif opacity > 255:
            opacity = 255
        self.img.set_alpha(opacity)
        surface.blit(self.img,(0,0,SCREEN_WIDTH,SCREEN_HEIGHT))  

class TypingArea:

    def __init__(self, text, area, font, fg_color, bk_color, wps=80):

        self.char_queue = deque(text)
        self.rect = area.copy()
        self.font = font
        self.fg_color = fg_color
        self.bk_color = bk_color

        self.size = area.size
        self.area_surface = pygame.Surface(self.size, flags=pygame.SRCALPHA)
        self.area_surface.fill(bk_color)

        self.wps = wps
        self.y = 10
        self.y_delta = self.font.size("M")[1]+10

        self.line = "" 
        self.next_time = time  
        self.dirty = 0  

    def _render_new_line(self):  
        self.y += self.y_delta  
        self.line = "" 
        if self.y + self.y_delta > self.size[1]: 
   
            self.area_surface.blit(self.area_surface, (0, -self.y_delta))
            self.y += -self.y_delta  
            
            pygame.draw.rect(self.area_surface, self.bk_color,
                             (0, self.y, self.size[0], self.size[1] - self.y))

    def _render_char(self, c): 
        if c == '\n':
            self._render_new_line()
        else:
            self.line += c 
            text = self.font.render(self.line, True, self.fg_color)
            self.area_surface.blit(text, (10, self.y))  

    def update(self):
        while self.char_queue and self.next_time <= time:
            self._render_char(self.char_queue.popleft()) 
            self.next_time += 1000
            
        self.next_time = time

    def draw(self, screen,Scroll):
        screen.blit(self.area_surface, (self.rect.x-Scroll,self.rect.y))  
        
class Thermometer():
    def __init__(self,x,y,size:tuple,value):
        
        self.images = [
            pygame.transform.scale(pygame.image.load(r'assets/img/thermo/thermo1.png'),(size)),
            pygame.transform.scale(pygame.image.load(r'assets/img/thermo/thermo2.png'),(size)),
            pygame.transform.scale(pygame.image.load(r'assets/img/thermo/thermo3.png'),(size)),
            pygame.transform.scale(pygame.image.load(r'assets/img/thermo/thermo4.png'),(size)),
            pygame.transform.scale(pygame.image.load(r'assets/img/thermo/thermo5.png'),(size)),
            pygame.transform.scale(pygame.image.load(r'assets/img/thermo/thermo6.png'),(size))
        ]
        self.images.reverse()
        self.img = self.images[value]
        self.rect = self.img.get_rect(topleft=(x,y))
        self.maxvalue = 5

    def draw(self,surface,value):
        if value < self.maxvalue:
            self.maxvalue = value
        if time % 1 <= 0.5:
            
            self.img = self.images[self.maxvalue]
            self.maxvalue = 10


        surface.blit(self.img,self.rect)

def resize_Cube(self):
    self.Faces = {
        'Idle'  :pygame.transform.scale(pygame.image.load(r'assets/img/player/IceCube.png'), (self.width,self.height)), 
        'WalkL' :pygame.transform.scale(pygame.image.load(r'assets/img/player/IceCubeWalkL.png'), (self.width,self.height)),
        'WalkR' :pygame.transform.scale(pygame.image.load(r'assets/img/player/IceCubeWalkR.png'), (self.width,self.height)),
        'Jump1' :pygame.transform.scale(pygame.image.load(r'assets/img/player/IceCubeJump1.png'), (self.width,self.height)),
        'Jump2' :pygame.transform.scale(pygame.image.load(r'assets/img/player/IceCubeJump2.png'), (self.width,self.height)),
        'Jump1L':pygame.transform.scale(pygame.image.load(r'assets/img/player/IceCubeJump1L.png'), (self.width,self.height)),
        'Jump2L':pygame.transform.scale(pygame.image.load(r'assets/img/player/IceCubeJump2L.png'), (self.width,self.height)),
        'Jump1R':pygame.transform.scale(pygame.image.load(r'assets/img/player/IceCubeJump1R.png'), (self.width,self.height)),  
        'Jump2R':pygame.transform.scale(pygame.image.load(r'assets/img/player/IceCubeJump2R.png'), (self.width,self.height)),
        'DashL' :pygame.transform.scale(pygame.image.load(r'assets/img/player/IceCubeDashL.png'), (self.width,self.height)),
        'DashR' :pygame.transform.scale(pygame.image.load(r'assets/img/player/IceCubeDashR.png'), (self.width,self.height)),
        'Sneak' :pygame.transform.scale(pygame.image.load(r'assets/img/player/IceCubeCrouch.png'), (self.width,self.height*17/20)),
        'SneakR':pygame.transform.scale(pygame.image.load(r'assets/img/player/IceCubeCrouchR.png'), (self.width,self.height*17/20)),
        'SneakL':pygame.transform.scale(pygame.image.load(r'assets/img/player/IceCubeCrouchL.png'), (self.width,self.height*17/20)),
        'Sleep':pygame.transform.scale(pygame.image.load(r'assets/img/player/IceCubeSleep.png'), (self.width,self.height))
        }

def spawn_Particle(x,y,amount,fade,col,size,speedx,speedy,devx,devy,where,despawn = False):
    if amount < 1:
        if random.random() < amount:
            amount = 1
        else: amount = 0
    
    for i in range(amount):
        
        direction = pygame.math.Vector2(random.uniform(-1,1), random.uniform(-1,1))
        direction = direction.normalize()
        if where == 1:
            Particles1.append(Particle(x,y,fade,col,size,speedx,speedy,devx,devy,despawn))
        elif where == 2:
            Particles2.append(Particle(x,y,fade,col,size,speedx,speedy,devx,devy,despawn))
        else:
            Particles3.append(Particle(x,y,fade,col,size,speedx,speedy,devx,devy,despawn))
    
def update_Particle1(surface,Scroll):
    for particle in Particles1:
        if particle.update():
            Particles1.remove(particle)
        particle.draw(surface,Scroll)

def update_Particle2(surface,Scroll):
    for particle in Particles2:
        if particle.update():
            Particles2.remove(particle)
        particle.draw(surface,Scroll)

def update_Particle3(surface):
    for particle in Particles3:
        if particle.update():
            Particles3.remove(particle)
        particle.draw(surface,0)

def load_World(level,max_cols):
    world_data = []
    for row in range(ROWS):
        r = [-1] * max_cols
        world_data.append(r)
    
    with open(f'assets/level{level}_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter = ',')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                world_data[x][y] = tile
    return world_data

def draw_shade(surface,x,y,Scroll):
    pygame.draw.polygon(surface, (100,100,100,10), [(x*tile_size-Scroll,y*tile_size+tile_size/2),(x*tile_size-Scroll+tile_size-1,y*tile_size+tile_size/2),(x*tile_size-Scroll+tile_size-150,y*tile_size+SCREEN_HEIGHT),(x*tile_size-Scroll-150,y*tile_size+SCREEN_HEIGHT)])

def get_shade(x,y,Scroll):
    img = pygame.surface.Surface((150,SCREEN_HEIGHT))
    img.set_colorkey('BLACK')
    pygame.draw.polygon(img, 'WHITE', [(100,tile_size/2),(100+tile_size-1,tile_size/2),(-50,SCREEN_HEIGHT*1.4),(tile_size-150,SCREEN_HEIGHT*1.4)])
    return pygame.rect.Rect(x*tile_size-Scroll+tile_size-150,y*tile_size+tile_size/2,150,SCREEN_HEIGHT),pygame.mask.from_surface(img),x

def load_images(path):

    images = []
    for file_name in os.listdir(path):
        image = pygame.image.load(path + os.sep + file_name).convert()
        image = pygame.transform.scale(image,(SCREEN_WIDTH,SCREEN_HEIGHT))
        images.append(image)
    return images


global time
time = 0

gamestate = 'Home'

Homescreen = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
Playscreen = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))

Start_Button = Button((SCREEN_WIDTH/2-SCREEN_WIDTH/8,SCREEN_HEIGHT/3),(SCREEN_WIDTH/4,SCREEN_HEIGHT/8),'Start','Brown')
Level_Button = Button((SCREEN_WIDTH/2-SCREEN_WIDTH/8,SCREEN_HEIGHT/2),(SCREEN_WIDTH/4,SCREEN_HEIGHT/8),'Levels','Brown')
Credits_Button = Button((SCREEN_WIDTH/2-SCREEN_WIDTH/8,SCREEN_HEIGHT/2+SCREEN_HEIGHT/6),(SCREEN_WIDTH/4,SCREEN_HEIGHT/8),'Credits','Brown')
Quit_Button = Button((SCREEN_WIDTH/2-SCREEN_WIDTH/12,SCREEN_HEIGHT/2+SCREEN_HEIGHT/3),(SCREEN_WIDTH/6,SCREEN_HEIGHT/8),'Quit','Brown')

Back_Button = Button((SCREEN_WIDTH/40,SCREEN_HEIGHT/2+SCREEN_HEIGHT/3),(SCREEN_WIDTH/8,SCREEN_HEIGHT/10),'Back','Brown')
LevelSelect_Buttons = []

Resume_Button = Button((SCREEN_WIDTH-SCREEN_WIDTH/4-SCREEN_WIDTH/6,SCREEN_HEIGHT/3*2),(SCREEN_WIDTH/6,SCREEN_HEIGHT/10),'Resume','Brown')
Home_Button = Button((SCREEN_WIDTH/4,SCREEN_HEIGHT/3*2),(SCREEN_WIDTH/6,SCREEN_HEIGHT/10),'Home','Brown')

Home2_Button = Button((SCREEN_WIDTH/2-SCREEN_WIDTH/12,SCREEN_HEIGHT/3*2),(SCREEN_WIDTH/6,SCREEN_HEIGHT/10),'Home','Brown')

Tutorial = Tutorial_Banner()
count = 0
for y in range(3):
    for x in range(3):
        LevelSelect_Buttons.append(LevelButton((SCREEN_WIDTH/4+x*SCREEN_WIDTH/5,SCREEN_HEIGHT/5+y*SCREEN_HEIGHT/5),(SCREEN_WIDTH/8,SCREEN_HEIGHT/8),str(count),'Brown'))
        count += 1

Select_Button = LevelButton((SCREEN_WIDTH/4+SCREEN_WIDTH/5,SCREEN_HEIGHT/2.5+SCREEN_HEIGHT/2.5),(SCREEN_WIDTH/8,SCREEN_HEIGHT/8),str(count),'Brown')

Bannerimg = pygame.transform.scale(pygame.image.load(r'assets\img\ThePerfectDrinkBanner.png'),(SCREEN_WIDTH/10*9,SCREEN_HEIGHT/4))

STORY="""                                                  
Ahoy there, young Ice Cube!                                                                                                              
Welcome to the frosty world of The Perfect Drink!                                                                                       
I see you're ready to embark on your chilly adventure.                                                                                 
Allow me, Grandpa Cube, to guide you through the basics.                                                                                
                                                    
First things first,                                                                                                      
your mission is to hop into your drink                                                          
before you melt away completely!                                                         
                                                    
Fear not, young one!                                                 
It's all about timing and precision.                                                 
You'll need to navigate through various obstacles and                                                                              
platforms to reach your cocktail. But remember,                                                                                  
time is of essence!                                                                                             
You're melting,                                                
and we don't want any ice cubes                                                 
splashing into the desert sands.                                                                                      
Try to stand in the shadows to dont melt.                                                                                     
                                                    
There is something else you should know, young Ice Cube!                                                                                               
There are some Fridges scattered around this place.                                                                                             
If it happens that you melt, you can continue from the Fridge.                                                                                               
Also before I forget, take this! Its an thermometer wich will                                                                                                      
indicate you how fast you are melting. Keep an eye on it.                                                                                           
But be careful! Some obstacles might make you melt faster.                                                                                                
                                                                        
Now, off you go.                                              
Your drink awaits, and time is ticking away!                        
Good luck on your frosty journey!                         
You have a big Adventure ahead of yourself!       """

messagex = 3300
area_rect = pygame.Rect(messagex, SCREEN_HEIGHT/3, 800, 100)
message = TypingArea(STORY, area_rect, pygame.font.Font(r'assets/img/Font.ttf',int(SCREEN_WIDTH/140)), 'BLACK', 'WHITE', wps=1)

with open('Data.txt','r') as file:
    Latest_Level = int(file.read(1))

clicked = False
pause = False

pygame.mixer.Channel(0).play(pygame.mixer.Sound(r'assets\sounds\music\main_menu.mp3'),loops=-1)
run = True
while run:

    pos = pygame.mouse.get_pos()

    clock.tick(FPS)
    time += 1/FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if gamestate == 'Game'or'Paused':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not pause:
                    pause = True
                    if gamestate == 'Game': gamestate = 'Paused'
                    else: gamestate = 'Game'
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    pause = False

    if gamestate == 'Home':
        Particles1 = []
        Particles2 = []
        Particles3 = []
        Homescreen.fill('Lightblue')

        if Start_Button.draw(Homescreen):

            with open('Data.txt','r') as file:
                Latest_Level = int(file.read(1))

            level = World(load_World(Latest_Level,Level_Dat[Latest_Level][1]),Level_Dat[Latest_Level][0],Latest_Level) 
            player = Player(500,300,100,level)
            
            SUNMELT = Level_Dat[level.Id][2]/200
            thermometer = Thermometer(00,20,(200,200),5-level.Texturepack)
            pygame.mixer.Channel(0).play(Level_Dat[level.Id][5],loops=-1)
            gamestate = 'Game'

        if Level_Button.draw(Homescreen):
            with open('Data.txt','r') as file:
                Latest_Level = int(file.read(1))
            gamestate = 'Level'

        if Credits_Button.draw(Homescreen):
            Credits =[  
            CreditText(10,1,30,'THE PERFECT DRINK','orangered'),
            CreditText(600,1.5,55,'by gabl18 and sir-lordmike','White'),
            CreditText(700,1.5,60,'made in one week for the','White'),
            CreditText(750,1.5,60,'Pygame Community Spring Jam 2024','White'),

            CreditText(850,1.5,60,'This was our first Jam and','lightblue4'),
            CreditText(900,1.5,60,'one of our first Pygame Games','lightblue4'),

            CreditText(1200,1,55,'Lead Programmer: Michael','White'),
            CreditText(1250,1,55,'Lead Artist: Gabriel','White'),

            CreditText(1400,1,55,'Special Thanks:','grey36'),
            CreditText(1450,1,60,'Felix','White'),
            CreditText(1500,1,60,'Ted-Klein-Bergman','White'),

            CreditText(1650,1,60,'for making some Assets','White'),
            CreditText(1700,1,60,'and helping with Cutscenes','White'),

            CreditText(1850,1,60,'Also Special thanks to the','lightblue4'),
            CreditText(1900,1,60,'Folks from the Pygame Discord','lightblue4'),
            CreditText(1950,1,60,'for making this possible','lightblue4'),

            CreditText(2100,1,55,'Not self made Assets:','grey36'),
            CreditText(2150,1,60,'quinquefive-font','White'),

            CreditText(2300,1,55,'The Guy who also exists:','grey36'),
            CreditText(2350,1,60,'Noah','White'),

            CreditText(2500,1,55,'Programms Used:','grey36'),
            CreditText(2550,1,70,'Paint.net','White'),
            CreditText(2600,1,70,'Photoshop','White'),
            CreditText(2650,1,70,'Bandlab','White'),
            CreditText(2700,1,70,'JSFXR','White'),
            CreditText(2750,1,70,'VSCode, Pyhton and Pygame','White'),
            CreditText(3000,0.7,55,'GEH SCHEIßEN!','orangered'),
            CreditText(3050,0.7,65,'and thanks for playing the Game','grey36'),

            CreditText(4200,1.5,60,'Bro why you waitin?','White'),

            CreditText(5000,1.5,60,'There is no more!','White'),

            CreditText(7000,1.5,60,'If you already wait,','White'),
            CreditText(7050,1.5,60,'donate us something!','White'),

            CreditText(9500,1.5,60,'Play our Games or Ice Cube','White'),
            CreditText(9550,1.5,60,'will never return','White'),

            CreditText(11000,1.5,60,'Thanks for waisting','White'),
            CreditText(11050,1.5,60,'your Time!','White')
            ]
            gamestate = 'Credits'

        if Quit_Button.draw(Homescreen):
            run = False

        Homescreen.blit(Bannerimg,(SCREEN_WIDTH/20,0))
        window.blit(Homescreen,(0,0))
        
    elif gamestate == 'Level':
        Homescreen.fill('Lightblue')

        if Back_Button.draw(Homescreen):
            gamestate = 'Home'

        for button in LevelSelect_Buttons:
            if button.draw(Homescreen,Latest_Level):
                if Latest_Level >= int(button.Id):
                    level = World(load_World(int(button.Id),Level_Dat[button.Id][1]),Level_Dat[int(button.Id)][0],button.Id) 
                    player = Player(500,300,100,level)
                    thermometer = Thermometer(00,20,(200,200),5-level.Texturepack)
                    pygame.mixer.Channel(0).play(Level_Dat[level.Id][5],loops=-1)
                    SUNMELT = Level_Dat[level.Id][2]/200 
                    gamestate = 'Game'                  

        if Latest_Level >= 9:
            if Select_Button.draw(Homescreen,Latest_Level):
                level = World(load_World(int(9),Level_Dat[9][1]),Level_Dat[int(9)][0],9)
                player = Player(500,300,100,level)
                thermometer = Thermometer(00,20,(200,200),5-level.Texturepack)
                pygame.mixer.Channel(0).play(Level_Dat[level.Id][5],loops=-1)
                SUNMELT = Level_Dat[level.Id][2]/200
                gamestate = 'Game'

        window.blit(Homescreen,(0,0))
        
    elif gamestate == 'Game':
        
        l = [(SCREEN_WIDTH/5+100,100),(SCREEN_WIDTH/5+400,300),(SCREEN_WIDTH/5*2+400,300),(SCREEN_WIDTH/5*3+400,300),(SCREEN_WIDTH/5*4+400,300),(SCREEN_WIDTH,300)]

        for i in range(0,5):
            spawn_Particle(l[i][0],0,Level_Dat[level.Id][4],0,Level_Dat[level.Id][3],5,-4,4,3,5,3,despawn=l[i][1])

        Playscreen.fill('LightBlue')

        level.update()
        
        level.draw(Playscreen)
        update_Particle1(Playscreen,level.Scroll)
        
        if player.Respawntime < 0:
            player.update()
            player.draw(Playscreen)
        player.Deathcheck()
        x,gif = player.Wincheck()
        update_Particle3(Playscreen)
        if x: 
            gamestate = 'Win'
            if player.Level.Id >= Latest_Level and Latest_Level < 9:
                Latest_Level = player.Level.Id +1
            Finished = False,False
            with open('Data.txt','w') as file:
                file.write(str(Latest_Level))

        elif time > player.Respawntime and player.Respawntime > 0:
            player.Respawn()

        if level.Id == 0 and level.Scroll<355:
            Tutorial.draw(Playscreen,level.Scroll)

        if level.Id == 0 and level.Scroll > messagex-SCREEN_WIDTH and level.Scroll < messagex :
            message.update()
            message.draw(Playscreen,level.Scroll)

        if not (level.Id == 0 and level.Scroll < messagex):
            thermometer.draw(Playscreen,thermoindex)

        window.blit(Playscreen,(0,0))

    elif gamestate == 'Win':
        if not Finished[0]:Finished =  gif.update(clock.tick(FPS) / 1000)
        window.blit(gif.image,gif.rect)
        if Finished[0]:
            if Home2_Button.draw(window):
                gamestate = 'Home'   
                pygame.mixer.Channel(0).stop()
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(r'assets\sounds\music\main_menu.mp3'),loops=-1)

    elif gamestate == 'Paused':
        pygame.mixer.Channel(0).pause()
        level.draw(Playscreen)
        player.draw(Playscreen)
        img = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
        img.set_alpha(200)
        Playscreen.blit(img,(0,0))
        CreditText(-SCREEN_HEIGHT/3*2,0,15,'Paused','White').draw(Playscreen)

        if Resume_Button.draw(Playscreen):
            gamestate = 'Game'
            pygame.mixer.Channel(0).unpause()
        if Home_Button.draw(Playscreen):
            gamestate = 'Home'
            pygame.mixer.Channel(0).stop()
            pygame.mixer.Channel(0).play(pygame.mixer.Sound(r'assets\sounds\music\main_menu.mp3'),loops=-1)

        window.blit(Playscreen,(0,0))

    elif gamestate == 'Credits':
        Homescreen.fill('Lightblue')

        if Back_Button.draw(Homescreen):
            gamestate = 'Home'
            
        for Line in Credits:
            Line.draw(Homescreen)

        window.blit(Homescreen,(0,0))

    pygame.display.update()

with open('Data.txt','w') as file:
    file.write(str(Latest_Level))

pygame.quit()