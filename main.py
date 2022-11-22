import sys, math, random
try:
    import pygame
except ModuleNotFoundError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame

class Engine:

    def __init__(self, screen):
        self.screen = screen
        self.SCREEN_SIZE = self.screen.get_size()
        print("Screen Size:", self.SCREEN_SIZE)
        self.FOV = 60
        print("FOV:", self.FOV)
        self.SCREEN_DIST = (self.SCREEN_SIZE[0]/2)/math.tan(math.radians(self.FOV/2))
        self.cameraX = 200
        self.cameraY = 150
        self.cameraZ = 0
        self.keyboard = {}
        self.objects = []

    def create3dObject(self, pos, pointsCoordinates, color=(255, 0, 0)):
        """
        pos: position of the object in the 3D scene
        points: list of tuples which are point's 3D coordinates relative to object's ones
        ex: [(0, 0, 0), (0, 0, 10), (0, 10, 0), (10, 0, 0)]
        Returns a reference to the created object
        """
        self.objects.append(Object(pos, pointsCoordinates, self, color))
        return self.objects[len(self.objects)-1]

    def open3dObject(self, sourceFile: str, pos=(0, 0, 0)):
        """
        sourceFile: path of the object file
        pos: position of the new object in the 3D scene
        Opens the file, extracts the coordinates and creates a new Object
        Returns a reference of the created object
        """
        try:
            with open(sourceFile, "r") as f:
                if sourceFile[-3:] == "obj":
                    coords = []
                    for line in f:
                        if line[0:2] == "v ":
                            coords.append(tuple((-float(line.strip("v ").split()[0]), -float(line.strip("v ").split()[1]), -float(line.strip("v ").split()[2]))))
                elif sourceFile[-3:] == "dae":
                    geometryName = "Mesh"
                    coords = []
                    for line in f:
                        if '<geometry' in line:
                            geometryName = line[line.index('name="')+6:-3]
                        if f'float_array id="{geometryName}-mesh-positions-array"' in line:
                            line = line.strip()
                            i = line.index(">")
                            array = line[i+1:].strip("</float_array>").split()
                            for i in range(0, len(array), 3):
                                coords.append((float(array[i]), float(array[i+1]), float(array[i+2])))
                else:
                    print("Error: File format not supported")
                    return []
                f.close()
        except FileNotFoundError:
            print(f"Error: File not found: No such file or directory: '{sourceFile}'")
            return []

        return self.create3dObject(pos, coords)


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
        self.scale = (1, 1, 1)
        self.direction = (0, 0, 0)
        self.points = []
        for point in pointsCoordinates:
            self.create3dPoint(point)

    def create3dPoint(self, pos):
        self.points.append(Point(pos, self, self.engine))
    
    def scale3d(self, scalingFactors=(1, 1, 1)):
        """
        scalingFactors: 3d tuple to rescale the object on the 3 axis
        Scales the object
        """
        self.scale = scalingFactors
        for point in self.points:
            point.x = point.originX*scalingFactors[0]
            point.y = point.originY*scalingFactors[1]
            point.z = point.originZ*scalingFactors[2]
        self.width *= scalingFactors[0]
        self.height *= scalingFactors[1]
        self.depth *= scalingFactors[2]
    
    def rotate3d(rotatingAngle=(0, 0, 0)):
        """
        rotatingAngle: tuple of angles (in radian) | 1 angle for each 1 axis to rotate around
        Rotates each point of the object
        """
        return "ALED"
        
    def drawWireframe(self):
        for point in self.points:
            point.projectPointOnScreen()

        for pointA in self.points:
            for pointB in self.points:
                if not pointB is pointA:
                    if pointA.z-self.engine.cameraZ > -self.engine.SCREEN_DIST and pointB.z-self.engine.cameraZ > -self.engine.SCREEN_DIST:
                        pygame.draw.line(self.engine.screen, self.color, (pointA.projectedX, pointA.projectedY), (pointB.projectedX, pointB.projectedY))

    def drawPolygons(self):
        for pointA in self.points:
            for pointB in self.points:
                if not pointA is pointB:
                    for pointC in self.points:
                        if not pointA is pointB and not pointA is pointC and not pointB is pointC:
                            pygame.draw.polygon(self.engine.screen, self.color, [(pointA.projectedX, pointA.projectedY), (pointB.projectedX, pointB.projectedY), (pointC.projectedX, pointC.projectedY)])
        """
        for iPoint in range(len(self.points)):
            if iPoint+2 < len(self.points):
                pygame.draw.polygon(self.engine.screen, self.color, [(self.points[iPoint].projectedX, self.points[iPoint].projectedY), (self.points[iPoint+1].projectedX, self.points[iPoint+1].projectedY), (self.points[iPoint+2].projectedX, self.points[iPoint+2].projectedY)])
            elif iPoint+1 < len(self.points):
                pygame.draw.polygon(self.engine.screen, self.color, [(self.points[iPoint].projectedX, self.points[iPoint].projectedY), (self.points[iPoint+1].projectedX, self.points[iPoint+1].projectedY), (self.points[0].projectedX, self.points[0].projectedY)])

            if iPoint-2 >= 0:
                pygame.draw.polygon(self.engine.screen, self.color, [(self.points[iPoint-2].projectedX, self.points[iPoint-2].projectedY), (self.points[iPoint-1].projectedX, self.points[iPoint-1].projectedY), (self.points[iPoint].projectedX, self.points[iPoint].projectedY)])
            elif iPoint-1 >= 0:
                pygame.draw.polygon(self.engine.screen, self.color, [(self.points[len(self.points)-1].projectedX, self.points[len(self.points)-1].projectedY), (self.points[iPoint-1].projectedX, self.points[iPoint-1].projectedY), (self.points[iPoint].projectedX, self.points[iPoint].projectedY)])
        """

