#---Imports---
import pygame
from pygame.threads import WorkerQueue
from colors  import *
import button
import csv #used to save the level data


#---initiate Pygame---
pygame.init() 


#---FPS limiter---
clock = pygame.time.Clock()
FPS = 60 

#---Window Initialisation---
windowWidth = 800 #sets the width of the pygame window
windowHeight = int(windowWidth * 0.8) #sets the height of the pygame window(80% of the width)
lowerMargin = 100 #seperates elements of the screen where the ui will go
sideMargin = 300 #seperates elements of the screen where the ui will go
editorWindow = pygame.display.set_mode((windowWidth + sideMargin, windowHeight + lowerMargin)) #creates the window
pygame.display.set_caption('LEVEL EDITOR') #gives the pygame window a title


#---Create Editors Variables---
ROWS = 16
MAXCOLUMNS = 150 #maximum amount of collums in the editor
TILESIZE = windowHeight // ROWS #gets the size for each tile (// gives int)
currentTile = 0 #sets the current tile button selected 
TILETYPES = 21 #amount of types used as an index
level = 0 #level count
scrollLeft = False #trigger for scrolling screen left 
scrollRight = False #trigger for scrolling screen right
scroll = 0 #acts as the x coordinate 
scrollSpeed = 1 #the speed of the scrolling


#---Load Images---
tree1Img = pygame.image.load('img/background/tree1.png').convert_alpha() #adds image to variable
tree2Img = pygame.image.load('img/background/tree2.png').convert_alpha() #adds image to variable
mountainImg = pygame.image.load('img/background/mountain.png').convert_alpha() #adds image to variable
skyImg = pygame.image.load('img/background/sky.png').convert_alpha() #adds image to variable
#store tiles in list
imgList = []
for x in range(TILETYPES):
    img = pygame.image.load(f'img/tile/{x}.png').convert_alpha() #uses the index as the png name
    img = pygame.transform.scale(img, (TILESIZE, TILESIZE)) #pushes image to be the correct size
    imgList.append(img) #adds image to the list

saveImg = pygame.image.load('img/saveButton.png').convert_alpha() #adds image to variable
loadImg = pygame.image.load('img/loadButton.png').convert_alpha() #adds image to variable



#---Create Level Data---
#create an empty tile list
levelData = [] #holds the level
for row in range(ROWS): #itterate through, creating every row
    r = [-1] * MAXCOLUMNS #creates 150 empty tiles (1 row)
    levelData.append(r) #add row to the level data

#create the ground
for tile in range(0, MAXCOLUMNS):
    levelData[ROWS - 1][tile] = 0 #last row changed to ground tile


#---Output Text To Screen---
font = pygame.font.SysFont('Futura', 30) #font choice, size

def drawText(text, font, textCol, x, y):
    img = font.render(text, True, textCol) #render font into an image
    editorWindow.blit(img, (x, y))#draw the text to screen


#---Draw Background---
def drawBackground():
    editorWindow.fill(LIGHTGREEN) #removes trailing effect
    width = skyImg.get_width() #all images are the same width 
    #loop background
    for x in range(4):
        #layer the images
        editorWindow.blit(skyImg, ((x * width) -scroll * 0.5, 0)) #negative scroll inverts it to make it scroll across, second multiplication used for depth
        editorWindow.blit(mountainImg, (((x * width) -scroll * 0.6), windowHeight - mountainImg.get_height() - 300))
        editorWindow.blit(tree1Img, (((x * width) -scroll * 0.7), windowHeight - tree1Img.get_height() - 150))
        editorWindow.blit(tree2Img, (((x * width) -scroll * 0.8), windowHeight - tree2Img.get_height()))

#---Draw Grid---
def drawGrid():
    #verticle lines
    for c in range(MAXCOLUMNS + 1):
        pygame.draw.line(editorWindow, WHITE, (c * TILESIZE - scroll, 0), (c * TILESIZE - scroll, windowHeight))#x coordinate increases with each loop
    #horizontal lines
    for c in range(ROWS + 1):
        pygame.draw.line(editorWindow, WHITE, (0, c * TILESIZE), (windowWidth, c * TILESIZE))#x coordinate increases with each loop


#---Function For Drawing Level Tiles---
#iterate with a for loop through every value in the list
def drawLevel():
    #iterate through rows
    for y, row in enumerate(levelData): #gets row list and which row the current iteration is on
        #iterate through tiles
        for x, tile in enumerate(row):
            if tile >= 0: #doesnt drawn empty tiles
                editorWindow.blit(imgList[tile], (x * TILESIZE - scroll, y * TILESIZE))#draws image at x and y using the enumeraters. 
                                                                                #-scroll makes it scroll with gird and background




