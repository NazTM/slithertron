from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

game_mode = "menu"  
camera_mode = "third_person"
game_over = False
score = 0
high_score = 0
level = 0

snake_segments = [[0, 0, 0]]
snake_direction = [1, 0, 0]
snake_speed = 5.0
snake_growth = 0
last_move_time = 0

camera_angle_x = 45
camera_angle_y = -45
fovY = 60
GRID_LENGTH = 100
GRID_SIZE = 14

min_bound = -GRID_SIZE * GRID_LENGTH // 2
max_bound = GRID_SIZE * GRID_LENGTH // 2
walls = []
food = []

def draw_text(x, y, text):
    glColor3f(1, 1, 1)
    glWindowPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

def draw_large_text(x, y, text):
    glColor3f(1, 1, 1)
    glWindowPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))

def init_level1():
    global walls, snake_segments, snake_direction, snake_speed
    walls = []
    snake_segments = [[0, 0, 0]]
    snake_direction = [1, 0, 0]
    snake_speed = 5.0
    
    for _ in range(10):
        x = random.randint(min_bound + GRID_LENGTH, max_bound - GRID_LENGTH)
        y = random.randint(min_bound + GRID_LENGTH, max_bound - GRID_LENGTH)
        walls.append((x, y, 0, GRID_LENGTH))
    
    spawn_food()

def init_endless():
    global snake_segments, snake_direction, snake_speed, walls
    walls = []
    snake_segments = [[0, 0, 0]]
    snake_direction = [1, 0, 0]
    snake_speed = 5.0
    spawn_food()

def spawn_food():
    global food
    while True:
        x = random.randint(min_bound + GRID_LENGTH, max_bound - GRID_LENGTH)
        y = random.randint(min_bound + GRID_LENGTH, max_bound - GRID_LENGTH)
        
        valid = True
        for wall in walls:
            if abs(x - wall[0]) < GRID_LENGTH and abs(y - wall[1]) < GRID_LENGTH:
                valid = False
                break
        
        if valid:
            food = [(x, y, 0)]
            break

