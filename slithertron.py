from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math, random, time, sys, os

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
GRID_SIZE = 600
CELL_SIZE = 37

endless = False
game_complete = False
paused = False
looking_back = False
snake_dir = (1, 0)
snake_speed = 1.5
snake_grow = 0
snake_radius = 20
snake = [(i * - snake_radius * 2, 0) for i in range(20)]
snake_invisible = False
invisible_timer = 0
invisibility_powerup_pos = None
invisibility_powerup_color = (1.0, 1.0, 1.0)

bullets = []
enemies = []
num_enemies = 5
projectiles = []
enemy_speed = 1.0
projectile_speed = 5.0
shoot_timer = 0
enemy_radius = 20

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
player_pos = [0, 0, 0]

def close_callback():
    """Callback function for window close event"""
    print("Exiting game...")
    sys.exit(0)  # fallback if glutLeaveMainLoop doesn't work
    print("Force exiting game...")
    os._exit(0)  # Kills the process immediately, bypassing GLUT issues


def reset_game():
    global snake, snake_speed, snake_radius, snake_dir, snake_grow, food_pos, score, game_over, level, powerup_pos, shrink_pos, barriers
    snake = [(i * -snake_radius * 2, 0) for i in range(20)]  # Minimum snake length
    snake_dir = (1, 0)
    snake_grow = 0
    snake_speed = 1.5
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
    global snake_invisible
    for x, y in snake:
        glPushMatrix()
        glTranslatef(x, y, snake_radius)
        if snake_invisible:
            glColor4f(1, 1, 1, 0)  # Invisible (fully transparent)
        else:
            glColor3f(0, 1, 0)  # Normal snake color
        glutSolidSphere(snake_radius, 16, 16)
        glPopMatrix()



def draw_food():
    glColor3f(0, 1, 0 if score == 8 else 1)  # Green if transition food
    glPushMatrix()
    glTranslatef(food_pos[0], food_pos[1], snake_radius)
    glutSolidSphere(snake_radius, 16, 16)
    glPopMatrix()

