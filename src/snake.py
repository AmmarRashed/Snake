import pickle
import random
import time
import turtle
from datetime import datetime
from functools import partial
from os.path import join
from typing import List

SPEED = 25
DELAY = 0.025
SEGMENT_SIZE = 25
STATIC_DIR = "static"
SCORES_PATH = join(STATIC_DIR, "scores.pkl")
scores = pickle.load(open(SCORES_PATH, 'rb'))
try:
    HIGH_SCORE = max(scores)[0]
except ValueError:
    HIGH_SCORE = 0

# window
wn = turtle.Screen()
wn.title("Snake V1.0")
wn.setup(800, 800)
height = 1000
width = 1000
wn.setworldcoordinates(0, 0, width, height)
wn.tracer(0)

# loading images
UP = join(STATIC_DIR, "up.gif")
DOWN = join(STATIC_DIR, "down.gif")
RIGHT = join(STATIC_DIR, "right.gif")
LEFT = join(STATIC_DIR, "left.gif")
TAIL = join(STATIC_DIR, "tail.gif")
APPLE = join(STATIC_DIR, "apple.gif")

for s in [UP, DOWN, RIGHT, LEFT, TAIL, APPLE]:
    wn.register_shape(s)


class SnakeHead(turtle.Turtle):
    direction = "stop"


head: SnakeHead
snake: List[turtle.Turtle]
apple: turtle.Turtle
pen: turtle.Turtle
score: int = 0


def init_game():
    global head, snake, apple, pen, HIGH_SCORE
    # scores
    pen = turtle.Turtle()
    pen.speed(0)
    pen.shape("square")
    pen.color("red")
    pen.penup()
    pen.hideturtle()
    pen.goto(width // 2, height * 9 // 10)
    pen.write("Score: 0 High Score: {}".format(HIGH_SCORE), align="center", font=("Courier", 24, "normal"))

    # snake head
    head = turtle.Turtle()
    head.speed(0)
    head.shape(RIGHT)
    head.shapesize(SEGMENT_SIZE, SEGMENT_SIZE)
    head.color("green")
    head.penup()
    head.direction = "stop"
    head.goto(width // 2, height // 2)
    snake = [head]

    # food
    apple = turtle.Turtle()
    apple.speed(0)
    apple.shape(APPLE)
    apple.penup()

    generate_apple()

    # controls
    wn.listen()
    wn.onkeypress(partial(goto, direction="up", invalid="down"), "Up")
    wn.onkeypress(partial(goto, direction="down", invalid="up"), "Down")
    wn.onkeypress(partial(goto, direction="left", invalid="right"), "Left")
    wn.onkeypress(partial(goto, direction="right", invalid="left"), "Right")


def reset():
    global score
    wn.reset()
    wn.clear()
    for s in snake:
        s.goto(width + SEGMENT_SIZE, height + SEGMENT_SIZE)
    score = 0
    init_game()


def game_over():
    scores.append((score, datetime.now().strftime("%I:%M%p on %B %d, %Y")))
    pickle.dump(scores, open(SCORES_PATH, 'wb'))
    reset()


def generate_apple():
    apple.goto(random.randint(1, width - 1), random.randint(1, height - 1))


# movements
def goto(direction, invalid):
    if head.direction != invalid:
        head.direction = direction
        head.shape(join(STATIC_DIR, f"{direction}.gif"))


def pause():
    head.direction = "stop"


def generate_segment():
    segment = turtle.Turtle()
    segment.speed(0)
    segment.shape(TAIL)
    segment.penup()
    segment.shapesize(SEGMENT_SIZE, SEGMENT_SIZE)
    return segment


def grow():
    new_segment = generate_segment()
    snake.append(new_segment)


def update_tail():
    if head.direction != "stop":
        # Each segment is going to move to the position of the one before it
        for i in range(len(snake) - 1, 0, -1):
            x = snake[i - 1].xcor()
            y = snake[i - 1].ycor()
            snake[i].goto(x, y)


def body_collision():
    global snake
    for segment in snake[1:]:
        if segment.distance(head) < SEGMENT_SIZE:  # BAM!
            return True
    return False


def update_score():
    global HIGH_SCORE, score
    pen.clear()
    HIGH_SCORE = max(HIGH_SCORE, score)
    pen.write("score: {} High Score: {}".format(score, HIGH_SCORE), align="center", font=("Courier", 24, "normal"))


def step():
    global score
    update_tail()
    # move
    y = head.ycor()
    x = head.xcor()

    if head.direction == "down":
        new_y = y - SPEED
        if new_y < 0:
            new_y += height
        head.sety(new_y)

    elif head.direction == "up":
        new_y = y + SPEED
        if new_y > height:
            new_y = 0
        head.sety(new_y)

    elif head.direction == "right":
        new_x = x + SPEED
        if new_x > width:
            new_x = 0
        head.setx(new_x)

    elif head.direction == "left":
        new_x = x - SPEED
        if new_x < 0:
            new_x = width
        head.setx(new_x)

    # eat, if you catch the apple
    if head.distance(apple) < SEGMENT_SIZE:
        grow()
        score += 10
        update_score()
        # regenerate another apple at a different random position
        generate_apple()

    if body_collision():
        game_over()


init_game()

while True:
    wn.update()
    time.sleep(DELAY)
    step()
