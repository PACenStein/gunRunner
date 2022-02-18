#imports
import os
import pygame
from pygame import mixer
from colors import *
import random
import csv
import button

import cv2


#---initiate pygame---
mixer.init()
pygame.init() 


#---clock for framerate---
clock = pygame.time.Clock()
FPS = 60 #max frame rate for the game

#---Window Initialisation---
windowWidth = 800 #sets the width of the pygame window
windowHeight = int(windowWidth * 0.8) #sets the height of the pygame window(80% of the width)
gameWindow = pygame.display.set_mode((windowWidth, windowHeight)) #creates the window
pygame.display.set_caption('GUN RUNNER') #gives the pygame window a title


#---game variables---
GRAVITY = 0.75
SCROLLTHRESH = 200 #the distance the player has to reach for the screen to scroll
ROWS = 16 #amount of rows in a level
MAXCOLUMNS = 150 #max amount of columns in a level
TILESIZE = windowHeight // ROWS #scales the tile size to match the level. // gives an int
TILETYPES = 21 #the amount of different types of tiles
MAXLEVELS = 3
gameScroll = 0
backgroundScroll = 0
level = 1 #holds which level is loaded/ the player is on
startGame = False #trigger to start game



#---Player Action Variables---
movingLeft = False
movingRight = False
shoot = False
grenade = False
grenadeThrown = False

#---load music and sounds---
pygame.mixer.music.load('audio/music2.mp3')
pygame.mixer.music.set_volume(0.3)#30% of original volume
pygame.mixer.music.play(-1, 0.0, 5000)#loop(-1 is infinte), delay, fade in (miliseconds)

jumpFX = pygame.mixer.Sound('audio/jump.mp3')
jumpFX.set_volume(0.5)#50% of original volume
shotFX = pygame.mixer.Sound('audio/shot.mp3')
shotFX.set_volume(0.5)#50% of original volume
grenadeFX = pygame.mixer.Sound('audio/grenade.mp3')
grenadeFX.set_volume(0.5)#50% of original volume
deathFX = pygame.mixer.Sound('audio/death.mp3')
deathFX.set_volume(0.5)
deathSound = True
startFX = pygame.mixer.Sound('audio/start.wav')
startFX.set_volume(0.5)



#---load images---
#button images
startImg = pygame.image.load('img/startButton.png').convert_alpha() #adds image to variable
exitImg = pygame.image.load('img/exitButton.png').convert_alpha() #adds image to variable
restartImg = pygame.image.load('img/restartButton.png').convert_alpha()

#load background images
tree1Img = pygame.image.load('img/background/tree1.png').convert_alpha() #adds image to variable
tree2Img = pygame.image.load('img/background/tree2.png').convert_alpha() #adds image to variable
mountainImg = pygame.image.load('img/background/mountain.png').convert_alpha() #adds image to variable
skyImg = pygame.image.load('img/background/sky.png').convert_alpha() #adds image to variable
#load level tiles
imgList = []
for x in range(TILETYPES):
    img = pygame.image.load(f'img/tile/{x}.png').convert_alpha() #uses the index as the png name
    img = pygame.transform.scale(img, (TILESIZE, TILESIZE)) #pushes image to be the correct size
    imgList.append(img) #adds image to the list

#load bullet sprite
bulletImg = pygame.image.load('img/icons/bullet.png').convert_alpha() #assings sprite to variable
#load grenade sprite
grenadeImg = pygame.image.load('img/icons/grenade.png').convert_alpha()
#load item box sprites
healthBoxImg = pygame.image.load('img/icons/healthbox.png').convert_alpha()
ammoBoxImg = pygame.image.load('img/icons/ammobox.png').convert_alpha()
grenadeBoxImg = pygame.image.load('img/icons/grenadebox.png').convert_alpha()
itemBoxes = {
    'Health'    : healthBoxImg,
    'Ammo'      : ammoBoxImg,
    'Grenade'   : grenadeBoxImg
} #dictonary relating strings to item sprites


#---draw text to screen---
font = pygame.font.SysFont('Futura', 30) #font choice, size

