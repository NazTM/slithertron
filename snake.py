from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

snake_body = [(0, 0, 0)]
snake_dir = (0, 0, 10)
snake_max_length = 8

fovY = 100
GRID_LENGTH = 600
camera_mode = "third"

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_cube(x, y, z, size=20):
    glPushMatrix()
    glTranslatef(x, y, z)
    glutSolidCube(size)
    glPopMatrix()

def draw_snake():
    glColor3f(0, 1, 0)
    for segment in snake_body:
        draw_cube(*segment, size=20)

def draw_shapes():
    glPushMatrix()
    glColor3f(1, 0, 0)
    glTranslatef(0, 0, 0)
    glutSolidCube(60)
    glTranslatef(0, 0, 100)
    glColor3f(0, 1, 0)
    glutSolidCube(60)
    glColor3f(1, 1, 0)
    gluCylinder(gluNewQuadric(), 40, 5, 150, 10, 10)
    glTranslatef(100, 0, 100)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 40, 5, 150, 10, 10)
    glColor3f(0, 1, 1)
    glTranslatef(300, 0, 100)
    gluSphere(gluNewQuadric(), 80, 10, 10)
    glPopMatrix()

def keyboardListener(key, x, y):
    global camera_mode
    if key == b'c':
        camera_mode = "first" if camera_mode == "third" else "third"

def specialKeyListener(key, x, y):
    pass

def mouseListener(button, state, x, y):
    pass

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    head_x, head_y, head_z = snake_body[0]
    if camera_mode == "third":
        gluLookAt(head_x - 150, 200, head_z - 150, head_x, 0, head_z, 0, 1, 0)
    else:
        gluLookAt(head_x, head_y + 10, head_z, head_x + snake_dir[0], head_y, head_z + snake_dir[2], 0, 1, 0)

def idle():
    head = snake_body[0]
    dx, dy, dz = snake_dir
    new_head = (head[0] + dx, head[1] + dy, head[2] + dz)
    snake_body.insert(0, new_head)
    if len(snake_body) > snake_max_length:
        snake_body.pop()
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()
    glPointSize(20)
    glBegin(GL_POINTS)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glEnd()
    glBegin(GL_QUADS)
    glColor3f(1, 1, 1)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(0, GRID_LENGTH, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(-GRID_LENGTH, 0, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(0, -GRID_LENGTH, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(GRID_LENGTH, 0, 0)
    glColor3f(0.7, 0.5, 0.95)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, GRID_LENGTH, 0)
    glEnd()
    draw_text(10, 770, f"Snake Length: {len(snake_body)} | View: {camera_mode}")
    draw_snake()
    draw_shapes()
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Snake with Camera Modes")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()
