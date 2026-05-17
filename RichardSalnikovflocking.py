
#RichardSalnikov

import pygame
#Used for: opening a window, drawing graphics, handling input, timing

import random
#Used to: spawn boids at random positions, give random starting directions

import math
#Used for: trigonometry, vector calculations, square roots, angles

# Settings

WIDTH, HEIGHT = 1000, 700
NUM_BOIDS = 80
#Defines: screen size, number of boids

##_________________________
MAX_SPEED = 5
MAX_FORCE = 0.08
#These are important.
# MAX_SPEED: Limits how fast a boid can move.
# Without this: boids would accelerate forever, simulation becomes chaotic
# MAX_FORCE: Limits steering strength.
# Without this: boids turn instantly movement looks robotic.
# This creates:smooth curves

#_______________________________________________________________________

NEIGHBOR_RADIUS = 50
SEPARATION_RADIUS = 25
#Neighbor Radius: How far a boid can "see".
#Inside this range: alignment works, cohesion works
#
#Separation Radius:
#Smaller radius for collision avoidance.
#Inside this range the boids repel each other

###________
ALIGNMENT_WEIGHT = 1.0
COHESION_WEIGHT = 0.8
SEPARATION_WEIGHT = 1.5

#Obstacle Settings
OBSTACLE_RADIUS = 15
#Radius of the movable obstacle/dot

#obstacle_pos = [WIDTH // 2, HEIGHT // 2]
obstacle_pos = [500, 500]

#Starts obstacle in center of screen





# These scale the behaviors.
# The final steering force is: # F=aA+cC+sS



# Where:
# A = alignment
# C = cohesion
# S = separation




##_____________________________
pygame.init()
#pygame.init() Starts all pygame systems.

screen = pygame.display.set_mode((WIDTH, HEIGHT))
#This creates the game window.

clock = pygame.time.Clock()
#Controls FPS.
#Later: clock.tick(60)
#limits simulation to: 60 frames per second


# Vector Helpers

def limit_vector(vec, max_value):

##Limits vector length.
#
# A vector has: direction and magnitude.
# Magnitude is the speed/force strength.
# If magnitude becomes too large: movement explodes

    length = math.hypot(vec[0], vec[1])

### Computes vector magnitude:
# sqrt(x_2 + y_2)

    if length > max_value:

        scale = max_value / length

### If vector is too large, then it must be shrunk proportionally
#
# This preserves direction.

        return [vec[0] * scale, vec[1] * scale]

    return vec


def normalize(vec):

    length = math.hypot(vec[0], vec[1])

    if length == 0:
        return [0, 0]

### Converts vector into unit vector
#
# Formula:
# v^ = v / |v|
#
# Keeps direction
# Makes magnitude = 1

    return [vec[0] / length, vec[1] / length]


#######__________________________________________
# Boid Class


class Boid:

    def __init__(self):

        self.position = [
            random.uniform(0, WIDTH),
            random.uniform(0, HEIGHT)
        ]

## Random spawn location.

        angle = random.uniform(0, math.pi * 2)

## Random angle between:
# 0 → 2*pi
#
# Full circle

        self.velocity = [
            math.cos(angle) * MAX_SPEED,
            math.sin(angle) * MAX_SPEED
        ]

### Converts angle into movement vector
#
# Uses unit circle: (cos(theta), sin(theta))

        self.acceleration = [0, 0]

### Stores forces for current frame
# This is the force accumulator


    def update(self):


### Physics integration step

# Using Euler integration

        self.velocity[0] += self.acceleration[0]
        self.velocity[1] += self.acceleration[1]

### Implements:
# v(t+1) = v(t) + a*(delta)t

        self.velocity = limit_vector(self.velocity, MAX_SPEED)

### Caps velocity
#
# Prevents infinite acceleration

        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

### Implements:

# x(t+1) = x(t) + v*(delta)t

        self.acceleration = [0, 0]

### IMPORTANT
#
# Forces only apply for ONE frame
#
# Next frame: recomputes all flocking forces again

        self.wrap_edges()

### Teleports boids across screen edges
#
# Without this:
# the boids will disappear forever


    def apply_force(self, force):

        self.acceleration[0] += force[0]
        self.acceleration[1] += force[1]

### This adds force into acceleration accumulator
#
# It is equivalent to: F_total = F1 + F2 + F3


    def flock(self, boids):

### Main AI behavior
#
# It calculates:
# alignment
# cohesion
# separation
# obstacle avoidance
#
# Then combines them

        alignment = self.align(boids)
        cohesion = self.cohesion(boids)
        separation = self.separation(boids)
        avoidance = self.avoid_obstacle()

        alignment[0] *= ALIGNMENT_WEIGHT
        alignment[1] *= ALIGNMENT_WEIGHT

        cohesion[0] *= COHESION_WEIGHT
        cohesion[1] *= COHESION_WEIGHT

        separation[0] *= SEPARATION_WEIGHT
        separation[1] *= SEPARATION_WEIGHT

### Obstacle avoidance gets extra strength
#
# Makes boids strongly avoid obstacle

        avoidance[0] *= 2.5
        avoidance[1] *= 2.5

        self.apply_force(alignment)
        self.apply_force(cohesion)
        self.apply_force(separation)
        self.apply_force(avoidance)


    def align(self, boids):

### The Goal is to match neighbor velocity

        steering = [0, 0]
        total = 0

        for other in boids:

            d = distance(self.position, other.position)

### Distance formula:
# sqrt((x_2 - x_1)^2 + (y_2 - y_1)^2)

            if other != self and d < NEIGHBOR_RADIUS:

                steering[0] += other.velocity[0]
                steering[1] += other.velocity[1]

