from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, random, time

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
GRID_SIZE = 600
CELL_SIZE = 37

snake = [(0, 0)]
snake_dir = (1, 0)
snake_speed = 1.5  
snake_grow = 0
snake_radius = 12

food_pos = (100, 100)
score = 0

camera_mode = None  # None = choose, 1 = third-person, 2 = first-person
first_person = False
game_over = False

camera_pos = (0, 600, 600)
fovY = 90

level = 1
powerup_timer = 0
powerup_pos = None
shrink_timer = 0
shrink_pos = None
barriers = []

def reset_game():
    global snake, snake_dir, snake_grow, food_pos, score, game_over, level, powerup_pos, shrink_pos, barriers
    snake = [(0, 0)]
    snake_dir = (1, 0)
    snake_grow = 0
    food_pos = (random.randint(-GRID_SIZE // 2, GRID_SIZE // 2), random.randint(-GRID_SIZE // 2, GRID_SIZE // 2))
    score = 0
    game_over = False
    level = 1
    powerup_pos = None
    shrink_pos = None
    barriers = []

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

def draw_grid():
    glBegin(GL_QUADS)
    for i in range(-GRID_SIZE, GRID_SIZE, CELL_SIZE):
        for j in range(-GRID_SIZE, GRID_SIZE, CELL_SIZE):
            if (i + j) // CELL_SIZE % 2 == 0:
                glColor3f(0.1, 0.1, 0.1)
            else:
                glColor3f(0.2, 0.2, 0.2)
            glVertex3f(i, j, 0)
            glVertex3f(i + CELL_SIZE, j, 0)
            glVertex3f(i + CELL_SIZE, j + CELL_SIZE, 0)
            glVertex3f(i, j + CELL_SIZE, 0)
    glEnd()

def draw_snake():
    glColor3f(0, 1, 0)
    for x, y in snake:
        glPushMatrix()
        glTranslatef(x, y, snake_radius)
        glutSolidSphere(snake_radius, 16, 16)
        glPopMatrix()

def draw_food():
    glColor3f(0, 1, 0 if score == 8 else 1)  # Green if transition food
    glPushMatrix()
    glTranslatef(food_pos[0], food_pos[1], snake_radius)
    glutSolidSphere(snake_radius, 16, 16)
    glPopMatrix()

def draw_powerups():
    global powerup_pos, shrink_pos
    if powerup_pos:
        glColor3f(0, 0, 1)
        glPushMatrix()
        glTranslatef(powerup_pos[0], powerup_pos[1], snake_radius)
        glutSolidSphere(snake_radius, 16, 16)
        glPopMatrix()
    if shrink_pos:
        glColor3f(1, 0.5, 0)
        glPushMatrix()
        glTranslatef(shrink_pos[0], shrink_pos[1], snake_radius)
        glutSolidSphere(snake_radius, 16, 16)
        glPopMatrix()

def draw_barriers():
    glColor3f(0.8, 0.1, 0.1)
    for x, y in barriers:
        glPushMatrix()
        glTranslatef(x, y, 20)
        glScalef(20, 20, 40)
        glutSolidCube(1)
        glPopMatrix()

def draw_obstacles():
    if level == 2:
        glColor3f(0.5, 0.2, 0.7)
        for i in range(-200, 201, 100):
            glPushMatrix()
            glTranslatef(i, 0, 20)
            glScalef(20, 100, 40)
            glutSolidCube(1)
            glPopMatrix()

def draw_walls():
    def wall(x, y, w, h, color):
        glColor3f(*color)
        glPushMatrix()
        glTranslatef(x, y, 30)
        glScalef(w, h, 60)
        glutSolidCube(1)
        glPopMatrix()

    s = GRID_SIZE
    wall(0, -s - 10, s * 2, 10, (0.2, 0.3, 1))
    wall(0,  s + 10, s * 2, 10, (0.2, 1, 0.3))
    wall(-s - 10, 0, 10, s * 2, (1, 0.2, 0.2))
    wall( s + 10, 0, 10, s * 2, (1, 1, 0.2))

def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, WINDOW_WIDTH / WINDOW_HEIGHT, 1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if camera_mode == 2:  # first-person
        head_x, head_y = snake[0]
        dir_x, dir_y = snake_dir
        cx = head_x
        cy = head_y
        gluLookAt(cx, cy, 60, cx + dir_x * 20, cy + dir_y * 20, 60, 0, 0, 1)
    else:  # third-person
        x, y, z = camera_pos
        gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)

def update_snake():
    global snake, food_pos, score, snake_grow, game_over, level, powerup_pos, shrink_pos, powerup_timer, shrink_timer, barriers, snake_speed
    if game_over or camera_mode is None:
        return

    head_x, head_y = snake[0]
    dir_x, dir_y = snake_dir
    new_head = (round(head_x + dir_x * snake_speed), round(head_y + dir_y * snake_speed))

    if new_head in snake and camera_mode == 2:
        game_over = True
        return

    half_grid = GRID_SIZE
    if abs(new_head[0]) > half_grid or abs(new_head[1]) > half_grid:
        game_over = True
        return

    if level == 2:
        for bx, by in barriers:
            if abs(new_head[0] - bx) < snake_radius * 2 and abs(new_head[1] - by) < snake_radius * 2:
                game_over = True
                return

    snake.insert(0, new_head)

    if abs(new_head[0] - food_pos[0]) < snake_radius * 2 and abs(new_head[1] - food_pos[1]) < snake_radius * 2:
        if score == 8:
            level = 2
            food_pos = (random.randint(-GRID_SIZE // 2, GRID_SIZE // 2), random.randint(-GRID_SIZE // 2, GRID_SIZE // 2))
            barriers = [(random.randint(-GRID_SIZE // 2 + 50, GRID_SIZE // 2 - 50),
                         random.randint(-GRID_SIZE // 2 + 50, GRID_SIZE // 2 - 50)) for _ in range(10)]
        score += 1
        snake_speed+=0.1
        snake_grow += 3
        food_pos = (random.randint(-GRID_SIZE // 2, GRID_SIZE // 2), random.randint(-GRID_SIZE // 2, GRID_SIZE // 2))
        if level == 2:
            powerup_pos = (random.randint(-GRID_SIZE // 2, GRID_SIZE // 2), random.randint(-GRID_SIZE // 2, GRID_SIZE // 2))
            shrink_pos = (random.randint(-GRID_SIZE // 2, GRID_SIZE // 2), random.randint(-GRID_SIZE // 2, GRID_SIZE // 2))
            powerup_timer = time.time()
            shrink_timer = time.time()
    elif powerup_pos and abs(new_head[0] - powerup_pos[0]) < snake_radius * 2 and abs(new_head[1] - powerup_pos[1]) < snake_radius * 2:
        score += 2
        powerup_pos = None
    elif shrink_pos and abs(new_head[0] - shrink_pos[0]) < snake_radius * 2 and abs(new_head[1] - shrink_pos[1]) < snake_radius * 2:
        if len(snake) > 3:
            del snake[-3:]
        shrink_pos = None
    elif snake_grow > 0:
        snake_grow -= 1
    else:
        snake.pop()

    if shrink_pos and time.time() - shrink_timer > 3:
        shrink_pos = None
    if powerup_pos and time.time() - powerup_timer > 6:
        powerup_pos = None

def show_score():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

    glColor3f(1, 1, 1)
    draw_text(10, WINDOW_HEIGHT - 20, f"Score: {score}  Level: {level}")
    if game_over:
        draw_text(400, 400, "Game Over! Press R to Restart")

    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    glLoadIdentity()

    if camera_mode is None:
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glColor3f(1, 1, 1)
        draw_text(300, 400, "Press 1 for Third-Person Mode")
        draw_text(300, 370, "Press 2 for First-Person Mode")
        glutSwapBuffers()
        return

    setup_camera()
    draw_grid()
    draw_walls()
    draw_obstacles()
    draw_food()
    draw_powerups()
    draw_barriers()
    draw_snake()
    show_score()
    glutSwapBuffers()

def keyboard(key, x, y):
    global snake_dir, camera_mode
    if camera_mode is None:
        if key in [b'1', b'\x31']:
            camera_mode = 1
        elif key in [b'2', b'\x32']:
            camera_mode = 2
        return

    if key in b's' and snake_dir != (0, -1):
        snake_dir = (0, 1)
    elif key in b'w' and snake_dir != (0, 1):
        snake_dir = (0, -1)
    elif key in b'd' and snake_dir != (1, 0):
        snake_dir = (-1, 0)
    elif key in b'a' and snake_dir != (-1, 0):
        snake_dir = (1, 0)
    elif key in [b'r', b'R']:
        reset_game()
        camera_mode = None

def idle():
    update_snake()
    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"3D Snake Game")
    glEnable(GL_DEPTH_TEST)
    reset_game()
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()
