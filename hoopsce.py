from ti_draw import *
from ti_system import *
from math import *
from random import *

# --- TI-84 PLUS CE KEY CODES ---
K_UP = 25
K_DOWN = 34
K_LEFT = 24
K_RIGHT = 26
K_2ND = 21
K_ALPHA = 31
K_ENTER = 105
K_CLEAR = 45

# --- RETRO PIXEL SPRITE MATRICES (12x16 pixels) ---
# 0 = Transparent, 1 = Skin, 2 = Jersey Blue/Red, 3 = White Trim, 4 = Shoes, 5 = Hair
P_SPRITE = [
    [0,0,0,5,5,5,5,5,0,0,0,0],
    [0,0,5,5,5,5,5,5,5,0,0,0],
    [0,0,1,1,1,1,1,1,1,0,0,0],
    [0,0,1,3,3,3,3,3,1,0,0,0], # Headband
    [0,0,0,1,1,1,1,1,0,0,0,0], # Face
    [0,2,2,2,2,2,2,2,2,2,0,0], # Jersey shoulders
    [2,2,2,3,2,2,2,3,2,2,2,0], # Jersey chest
    [2,2,2,2,2,2,2,2,2,2,2,0],
    [0,2,2,2,2,2,2,2,2,2,0,0],
    [0,0,2,2,2,2,2,2,2,0,0,0], # Shorts
    [0,0,1,1,0,0,1,1,0,0,0,0], # Legs
    [0,0,1,1,0,0,1,1,0,0,0,0],
    [0,0,1,1,0,0,1,1,0,0,0,0],
    [0,0,4,4,4,0,4,4,4,0,0,0], # Sneakers
    [0,4,4,4,4,0,4,4,4,4,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0]
]

# --- GAME STATE ---
px, py = 70, 125
dx, dy = 185, 125
score = 0
cpu = 0
shot_clock = 24.0
qtr = 1
dribble = 0
juke_cd = 0
aiming = False
aim_ang = 48.0
aim_dir = 1
aim_pwr = 0.0
pwr_dir = 1
phase = 0  # 0=dribble, 1=angle, 2=power, 3=flight
bx, by, bvx, bvy = 0.0, 0.0, 0.0, 0.0
is_three = False
msg = ""
msg_t = 0
rim_x, rim_y = 276, 86

def draw_court():
  # Crowd / Arena backdrop
  set_color(24, 28, 42)
  fill_rect(0, 0, 320, 62)
  for cx in range(4, 320, 14):
    for cy in range(18, 56, 12):
      set_color(60 + (cx * 3) % 120, 50 + (cy * 5) % 110, 80 + (cx + cy) % 120)
      fill_circle(cx, cy, 3)
      fill_rect(cx - 3, cy + 3, 6, 5)

  # Hardwood court base + detailed planks
  set_color(218, 156, 88)
  fill_rect(0, 62, 320, 148)
  set_color(202, 140, 72)
  for y in range(62, 210, 10):
    fill_rect(0, y, 320, 4)
  set_color(182, 122, 58)
  for y in range(62, 210, 5):
    draw_line(0, y, 320, y)
    off = (y % 10) * 16
    for x in range(off, 320, 32):
      draw_line(x, y, x, y + 5)

  # Painted Key & Out-of-bounds apron
  set_color(18, 52, 116)
  fill_rect(0, 62, 320, 4)
  fill_rect(0, 204, 320, 6)
  fill_rect(225, 108, 75, 56)

  # Court lines (White)
  set_color(255, 255, 255)
  set_pen("medium", "solid")
  draw_rect(225, 108, 75, 56)
  draw_line(14, 65, 14, 204)
  draw_line(300, 65, 300, 204)
  # 3-Point Arc
  draw_line(240, 74, 300, 74)
  draw_line(240, 196, 300, 196)
  draw_arc(178, 74, 124, 122, 900, 1800)
  # Free throw circle
  draw_arc(205, 114, 40, 44, 900, 1800)
  set_pen("thin", "solid")

  # Stanchion & Glass Backboard
  set_color(40, 45, 55)
  fill_rect(296, 62, 8, 86)
  fill_rect(288, 62, 14, 6)
  set_color(235, 245, 255)
  fill_rect(286, 54, 4, 42)
  set_color(220, 35, 35)
  draw_rect(285, 54, 6, 42)
  fill_rect(285, 72, 3, 12)
  # Rim & Net
  set_color(240, 75, 15)
  fill_rect(268, 85, 18, 3)
  set_color(245, 245, 245)
  draw_line(270, 88, 273, 102)
  draw_line(284, 88, 281, 102)
  draw_line(273, 102, 281, 102)
  draw_line(271, 94, 282, 94)

