import pyglet, random, math
window = pyglet.window.Window(resizable=True)
window.maximize()
print(window.get_size())

class boid():
    x, y = 0, 0
    angle = 0 
    angle_speed = 15
    speed = 200
    xspeed, yspeed = 0, 0 
    sight= 200
    xsight, ysight = 0, 0
    size=10
    near_edge = False
    cluster=[] #array of positions of nearby entities
    def __init__(self, number, mini, maxi):
        self.number=number
        self.angle = random.randint(0, 360)
        self.xsight, self.ysight = self.sight*math.cos(math.radians(self.angle)), self.sight*math.sin(math.radians(self.angle))
        self.x, self.y = random.randint(mini, maxi), random.randint(mini, maxi)
        self.appearance = pyglet.shapes.Circle(self.x, self.y, radius=self.size, color=(255, 225, 255))
        self.sight_line = pyglet.shapes.Line(self.x, self.y, self.x+self.xspeed, self.y+self.yspeed, width=1, color=(255, 0, 0))
        self.cluster_center = pyglet.shapes.Line(0, 0, 0, 0, width=1, color=(255, 0, 0))
    
    def turn(self):
        self.angle %= 360
        cos, sin = math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))
        self.xspeed, self.yspeed = self.speed*cos, self.speed*sin
        self.xsight, self.ysight = self.sight*cos, self.sight*sin
    
    def treadmill(self):
        #makes entities teleport to opposing border when they touch a border
        #something to be done with modulos here, dont wanna do it
        if self.x >= window.get_size()[0]:
            self.x = 0
        elif self.x <= 0:
            self.x = window.get_size()[0]  
        elif self.y >= window.get_size()[1]:
            self.y = 0
        elif self.y <= 0:
            self.y = window.get_size()[1]

    def detect_obstacles(self):
        #only walls for now
        right = False #boolean value for turning either right or left
        if (self.x-self.sight <= 0 and 90 < self.angle < 270):
            self.near_edge = True
            if self.angle <= 180 and self.y < window.get_size()[1]-self.sight:
                right = True 
        elif (self.x+self.sight >= window.get_size()[0] and (self.angle<90 or self.angle>270)):
            self.near_edge = True
            if self.angle >= 270 and self.y > self.sight:
                right = True
        elif (self.y-self.sight <= 0 and 180 < self.angle < 360):
            self.near_edge = True
            if self.angle <= 270 and self.x > self.sight:
                right = True
        elif (self.y+self.sight >= window.get_size()[1] and 0 < self.angle < 180):
            self.near_edge = True
            if self.angle <= 90 and self.x < window.get_size()[0]-self.sight:
                right = True
        else:
            self.near_edge = False
        #turn according
        if self.near_edge == True:
            if right == True:
                self.angle -= self.angle_speed
                #self.angle -= random.randint(0, 45)
            else:
                self.angle += self.angle_speed
                #self.angle += random.randint(0, 45)

    def smoothturn(self, angle): #slows down the turn when the angle to turn is geting small with a slightly modified logistic function
        steepness = 0.05
        if -self.angle_speed <= angle <= self.angle_speed:
            return abs(2/(1+math.exp(-steepness*angle))-1)
        else:
            return 1

    def assess(self):
        rows = len(self.cluster)
        if rows>0 and self.near_edge == False:
            mean_x = (sum([self.cluster[i][0] for i in range(rows)])+self.x)/(rows+1) #center of the cluster (average of positions)
            mean_y = (sum([self.cluster[i][1] for i in range(rows)])+self.y)/(rows+1)
            mean_xspeed = (sum([self.cluster[i][2] for i in range(rows)])+self.xspeed)/(rows+1) #mean speed vector
            mean_yspeed = (sum([self.cluster[i][3] for i in range(rows)])+self.yspeed)/(rows+1)
            mean_dir = (sum([self.cluster[i][4] for i in range(rows)])+self.angle)/(rows+1)# mean direction angle of all entities in the cluster
            mean_angle = math.degrees(math.atan2(mean_yspeed, mean_xspeed))
            center_distance = math.hypot(mean_x, mean_y)
            center_angle = vector_angle(self.x-mean_x, self.y-mean_y, center_distance, self.xspeed, self.yspeed, self.speed)
            #if too far from the center of the cluster, get closer
            print(center_angle)
            #align with average direction of cluster by finding the shortest angle path:
            direction = ((self.angle-mean_angle+180)%360)-180
            if direction > 0:
                self.angle-=self.angle_speed*self.smoothturn(direction)
            elif direction < 0:
                self.angle+=self.angle_speed*self.smoothturn(direction)


            self.cluster_center = pyglet.shapes.Line(mean_x, mean_y, mean_x+(100*math.cos(math.radians(mean_angle))), mean_y+(100*math.sin(math.radians(mean_angle))), width=1, color=(0, 0, 255)) #draws vector starting at position center oriented with mean cluster angle
        else:
            self.cluster_center = pyglet.shapes.Line(0, 0, 0, 0, width=1, color=(255, 0, 0))
        self.cluster = []

    def update(self, dt):
        if self.near_edge == False: self.assess()
        self.treadmill()
        #self.detect_obstacles()
        self.turn()#can be optimized
        self.x += self.xspeed*dt
        self.y += self.yspeed*dt
        self.appearance = pyglet.shapes.Circle(self.x, self.y, radius=self.size, color=(255, 225, 255))
        #self.speed_line = pyglet.shapes.Line(self.x, self.y, self.x+self.xspeed, self.y+self.yspeed, width=1, color=(255, 0, 0))
        self.sight_line = pyglet.shapes.Line(self.x, self.y, self.x+self.xsight, self.y+self.ysight, width=1, color=(255, 0, 0))

def vector_angle(x1, y1, norm1, x2, y2, norm2): #gets the angle between two 2d vectors with a dot product
    return math.degrees(math.acos((x1*x2+y1*y2)/(norm1*norm2)))

n=20
creation = [boid(i,100,900) for i in range(n)]

def distances(array):
    square = boid.sight*2 #verify if its within a "square" distance first, easier to calculate
    n = len(array)
    for i in range(n):
        for j in range(i+1, n):
            if abs(array[j].x-array[i].x) < square and abs(array[j].y-array[i].y) < square:
                if math.hypot(array[j].x-array[i].x, array[j].y-array[i].y)<=boid.sight:
                    #pyglet.shapes.Line(array[i].x, array[i].y, array[j].x, array[j].y, width=1, color=(100, 100, 100)).draw()
                    array[i].cluster.append([array[j].x, array[j].y, array[j].xspeed, array[j].yspeed, array[j].angle])
                    array[j].cluster.append([array[i].x, array[i].y, array[i].xspeed, array[i].yspeed, array[i].angle])

def update(dt):
    for boid in creation:
        boid.update(dt)

@window.event
def on_draw():
    window.clear()
    distances(creation)
    for boid in creation:
        boid.appearance.draw()
        boid.sight_line.draw()
        #boid.cluster_center.draw()

pyglet.clock.schedule_interval(update, 1/30.0)
pyglet.app.run()
