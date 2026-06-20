import cv2
import time
import keyboard
import numpy as np
from PIL import ImageGrab
from collections import deque, namedtuple

tofind = (950, 155, 1335, 685)
ROWS = 4
COLS = 2

parts = [[(482, 279, 482 + 102, 279 + 102), (0, 0)],
[(627, 279, 627 + 102, 279 + 102), (1, 0)],
[(482, 423, 482 + 102, 423 + 102), (0, 1)],
[(627, 423, 627 + 102, 423 + 102), (1, 1)],
[(482, 566, 482 + 102, 566 + 102), (0, 2)],
[(627, 566, 627 + 102, 566 + 102), (1, 2)],
[(482, 711, 482 + 102, 711 + 102), (0, 3)],
[(627, 711, 627 + 102, 711 + 102), (1, 3)]]

def is_in(img, subimg):
    """return if 'subimg' is in 'img'"""
    subimg1 = cv2.cvtColor(np.array(subimg), cv2.COLOR_BGR2GRAY) # need gray image to do the matchTemplate
    res = cv2.matchTemplate(img, subimg1, cv2.TM_CCOEFF_NORMED)
    threshold = 0.65 # error coef
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        return True
    return False

def crop_box(im, box):
    width, height = im.size
    x1, y1, x2, y2 = box
    return im.crop((
        max(0, x1),
        max(0, y1),
        min(width, x2),
        min(height, y2)
    ))

def selection_score(im, box):
    """Score the white corner brackets that mark the current selector."""
    x1, y1, x2, y2 = box
    outside_near = 4
    outside_far = 34
    inside = 28
    strip = 8

    corner_strips = [
        (x1 - outside_far, y1 - strip, x1 - outside_near, y1 + inside),
        (x1 - strip, y1 - outside_far, x1 + inside, y1 - outside_near),
        (x2 + outside_near, y1 - strip, x2 + outside_far, y1 + inside),
        (x2 - inside, y1 - outside_far, x2 + strip, y1 - outside_near),
        (x1 - outside_far, y2 - inside, x1 - outside_near, y2 + strip),
        (x1 - strip, y2 + outside_near, x1 + inside, y2 + outside_far),
        (x2 + outside_near, y2 - inside, x2 + outside_far, y2 + strip),
        (x2 - inside, y2 + outside_near, x2 + strip, y2 + outside_far),
    ]

    score = 0
    active_corners = 0
    for corner in corner_strips:
        crop = np.array(crop_box(im, corner))
        if crop.size == 0:
            continue

        hsv = cv2.cvtColor(crop, cv2.COLOR_RGB2HSV)
        saturation = hsv[:, :, 1]
        value = hsv[:, :, 2]
        white_pixels = (saturation < 95) & (value > 170)
        white_count = int(np.count_nonzero(white_pixels))
        score += white_count
        if white_count > 20:
            active_corners += 1

    return score + (active_corners * 180)

def find_current_position(im):
    scores = [(selection_score(im, part[0]), part[1]) for part in parts]
    scores.sort(reverse=True, key=lambda score: score[0])

    best_score, best_position = scores[0]
    next_score = scores[1][0]
    printable_scores = ', '.join([f'{position}:{score:.1f}' for score, position in scores])
    print(f'[*] Fingerprint selector scores: {printable_scores}')

    if best_score < 220 or best_score - next_score < 80:
        print('[!] Current selected fingerprint part not confidently detected; using top-left.')
        return (0, 0), scores

    print(f'[*] Current selected fingerprint part detected at {best_position}')
    return best_position, scores

def clicked_score(im, box):
    x1, y1, x2, y2 = box
    inset = 12
    crop = np.array(im.crop((x1 + inset, y1 + inset, x2 - inset, y2 - inset)))
    hsv = cv2.cvtColor(crop, cv2.COLOR_RGB2HSV)
    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]

    white_ridges = (saturation < 80) & (value > 175)
    return int(np.count_nonzero(white_ridges))

def find_clicked_components(im, current_position):
    clicked = []

    for box, position in parts:
        score = clicked_score(im, box)

        if score >= 450:
            clicked.append(position)

    print(f'[*] Already clicked fingerprint parts: {clicked}')
    return clicked

