'''
GameMap
Programmer: Dustin Loughrin
Email: dloughrin@cnm.edu
Purpose: Open files to load the map and associated tileset
'''

import pandas
import pygame
from pygame.locals import *

class GameMap:
    FILE = '../assets/dataSet.xlsx'
    SHEETS = ['Map 1','Map 2']
    
    def __init__(self):
        self.__maps = []
        for sh in GameMap.SHEETS:
            self.__maps.append(self.__loadMap(sh))
        self.__currentMap = self.__maps[0]
        self.currentTileSet = Tileset(self.__currentMap[0])        
        
    def __loadMap(self,sheetName):
        sheet = pandas.read_excel(io=GameMap.FILE, sheet_name=sheetName)
        return [sheetName,sheet.values.tolist()]
    
    def getCurrentMap(self):
        return self.__currentMap
    
    def getMapDimensions(self):
        h = self.__currentMap[1].__len__()
        w = 1
        for row in self.__currentMap[1]:
            if(w < row.__len__()):
                w = row.__len__()
        return [h,w]
    
    def getMapName(self):
        return self.__currentMap[0]
        
    def setMap(self,mapName):
        # map -> return a list of only the map names, then search for the map name
        tempList = list(map(lambda x: x[0], self.__maps))
        i = tempList.index(mapName)
        self.__currentMap = self.__maps[i]
        self.currentTileSet.file = self.__currentMap[0]
        self.currentTileSet.load()

#Example Tileset class from pygame with some adjustment
class Tileset:
    def __init__(self, file, size=(32, 32), margin=1, spacing=1):
        self.file = file
        self.size = size
        self.margin = margin
        self.spacing = spacing
        self.image = pygame.image.load('../assets/' + file + '.png')
        self.rect = self.image.get_rect()
        self.tiles = []
        self.tileKeys = []
        
        with open('../assets/' + file + '.txt') as f:
            lines = f.readlines()
        for line in lines:
            newLine = line.strip().split('\t')
            for c in newLine:
                self.tileKeys.append(c)
        
        self.load()

    def load(self):
        self.tiles = []
        x0 = y0 = self.margin
        w, h = self.rect.size
        dx = self.size[0] + self.spacing
        dy = self.size[1] + self.spacing
        
        for x in range(x0, w, dx):
            for y in range(y0, h, dy):
                tile = pygame.Surface(self.size)
                tile.blit(self.image, (0, 0), (x, y, *self.size))
                self.tiles.append(tile)
    
    def findKey(self, value):
        i = 0
        for y in self.tileKeys:
            if value[-1] == 'E' or value[-1] == 'C' or value[-1] == 'B':
                z = value[:-1]
                z = z[1:]
            else:
                z = value
            if y == z:
                return i
            i += 1
        return -1

    def __str__(self):
        return f'{self.__class__.__name__} file:{self.file} tile:{self.size}'
    
'''
maps = GameMap()
currentTiles = maps.currentTileSet;
screenX = 6*32
screenY = 8*32
screen = pygame.display.set_mode((screenX, screenY))
pygame.display.set_caption("Tile Set")

x = 0
y = 0
i = 0
tileLine = []
for tile in currentTiles.tiles:
    screen.blit(tile,(x*32, y*32))
    tileLine.append(currentTiles.tileKeys[i])
    x += 1
    i += 1
    if(x >= 6):
        x = 0
        y += 1
        print(tileLine)
        tileLine = []
    
pygame.display.flip()

running = True;
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            '''