import sys, math, random
try:
    import pygame
except ModuleNotFoundError:
    # if pygame is not installed, it installs it
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame
    del sys.modules["subprocess"]


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
        self.targetFPS = 0
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.keyboard = {}
        self.objects = []
    
    def updateClock(self):
        """
        Update the delta time (dt) : time difference since last clock.tick() call
        -> dt is used to control and keep a constant speed in the game even if the framerate varies
        """
        self.dt = self.clock.tick(self.targetFPS)/1000

    def create3dObject(self, pos, pointsCoordinates, faces=[], color=(255, 0, 0)):
        """
        pos: position of the object in the 3D scene
        points: list of tuples which are point's 3D coordinates relative to object's ones
        faces: !order sensitive! list of indexes of points that belong to the face
        ex: [(0, 0, 0), (0, 0, 10), (0, 10, 0), (10, 0, 0)]
        Return a reference to the created object
        """
        self.objects.append(Object(pos, pointsCoordinates, faces, self, color))
        return self.objects[-1]

    def open3dObject(self, sourceFile: str, pos=(0, 0, 0)):
        """
        sourceFile: path to the object file
        pos: position of the new object in the 3D scene
        Open the file, extracts the coordinates and creates a new Object
        Return a reference of the created object
        """
        try:
            with open(sourceFile, "r") as f:
                if sourceFile[-3:] == "obj":
                    coords = []
                    faces = []
                    for line in f:
                        if line[0:2] == "v ":
                            coords.append(tuple((-float(line.strip("v ").split()[0]), -float(line.strip("v ").split()[1]), -float(line.strip("v ").split()[2]))))
                        elif line[0:2] == "f ":
                            face = line.strip("f ").strip("\n").split(" ")
                            for item in range(len(face)):
                                face[item] = int(face[item].split("/")[0])-1

                            faces.append(tuple(face))
                elif sourceFile[-3:] == "dae":
                    geometryName = "Mesh"
                    coords = []
                    faces = []
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

        return self.create3dObject(pos, coords, faces, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))


