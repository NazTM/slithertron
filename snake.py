from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

camera_mode = 'third'  # Modes: 'third', 'first'
snake = [(0, 0, 0)]  # List of segments, head is first
snake_dir = (0, 0, 10)  # Movement direction
snake_length = 5
frame_count = 0

fovY = 100
GRID_LENGTH = 600

def draw_cube(x, y, z, size=20):
    glPushMatrix()
    glTranslatef(x, y, z)
    glutSolidCube(size)
    glPopMatrix()

def draw_snake():
    glColor3f(0, 1, 0)
    for segment in snake:
        draw_cube(segment[0], segment[1], segment[2], 20)

def update_snake():
    global snake
    head_x, head_y, head_z = snake[0]
    dx, dy, dz = snake_dir
    new_head = (head_x + dx, head_y + dy, head_z + dz)
    snake.insert(0, new_head)
    if len(snake) > snake_length:
        snake.pop()

def keyboardListener(key, x, y):
    global camera_mode
    if key == b'c':
        camera_mode = 'first' if camera_mode == 'third' else 'third'

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    head_x, head_y, head_z = snake[0]
    if camera_mode == 'third':
        gluLookAt(head_x - 150, 200, head_z - 150, head_x, 0, head_z, 0, 1, 0)
    else:
        gluLookAt(head_x, 20, head_z, head_x + snake_dir[0], 20, head_z + snake_dir[2], 0, 1, 0)

def draw_environment():
    glColor3f(0.6, 0.6, 0.6)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, -10, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH, -10, -GRID_LENGTH)
    glVertex3f(GRID_LENGTH, -10, GRID_LENGTH)
    glVertex3f(-GRID_LENGTH, -10, GRID_LENGTH)
    glEnd()

def idle():
    global frame_count
    frame_count += 1
    if frame_count % 5 == 0:
        update_snake()
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, 1000, 800)
    setupCamera()

    draw_environment()
    draw_snake()

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"3D Snake Game - Mode Switch")

    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()
