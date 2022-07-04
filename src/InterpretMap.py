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
    
    def getImage(self):
        return self.__image
             
class TileMap:
    def __init__(self, mapList):
        self.tiles = []
        self.updateMap(mapList)
    
    def updateMap(self, mapList):
        for row in mapList:
            tileRow = []
            for cell in row:
                if cell[0] == 'X':
                    #if X, it's something you can't walk through
                    tileRow.append(Tile(1,0,0,0,cell))
                elif cell[0] == '.':
                    #if ., it's the bare floor
                    tileRow.append(Tile(0,0,0,0,cell))
                elif cell[0] == 'Y':
                    #if Y, it's something that causes slowing
                    tileRow.append(Tile(0,1,0,0,cell))
                elif cell[0] == 'H':
                    #if Y, it's a house
                    tileRow.append(Tile(0,0,1,0,cell))
                elif cell[0] == 'C':
                    #if C, it's a castle
                    tileRow.append(Tile(0,1,1,1,cell))
                elif cell[0] == 'T':
                    #if T, it's a group of trees or underbrush
                    tileRow.append(Tile(0,1,0,1,cell))
                elif cell[-1] == 'E':
                    #enemy
                    tileRow.append(Tile(1,0,0,0,cell))
                elif cell[-1] == 'B':
                    #enemy
                    tileRow.append(Tile(1,0,0,0,cell))
                else:
                    #otherwise, character or something
                    tileRow.append(Tile(0,0,0,0,cell))
                    
            self.tiles.append(tileRow)
        
    