def drawText(text, font, textCol, x, y):
    img = font.render(text, True, textCol) #render font into an image
    gameWindow.blit(img, (x, y))#draw the text to screen


#---Draw and Update Background---
def drawBackground():
    gameWindow.fill(LIGHTGREEN) #removes trailing effect
    width = skyImg.get_width() #all images are the same width
    for x in range(5):
        gameWindow.blit(skyImg, ((x * width) - backgroundScroll * 0.5, 0))
        gameWindow.blit(mountainImg, ((x * width) - backgroundScroll * 0.6, windowHeight - mountainImg.get_height() - 300))
        gameWindow.blit(tree1Img, ((x * width) - backgroundScroll * 0.7, windowHeight - tree1Img.get_height() - 150))
        gameWindow.blit(tree2Img, ((x * width) - backgroundScroll * 0.8, windowHeight - tree2Img.get_height()))

#reset level function
def resetLevel():
    enemyGroup.empty() #pygame method to remove all sprites
    bulletGroup.empty()
    grenadeGroup.empty()
    explosionGroup.empty()
    itemBoxGroup.empty()
    decorationGroup.empty()
    waterGroup.empty()
    exitGroup.empty()

    #create empty tile list
    data = []
    for row in range(ROWS): #itterate through, creating every row
        r = [-1] * MAXCOLUMNS #creates 150 empty tiles (1 row)
        data.append(r) #add row to the level data

    return data