def shortest_path(start_coordinate, end_coordinate):
    Point = namedtuple('Point', ('x', 'y'))
    ReverseLinkedNode = namedtuple("ReverseLinkedNode", ('value', 'prev_node', 'idx'))
    directions = [(0, 1, 's'), (1, 0, 'd'), (0, -1, 'w'), (-1, 0, 'a')]

    start = start_coordinate if isinstance(start_coordinate, Point) else Point(*start_coordinate)
    end = end_coordinate if isinstance(end_coordinate, Point) else Point(*end_coordinate)
    queue = deque([(start, ReverseLinkedNode(None, None, -1))])
    seen = {start}

    while len(queue) > 0:
        current_pos, path_head = queue.popleft()
        if current_pos == end:
            output_list = [None] * (path_head.idx + 1)
            while path_head.idx >= 0:
                output_list[path_head.idx] = path_head.value
                path_head = path_head.prev_node
            return output_list

        for delta_x, delta_y, key in directions:
            new_x, new_y = current_pos.x + delta_x, current_pos.y + delta_y
            if new_x == -1:
                new_x, new_y = COLS-1, new_y-1
            elif new_x == COLS:
                new_x, new_y = 0, new_y+1
            new_y = new_y % ROWS

            next_pos = Point(new_x, new_y)
            if next_pos in seen:
                continue

            seen.add(next_pos)
            queue.append((next_pos, ReverseLinkedNode(key, path_head, path_head.idx+1)))

    raise Exception('No path found')

def make_deselect_moves(clicked_components, current_position):
    moves = []
    cursor = current_position

    for component in clicked_components:
        path = shortest_path(cursor, component)
        moves.extend(path)
        moves.append('return')
        cursor = component

    return moves, cursor

def find_shortest_solution(target_coordinates, start_coordinate=(0, 0)):
    Point = namedtuple('Point', ('x', 'y'))
    ReverseLinkedNode = namedtuple("ReverseLinkedNode", ('value', 'prev_node', 'idx'))
    directions = [(0, 1, 's'), (1, 0, 'd'), (0, -1, 'w'), (-1, 0, 'a')]  # (delta_x, delta_y, key)

    target_coordinates = [p if isinstance(p, Point) else Point(*p) for p in target_coordinates]
    start_pos = start_coordinate if isinstance(start_coordinate, Point) else Point(*start_coordinate)
    target_mask = 0
    for target in target_coordinates:
        target_mask |= 1 << ((target.y * COLS) + target.x)

    # BFS initialization
    current_pos = start_pos
    visited_mask = 1 << ((current_pos.y * COLS) + current_pos.x)
    path_head: ReverseLinkedNode = ReverseLinkedNode(None, None, -1)
    if current_pos in target_coordinates:
        path_head = ReverseLinkedNode('return', path_head, 0)
    queue = deque([(current_pos, visited_mask, path_head)])  # (current_position, visited_mask, path_head)

    # loop until all points have been visited or a solution has been found
    while len(queue) > 0:
        current_pos, visited_mask, path_head = queue.popleft()

        # if all target points are visited, return the final path
        if visited_mask & target_mask == target_mask:
            output_list = [None] * (path_head.idx + 1)
            while path_head.idx >= 0:
                output_list[path_head.idx] = path_head.value
                path_head = path_head.prev_node
            return output_list + ['tab']

        # explore neighbors
        for delta_x, delta_y, key in directions:
            new_x, new_y = current_pos.x + delta_x, current_pos.y + delta_y
            # correct for wrapping
            if new_x == -1:
                new_x, new_y = COLS-1, new_y-1
            elif new_x == COLS:
                new_x, new_y = 0, new_y+1
            new_y = new_y % ROWS

            next_pos = Point(new_x, new_y)
            pos_mask = 1 << ((next_pos.y * COLS) + next_pos.x)
            next_visited_mask = visited_mask | pos_mask
            # skip if visited
            if visited_mask == next_visited_mask:
                continue

            next_path_head = ReverseLinkedNode(key, path_head, path_head.idx+1)
            # if next_pos is a target point
            if target_mask & pos_mask != 0:
                next_path_head = ReverseLinkedNode('return', next_path_head, next_path_head.idx+1)
            queue.append((next_pos, next_visited_mask, next_path_head))

    raise Exception('No solution found')

def main(bbox):
    print('[*] Casino Fingerprint')
    im = ImageGrab.grab(bbox)
    im = im.resize((1920,1080))
    sub0_ = im.crop(tofind)
    sub0 = cv2.cvtColor(np.array(sub0_.resize((round(sub0_.size[0] * 0.77), round(sub0_.size[1] * 0.77)))), cv2.COLOR_BGR2GRAY) # need to resize the image because fingerprints parts is smaller than the image + need gray image to do the matchTemplate

    # will store the location of the rights fingerprints
    togo = [part[1] for part in parts if is_in(sub0, im.crop(part[0]))]
    current_position, _ = find_current_position(im)
    clicked_components = find_clicked_components(im, current_position)

    deselect_moves, current_position_after_deselect = make_deselect_moves(clicked_components, current_position)
    moves = deselect_moves + find_shortest_solution(togo, current_position_after_deselect)

    # closing every images
    sub0_.close()
    im.close()

    if len(togo) == 0:
        print('[!] No matching fingerprint targets detected; skipping key presses.')
        return

    print('-', moves)
    for key in moves:
        keyboard.press_and_release(key)
        time.sleep(0.025)
    print('[*] END')
    print('=============================================')