def draw_pixel_player(x, y, is_cpu, step, has_ball):
  ix, iy = int(x) - 6, int(y) - 8
  # Drop shadow on hardwood
  set_color(130, 85, 40)
  fill_rect(ix + 1, iy + 14, 10, 3)

  # Render 12x16 sprite matrix
  for r in range(16):
    for c in range(12):
      val = P_SPRITE[r][c]
      if val == 0:
        continue
      elif val == 1:
        set_color(145, 92, 56) if not is_cpu else set_color(228, 178, 134)
      elif val == 2:
        set_color(24, 72, 185) if not is_cpu else set_color(205, 30, 40)
      elif val == 3:
        set_color(250, 250, 250)
      elif val == 4:
        set_color(245, 245, 245) if not is_cpu else set_color(35, 35, 35)
      elif val == 5:
        set_color(25, 25, 30)

      # Animate running bounce
      bo = 1 if (step % 4 < 2 and r > 9) else 0
      set_pixel(ix + c, iy + r + bo)

  # Dribbling Basketball
  if has_ball:
    bounce = abs((step % 6) - 3)
    draw_ball(int(x) + 7, int(y) + 4 + bounce)

def draw_ball(x, y):
  ix, iy = int(x), int(y)
  set_color(230, 100, 18)
  fill_circle(ix, iy, 4)
  set_color(35, 18, 8)
  draw_circle(ix, iy, 4)
  draw_line(ix - 3, iy, ix + 3, iy)

def draw_hud():
  set_color(15, 18, 28)
  fill_rect(0, 0, 320, 16)
  set_color(250, 200, 40)
  draw_text(6, 2, "HOME:" + str(score))
  set_color(240, 85, 85)
  draw_text(98, 2, "AWAY:" + str(cpu))
  set_color(255, 255, 255)
  draw_text(192, 2, "Q" + str(qtr) + " " + str(int(shot_clock)) + "s")
  if juke_cd == 0:
    set_color(80, 235, 130)
    draw_text(266, 2, "[JUKE]")

def draw_arc_guide():
  rad = aim_ang * 3.14159 / 180.0
  spd = 8.5 + (aim_pwr / 100.0) * 7.5 if phase == 2 else 12.2
  vx = cos(rad) * spd
  vy = -sin(rad) * spd
  tx, ty = float(px + 4), float(py - 6)
  for i in range(1, 16):
    tx += vx * 1.4
    ty += vy * 1.4
    vy += 0.55 * 1.4
    if i % 2 == 0:
      set_color(255, 255, 255) if phase == 1 else set_color(80, 250, 120)
      fill_circle(int(tx), int(ty), 2)

  # Power meter bar
  if phase == 2:
    set_color(20, 20, 20)
    fill_rect(int(px) - 18, int(py) - 32, 36, 6)
    set_color(60, 235, 100) if 58 <= aim_pwr <= 76 else set_color(250, 190, 40)
    fill_rect(int(px) - 17, int(py) - 31, int(aim_pwr * 0.34), 4)

def reset_possession(scored):
  global px, py, dx, dy, phase, shot_clock, cpu, qtr, msg, msg_t
  if scored:
    pts = 3 if is_three else 2
    globals()['score'] += pts
    msg = "SWISH! +" + str(pts) + " PTS"
  else:
    msg = "MISSED! CPU +2"
    cpu += 2
  msg_t = 18
  px, py = 65, 128
  dx, dy = 185, 128
  phase = 0
  shot_clock = 24.0
  if score >= 21 or cpu >= 21:
    qtr = 5

# --- TITLE SCREEN ---
clear()
draw_court()
set_color(15, 18, 28)
fill_rect(35, 55, 250, 95)
set_color(250, 200, 40)
draw_rect(35, 55, 250, 95)
draw_text(65, 66, "CE HOOPS: GRIDIRON")
set_color(255, 255, 255)
draw_text(52, 88, "ARROWS: Move   ALPHA: Juke")
draw_text(52, 106, "2ND / ENTER: Aim & Shoot")
set_color(80, 235, 130)
draw_text(68, 128, "PRESS ANY KEY TO PLAY")
show_draw()
wait_key()