class Object:

    def __init__(self, pos, pointsCoordinates, faces, engine, color):
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
        self.faces = faces
        self.points = []
        for point in pointsCoordinates:
            self.create3dPoint(point)

    def create3dPoint(self, pos):
        self.points.append(Point(pos, self, self.engine))
        return self.points[-1]
    
    def setScale(self, scalingFactors=(1, 1, 1)):
        """
        scalingFactors: 3d tuple to rescale the object on the 3 axis
        Scales the object
        """
        self.scale = scalingFactors
        for point in self.points:
            point.x = point.originX*self.scale[0]
            point.y = point.originY*self.scale[1]
            point.z = point.originZ*self.scale[2]
        self.width *= self.scale[0]
        self.height *= self.scale[1]
        self.depth *= self.scale[2]

    def setRotate(self, rotationAngle=(0, 0, 0)):
        """
        rotatingAngle: tuple of angles (in radian) | 1 angle for each 1 axis to rotate around
        Rotates each point of the object
        """
        self.direction = rotationAngle
        for point in self.points:
            # X axis
            angle = math.atan2(point.y, point.z) + math.radians(self.direction[0])
            dist = math.sqrt(point.y**2 + point.z**2)
            point.y = math.sin(angle) * dist
            point.z = math.cos(angle) * dist
            # Y axis
            angle = math.atan2(point.x, point.z) + math.radians(self.direction[1])
            dist = math.sqrt(point.x**2 + point.z**2)
            point.x = math.sin(angle) * dist
            point.z = math.cos(angle) * dist
            # Z axis
            angle = math.atan2(point.y, point.x) + math.radians(self.direction[2])
            dist = math.sqrt(point.x**2 + point.y**2)
            point.x = math.cos(angle) * dist
            point.y = math.sin(angle) * dist

            #deltaX = point.x - self.x
            #deltaY = point.y - self.y
            # deltaZ = point.z# - self.z
            #distXY = math.sqrt(deltaX**2 + deltaY**2)
            # distXZ = math.sqrt(deltaX**2 + deltaZ**2)
            # distYZ = math.sqrt(deltaY**2 + deltaZ**2)
            #rotatedX = math.cos(math.radians(self.direction[2]))*distXY
            #rotatedY = math.sin(math.radians(self.direction[2]))*distXY
            # rotatedZ = math.sin(math.radians(self.direction[1]))*distXZ + math.cos(math.radians(self.direction[0]))
            #point.x = self.x + rotatedX
            #point.y = self.y + rotatedY
            # point.z = self.z + rotated Z
        
    def drawWireframe(self):
        for point in self.points:
            point.projectPointOnScreen()

        if len(self.faces) > 0:
            for face in self.faces:
                for iPoint in range(len(face)-1):
                    pygame.draw.line(self.engine.screen, self.color, (self.points[face[iPoint]].projectedX, self.points[face[iPoint]].projectedY), (self.points[face[iPoint+1]].projectedX, self.points[face[iPoint+1]].projectedY))            
                pygame.draw.line(self.engine.screen, self.color, (self.points[face[0]].projectedX, self.points[face[0]].projectedY), (self.points[face[-1]].projectedX, self.points[face[-1]].projectedY))            
        else:
            for pointA in self.points:
                for pointB in self.points:
                    if not pointB is pointA:
                        if pointA.z-self.engine.cameraZ > -self.engine.SCREEN_DIST and pointB.z-self.engine.cameraZ > -self.engine.SCREEN_DIST:
                            pygame.draw.line(self.engine.screen, self.color, (pointA.projectedX, pointA.projectedY), (pointB.projectedX, pointB.projectedY))

    def drawPolygons(self):
        for face in self.faces:
            try:
                pygame.draw.polygon(self.engine.screen, self.color, [(self.points[i].projectedX, self.points[i].projectedY) for i in face if self.points[i].z-self.engine.cameraZ > -self.engine.SCREEN_DIST//1.5])
            except:
                pass
            # (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                

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
        # print("x : ", self.x)
        # print("y : ", self.y)
        # print("z : ", self.z)
        self.projectedX = 0
        self.projectedY = 0

    def projectPointOnScreen(self):
        """
        Calculates the projectedX and projectedY coordinates
        It converts the 3D coords in the world to the 2d coords on the screen
        """
        if self.z-self.engine.cameraZ > -self.engine.SCREEN_DIST:
            self.projectedX = self.engine.SCREEN_DIST * (self.x + self.parentObject.x - self.engine.cameraX) / (self.engine.SCREEN_DIST + self.z + self.parentObject.z - self.engine.cameraZ) + self.engine.SCREEN_SIZE[0]/2
            self.projectedY = self.engine.SCREEN_DIST * (self.y + self.parentObject.y - self.engine.cameraY) / (self.engine.SCREEN_DIST + self.z + self.parentObject.z - self.engine.cameraZ) + self.engine.SCREEN_SIZE[1]/2

    def drawPoint(self):
        self.projectPointOnScreen()
        if self.z-self.engine.cameraZ > -self.engine.SCREEN_DIST:
            pygame.draw.circle(self.engine.screen, (255 - self.parentObject.color[0], 255 - self.parentObject.color[1], 255 - self.parentObject.color[2]), (self.projectedX, self.projectedY), 2)


pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption('TRUITE ENGINE • 3D GRAPHICS WIREFRAME')
engine = Engine(screen)
engine.create3dObject((-50, 0, 0), [(0, 0, 0), (100, 0, 0), (100, 100, 0), (0, 100, 0), (0, 0, 100), (100, 0, 100), (100, 100, 100), (0, 100, 100)], [(0, 1, 2, 3), (4, 5, 6, 7), (0, 3, 7, 4)], (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
# engine.create3dObject((0, 300, 50), [(0, 0, 0), (100, 0, 0), (100, 0, 100), (0, 0, 100), (50, -100, 50)], [], (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
# engine.create3dObject((300, 0, 0), [(25, 0, 0), (75, 0, 0), (100, 0, 25), (100, 0, 75), (75, 0, 100), (25, 0, 100), (0, 0, 75), (0, 0, 25), (25, 300, 0), (75, 300, 0), (100, 300, 25), (100, 300, 75), (75, 300, 100), (25, 300, 100), (0, 300, 75), (0, 300, 25)], [], (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
# engine.create3dObject((200, 50, 150), [(0, 0, 0), (100, 0, 0), (100, 100, 0), (0, 100, 0), (0, 0, 100), (100, 0, 100), (100, 100, 100), (0, 100, 100)], [], (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
suz = engine.open3dObject("3dModels/suzanne.obj", (150, 500, 0))
engine.open3dObject("3dModels/sphere.obj", (200, 50, 0))
engine.open3dObject("3dModels/cube.obj", (1000, -300, 500))
engine.open3dObject("3dModels/cube.obj", (500, 100, -500))
engine.open3dObject("3dModels/cube.obj", (40, -500, 100))
engine.open3dObject("3dModels/cube.obj", (1000, -0, 0))
suz.setScale((200, 200, 100))
FPSfont = pygame.font.Font("freesansbold.ttf", 15)
FRAMES = 0
while True:
    engine.updateClock()
    # print(f"\rFPS: {1/engine.dt:.2f}", end="")
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
        engine.cameraX += 1000*engine.dt
    if pygame.K_q in engine.keyboard and engine.keyboard[pygame.K_q] == True:
        engine.cameraX -= 1000*engine.dt
    if pygame.K_z in engine.keyboard and engine.keyboard[pygame.K_z] == True:
        engine.cameraZ += 1000*engine.dt
    if pygame.K_s in engine.keyboard and engine.keyboard[pygame.K_s] == True:
        engine.cameraZ -= 1000*engine.dt
    if pygame.K_LSHIFT in engine.keyboard and engine.keyboard[pygame.K_LSHIFT] == True:
        engine.cameraY += 1000*engine.dt
    if pygame.K_SPACE in engine.keyboard and engine.keyboard[pygame.K_SPACE] == True:
        engine.cameraY -= 1000*engine.dt
    if pygame.K_RIGHT in engine.keyboard and engine.keyboard[pygame.K_RIGHT] == True:
        engine.SCREEN_DIST += 3000*engine.dt
    if pygame.K_LEFT in engine.keyboard and engine.keyboard[pygame.K_LEFT] == True:
        engine.SCREEN_DIST -= 3000*engine.dt
        if engine.SCREEN_DIST <= 0:
            engine.SCREEN_DIST = 1
    
    #print(engine.cameraX, engine.cameraY)
    #print(engine.keyboard)
    # obj.setScale((abs(math.sin(FRAMES*0.001)), abs(math.sin(FRAMES*0.001)), abs(math.sin(FRAMES*0.001))))
    # obj2.setScale((1, 0.2 + abs(math.sin(FRAMES*0.001))*0.8, 1))
    # obj3.x = 200 + math.sin(FRAMES*0.001)*100
    # obj3.y = 50 + math.cos(FRAMES*0.001)*100
    # display on screen
    screen.fill((0, 0, 0)) # dark mode
    if pygame.K_l in engine.keyboard and engine.keyboard[pygame.K_l] == True:
        screen.fill((255, 255, 255)) # light mode
    pygame.draw.circle(engine.screen, (255, 0, 255), (engine.SCREEN_SIZE[0]/2, engine.SCREEN_SIZE[1]/2), 2)
    for object in engine.objects:
        # object.drawPolygons()
        object.drawWireframe()
        object.setRotate((300*engine.dt, 300*engine.dt, 300*engine.dt))
        # for point in object.points:
        #     point.drawPoint()
    screen.blit(FPSfont.render(f"{engine.clock.get_fps():.2f}", True, (255, 255, 255)), (10, 10))
    pygame.display.flip()
    FRAMES += 1