def draw_powerups():
    global powerup_pos, shrink_pos, invisibility_powerup_pos, invisibility_powerup_color
    if powerup_pos:
        glColor3f(0, 0, 1) #cyan
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
    if invisibility_powerup_pos:
        glColor3f(*invisibility_powerup_color)  # Use random color
        glPushMatrix()
        glTranslatef(invisibility_powerup_pos[0], invisibility_powerup_pos[1], snake_radius)
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
    global snake, food_pos, score, snake_grow, game_over, level, paused, game_complete
    global powerup_pos, shrink_pos, powerup_timer, shrink_timer
    global barriers, snake_speed, snake_invisible, invisible_timer, invisibility_powerup_pos

    if paused or game_complete or game_over or camera_mode is None:
        return


    # Invisibility timer check BEFORE returns
    if snake_invisible and invisible_timer > 0 and time.time() - invisible_timer > 10:
        snake_invisible = False

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

    if level == 2 and not snake_invisible:
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
            invisibility_powerup_pos = (random.randint(-GRID_SIZE // 2, GRID_SIZE // 2), random.randint(-GRID_SIZE // 2, GRID_SIZE // 2))  # NEW
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

    # Check invisibility power-up collection
    if invisibility_powerup_pos and abs(new_head[0] - invisibility_powerup_pos[0]) < snake_radius * 2 and abs(new_head[1] - invisibility_powerup_pos[1]) < snake_radius * 2:
        snake_invisible = True
        invisible_timer = time.time()
        invisibility_powerup_pos = None

    if snake_invisible and invisible_timer > 0 and time.time() - invisible_timer > 10:
        snake_invisible = False

    if not endless and not game_complete and score >= 20:
      game_complete = True
      return




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
    if level == 1:
        draw_text(10, WINDOW_HEIGHT - 40, f"Score 9 points to get to Level 2")
    if level == 2:
        draw_text(10, WINDOW_HEIGHT - 40, f"Score 16 points to get to Level 3")
    if game_complete:
        draw_text(400, 400, "Congratulations! Press R to Restart")
    if game_over:
        draw_text(400, 400, "Game Over! Press R to Restart")
    if paused:
        draw_text(10, WINDOW_HEIGHT - 60, f"Paused")
    if endless:
        draw_text(10, WINDOW_HEIGHT - 80, f"Endless Mode")

    if snake_invisible:
        remaining = int(10 - (time.time() - invisible_timer))
        draw_text(10, WINDOW_HEIGHT - 60, f"Invisibility: {remaining}s left")


    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def keyboard(key, x, y):
    global snake_dir, camera_mode, paused, endless

    if camera_mode is None and (key == b't' or key == b'T'):
      endless = not endless
      print(f"Endless Mode: {'On' if endless else 'Off'}")

    if key == b'\x1b':  # ESC key
        close_callback()
        return
    if camera_mode is None:
        if key in [b'1', b'\x31']:
            camera_mode = 1
        elif key in [b'2', b'\x32']:
            camera_mode = 2
        return

    # Toggle pause on 'P' press
    if key == b'p' or key == b'P':
        paused = not paused
        return

    # Turn controls for both modes
    if camera_mode == 2:  # First-person: use relative turning
        if key in b'a':  # Turn left
            if snake_dir == (1, 0):
                snake_dir = (0, 1)
            elif snake_dir == (-1, 0):
                snake_dir = (0, -1)
            elif snake_dir == (0, 1):
                snake_dir = (-1, 0)
            elif snake_dir == (0, -1):
                snake_dir = (1, 0)
        elif key in b'd':  # Turn right
            if snake_dir == (1, 0):
                snake_dir = (0, -1)
            elif snake_dir == (-1, 0):
                snake_dir = (0, 1)
            elif snake_dir == (0, 1):
                snake_dir = (1, 0)
            elif snake_dir == (0, -1):
                snake_dir = (-1, 0)
    else:  # Third-person: use direct control
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

    if key in [b'r', b'R']:
        reset_game()
        camera_mode = None

def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for adjusting the camera angle and height.
    """
    global camera_pos
    x, y, z = camera_pos
    # Move camera up (UP arrow key)
    if key == GLUT_KEY_UP:
        y += 1
    # Move camera down (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        y -= 1
    # moving camera left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        x -= 1  # Small angle decrement for smooth movement

    # moving camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        x += 1  # Small angle increment for smooth movement

    camera_pos = (x, y, z)

def idle():
    update_snake()
    if level == 3:
        env_interaction()
        hit_enemy()
    glutPostRedisplay()
# Additions to your global variables
# Add these at the start of your file where other globals are defined
ENEMY_TYPES = {
    "CHASER": 0,     # Directly chases the player
    "WANDERER": 1,   # Wanders randomly, changes direction occasionally
    "AMBUSHER": 2    # Tries to predict and intercept the player's path
}

enemies = []
num_enemies = 5
projectiles = []
enemy_radius = 20
projectile_speed = 5.0
last_frame_time = time.time()
delta_time = 0.0


# Simplified enemy creation function
def create_enemy(enemy_type=None, difficulty=1.0):
    """Create a new enemy with specific type and properties"""
    if enemy_type is None:
        # Use simple WANDERER type as default for reliability
        enemy_type = ENEMY_TYPES["WANDERER"]

    # Spawn away from the center (where player likely is)
    x = random.choice([-1, 1]) * random.randint(300, GRID_SIZE - 100)
    y = random.choice([-1, 1]) * random.randint(300, GRID_SIZE - 100)

    # Simplify colors for debugging visibility
    if enemy_type == ENEMY_TYPES["CHASER"]:
        color = (1.0, 0.0, 0.0)  # Pure red
        speed = 1.0 * difficulty  # Faster for visibility
    elif enemy_type == ENEMY_TYPES["WANDERER"]:
        color = (0.0, 0.0, 1.0)  # Pure blue
        speed = 0.7 * difficulty
    else:  # AMBUSHER
        color = (1.0, 0.6, 0.0)  # Orange
        speed = 0.8 * difficulty

    # Create simpler enemy dictionary
    return {
        'enemy_pos': [x, y, 20],
        'enemy_type': enemy_type,
        'color': color,
        'speed': speed,
        'scale': 1.0,
        'scale_direction': 0.01,  # More visible pulsing
        'wander_counter': 0,
        'wander_direction': (random.random() - 0.5, random.random() - 0.5),
        'projectile_cooldown': 0
    }


# Function to spawn multiple enemies based on level
def spawn_enemies(num_enemies, level, difficulty=1.0):
    """Spawn multiple enemies based on level"""
    enemies = []
    difficulty = max(difficulty, 1.0)  # Ensure enemies move at visible speed

    # Create one of each type for testing
    enemies.append({
        'enemy_pos': [200, 200, 20],
        'enemy_type': ENEMY_TYPES["CHASER"],
        'color': (1.0, 0.0, 0.0),  # Red
        'speed': 0.8 * difficulty,
        'scale': 1.0,
        'scale_direction': 0.01,
        'wander_counter': 0,
        'wander_direction': (0, 0),
        'projectile_cooldown': 0
    })

    enemies.append({
        'enemy_pos': [-200, 200, 20],
        'enemy_type': ENEMY_TYPES["WANDERER"],
        'color': (0.0, 0.0, 1.0),  # Blue
        'speed': 0.5 * difficulty,
        'scale': 1.0,
        'scale_direction': 0.01,
        'wander_counter': 0,
        'wander_direction': (0, 0),
        'projectile_cooldown': 0
    })

    enemies.append({
        'enemy_pos': [0, -200, 20],
        'enemy_type': ENEMY_TYPES["AMBUSHER"],
        'color': (1.0, 0.5, 0.0),  # Orange
        'speed': 0.6 * difficulty,
        'scale': 1.0,
        'scale_direction': 0.01,
        'wander_counter': 0,
        'wander_direction': (0, 0),
        'projectile_cooldown': 0
    })

    return enemies
# Update enemy positions and behaviors
def update_enemies(enemies, player_pos, snake, barriers, projectiles, level, delta_time):
    """Update all enemies positions and behaviors"""
    # Get snake head position for targeting
    if not snake or len(snake) == 0:
        return  # Don't update if there's no snake

    head_x, head_y = snake[0]

    for e in enemies:
        # Extract enemy properties
        enemy_type = e['enemy_type']
        enemy_speed = e['speed'] * delta_time * 60  # For frame rate independence

        # Calculate base direction to player
        dx, dy = head_x - e['enemy_pos'][0], head_y - e['enemy_pos'][1]
        dist = max(math.hypot(dx, dy), 0.1)  # Avoid division by zero

        # Different movement patterns based on enemy type
        if enemy_type == ENEMY_TYPES["CHASER"]:
            # Direct chase behavior
            e['enemy_pos'][0] += dx / dist * enemy_speed
            e['enemy_pos'][1] += dy / dist * enemy_speed

        elif enemy_type == ENEMY_TYPES["WANDERER"]:
            # Wanderer movement: random wandering with occasional player awareness
            e['wander_counter'] += delta_time

            # Change direction periodically or if hitting boundaries
            if e['wander_counter'] > 3 or abs(e['enemy_pos'][0]) > GRID_SIZE - 50 or abs(e['enemy_pos'][1]) > GRID_SIZE - 50:
                e['wander_counter'] = 0
                # 30% chance to move toward player, 70% random
                if random.random() < 0.3:
                    e['wander_direction'] = (dx / dist, dy / dist)
                else:
                    wx = random.random() - 0.5
                    wy = random.random() - 0.5
                    wlen = max(math.hypot(wx, wy), 0.1)
                    e['wander_direction'] = (wx / wlen, wy / wlen)

            # Apply movement
            wx, wy = e['wander_direction']
            e['enemy_pos'][0] += wx * enemy_speed * 0.7
            e['enemy_pos'][1] += wy * enemy_speed * 0.7

        elif enemy_type == ENEMY_TYPES["AMBUSHER"]:
            # Ambusher tries to predict player's path
            if 'snake_dir' in globals():
                # Calculate player direction
                dir_x, dir_y = snake_dir

                # Target ahead of player
                target_x = head_x + dir_x * 150
                target_y = head_y + dir_y * 150

                # Move toward predicted position
                dx_pred = target_x - e['enemy_pos'][0]
                dy_pred = target_y - e['enemy_pos'][1]
                dist_pred = max(math.hypot(dx_pred, dy_pred), 0.1)

                e['enemy_pos'][0] += dx_pred / dist_pred * enemy_speed
                e['enemy_pos'][1] += dy_pred / dist_pred * enemy_speed

                # In level 3, ambushers can shoot projectiles
                if 'camera_mode' in globals() and camera_mode is not None:
                    e['projectile_cooldown'] -= delta_time
                    if e['projectile_cooldown'] <= 0 and dist < 400:
                        e['projectile_cooldown'] = random.uniform(2.0, 4.0)
                        # Create projectile
                        try:
                            fire_projectile([e['enemy_pos'][0], e['enemy_pos'][1], e['enemy_pos'][2]],
                                           (dx/dist, dy/dist), projectiles)
                        except Exception as ex:
                            # Silently ignore projectile errors to prevent game crashes
                            pass
            else:
                # Fallback to chaser behavior
                e['enemy_pos'][0] += dx / dist * enemy_speed
                e['enemy_pos'][1] += dy / dist * enemy_speed

        # Keep enemies within grid bounds
        e['enemy_pos'][0] = max(min(e['enemy_pos'][0], GRID_SIZE - 50), -GRID_SIZE + 50)
        e['enemy_pos'][1] = max(min(e['enemy_pos'][1], GRID_SIZE - 50), -GRID_SIZE + 50)

        # Avoid barriers
        if barriers:
            for bx, by in barriers:
                barrier_dx = e['enemy_pos'][0] - bx
                barrier_dy = e['enemy_pos'][1] - by
                barrier_dist = math.hypot(barrier_dx, barrier_dy)
                if barrier_dist < 60:  # Avoid getting too close to barriers
                    if barrier_dist > 0.1:  # Avoid division by zero
                        e['enemy_pos'][0] += barrier_dx / barrier_dist * 2
                        e['enemy_pos'][1] += barrier_dy / barrier_dist * 2

        # Visual effect: Pulsating
        e['scale'] += e['scale_direction']
        if not 0.8 <= e['scale'] <= 1.2:
            e['scale_direction'] *= -1


# Fire projectile from enemy
def fire_projectile(position, direction, projectiles):
    """Fire a projectile from enemy position in specified direction"""
    projectiles.append({
        'pos': position.copy() if isinstance(position, list) else list(position),
        'dir': direction,
        'speed': projectile_speed,
        'lifetime': 3.0  # Seconds before disappearing
    })


# Update projectile positions
def update_projectiles(projectiles, delta_time):
    """Update projectile positions and lifetimes"""
    for p in projectiles[:]:
        # Move projectile
        p['pos'][0] += p['dir'][0] * p['speed'] * delta_time
        p['pos'][1] += p['dir'][1] * p['speed'] * delta_time

        # Decrease lifetime
        p['lifetime'] -= delta_time
        if p['lifetime'] <= 0:
            projectiles.remove(p)
            continue

        # Check if out of bounds
        if abs(p['pos'][0]) > GRID_SIZE or abs(p['pos'][1]) > GRID_SIZE:
            projectiles.remove(p)


# Simplified draw enemies function
def draw_enemies(enemies):
    """Draw all enemies with simpler rendering for debugging"""
    if not enemies:
        return

    for e in enemies:
        glPushMatrix()
        glTranslatef(e['enemy_pos'][0], e['enemy_pos'][1], e['enemy_pos'][2])
        glScalef(e['scale'], e['scale'], e['scale'])

        # Use the enemy's color
        glColor3f(*e['color'])

        # Simple sphere for all enemy types with different sizes
        if e['enemy_type'] == ENEMY_TYPES["CHASER"]:
            glutSolidSphere(enemy_radius * 1.2, 12, 12)
        elif e['enemy_type'] == ENEMY_TYPES["WANDERER"]:
            glutSolidSphere(enemy_radius, 12, 12)
        else:  # AMBUSHER
            glutSolidCube(enemy_radius * 1.5)

        glPopMatrix()


# Draw projectiles
def draw_projectiles(projectiles):
    """Draw all projectiles"""
    for p in projectiles:
        glPushMatrix()
        glTranslatef(p['pos'][0], p['pos'][1], 20)
        glColor3f(1.0, 0.5, 0.0)  # Orange-red projectile
        glutSolidSphere(8, 12, 12)
        glPopMatrix()


# Check for collisions between snake and enemies/projectiles
def check_enemy_collision(snake, enemies, projectiles, snake_invisible, game_over):
    """Check for collisions between snake, enemies and projectiles"""
    if game_over or snake_invisible:
        return game_over

    head_x, head_y = snake[0]

    # Check enemy collisions
    for e in enemies:
        ex, ey = e['enemy_pos'][0], e['enemy_pos'][1]
        # Distance-based collision
        if math.hypot(head_x - ex, head_y - ey) < snake_radius + enemy_radius:
            return True

    # Check projectile collisions
    for p in projectiles[:]:
        px, py = p['pos'][0], p['pos'][1]
        if math.hypot(head_x - px, head_y - py) < snake_radius + 8:
            projectiles.remove(p)
            return True

    return game_over


# Direct addition to your code - a debugging function to spawn test enemies
def spawn_test_enemies():
    """Manually spawn test enemies for debugging purposes"""
    global enemies
    enemies = []

    # Create one of each type at fixed positions for visibility
    enemies.append({
        'enemy_pos': [200, 200, 20],
        'enemy_type': ENEMY_TYPES["CHASER"],
        'color': (1.0, 0.0, 0.0),  # Red
        'speed': 0.5,
        'scale': 1.0,
        'scale_direction': 0.01,
        'wander_counter': 0,
        'wander_direction': (0, 0),
        'projectile_cooldown': 0
    })

    enemies.append({
        'enemy_pos': [-200, 200, 20],
        'enemy_type': ENEMY_TYPES["WANDERER"],
        'color': (0.0, 0.0, 1.0),  # Blue
        'speed': 0.3,
        'scale': 1.0,
        'scale_direction': 0.01,
        'wander_counter': 0,
        'wander_direction': (0, 0),
        'projectile_cooldown': 0
    })

    enemies.append({
        'enemy_pos': [0, -200, 20],
        'enemy_type': ENEMY_TYPES["AMBUSHER"],
        'color': (1.0, 0.5, 0.0),  # Orange
        'speed': 0.4,
        'scale': 1.0,
        'scale_direction': 0.01,
        'wander_counter': 0,
        'wander_direction': (0, 0),
        'projectile_cooldown': 0
    })

    print(f"Spawned {len(enemies)} test enemies")

# Modified reset_game function with option to test enemies
def reset_game():
    global snake, snake_speed, snake_radius, snake_dir, snake_grow, food_pos, score
    global game_over, level, powerup_pos, shrink_pos, barriers, enemies, projectiles

    snake = [(i * -snake_radius * 2, 0) for i in range(20)]  # Minimum snake length
    snake_dir = (1, 0)
    snake_grow = 0
    snake_speed = 1.5
    food_pos = (random.randint(-GRID_SIZE // 2, GRID_SIZE // 2), random.randint(-GRID_SIZE // 2, GRID_SIZE // 2))
    score = 0
    game_over = False
    level = 1
    powerup_pos = None
    shrink_pos = None
    barriers = []
    enemies = []
    projectiles = []

    # For immediate debugging, uncomment to spawn test enemies regardless of level
    # spawn_test_enemies()


# Updated idle function with debug prints and more robust enemy handling
def idle():
    global delta_time, last_frame_time, enemies, level, score

    # Calculate delta time
    current_time = time.time()
    delta_time = current_time - last_frame_time
    last_frame_time = current_time

    update_snake()

    # Force level 3 when score reaches 16
    if score >= 16 and level < 3:
        level = 3
        print("Level advanced to 3 - enemies should appear!")

    # Spawn enemies when level 3 starts
    if level == 3 and len(enemies) == 0:
        enemies = spawn_enemies(num_enemies, level)
        print(f"Spawned {len(enemies)} enemies")

    # Update enemies if they exist
    if enemies and level == 3:
        if len(snake) > 0:
            player_pos[0], player_pos[1] = snake[0]

        update_enemies(enemies, player_pos, snake, barriers, projectiles, level, delta_time)
        update_projectiles(projectiles, delta_time)

        global game_over
        game_over = check_enemy_collision(snake, enemies, projectiles, snake_invisible, game_over)

    glutPostRedisplay()
# Modified display function to always check and draw enemies
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
        draw_text(300, 600, "S L I T H E R T R O N")
        draw_text(300, 400, "Press 1 for Third-Person Mode")
        draw_text(300, 370, "Press 2 for First-Person Mode")
        draw_text(300, 240, "Instructions:")
        draw_text(300, 200, "Snake eats powerups - cyan lengthen it, orange shrinks it")
        draw_text(300, 180, "White powerup gives you invisibility")
        draw_text(300, 160, "Avoid walls and red enemies")
        draw_text(300, 140, f"Press T to toggle endless mode (Currently {'On' if endless else 'Off'})")
        glutSwapBuffers()
        return

    setup_camera()
    draw_grid()
    draw_walls()

    # Always draw enemies if they exist, regardless of level
    if enemies:
        draw_enemies(enemies)
    if projectiles:
        draw_projectiles(projectiles)

    draw_obstacles()
    draw_food()
    draw_powerups()
    draw_barriers()
    draw_snake()
    show_score()
    glutSwapBuffers()
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"3D Snake Game")

    # Set the close callback
    glutCloseFunc(close_callback)

    glEnable(GL_DEPTH_TEST)
    reset_game()
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(specialKeyListener)
    glutIdleFunc(idle)
    try:
        glutMainLoop()
    except SystemExit:
        os._exit(0)


if __name__ == "__main__":
    main()