# --- MAIN GAME LOOP ---
while qtr <= 4:
  k = get_key(0)
  if k == K_CLEAR:
    break

  if phase == 0:
    moved = False
    if k == K_UP and py > 74:
      py -= 4
      moved = True
    elif k == K_DOWN and py < 194:
      py += 4
      moved = True
    elif k == K_LEFT and px > 24:
      px -= 4
      moved = True
    elif k == K_RIGHT and px < 268:
      px += 4
      moved = True

    if k == K_ALPHA and juke_cd == 0:
      py += -22 if py > 130 else 22
      px = min(265, px + 14)
      juke_cd = 28
      moved = True

    if moved:
      dribble += 1
    if juke_cd > 0:
      juke_cd -= 1

    if dx > px + 16:
      dx -= 2
    elif dx < px + 12:
      dx += 2
    if dy < py:
      dy += 2
    elif dy > py:
      dy -= 2

    if abs(px - dx) < 11 and abs(py - dy) < 9 and juke_cd < 20:
      msg = "TURNOVER! CPU +2"
      msg_t = 16
      cpu += 2
      px, py = 65, 128
      dx, dy = 185, 128
      shot_clock = 24.0

    if k == K_2ND or k == K_ENTER:
      phase = 1
      aim_ang = 42.0
      aim_dir = 1
      is_three = (px < 218)

  elif phase == 1:
    aim_ang += aim_dir * 3.0
    if aim_ang > 72:
      aim_dir = -1
    elif aim_ang < 28:
      aim_dir = 1
    if k == K_2ND or k == K_ENTER:
      phase = 2
      aim_pwr = 10.0
      pwr_dir = 1

  elif phase == 2:
    aim_pwr += pwr_dir * 5.5
    if aim_pwr >= 100:
      pwr_dir = -1
    elif aim_pwr <= 5:
      pwr_dir = 1
    if k == K_2ND or k == K_ENTER:
      phase = 3
      rad = aim_ang * 3.14159 / 180.0
      spd = 8.5 + (aim_pwr / 100.0) * 7.5
      bx, by = float(px + 4), float(py - 6)
      bvx = cos(rad) * spd
      bvy = -sin(rad) * spd

  elif phase == 3:
    bx += bvx
    by += bvy
    bvy += 0.55
    if bx >= 283 and 54 <= by <= 96:
      bvx = -abs(bvx) * 0.55
      bx = 282
    if abs(bx - rim_x) < 9 and abs(by - rim_y) < 8 and bvy > 0:
      reset_possession(True)
    elif by > 195 or bx > 315:
      reset_possession(False)

  if phase < 3:
    shot_clock -= 0.14
    if shot_clock <= 0:
      reset_possession(False)

  # --- RENDER FRAME ---
  draw_court()
  draw_hud()

  if py < dy:
    draw_pixel_player(px, py, False, dribble, phase < 3)
    draw_pixel_player(dx, dy, True, dribble, False)
  else:
    draw_pixel_player(dx, dy, True, dribble, False)
    draw_pixel_player(px, py, False, dribble, phase < 3)

  if phase in (1, 2):
    draw_arc_guide()
  elif phase == 3:
    draw_ball(bx, by)

  if msg_t > 0:
    set_color(15, 18, 28)
    fill_rect(88, 24, 144, 18)
    set_color(250, 200, 40)
    draw_rect(88, 24, 144, 18)
    draw_text(96, 27, msg)
    msg_t -= 1

  show_draw()

# --- GAME OVER SCREEN ---
set_color(15, 18, 28)
fill_rect(50, 68, 220, 72)
set_color(250, 200, 40)
draw_rect(50, 68, 220, 72)
res = "YOU WIN!" if score > cpu else "CPU WINS!"
draw_text(118, 78, res)
set_color(255, 255, 255)
draw_text(82, 100, "FINAL: " + str(score) + " - " + str(cpu))
draw_text(74, 120, "PRESS CLEAR TO EXIT")
show_draw()
wait_key()