def draw_grid():
    glBegin(GL_QUADS)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x = (i - GRID_SIZE // 2) * GRID_LENGTH
            y = (j - GRID_SIZE // 2) * GRID_LENGTH
            glColor3f(0.3, 0.3, 0.3) if (i + j) % 2 == 0 else glColor3f(0.2, 0.2, 0.2)
            glVertex3f(x, y, 0)
            glVertex3f(x + GRID_LENGTH, y, 0)
            glVertex3f(x + GRID_LENGTH, y + GRID_LENGTH, 0)
            glVertex3f(x, y + GRID_LENGTH, 0)
    glEnd()

def draw_walls():
    for wall in walls:
        x, y, z, size = wall
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(0.8, 0.2, 0.2)
        glutSolidCube(size)
        glPopMatrix()

def draw_food():
    for f in food:
        x, y, z = f
        glPushMatrix()
        glTranslatef(x, y, z + 5)
        glColor3f(1.0, 0.0, 0.0)
        glutSolidSphere(GRID_LENGTH//3, 10, 10)
        glPopMatrix()

def draw_snake():
    for i, segment in enumerate(snake_segments):
        x, y, z = segment
        glPushMatrix()
        glTranslatef(x, y, z + 5)
        if i == 0:
            glColor3f(0.0, 1.0, 0.0)
        else:
            glColor3f(0.0, 0.7, 0.0)
        glutSolidCube(GRID_LENGTH * 0.8)
        glPopMatrix()

def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if camera_mode == "third_person":
        head = snake_segments[0]
        distance = 200
        
        rad_y = math.radians(camera_angle_y)
        rad_x = math.radians(camera_angle_x)
        
        cam_x = head[0] - distance * math.cos(rad_x) * math.sin(rad_y)
        cam_y = head[1] + distance * math.cos(rad_x) * math.cos(rad_y)
        cam_z = head[2] + distance * math.sin(rad_x)
        
        gluLookAt(cam_x, cam_y, cam_z,
                 head[0], head[1], head[2],
                 0, 0, 1)
    else:
        head = snake_segments[0]
        look_x = head[0] + snake_direction[0] * 100
        look_y = head[1] + snake_direction[1] * 100
        look_z = head[2] + snake_direction[2] * 100
        
        gluLookAt(head[0], head[1], head[2] + 30,
                 look_x, look_y, look_z,
                 0, 0, 1)

def move_snake():
    global snake_segments, snake_growth, score, game_over, last_move_time
    
    current_time = time.time()
    if current_time - last_move_time < 1.0 / snake_speed:
        return
    
    last_move_time = current_time
    
    head = snake_segments[0]
    new_head = [
        head[0] + snake_direction[0] * GRID_LENGTH,
        head[1] + snake_direction[1] * GRID_LENGTH,
        head[2] + snake_direction[2] * GRID_LENGTH
    ]
    
    if (new_head[0] < min_bound or new_head[0] > max_bound or
        new_head[1] < min_bound or new_head[1] > max_bound):
        game_over = True
        return
    
    for wall in walls:
        if (abs(new_head[0] - wall[0]) < GRID_LENGTH) and \
           (abs(new_head[1] - wall[1]) < GRID_LENGTH):
            game_over = True
            return
    
    for segment in snake_segments[1:]:
        if (abs(new_head[0] - segment[0]) < GRID_LENGTH) and \
           (abs(new_head[1] - segment[1]) < GRID_LENGTH):
            game_over = True
            return
    
    if food and (abs(new_head[0] - food[0][0]) < GRID_LENGTH) and \
                (abs(new_head[1] - food[0][1]) < GRID_LENGTH):
        score += 10
        snake_growth += 3
        spawn_food()
        if game_mode == "endless":
            snake_speed = min(15.0, snake_speed + 0.2)
    
    snake_segments.insert(0, new_head)
    
    if snake_growth > 0:
        snake_growth -= 1
    else:
        if len(snake_segments) > 1:
            snake_segments.pop()

def keyboard(key, x, y):
    global snake_direction, game_mode, camera_mode, game_over, score, high_score
    
    key = key.decode("utf-8").lower()
    
    if game_mode == "menu":
        if key == '1':
            game_mode = "level1"
            init_level1()
        elif key == '2':
            game_mode = "endless"
            init_endless()
        elif key == 'c':
            camera_mode = "third_person" if camera_mode == "first_person" else "first_person"
    elif game_over:
        if key == 'r':
            if game_mode == "level1":
                init_level1()
            else:
                init_endless()
            game_over = False
            if score > high_score:
                high_score = score
            score = 0
        elif key == 'm':
            game_mode = "menu"
    else:
        if key == 'w' and snake_direction != [0, -GRID_LENGTH, 0]:
            snake_direction = [0, GRID_LENGTH, 0]
        elif key == 's' and snake_direction != [0, GRID_LENGTH, 0]:
            snake_direction = [0, -GRID_LENGTH, 0]
        elif key == 'a' and snake_direction != [GRID_LENGTH, 0, 0]:
            snake_direction = [-GRID_LENGTH, 0, 0]
        elif key == 'd' and snake_direction != [-GRID_LENGTH, 0, 0]:
            snake_direction = [GRID_LENGTH, 0, 0]
        elif key == 'c':
            camera_mode = "third_person" if camera_mode == "first_person" else "first_person"

def special_keys(key, x, y):
    global snake_direction
    
    if game_over or game_mode == "menu":
        return
    
    if key == GLUT_KEY_UP and snake_direction != [0, -GRID_LENGTH, 0]:
        snake_direction = [0, GRID_LENGTH, 0]
    elif key == GLUT_KEY_DOWN and snake_direction != [0, GRID_LENGTH, 0]:
        snake_direction = [0, -GRID_LENGTH, 0]
    elif key == GLUT_KEY_LEFT and snake_direction != [GRID_LENGTH, 0, 0]:
        snake_direction = [-GRID_LENGTH, 0, 0]
    elif key == GLUT_KEY_RIGHT and snake_direction != [-GRID_LENGTH, 0, 0]:
        snake_direction = [GRID_LENGTH, 0, 0]

def draw_menu():
    draw_large_text(350, 500, "3D SNAKE GAME")
    draw_text(400, 450, "1: Level 1 (Obstacles)")
    draw_text(400, 400, "2: Endless Mode")
    draw_text(400, 350, "C: Toggle Camera")
    draw_text(400, 300, "WASD or Arrows to Move")
    draw_text(400, 250, f"High Score: {high_score}")

def draw_game():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    setup_camera()
    draw_grid()
    draw_walls()
    draw_food()
    draw_snake()
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    if game_mode == "level1":
        draw_text(20, 770, f"Level 1 - Score: {score}")
    else:
        draw_text(20, 770, f"Endless Mode - Score: {score} Speed: {snake_speed:.1f}")
    
    draw_text(20, 740, f"Camera: {camera_mode} (Press C to toggle)")
    
    if game_over:
        draw_text(400, 400, f"GAME OVER! Score: {score}")
        draw_text(400, 370, "Press R to restart or M for menu")
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glutSwapBuffers()

def idle():
    if game_mode != "menu" and not game_over:
        move_snake()
    glutPostRedisplay()

def display():
    if game_mode == "menu":
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        draw_menu()
        glutSwapBuffers()
    else:
        draw_game()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"3D Snake Game")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()
