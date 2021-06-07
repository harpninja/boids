import maya.cmds as cmds
import random
import math
import imp
v = imp.load_source('v', '/lhome/kristina/Documents/code/maya/boids/vector_class.py')   # maya python 2.7 weirdness
width = 100
height = 100
depth = 100  # was 150

class Particle(v.vec3):
    '''
    Class defining a single particle.
    '''
    def __init__(self, name):
        self.name = name
        super(v.vec3, self).__init__()      # Complies with Python 2.7 conventions in Maya.
                                            # Python 3+ is super().__init__(0.0, 0.0, 0.0)

        self.position = v.vec3(random.uniform(0, width), random.uniform(0, height), random.uniform(0, depth))
        self.velocity = v.vec3(math.cos(random.uniform(0.4, 1)), math.sin(random.uniform(0.4, 1)), math.tan(random.uniform(0.4, 1)))
        self.acceleration = v.vec3(0.0, 0.0, 0.0)
        self.size = 1
        self.max_steering_speed = 0.4 * 6
        self.max_steering_force = 0.8 * 2   # was 6
        self.desired_separation = math.pow(self.size, 2) + 6  # was + 3
        self.neighbour_distance = width/2
        self.add_geometry()
        # self.point_boid()
        self.add_shader()

    def __repr__(self):
        return self.name

    def add_shader(self):
        '''
        Create a random coloured shader.
        Apply shader to object geometry.
        '''
        name_shader = 'aiStandardSurface' + self.name
        red = random.uniform(0.0, 0.1)
        green = random.uniform(0.0, 1.0)
        blue = random.uniform(0.3, 1.0)
        cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=name_shader+'SG')
        cmds.shadingNode('aiStandardSurface', asShader=True, name=name_shader)
        cmds.setAttr(name_shader+'.baseColor', red, green, blue, type='double3')
        cmds.setAttr(name_shader+'.base', 0.85)
        cmds.setAttr(name_shader+'.specular', 1)
        cmds.setAttr(name_shader+'.emission', 1)
        cmds.setAttr(name_shader+'.emissionColor', red, green, blue, type='double3')
        cmds.setAttr(name_shader+'.specularColor', red, green, blue, type='double3')
        cmds.connectAttr(name_shader+'.outColor', name_shader+'SG.surfaceShader')
        cmds.sets(self.name, edit=True, forceElement=name_shader+'SG')

    def add_geometry(self):
        '''
        Create boid geometry.
        '''
        # cmds.polyPlatonicSolid(n=self.name, solidType=0)    # dodecahedron
        #cmds.polyCone(n=self.name, sx=24, sy=1, sz=0, ax=[0, -1, 0], rcp=0, cuv=3, ch=1, radius=self.size/2)
        cmds.sphere(n=self.name, radius=self.size)
        # cmds.polyCube(n=self.name)

    def set_key(self, frame):
        '''
        Set keyframe for boid at frame number.
        '''
        cmds.select(self.name)
        cmds.setKeyframe(self.name, t=frame)

    def point_boid(self):
        '''
        Point boid in the direction it is travelling in Maya scene.
        '''
        cmds.select(self.name)
        degrees_tuple = self.velocity.cosine_direction()
        cmds.rotate(degrees_tuple[0], degrees_tuple[1], degrees_tuple[2], absolute=True, componentSpace=True)

    def move_boid(self):
        '''
        Move boid in Maya scene.
        '''
        cmds.select(self.name)
        cmds.move(self.position.x, self.position.y, self.position.z, relative=True)

    def move_boid_absolute(self):
        '''
        Move boid in Maya scene.
        '''
        cmds.select(self.name)
        cmds.move(self.position.x, self.position.y, self.position.z, absolute=True)

    def update(self):
        '''
        Update velocity, position and lifespan for this particle.
        '''
        self.velocity = self.velocity + self.acceleration
        self.position = self.position + self.velocity
        self.acceleration = self.acceleration * 0
        self.move_boid()
        self.point_boid()

    def apply_force(self, force):
        '''
        Add force vector to acceleration vector
        @param {float} force
        '''
        self.acceleration = self.acceleration + force

    def flock(self, others):
        '''
        Apply flocking behaviours.
        '''
        separation_force = self.separate(others)
        separation_force = separation_force * 0.5
        self.apply_force(separation_force)

        alignment_force = self.align(others)
        alignment_force = alignment_force * 0.5
        self.apply_force(alignment_force)

        cohesion_force = self.cohesion(others)
        cohesion_force = cohesion_force * 0.5
        self.apply_force(cohesion_force)

    def seek(self, target):
        '''
        Steer particle towards target.
        Called by cohesion().
        '''
        desired = target - self.position    # point from position to target
        desired = desired.unit_vector()
        desired = desired * self.max_steering_speed
        steer = desired - self.velocity
        steer.limit(self.max_steering_force)
        return steer

    def separate(self, others):
        '''
        Separate self from others.
        Separation is the average of all the vectors pointing away from any close others.
        '''
        sum = v.vec3(0, 0, 0)
        count = 0
        steer = self.velocity

        for other in others:
            d = self.position.distance(other.position)
            if ((d > 0) and (d < self.desired_separation)):
                # calculate vector pointing away from other
                difference = self.position - other.position
                difference = difference.unit_vector()
                difference = difference / d     # weight by distance.  More flee from closer things.
                sum = sum + difference  # average of all vectors pointing away from close particles.
                count += 1
        if count > 0:
            sum = sum / count
            sum = sum.unit_vector()
            sum = sum * self.max_steering_speed     # go this way!
            steer = sum - self.velocity     # steering = desired - velocity
        steer.limit(self.max_steering_force)
        return steer

    def align(self, others):
        '''
        Align self with others.
        '''
        sum = v.vec3(0, 0, 0)
        count = 0

        for other in others:
            d = self.position.distance(other.position)
            if ((d > 0) and (d < self.neighbour_distance)):
                sum = sum + other.velocity
                count += 1
        if count > 0:
            sum = sum / count
            sum = sum.unit_vector()
            sum = sum * self.max_steering_speed     # go this way!
            steer = sum - self.velocity     # steering = desired - velocity
            steer.limit(self.max_steering_force)
            return steer
        else:
            return v.vec3(0, 0, 0)     # if no close boids then steering force is zero

    def cohesion(self, others):
        '''
        Cohesion of self with others.
        '''
        sum = v.vec3(0, 0, 0)
        count = 0

        for other in others:
            d = self.position.distance(other.position)
            if ((d > 0) and (d < self.neighbour_distance)):
                sum = sum + other.position      # sum location of others
                count += 1
        if count > 0:
            sum = sum / count
            return self.seek(sum)
        else:
            return v.vec3(0, 0, 0)     # if no close boids then cohesion force is zero

    def borders(self):
        '''
        Move particle to wrap around borders of drawing area.
        '''
        if self.position.x < -self.desired_separation:
            self.position.x = width + self.desired_separation
        if self.position.y < -self.desired_separation:
            self.position.y = height + self.desired_separation
        if self.position.z < -self.desired_separation:
            self.position.z = depth + self.desired_separation
        if self.position.x > width + self.desired_separation:
            self.position.x = -self.desired_separation
        if self.position.y > height + self.desired_separation:
            self.position.y = -self.desired_separation
        if self.position.z > depth + self.desired_separation:
            self.position.z = -self.desired_separation
        self.move_boid_absolute()
        self.point_boid()

    def borders1(self):
        '''
        Move particle stay within borders of drawing area.
        Not used.
        '''
        if self.position.x > width or self.position.x < 0:
            self.velocity.x = self.velocity.x * -1
        if self.position.y > height or self.position.y < 0:
            self.velocity.y = self.velocity.y * -1
        if self.position.z > depth or self.position.z < 0:
            self.velocity.z = self.velocity.z * -1
        self.move_boid_absolute()
        self.point_boid()

# initialise particle system
boids = []
for a in range(2400):
    name = 'cube' + str(a)
    obj = Particle(name)
    boids.append(obj)

FRAMES = 420
frame = 1
while frame < FRAMES:
    print('frame = ', frame)
    for boid in boids:
        boid.borders()
        boid.flock(boids)
        boid.update()
        boid.set_key(frame)
    frame += 1