#---Classes---
class Mercenary(pygame.sprite.Sprite): #class for the merceneraies in the game
    
    def __init__(self, charType, x, y, scale, speed, ammo, grenades): #charType for chosing between player or enemy, x, y for coordinates, scale for sprite scaling factor, speed for movement speed
        
        pygame.sprite.Sprite.__init__(self) #takes functionality from pygames sprite class
        self.alive = True
        self.charType = charType #the character type used as an argument in the sprites path
        self.speed = speed #Mercenaries movement speed
        self.ammo = ammo # current ammo
        self.startAmmo = ammo #ammo the player begins with
        self.shootCooldown = 0
        self.grenades = grenades #holds amount of grenades.
        self.health = 100 #starting amount of health
        self.maxHealth = self.health #max health for health bars
        self.velY = 0 #y coordinate velocity
        self.direction = 1 #1 facing right (initial) 2 facing left
        self.jump = False #player is not currently jumping
        self.inAir = True #assume player is in air until they land
        self.flip = False #flips the sprite when true
        
        #---animation---
        self.animationList = [] #blank list to load sprites into for animation
        self.frameIndex = 0 #represents the frame that the sprite animation is on
        self.action = 0 #action referes to which animation needs to play 0 refers to idle
        self.updateTime = pygame.time.get_ticks()#gets time when instance is first created, starting clock for updating animation
       
       #ai specific variables
        self.moveCounter = 0 #used for direction changing 
        self.vision = pygame.Rect(0, 0, 150, 20)#x, y, width, height. Increasing width increases distance the enemy can see
        self.idling = False #causes the enemy to stand still
        self.idlingCounter = 0 #used to stop enemy from idling



        #Load all images for the mercenary
        animationTypes = ['idle', 'run', 'jump', 'death'] #folder names
        for animation in animationTypes:
            #reset temp list of sprites
            tempList = [] #list for sprites
            #count number of frames in folder
            numFrames = len(os.listdir(f'img/{self.charType}/{animation}')) #length/ amount of frames
            for i in range(numFrames): #range number is the amount of frames
                img = pygame.image.load(f'img/{self.charType}/{animation}/{i}.png').convert_alpha() #set the sprite for the player 
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale))) #scale player sprite
                tempList.append(img) #append to a temporary list of sprites
            self.animationList.append(tempList) #append temporary list to actual animation list

        self.image = self.animationList[self.action][self.frameIndex]#Gets relevant list to the players action, then gets the frame index
        self.rect = self.image.get_rect() #physical aspect of mercenary. Responsible for movement and collision
        self.rect.center = (x, y) #finds the center of the sprite
        self.width = self.image.get_width() #holds the width of the sprite
        self.height = self.image.get_height() #holds the height of the sprite

    #---Update method---
    def update(self):
        self.updateAnimation()
        self.checkAlive()#method to check if instance is alive
        #update cooldown
        if self.shootCooldown > 0: #loop, subtracting 1 eachtime
            self.shootCooldown -= 1 

    #---Method for Movement---
    def move(self, movingLeft, movingRight):
        #hard reset for movemnt variables, Delta stands for Change in (X or y)
        gameScroll = 0
        deltaX = 0
        deltaY = 0

        #variables for directional movement
        if movingLeft:
            deltaX = -self.speed #decrease in speed = left movement on x axis
            self.flip = True #sprite flipped to make the mercenary face left
            self.direction = -1 #facing left
        if movingRight:
            deltaX = self.speed 
            self.flip = False #sprite not flipped
            self.direction = 1 #facing right

        #variables for jumping 
        if self.jump == True and self.inAir == False:
            self.velY = -11 #increases height
            self.jump = False #resets jump
            self.inAir = True


        #create gravity
        self.velY += GRAVITY #+ means moving down
        if self.velY > 10: #if terminal velocity exceeded, reset velocity to terminal velocity 
            self.velY = 10
        deltaY += self.velY #increase change in y

        #check for collision 
        for tile in levelProcess.obstacleList:
            #check collision on x axis
            if tile[1].colliderect(self.rect.x + deltaX, self.rect.y, self.width, self.height): #tile is a tuple. Index 1 is its rect. 
                                                                            #Checking against players change in x prevents intersection 
                deltaX = 0 #stops movement
                #if the ai has hit wall, change direction
                if self.charType == 'enemy':
                    self.direction *= -1
                    self.moveCounter = 0
            #check collision on y axis
            if tile[1].colliderect(self.rect.x, self.rect.y + deltaY, self.width, self.height): #tile is a tuple. Index 1 is its rect. 
                                                                            #Checking against players change in y prevents intersection 
                #check if player is below ground/ jumping
                if self.velY < 0: #if player is moving up
                    self.velY = 0 #stop moving up
                    #set max jump when colliding
                    deltaY = tile[1].bottom - self.rect.top#gap between players head and tile
                #check if player is falling
                elif self.velY >= 0:
                    self.velY = 0 #hit gorund so no longer falling
                    self.inAir = False #no longer in air, can jump
                    deltaY = tile[1].top - self.rect.bottom#gap between players feet and tile

        #check for collision with water
        if pygame.sprite.spritecollide(self, waterGroup, False):
            self.health = 0 #check alive will then return false

        #check for collision with exit
        levelComplete = False #level not finished
        if pygame.sprite.spritecollide(self, exitGroup, False):
            levelComplete = True
        
        #check if off map
        if self.rect.bottom > windowHeight:
            self.health = 0

        #check if going off edges
        if self.charType == 'player': #only player needs to be checked
            if self.rect.left + deltaX < 0 or self.rect.right + deltaX > windowWidth:
                self.speed = 0

            

        #update mercenaries rect position
        self.rect.x += deltaX
        self.rect.y += deltaY

        #update scoll based on player pos
        if self.charType == 'player': #only player can scroll the screen
            if (self.rect.right > windowWidth - SCROLLTHRESH and backgroundScroll < (levelProcess.levelLen * TILESIZE) - windowWidth) \
                or (self.rect.left < SCROLLTHRESH and backgroundScroll > abs(deltaX)): #if close to either edge of window and not at end of level. \ LINE SPLIT
                #when screen scrolls, player needs to be moved back across the screen
                self.rect.x -= deltaX 
                gameScroll = -deltaX #if moving left, move right. If right, move left 

        return gameScroll, levelComplete


        
    #---method for shooting---
    def shoot(self):
        if self.shootCooldown == 0 and self.ammo > 0: 
            self.shootCooldown = 20 #lower the number, the quicker the reload
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)#spawn sprite at x center of the rect, y center of rect, direction
            bulletGroup.add(bullet)#add instance to group
            self.ammo -= 1 #decrease ammo
            shotFX.play()

    def ai(self):
        if self.alive and player.alive:
            if not self.idling and random.randint(1, 200) == 1:#gives random probability of idling enemy
                self.idling = True #enemy stands still
                self.updateAction(0)#idle animation
                self.idlingCounter = 50 #count down to stop idle
            #check if the ai is near the player
            if self.vision.colliderect(player.rect):
                #stop moving and face player
                self.updateAction(0) #0 is idle
                #shoot
                self.shoot()
            else: #if no collision detected
                if self.idling == False:
                    if self.direction == 1: #direction is facing right
                        aiMovingRight = True #move right
                    else:
                        aiMovingRight = False #if not looking right dont move right
                    aiMovingLeft = not aiMovingRight #left will equal opposite to right
                    self.move(aiMovingLeft, aiMovingRight)
                    self.updateAction(1)#running action is 1
                    self.moveCounter += 1 #increase per itteration to change direction
                    #update ai vision as enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery) #centers rectangle then offsets it by half of the width (only see in 1 dir)
                    #pygame.draw.rect(gameWindow, RED, self.vision) #draws the vision rect, so it can be seen for testing
    
                    if self.moveCounter > TILESIZE: #when level is made, enemy will move one tile then change direction
                        self.direction *= -1 #flips direction
                        self.moveCounter *= -1 #changes counter to cause direction to change
                else:
                    self.idlingCounter -= 1 #decrease idle timer
                    if self.idlingCounter <= 0:
                        self.idling = False

        #scroll
        self.rect.x += gameScroll


    #--method for animation--
    def updateAnimation(self):
        #update animation
        ANIMATION_COOLDOWN = 100 #limit speed of animation
        #update image depending on current frame
        self.image = self.animationList[self.action][self.frameIndex] #Gets relevant list to the players action, then gets the frame index
        #check if enough time has passed since last frame change
        if pygame.time.get_ticks() - self.updateTime > ANIMATION_COOLDOWN:
            self.updateTime = pygame.time.get_ticks() #updates time for loop
            self.frameIndex += 1 #increments the index by 1 frame
        #if the animation has run out of frames, reset back to the first frame
        if self.frameIndex >= len(self.animationList[self.action]): #if more frames then list length then
            if self.action == 3: #if death animation then
                self.frameIndex = len(self.animationList[self.action]) - 1 #set the frame to stay on the last of the aimation
            else:
                self.frameIndex = 0 #reset frames

    def updateAction(self, newAction):
        #check if the new action is different to the previous one
        if newAction != self.action: #if new update is not the same as current action then
            self.action = newAction #update the action
            #update the animation settings to reset the frame index
            self.frameIndex = 0 #reset the frames
            self.updateTime = pygame.time.get_ticks()

    def checkAlive(self):
        
        if self.health <= 0:
            self.health = 0 #set health to 0
            self.speed = 0 #stops any movements when the instance dies 
            self.alive = False #kills instance
            self.updateAction(3)#animation 3 is death animation
            
            


    #---Method for drawing the Mercenary---
    def draw(self): #draw function draws to screen instead of using gameWindow.blit() for every part drawn on to screen.
        gameWindow.blit(pygame.transform.flip(self.image, self.flip, False), self.rect) #draws player to screen, image values, coordinates