class Point:

    def __init__(self, pos, parentObject, engine):
        self.engine = engine
        self.parentObject = parentObject
        self.originX = pos[0]
        self.originY = pos[1]
        self.originZ = pos[2]
        self.x = self.originX
        self.y = self.originY
        self.z = self.originZ
        self.projectedX = 0
        self.projectedY = 0

    def projectPointOnScreen(self):
        """
        Calculates the projectedX and projectedY coordinates
        It converts the 3D coords in the world to the 2d coords on the screen
        """
        self.projectedX = self.engine.SCREEN_DIST * (self.x + self.parentObject.x - self.engine.cameraX) / (self.engine.SCREEN_DIST + self.z + self.parentObject.z - self.engine.cameraZ) + self.engine.SCREEN_SIZE[0]/2
        self.projectedY = self.engine.SCREEN_DIST * (self.y + self.parentObject.y - self.engine.cameraY) / (self.engine.SCREEN_DIST + self.z + self.parentObject.z - self.engine.cameraZ) + self.engine.SCREEN_SIZE[1]/2

    def drawPoint(self):
        self.projectPointOnScreen()
        if self.z-self.engine.cameraZ > -self.engine.SCREEN_DIST:
            pygame.draw.circle(self.engine.screen, (255 - self.parentObject.color[0], 255 - self.parentObject.color[1], 255 - self.parentObject.color[2]), (self.projectedX, self.projectedY), 2)


pygame.init()
screen = pygame.display.set_mode((720, 720))
pygame.display.set_caption('TRUITE ENGINE • 3D GRAPHICS WIREFRAME')
engine = Engine(screen)
obj = engine.create3dObject((-50, 0, 0), [(0, 0, 0), (100, 0, 0), (100, 100, 0), (0, 100, 0), (0, 0, 100), (100, 0, 100), (100, 100, 100), (0, 100, 100)], (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
engine.create3dObject((0, 300, 50), [(0, 0, 0), (100, 0, 0), (100, 0, 100), (0, 0, 100), (50, -100, 50)], (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
obj2 = engine.create3dObject((300, 0, 0), [(25, 0, 0), (75, 0, 0), (100, 0, 25), (100, 0, 75), (75, 0, 100), (25, 0, 100), (0, 0, 75), (0, 0, 25), (25, 300, 0), (75, 300, 0), (100, 300, 25), (100, 300, 75), (75, 300, 100), (25, 300, 100), (0, 300, 75), (0, 300, 25)], (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
engine.create3dObject((200, 50, 150), [(0, 0, 0), (100, 0, 0), (100, 100, 0), (0, 100, 0), (0, 0, 100), (100, 0, 100), (100, 100, 100), (0, 100, 100)], (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
#engine.open3dObject("3dModels/cone.obj", (300, -200, 0))
# obj0 = engine.open3dObject("3dModels/cone.dae", (0, -200, 0))
# obj0.scale3d((10, 10, 10))
FRAMES = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            engine.keyboard[event.key] = True

        elif event.type == pygame.KEYUP:
            engine.keyboard[event.key] = False
    

    # Controls
    if pygame.K_d in engine.keyboard and engine.keyboard[pygame.K_d] == True:
        engine.cameraX += 1
    if pygame.K_q in engine.keyboard and engine.keyboard[pygame.K_q] == True:
        engine.cameraX -= 1
    if pygame.K_z in engine.keyboard and engine.keyboard[pygame.K_z] == True:
        engine.cameraZ += 1
    if pygame.K_s in engine.keyboard and engine.keyboard[pygame.K_s] == True:
        engine.cameraZ -= 1
    if pygame.K_DOWN in engine.keyboard and engine.keyboard[pygame.K_DOWN] == True:
        engine.cameraY += 1
    if pygame.K_UP in engine.keyboard and engine.keyboard[pygame.K_UP] == True:
        engine.cameraY -= 1
    if pygame.K_RIGHT in engine.keyboard and engine.keyboard[pygame.K_RIGHT] == True:
        engine.SCREEN_DIST += 3
    if pygame.K_LEFT in engine.keyboard and engine.keyboard[pygame.K_LEFT] == True:
        engine.SCREEN_DIST -= 3
        if engine.SCREEN_DIST <= 0:
            engine.SCREEN_DIST = 1
    
    #print(engine.cameraX, engine.cameraY)
    #print(engine.keyboard)
    obj.scale3d((abs(math.sin(FRAMES*0.001)), abs(math.sin(FRAMES*0.001)), abs(math.sin(FRAMES*0.001))))
    obj2.scale3d((1, 0.2 + abs(math.sin(FRAMES*0.001))*0.8, 1))
    obj2.x = 300 + math.sin(FRAMES*0.001)*100
    # display on screen
    screen.fill((0, 0, 0)) # dark mode
    if pygame.K_SPACE in engine.keyboard and engine.keyboard[pygame.K_SPACE] == True:
        screen.fill((255, 255, 255)) # light mode
    pygame.draw.circle(engine.screen, (255, 0, 255), (engine.SCREEN_SIZE[0]/2, engine.SCREEN_SIZE[1]/2), 2)
    for object in engine.objects:
        #object.drawPolygons()
        object.drawWireframe()
        for point in object.points:
            point.drawPoint()
    pygame.display.flip()
    FRAMES += 1