#---Create Buttons---
saveButton = button.Button(windowWidth // 2, windowHeight + lowerMargin - 50, saveImg, 1) #x, y, img, scale
loadButton = button.Button(windowWidth // 2 + 200, windowHeight + lowerMargin - 50, loadImg, 1) #x, y, img, scale
#make button list
buttonList = []
buttonCol = 0 #iterates through the collums
buttonRow = 0 #iterates through the rows
for i in range(len(imgList)): #for each image, create a button
    tileButton = button.Button(windowWidth + (75 * buttonCol) + 50, 75 * buttonRow + 50, imgList[i], 1) #x, y, image, scale
    buttonList.append(tileButton)
    buttonCol += 1 #moves by another 75 pixles across 
    #after 3 collumns, shift down and back to the first collumn
    if buttonCol == 3:
        buttonRow += 1
        buttonCol = 0


running = True #controls whether the main loop is running
while running == True:

    #---Limit FPS---
    clock.tick(FPS)

    #---Call Functions---
    drawBackground()
    drawGrid()
    drawLevel()
    drawText(f'Level: {level}', font, WHITE, 10, windowHeight + lowerMargin - 90)
    drawText('Press UP or DOWN to change level', font, WHITE, 10, windowHeight + lowerMargin - 60)

    #---Save and Load Data---
    if saveButton.draw(editorWindow): #if save button clicked
        #save level data
        with open(f'level{level}Data.csv', 'w', newline='') as csvfile: #open level data csv file
            writer = csv.writer(csvfile, delimiter = ',') #delimiter seperates each value with chosen char (,)
            #take data from list and save to file, by itterating through each row and saving it to the file
            for row in levelData:
                writer.writerow(row) #writes row

    if loadButton.draw(editorWindow):
    #load level data
        #reset scroll to start of the level
        scroll = 0
        with open(f'level{level}Data.csv', 'r', newline='') as csvfile: #open level data csv file
            reader = csv.reader(csvfile, delimiter = ',') #delimiter seperates each value with chosen char (,)
            #reading csv will return as a string. The level editor requires numbers. This means each value needs to be iterated through 
            #and converted to an int
            for x, row in enumerate(reader):
                for y, tile in enumerate(row): #each individual tile
                    levelData[x][y] = int(tile)

    #---Draw Tile Pannel And Buttons---
    pygame.draw.rect(editorWindow, LIGHTGREEN, (windowWidth, 0, sideMargin, windowHeight)) #display, colour, x, y
        




    #---Choose a Tile---
    buttonCount = 0
    for buttonCount, i in enumerate(buttonList): #creates a running counter. The current tile will be the one that is interacted with
        if i.draw(editorWindow):
            currentTile = buttonCount
    #highlight selected button
    pygame.draw.rect(editorWindow, RED, buttonList[currentTile].rect, 3) #draw buttons rectangle from the list. 3 makes it an outline
    #print(currentTile) #used for testing

    #---Scroll The Level---
    if scrollLeft == True and scroll > 0: #scroll > 0 stops scrolling past the edge of the level
        scroll -= 5 * scrollSpeed #move screen left on the x axis, increase speed if shift held
    if scrollRight == True and scroll < (MAXCOLUMNS * TILESIZE) - windowWidth:
        scroll += 5 * scrollSpeed #move screen right on the x axis, increase speed if shift held

    #---Add New Tiles To The Window---
    #get mouse pos
    pos = pygame.mouse.get_pos()
    x = (pos[0] + scroll) // TILESIZE #pos 0 is the x value of the mouse position, scroll keeps it scrolling with grid, //TILESIZE rounds the pos to the nearest tile
    y = pos[1] // TILESIZE #pos 1 is the y value of the mouse position, // TILESIZE rounds it to the nearest tile

    #check that coordinates are within visable grid
    if pos[0] < windowWidth and pos[1] < windowHeight:
        #update tile value when mouse clicked
        if pygame.mouse.get_pressed()[0] == 1: #if left mouse button clicked
            if levelData[y][x] != currentTile: #y is rows. Isolates mouse pos row. x is columns. isolates mouse pos column. If the tile is not the correct tile then,
                levelData[y][x] = currentTile #set the tile to the current tile
        #remove tile
        if pygame.mouse.get_pressed()[2] == 1: #if right mouse button clicked
            levelData[y][x] = -1



    #---Event Getter---
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT: #if quit button pressed
            running = False #ends the loop
        #key presses
        if event.type == pygame.KEYDOWN: #if key pressed
            if event.key == pygame.K_UP: #if up arrow key pressed
                level += 1
            if event.key == pygame.K_DOWN and level > 0: #if down key pressed and level is not 0
                level -= 1
            if event.key == pygame.K_LEFT: #if left arrow key pressed
                scrollLeft = True
            if event.key == pygame.K_RIGHT: #if right arrow key pressed
                scrollRight = True
            if event.key == pygame.K_LSHIFT: #if shift is pressed it will increase the speed
                scrollSpeed = 5
                #print(scrollSpeed) #Used for testing

        #keys released  
        if event.type == pygame.KEYUP: #if key pressed
            if event.key == pygame.K_LEFT: #if left arrow key pressed
                scrollLeft = False
            if event.key == pygame.K_RIGHT: #if right arrow key pressed
                scrollRight = False  
            if event.key == pygame.K_LSHIFT: #if shift is let go, scroll speed will reset
                scrollSpeed = 1
                #print(scrollSpeed) #Used for testing
        
        
        


    pygame.display.update() #update whats on the screen

pygame.quit()