class LevelProcess():
    def __init__(self):
        self.obstacleList = []

    def processData(self, data): #data will be the level data from csv file
        self.levelLen = len(data[0]) #amount of columns
        #iterate through each value in level data value, and carry out action per tile 
        for y, row in enumerate(data): #iterate through each row
            for x, tile in enumerate(row): #iterate through all rows
                if tile >= 0: #-1 tile is blank space so does not need to be processed 
                    img = imgList[tile] #set img to correct tile image
                    imgRect = img.get_rect() #create rectangle for the tile
                    imgRect.x = x * TILESIZE #gets x from enumerated value
                    imgRect.y = y * TILESIZE #gets y from enumerated value
                    tileData = (img, imgRect) #holds image and rectangle 
                    if tile >= 0 and tile <= 8:
                        self.obstacleList.append(tileData)
                    elif tile >= 9 and tile <= 10:
                        water = Water (img, x * TILESIZE, y * TILESIZE)#img, x, y
                        waterGroup.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decortaion (img, x * TILESIZE, y * TILESIZE)#img, x, y
                        decorationGroup.add(decoration)
                    elif tile == 15:
                        #create player instance
                        player = Mercenary('player', x * TILESIZE, y * TILESIZE , 1.65, 5, 20, 5) #characterType, x, y, scale, speed, ammo, grenades
                        healthBar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:
                        #create enemy instance
                        enemy = Mercenary('enemy', x * TILESIZE, y * TILESIZE, 1.65, 2, 20, 0) #characterType, x, y, scale, speed, ammo, grenades
                        enemyGroup.add(enemy) #add enemy instance to group
                    elif tile == 17:
                        #create ammo box
                        itemBox = ItemBox('Ammo', x * TILESIZE, y * TILESIZE)#type, x, y
                        itemBoxGroup.add(itemBox)
                    elif tile == 18:
                        #create grenade box
                        itemBox = ItemBox('Grenade', x * TILESIZE, y * TILESIZE)#type, x, y
                        itemBoxGroup.add(itemBox)
                    elif tile == 19:
                        #create health box
                        itemBox = ItemBox('Health', x * TILESIZE, y * TILESIZE)#type, x, y
                        itemBoxGroup.add(itemBox)
                    elif tile == 20:
                        exit = Exit (img, x * TILESIZE, y * TILESIZE)#img, x, y
                        exitGroup.add(exit)

        return player, healthBar

    def draw(self):
        for tile in self.obstacleList:
            tile[1][0] += gameScroll #1 is rectangle, 0 is x
            gameWindow.blit(tile[0], tile[1]) #tile is a tuple containing the image and its rect


