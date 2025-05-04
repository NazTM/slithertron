from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, random, time

# Camera-related variables
camera_pos = (0,500,500)
fovY = 120  # Field of view
GRID_LENGTH = 100  # Length of grid lines
GRID_SIZE = 14
rand_var = 423
game_over = False
score = 0
level = 0

snake_body = [
    [0, 0, 0],
    [-GRID_LENGTH, 0, 0],
    [-2*GRID_LENGTH, 0, 0]
]

snake_dir = [GRID_LENGTH, 0, 0]  # Moving along +X direction
snake_speed = 10  # Frames per movement
frame_counter = 0


player_pos = [0, 0, 0]
player_angle = 0
camera_mode = "third"  

# Entities
powerups = []
enemies = []
num_enemies = 5

# Invisibility
invisible = False
lastx = lasty = lastz = 0

# World Boundaries
min_bound = -GRID_SIZE * GRID_LENGTH // 2
max_bound = GRID_SIZE * GRID_LENGTH // 2


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_grid(GRID_SIZE):
    glBegin(GL_QUADS)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x = (i - GRID_SIZE // 2) * GRID_LENGTH
            y = (j - GRID_SIZE // 2) * GRID_LENGTH
            glColor3f(*(1, 1, 1) if (i + j) % 2 == 0 else (0.7, 0.5, 0.95))
            for dx, dy in [(0, 0), (1, 0), (1, 1), (0, 1)]:
                glVertex3f(x + dx * GRID_LENGTH, y + dy * GRID_LENGTH, 0)
    glEnd()



def draw_snake():
    for i, segment in enumerate(snake_body):
        x, y, z = segment
        glPushMatrix()
        glTranslatef(x, y, z + 5)
        if i == 0:
            glColor3f(0.0, 1.0, 0.0)  # Head = bright green
        else:
            glColor3f(0.2, 0.6, 0.2)  # Body = darker green
        glutSolidCube(GRID_LENGTH * 0.8)
        glPopMatrix()



def draw_border_walls():
    wall_height = 100
    offset = GRID_LENGTH * GRID_SIZE // 2

    walls = [
        ((0.01, 0.9, 1), [(-offset, -offset), (offset, -offset)]),  # Bottom
        ((1, 1, 1), [(-offset, offset), (offset, offset)]),         # Top
        ((0, 0, 1), [(-offset, -offset), (-offset, offset)]),       # Left
        ((0.01, 0.9, 0.01), [(offset, -offset), (offset, offset)])  # Right
    ]

    def draw_wall(color, vertices):
        v1, v2 = vertices
        glColor3f(*color)
        glVertex3f(*v1, 0)
        glVertex3f(*v2, 0)
        glVertex3f(*v2, wall_height)
        glVertex3f(*v1, wall_height)

    glBegin(GL_QUADS)
    for color, vertices in walls:
        draw_wall(color, vertices)
    glEnd()

def colorTranslate(tup1, tup2):
    glColor3f(*tup1)
    glTranslatef(*tup2)

def translateRotate(tup1, tup2):
    glTranslatef(*tup1) 
    glRotatef(*tup2)

def keyboardListener(key, x, y):
    global snake_dir, game_over
    if key == b'r' or key == b'R':
        restart_game()

    if key == b'd' and snake_dir != [-GRID_LENGTH, 0, 0]:
        snake_dir = [GRID_LENGTH, 0, 0]  # → right (positive X)
    elif key == b'a' and snake_dir != [GRID_LENGTH, 0, 0]:
        snake_dir = [-GRID_LENGTH, 0, 0]  # ← left (negative X)
    elif key == b'w' and snake_dir != [0, -GRID_LENGTH, 0]:
        snake_dir = [0, GRID_LENGTH, 0]  # ↑ up (positive Y)
    elif key == b's' and snake_dir != [0, GRID_LENGTH, 0]:
        snake_dir = [0, -GRID_LENGTH, 0]  # ↓ down (negative Y)






def move_snake():
    global snake_body, snake_dir, game_over

    head = snake_body[0]
    new_head = [head[0] + snake_dir[0], head[1] + snake_dir[1], head[2] + snake_dir[2]]

    # Boundary check
    if (new_head[0] < min_bound or new_head[0] > max_bound or
        new_head[1] < min_bound or new_head[1] > max_bound):
        game_over = True
        print("Game Over: Snake hit the wall.")
        return

    # Insert new head and remove tail
    snake_body.insert(0, new_head)
    snake_body.pop()


def setupCamera():
    global lastx, lasty, lastz
    """
    Configures the camera's projection and view settings.
    Uses a perspective projection and positions the camera to look at the target.
    """
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix
    # Set up a perspective projection (field of view, aspect ratio, near clip, far clip)
    gluPerspective(fovY, 1.25, 0.1, 1500) # Think why aspect ration is 1.25?
    glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
    glLoadIdentity()  # Reset the model-view matrix

    if camera_mode == "third":
        # Extract camera position and look-at target
        x, y, z = camera_pos
        # Position the camera and set its orientation
        gluLookAt(x, y, z,  # Camera position
                0, 0, 0,  # Look-at target
                0, 0, 1)  #Up vector flipped
        
last_move_time = time.time()
move_interval = 0.2  # seconds between moves

def idle():
    global last_move_time
    if not game_over:
        current_time = time.time()
        if current_time - last_move_time >= move_interval:
            last_move_time = current_time
            move_snake()
    glutPostRedisplay()

def restart_game():
    global snake_body, snake_dir, score, game_over, last_move_time

    snake_body = [
        [0, 0, 0],
        [-GRID_LENGTH, 0, 0],
        [-2*GRID_LENGTH, 0, 0]
    ]
    snake_dir = [-GRID_LENGTH, 0, 0]
    score = 0
    game_over = False
    last_move_time = time.time()

def specialKeyListener(key, x, y):
    global snake_dir

    if key == GLUT_KEY_RIGHT and snake_dir != [-GRID_LENGTH, 0, 0]:
        snake_dir = [GRID_LENGTH, 0, 0]  # → right (positive X)
    elif key == GLUT_KEY_LEFT and snake_dir != [GRID_LENGTH, 0, 0]:
        snake_dir = [-GRID_LENGTH, 0, 0]  # ← left (negative X)
    elif key == GLUT_KEY_UP and snake_dir != [0, GRID_LENGTH, 0]:
        snake_dir = [0, GRID_LENGTH, 0]  # ↑ up (positive Y)
    elif key == GLUT_KEY_DOWN and snake_dir != [0, -GRID_LENGTH, 0]:
        snake_dir = [0, -GRID_LENGTH, 0]  # ↓ down (negative Y)


def keyboardListener(key, x, y):
    global snake_dir, game_over
    if key == b'r' or key == b'R':
        restart_game()

    if key == b'd' and snake_dir != [-GRID_LENGTH, 0, 0]:
        snake_dir = [GRID_LENGTH, 0, 0]
    elif key == b'a' and snake_dir != [GRID_LENGTH, 0, 0]:
        snake_dir = [-GRID_LENGTH, 0, 0]
    elif key == b'w' and snake_dir != [0, -GRID_LENGTH, 0]:
        snake_dir = [0, GRID_LENGTH, 0]
    elif key == b's' and snake_dir != [0, GRID_LENGTH, 0]:
        snake_dir = [0, -GRID_LENGTH, 0]


def showScreen():
    """
    Display function to render the game scene:
    - Clears the screen and sets up the camera.
    - Draws everything on the screen.
    """
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1000, 800)  # Set viewport size

    setupCamera()  # Configure camera perspective

    # Draw a random points
    glPointSize(20)
    glBegin(GL_POINTS)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glEnd()
    
    draw_grid(GRID_SIZE)
    draw_border_walls()
    draw_snake()


    # Draw text above everything else
    if not game_over:
        draw_text(10, 770, f"Campaign Mode")
        draw_text(10, 750, f"Game Score: {score}")
        draw_text(10, 730, f"Level: {level}")
    else:
        draw_text(10, 760, f"Game is Over. Your score is {score}.")
        draw_text(10, 740, f'Press "R" to RESTART the Game.')

    # Swap buffers for smooth rendering (double buffering)
    glutSwapBuffers()


# Main function to set up OpenGL window and loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1000, 800)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    wind = glutCreateWindow(b"3D OpenGL Intro")  # Create the window

    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)
    #glutMouseFunc(mouseListener)
    glutIdleFunc(idle)  # Register the idle function to move the bullet automatically

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()