### Adds all neighbor velocities
#
# Computes:
# v_avg = (Sum)v / n

                total += 1

        if total > 0:

            steering[0] /= total
            steering[1] /= total

            steering = normalize(steering)

            steering[0] *= MAX_SPEED
            steering[1] *= MAX_SPEED

            steering[0] -= self.velocity[0]
            steering[1] -= self.velocity[1]

### The steering formula:
# v_steer = v_desired - v_current
#
# Produces smooth turning

            steering = limit_vector(steering, MAX_FORCE)

        return steering


    def cohesion(self, boids):

### My goal is to move toward center of flock

        steering = [0, 0]
        total = 0

        for other in boids:

            d = distance(self.position, other.position)

            if other != self and d < NEIGHBOR_RADIUS:

                steering[0] += other.position[0]
                steering[1] += other.position[1]

### Computing the flock center:
# p_avg = Sum p / n

                total += 1

        if total > 0:

            steering[0] /= total
            steering[1] /= total

            steering[0] -= self.position[0]
            steering[1] -= self.position[1]

### This creates a vector toward flock center

            steering = normalize(steering)

            steering[0] *= MAX_SPEED
            steering[1] *= MAX_SPEED

            steering[0] -= self.velocity[0]
            steering[1] -= self.velocity[1]

            steering = limit_vector(steering, MAX_FORCE)

        return steering


    def separation(self, boids):

### The goal is to prevent collisions

        steering = [0, 0]
        total = 0

        for other in boids:

            d = distance(self.position, other.position)

            if other != self and d < SEPARATION_RADIUS:

                diff = [
                    self.position[0] - other.position[0],
                    self.position[1] - other.position[1]
                ]

### Vector is now pointing away from neighbor

                if d != 0:

                    diff[0] /= d
                    diff[1] /= d

### Closer boids create stronger repulsion, approximates inverse-distance force

                steering[0] += diff[0]
                steering[1] += diff[1]

                total += 1

        if total > 0:

            steering[0] /= total
            steering[1] /= total

            steering = normalize(steering)

            steering[0] *= MAX_SPEED
            steering[1] *= MAX_SPEED

            steering[0] -= self.velocity[0]
            steering[1] -= self.velocity[1]

            steering = limit_vector(steering, MAX_FORCE)

        return steering


    def avoid_obstacle(self):

### My Goal here is to avoid the movable obstacle/dot

        steering = [0, 0]

        d = distance(self.position, obstacle_pos)

### Only avoid obstacle if close enough

        if d < OBSTACLE_RADIUS + 60:

            steering[0] = self.position[0] - obstacle_pos[0]
            steering[1] = self.position[1] - obstacle_pos[1]

### Creates vector away from the obstacle

            if d != 0:

                steering[0] /= d
                steering[1] /= d

### Closer obstacle = stronger repulsion

            steering = normalize(steering)

            steering[0] *= MAX_SPEED
            steering[1] *= MAX_SPEED

            steering[0] -= self.velocity[0]
            steering[1] -= self.velocity[1]


# v_steer = desired_velocity - current_velocity

            steering = limit_vector(steering, MAX_FORCE * 3)

### Stronger than normal steering
# Emergency avoidance force

        return steering


    def wrap_edges(self):

### Screen looping, it creates toroidal space: left connects to right, top connects to bottom

        if self.position[0] > WIDTH:
            self.position[0] = 0

        elif self.position[0] < 0:
            self.position[0] = WIDTH

        if self.position[1] > HEIGHT:
            self.position[1] = 0

        elif self.position[1] < 0:
            self.position[1] = HEIGHT


    def draw(self, surface):

### Renders boid triangle

        angle = math.atan2(
            self.velocity[1],
            self.velocity[0]
        )

### Computes facing direction from velocity

        size = 10

        points = [

            (
                self.position[0] + math.cos(angle) * size,
                self.position[1] + math.sin(angle) * size
            ),

            (
                self.position[0] + math.cos(angle + 2.5) * size,
                self.position[1] + math.sin(angle + 2.5) * size
            ),

            (
                self.position[0] + math.cos(angle - 2.5) * size,
                self.position[1] + math.sin(angle - 2.5) * size
            )
        ]

### This should generate forward-facing triangle
# Boid visually points where it flies

        pygame.draw.polygon(
            surface,
            (255, 255, 255),
            points
        )



# Utility Functions

def distance(a, b):

### Euclidean distance formula:
# sqrt((x_2 - x_1)^2 + (y_2 - y_1)^2)

    return math.hypot(
        a[0] - b[0],
        a[1] - b[1]
    )



# Main part

boids = [Boid() for _ in range(NUM_BOIDS)]

running = True

while running:

    clock.tick(60)

### Limits simulation to 60 FPS

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

### Keyboard input for moving obstacle

    keys = pygame.key.get_pressed()

    speed = 5

    if keys[pygame.K_LEFT]:
        obstacle_pos[0] -= speed

    if keys[pygame.K_RIGHT]:
        obstacle_pos[0] += speed

    if keys[pygame.K_UP]:
        obstacle_pos[1] -= speed

    if keys[pygame.K_DOWN]:
        obstacle_pos[1] += speed

### Arrow keys move the obstacle

    screen.fill((20, 20, 30))

### Clears screen every frame
#
# Prevents trails

### Drawing the movable obstacle

    pygame.draw.circle(
        screen,
        (255, 50, 60),
        (int(obstacle_pos[0]), int(obstacle_pos[1])),
        OBSTACLE_RADIUS
    )

### For the red obstacle dot
# Boids avoid touching it

    for boid in boids:

        boid.flock(boids)
        boid.update()
        boid.draw(screen)

### Each boid: Calculates steering, updates physics, draws itself

    pygame.display.flip()

### Updates entire screen

pygame.quit()