class Decortaion(pygame.sprite.Sprite):
    def __init__(self, img, x, y, ):
        pygame.sprite.Sprite.__init__(self) 
        self.image = img #set image to the image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILESIZE // 2, y + (TILESIZE - self.image.get_height())) #sets the coordinates based on the mid top of image

    def update(self):
        self.rect.x += gameScroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y, ):
        pygame.sprite.Sprite.__init__(self) 
        self.image = img #set image to the image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILESIZE // 2, y + (TILESIZE - self.image.get_height())) #sets the coordinates based on the mid top of image

    def update(self):
        self.rect.x += gameScroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y, ):
        pygame.sprite.Sprite.__init__(self) 
        self.image = img #set image to the image
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILESIZE // 2, y + (TILESIZE - self.image.get_height())) #sets the coordinates based on the mid top of image

    def update(self):
        self.rect.x += gameScroll

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, itemType, x, y, ):
        pygame.sprite.Sprite.__init__(self) #inheriate methords from sprites
        self.itemType = itemType #dictates the type of item box
        self.image = itemBoxes[self.itemType] #list for finding the correct sprite, using the item type as the index
        self.rect = self.image.get_rect() #create rectangle for the object
        self.rect.midtop = (x + TILESIZE // 2, y + (TILESIZE - self.image.get_height()))#in the middle of a tile

    def update(self):
        #scroll
        self.rect.x += gameScroll
        #check if the player has picked up a box
        if pygame.sprite.collide_rect(self, player): #finds collsion between self rect and player rect
            #check box type
            if self.itemType == 'Health': #if it is a health box
                player.health += 25
                if player.health > player.maxHealth:
                    player.health = player.maxHealth #if health exceeds max, set max
            elif self.itemType == 'Ammo': #if it is an ammo box
                player.ammo += 15
            elif self.itemType == 'Grenade': #if it is a grenade box
                player.grenades += 3
            #delete box
            self.kill()

class HealthBar():
    def __init__(self, x, y, health, maxHealth):
        self.x = x
        self.y = y
        self.health = health #current health
        self.maxHealth = maxHealth #maxium health 

    def draw(self, health):
        #update to new health value
        self.health = health 
        #calculate health ratio
        ratio = self.health / self.maxHealth #used to create the smaller health bar (actual health)
        pygame.draw.rect(gameWindow, BLACK, (self.x - 2, self.y -2, 154, 24)) #adds black border
        pygame.draw.rect(gameWindow, RED, (self.x, self.y, 150, 20)) #draws the max health bar
        pygame.draw.rect(gameWindow, GREEN, (self.x, self.y, 150 * ratio, 20)) #draws the current health bar

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self) #inheriate methords from sprites
        self.speed = 10 #speed will not vary so this is not an attribute that can be changed
        self.image = bulletImg #call the bullet sprite
        self.rect = self.image.get_rect() #crate a rectangle for the image sprite
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #move bullet
        self.rect.x += (self.direction * self.speed) + gameScroll#move in positive or negative direction at set speed.
        #check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > windowWidth: #if right side of the rectangle is off of the screen or the left side of the screen is greate then the width then
            self.kill()
        
        #check for collisons with level 
        for tile in levelProcess.obstacleList:
            if tile[1].colliderect(self.rect):
                self.kill() #delete bullet on collison
        #check collisions with characters
        if pygame.sprite.spritecollide(player, bulletGroup, False): #what character collisons are bing checked for, what it collides with, whether or not the object is deleted on collision
            if player.alive: #collision wont count for dead instances
                player.health -= 5 #lower for player 
                self.kill() #delete bullet
        for enemy in enemyGroup:
            if pygame.sprite.spritecollide(enemy, bulletGroup, False): #what character collisons are bing checked for, what it collides with, whether or not the object is deleted on collision
                if enemy.alive: #collision wont count for dead instances
                    enemy.health -= 25 #more damage to enemies
                    self.kill() #delete bullet

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self) #inheriate methords from sprites
        self.timer = 100 #the fuse time on the grenade
        self.velY = -11 #negative travles up screen
        self.speed = 7 #speed will not vary so this is not an attribute that can be changed
        self.image = grenadeImg #call the grenade sprite
        self.rect = self.image.get_rect() #crate a rectangle for the image sprite
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        self.velY += GRAVITY #changes y to a peek then decreases
        deltaX = self.direction * self.speed #direction * speed gives change in velocity
        deltaY = self.velY

        #check for collisons with level
        for tile in levelProcess.obstacleList:
                #check for collisions with walls
            if tile[1].colliderect(self.rect.x + deltaX, self.rect.y, self.width, self.height): 
                self.direction *= -1 #flip the grenades direction
                deltaX = self.direction * self.speed
            #check for collision in the y  
            if tile[1].colliderect(self.rect.x, self.rect.y  + deltaY, self.width, self.height): 
                self.speed = 0 #when collide stop left and right movement
                if self.velY < 0: #if grenade is moving up
                    self.velY = 0 #stop moving up
                    #set max height when colliding
                    deltaY = tile[1].bottom - self.rect.top#gap between players head and tile
                #check if player is falling
                elif self.velY >= 0:
                    self.velY = 0 #hit gorund so no longer falling
                    deltaY = tile[1].top - self.rect.bottom

    #update pos
        self.rect.x += deltaX + gameScroll #x position increases by change
        self.rect.y += deltaY #position increases by change

    #grenade countdown/ fuse
        self.timer -= 1
        if self.timer <= 0:
            self.kill() #delete grenade before explosion
            grenadeFX.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)# coords, scale
            explosionGroup.add(explosion)
            #damage instances nearby
            if abs(self.rect.centerx - player.rect.centerx) < TILESIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILESIZE * 2: #tile size will be used as the games scale later in development
                player.health -= 50 #remove 50 health points    
            for enemy in enemyGroup:    
                if abs(self.rect.centerx - enemy.rect.centerx) < TILESIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILESIZE * 2: #tile size will be used as the games scale later in development
                    enemy.health -= 50 #remove 50 health points 

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self) #inheriate methords from sprites
        self.images = []#sprite list
        for num in range (1,6):
            img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)   
        self.frameIndex = 0 #represents the current sprite    
        self.image = self.images[self.frameIndex]
        self.rect = self.image.get_rect() #crate a rectangle for the image sprite
        self.rect.center = (x, y)
        self.counter = 0 #controls animation (works like a cooldown)


    def update(self):
        #scroll
        self.rect.x += gameScroll
        EXPLOSIONSPEED = 4 #the speed the animation plays
        #update animation
        self.counter += 1
        if self.counter >= EXPLOSIONSPEED: #if required time passed go on to next frame
            self.counter = 0 #reset counter
            self.frameIndex += 1 #next frame
            #if animation is complete, delete exploosion
            if self.frameIndex >= len(self.images): #if the frame index is more then the total frames, kill instance
                self.kill()
            else:
                self.image = self.images[self.frameIndex] #animate next frame


    

