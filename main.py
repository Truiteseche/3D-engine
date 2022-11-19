import pygame, sys
import math
import random

class Engine:

    def __init__(self, screen):
        self.screen = screen
        self.SCREEN_SIZE = self.screen.get_size()
        print("Screen Size :", self.SCREEN_SIZE)
        self.FOV = 60
        print("FOV :", self.FOV)
        self.SCREEN_DIST = (self.SCREEN_SIZE[0]/2)/math.tan(math.radians(self.FOV/2))
        self.cameraX = 200
        self.cameraY = 150
        self.cameraZ = 0
        self.keyboard = {}
        self.objects = []

    def create3dObject(self, pos, pointsCoordinates, color=(255, 0, 0)):
        """
        pos : pos of the object
        points : list of tuples which are point's 3D coordinates relative to object's ones
        ex : [(0, 0, 0), (0, 0, 10), (0, 10, 0), (10, 0, 0)]
        """
        self.objects.append(Object(pos, pointsCoordinates, self, color))
        return self.objects[len(self.objects)-1]


class Object:

    def __init__(self, pos, pointsCoordinates, engine, color):
        self.engine = engine
        self.x = pos[0]
        self.y = pos[1]
        self.z = pos[2]
        self.width = max(pointsCoordinates, key=lambda item:item[0])[0] - min(pointsCoordinates, key=lambda item:item[0])[0]
        self.height = max(pointsCoordinates, key=lambda item:item[1])[1] - min(pointsCoordinates, key=lambda item:item[1])[1]
        self.depth = max(pointsCoordinates, key=lambda item:item[2])[2] - min(pointsCoordinates, key=lambda item:item[2])[2]
        self.color = color
        self.points = []
        for point in pointsCoordinates:
            self.create3dPoint(point)

    def create3dPoint(self, pos):
        self.points.append(Point(pos, self, self.engine))
        
    def drawWireframe(self):
        for point in self.points:
            point.projectPointOnScreen()

        for point in self.points:
            for otherPoint in self.points:
                if not otherPoint is point:
                    pygame.draw.line(self.engine.screen, self.color, (point.projectedX, point.projectedY), (otherPoint.projectedX, otherPoint.projectedY))


class Point:

    def __init__(self, pos, parentObject, engine):
        self.engine = engine
        self.parentObject = parentObject
        self.x = pos[0]
        self.y = pos[1]
        self.z = pos[2]
        self.projectedX = 0
        self.projectedY = 0

    def projectPointOnScreen(self):
        """
        Calculates the projectedX and projectedY coordinates
        It converts 3d coord to 2d coord on the screen
        """
        self.projectedX = self.engine.SCREEN_DIST * (self.x + self.parentObject.x - self.engine.cameraX) / (self.engine.SCREEN_DIST + self.z - self.engine.cameraZ) + self.engine.SCREEN_SIZE[0]/2
        self.projectedY = self.engine.SCREEN_DIST * (self.y + self.parentObject.y - self.engine.cameraY) / (self.engine.SCREEN_DIST + self.z - self.engine.cameraZ) + self.engine.SCREEN_SIZE[1]/2

    def drawPoint(self):
        self.projectPointOnScreen()
        pygame.draw.circle(self.engine.screen, (255 - self.parentObject.color[0], 255 - self.parentObject.color[1], 255 - self.parentObject.color[2]), (self.projectedX, self.projectedY), 2)


pygame.init()
screen = pygame.display.set_mode((500, 480))
pygame.display.set_caption('TRUITE ENGINE • 3D GRAPHICS')
engine = Engine(screen)
engine.create3dObject((0, 0, 0), [(0, 0, 0), (100, 0, 0), (100, 100, 0), (0, 100, 0), (0, 0, 100), (100, 0, 100), (100, 100, 100), (0, 100, 100)], (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
engine.create3dObject((0, 300, 0), [(0, 0, 0), (100, 0, 0), (100, 0, 100), (0, 0, 100), (50, -100, 50)], (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
engine.create3dObject((300, 0, 0), [(25, 0, 0), (75, 0, 0), (100, 0, 25), (100, 0, 75), (75, 0, 100), (25, 0, 100), (0, 0, 75), (0, 0, 25), (25, 300, 0), (75, 300, 0), (100, 300, 25), (100, 300, 75), (75, 300, 100), (25, 300, 100), (0, 300, 75), (0, 300, 25)], (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            engine.keyboard[event.key] = True

        elif event.type == pygame.KEYUP:
            engine.keyboard[event.key] = False
    

    if pygame.K_d in engine.keyboard and engine.keyboard[pygame.K_d] == True:
        engine.cameraX += 0.3
    if pygame.K_q in engine.keyboard and engine.keyboard[pygame.K_q] == True:
        engine.cameraX -= 0.3
    if pygame.K_z in engine.keyboard and engine.keyboard[pygame.K_z] == True:
        engine.cameraZ += 0.3
    if pygame.K_s in engine.keyboard and engine.keyboard[pygame.K_s] == True:
        engine.cameraZ -= 0.3
    if pygame.K_DOWN in engine.keyboard and engine.keyboard[pygame.K_DOWN] == True:
        engine.cameraY += 0.3
    if pygame.K_UP in engine.keyboard and engine.keyboard[pygame.K_UP] == True:
        engine.cameraY -= 0.3
    if pygame.K_RIGHT in engine.keyboard and engine.keyboard[pygame.K_RIGHT] == True:
        engine.SCREEN_DIST += 1
    if pygame.K_LEFT in engine.keyboard and engine.keyboard[pygame.K_LEFT] == True:
        engine.SCREEN_DIST -= 1
    
    #print(engine.cameraX, engine.cameraY)
    #print(engine.keyboard)

    # display on screen
    screen.fill((0, 0, 0)) # dark mode
    if pygame.K_SPACE in engine.keyboard and engine.keyboard[pygame.K_SPACE] == True:
        screen.fill((255, 255, 255)) # light mode
    pygame.draw.circle(engine.screen, (255, 0, 255), (engine.SCREEN_SIZE[0]/2, engine.SCREEN_SIZE[1]/2), 2)
    for object in engine.objects:
        object.drawWireframe()
        for point in object.points:
            point.drawPoint()
    pygame.display.flip()
