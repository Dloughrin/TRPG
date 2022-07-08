'''
InterpretMap
Programmer: Dustin Loughrin
Email: dloughrin@cnm.edu
Purpose: Loads map data and recreates the map with tiles
'''

class Tile:
    def __init__(self, block, slow, heal, cover, key):
        self.block = block
        self.slow = slow
        self.heal = heal
        self.cover = cover
        self.__image = key   
    
    def setLocation(self, x, y):
        self.position = (x,y)
    
    def getImage(self):
        return self.__image
    
    def __str__(self):
        return "block {}, slow {}, heal {}, cover {}, pos ({},{})".format(self.block,self.slow,self.heal,self.cover,self.position[0],self.position[1])
             
class TileMap:
    def __init__(self, mapList):
        self.tiles = []
        self.updateMap(mapList)
    
    def updateMap(self, mapList):
        x = 0
        for row in mapList:
            tileRow = []
            y = 0
            for cell in row:
                tile = 0
                if cell[0] == 'X':
                    #if X, it's something you can't walk through
                    tile = Tile(1,0,0,0,cell)
                elif cell[0] == '.':
                    #if ., it's the bare floor
                    tile = Tile(0,0,0,0,cell)
                elif cell[0] == 'Y':
                    #if Y, it's something that causes slowing
                    tile = Tile(0,1,0,0,cell)
                elif cell[0] == 'H':
                    #if Y, it's a house
                    tile = Tile(0,0,1,0,cell)
                elif cell[0] == 'C':
                    #if C, it's a castle
                    tile = Tile(0,1,1,1,cell)
                elif cell[0] == 'T':
                    #if T, it's a group of trees or underbrush
                    tile = Tile(0,1,0,1,cell)
                else:
                    #otherwise, character or something
                    tile = Tile(0,0,0,0,cell)
                tile.setLocation(x, y)
                tileRow.append(tile)
                y += 1
            x += 1
            self.tiles.append(tileRow)
        
    