#---Create Buttons---
startButton = button.Button(windowWidth // 2 - 130, windowHeight // 2 - 150, startImg, 1)
exitButton = button.Button(windowWidth // 2 - 110, windowHeight // 2 + 50, exitImg, 1)
restartButton = button.Button(windowWidth // 2 - 100, windowHeight // 2 - 50, restartImg, 2)

#---create sprite groups---
enemyGroup = pygame.sprite.Group()
bulletGroup = pygame.sprite.Group() #can use methods from sprite class
grenadeGroup = pygame.sprite.Group() #can use methods from sprite class
explosionGroup = pygame.sprite.Group()
itemBoxGroup = pygame.sprite.Group()
decorationGroup = pygame.sprite.Group()
waterGroup = pygame.sprite.Group()
exitGroup = pygame.sprite.Group()

#---Load Data---
#create empty tile list (no level data loaded)
levelData = []
for row in range(ROWS): #itterate through, creating every row
    r = [-1] * MAXCOLUMNS #creates 150 empty tiles (1 row)
    levelData.append(r) #add row to the level data
#load the level and create it 
with open(f'level{level}Data.csv', 'r', newline='') as csvfile: #open level data csv file
            reader = csv.reader(csvfile, delimiter = ',') #delimiter seperates each value with chosen char (,)
            #reading csv will return as a string. The level editor requires ints. This means each value needs to be iterated through 
            #and converted to an int
            for x, row in enumerate(reader):
                for y, tile in enumerate(row): #each individual tile
                    levelData[x][y] = int(tile)
#print(levelData) #used for testing
#process data
levelProcess = LevelProcess() #process level data, assining tile values to sprites and adding functionality to the tiles
player, healthBar = levelProcess.processData(levelData) #get returns from classes method


running = True #boolean varible to control the main loop
#---main game loop---
while running:
    
    #---FPS limiter---
    clock.tick(FPS) 

    #starting condition
    if startGame == False:
        #---MAIN MENU---
        #Draw Menu
        gameWindow.fill(LIGHTGREEN)
        #add buttons
        if startButton.draw(gameWindow):
            startGame = True #game starts
            startFX.play()
        if exitButton.draw(gameWindow):
            running = False #window closes
        
    else:
        #---MAIN GAME LOOP---

        #---Functions---
        #draw the background
        drawBackground() #First in order to clear whole screen
        #draw the level 
        levelProcess.draw() 
        #show player health
        healthBar.draw(player.health) #passes in health any time it changes
        #show ammo
        drawText(f'AMMO: ', font, WHITE, 10, 35)
        for x in range(player.ammo):
            gameWindow.blit(bulletImg, (90 + (x * 10), 40)) #x coordinate needs to increase every iteration
        #show grenades
        drawText(f'GRENADES: ', font, WHITE, 10, 60)
        for x in range(player.grenades):
            gameWindow.blit(grenadeImg, (135 + (x * 15), 60))#x coordinate needs to increase every iteration
    
        #---call instances---
        player.update()
        player.draw() #draw the player

        for enemy in enemyGroup: #iterate thorugh every enemy instance
            enemy.ai() #calls the ai
            enemy.update() #updates the enemies
            enemy.draw() #draw the enemies


        #---Update Groups---
        bulletGroup.update()
        grenadeGroup.update()
        explosionGroup.update()
        itemBoxGroup.update()
        decorationGroup.update()
        waterGroup.update()
        exitGroup.update()
        
        #---Draw Groups---
        bulletGroup.draw(gameWindow)
        grenadeGroup.draw(gameWindow)
        explosionGroup.draw(gameWindow)
        itemBoxGroup.draw(gameWindow)
        decorationGroup.draw(gameWindow)
        waterGroup.draw(gameWindow)
        exitGroup.draw(gameWindow)


        #---update player actions---
        if player.alive:
            #shoot
            if shoot:
                player.shoot()#calls the instances shoot method
            #throw grenades
            elif grenade and grenadeThrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), \
                                player.rect.top, player.direction)
                grenadeGroup.add(grenade)
                grenadeThrown = True
                player.grenades -= 1
            
            if player.inAir:
                player.updateAction(2)#2 is jump
            elif movingLeft or movingRight: #if player is moving left or right, play running animation
                player.updateAction(1)#index for running is 1
            else: #if player is not moving play idle animation
                player.updateAction(0)#index for idle is 0
            gameScroll, levelComplete = player.move(movingLeft, movingRight) 
            backgroundScroll -= gameScroll
            #check if player has completed the level
            if levelComplete:
                level += 1 #next level
                backgroundScroll = 0
                levelData = resetLevel()
                if level <= MAXLEVELS: #prevents the game from trying to load nonexistent levels
                    with open(f'level{level}Data.csv', 'r', newline='') as csvfile: #open level data csv file
                            reader = csv.reader(csvfile, delimiter = ',') #delimiter seperates each value with chosen char (,)
                            #reading csv will return as a string. The level editor requires ints. This means each value needs to be iterated through 
                            #and converted to an int
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row): #each individual tile
                                    levelData[x][y] = int(tile)
                    levelProcess = LevelProcess() #process level data, assining tile values to sprites and adding functionality to the tiles
                    player, healthBar = levelProcess.processData(levelData) #get returns from classes method

        else:
            while deathSound == True: #stops the sound playing multiple times
                deathFX.play()
                deathSound = False
            gameScroll = 0
            if restartButton.draw(gameWindow):
                backgroundScroll = 0
                levelData = resetLevel() #level data will become the returned list
                #load the level and create it 
                with open(f'level{level}Data.csv', 'r', newline='') as csvfile: #open level data csv file
                            reader = csv.reader(csvfile, delimiter = ',') #delimiter seperates each value with chosen char (,)
                            #reading csv will return as a string. The level editor requires ints. This means each value needs to be iterated through 
                            #and converted to an int
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row): #each individual tile
                                    levelData[x][y] = int(tile)
                #print(levelData) #used for testing
                #process data
                levelProcess = LevelProcess() #process level data, assining tile values to sprites and adding functionality to the tiles
                player, healthBar = levelProcess.processData(levelData) #get returns from classes method
                deathSound = True



    #---Event Getter---
    for event in pygame.event.get(): #event getter
       
        if event.type == pygame.QUIT: #quit game event
            running = False #breaks the loops conditions

        #---Keyboard Input---
        if event.type == pygame.KEYDOWN: #if key is pressed down then
            if event.key == pygame.K_LEFT and player.alive: #if left arrow pressed
                movingLeft = True
            if event.key == pygame.K_RIGHT and player.alive: #if right arrow pressed
                movingRight = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_g:
                grenade = True
            if event.key == pygame.K_UP and player.alive: #if up arrow pressed and player is alive
                player.jump = True #player jumps
                jumpFX.play()
            if event.key == pygame.K_ESCAPE: #if esc pressed, close game
                running = False
       

        if event.type == pygame.KEYUP: #if key is let go
            if event.key == pygame.K_LEFT: #if left arrow released
                movingLeft = False
            if event.key == pygame.K_RIGHT: #if right arrow released
                movingRight = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_g:
                grenade = False
                grenadeThrown = False
        


    pygame.display.update() #updates entire screen


pygame.quit()






