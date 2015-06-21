# coding=utf8

# Copyright (C) 2015 by Vincent Povirk
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import random
import sys

import maze

random.seed()

directions = [(0,-1), (1,0), (0,1), (-1,0)]

def get_random_weighted(total_weights, objects):
    i = random.randint(1, total_weights)
    for weight, obj in objects:
        i -= weight
        if i <= 0:
            return obj
    raise ValueError("total_weights was less than the sum of weights in objects")

def get_random_obj(obj, direction, probabilities):
    if (obj, direction) in probabilities:
        return get_random_weighted(*probabilities[obj, direction])
    return get_random_weighted(*probabilities[None])

def generate_map(width, height, probabilities):
    # probabilities: dictionary of (object, direction) to (sum of weights, list of (weight, object))
    # probabilities[None] is used as a fallback

    result = [None] * (width * height)

    edges = maze.gen_grid_maze(width, height)

    start_x, start_y = random.randint(0, width-1), random.randint(0, height-1)

    result[start_x + start_y*width] = get_random_weighted(*probabilities[None])

    to_check = [(start_x, start_y)]

    while to_check:
        check_x, check_y = to_check.pop()
        
        for dir_x, dir_y in directions:
            neighbor_x = check_x + dir_x
            neighbor_y = check_y + dir_y

            if not (0 <= neighbor_x < width) or not (0 <= neighbor_y < height):
                continue

            if result[neighbor_x + neighbor_y*width] is not None:
                continue

            if ((check_x, check_y), (neighbor_x, neighbor_y)) not in edges and \
                ((neighbor_x, neighbor_y), (check_x, check_y)) not in edges:
                continue

            result[neighbor_x + neighbor_y*width] = get_random_obj(result[check_x + check_y*width], (dir_x,dir_y), probabilities)

            to_check.append((neighbor_x, neighbor_y))

    return result

def print_map(width, height, values):
    for y in range(height):
        for x in range(width):
            sys.stdout.write(values[x + y*width])
        sys.stdout.write('\n')
    sys.stdout.flush()

def parse_puzzlescript_levels(levels_text):
    levels = []
    this_level = []

    rotations = {}

    for line in levels_text.splitlines():
        line = line.lower().strip()
        if line.startswith('message '):
            continue

        if line.startswith('rotations '):
            for r in line.split()[1:]:
                rotations[r[0]] = r[1]
                rotations[r[1]] = r[2]
                rotations[r[2]] = r[3]
                rotations[r[3]] = r[0]
            continue

        if not line:
            if this_level:
                levels.append(this_level)
                this_level = []
            continue

        this_level.append(line)

    parsed_levels = []

    for level in levels:
        width = len(level[0])
        height = len(level)
        parsed = [None]*(width * height)

        for y, line in enumerate(level):
            parsed[y*width:y*width+width] = list(line)

        parsed_levels.append((width, height, parsed))

    probabilities = {}

    # add rotations
    if rotations:
        to_rotate = parsed_levels
        for x in range(3):
            rotated_levels = []
            
            for width, height, old_objects in to_rotate:
                rotated = [None] * (height * width)
                
                for y in range(height):
                    for x in range(width):
                        rx = height - 1 - y
                        ry = x
                        
                        rotated[rx + ry * height] = rotations.get(old_objects[x + y * width], old_objects[x + y * width])

                rotated_levels.append((height, width, rotated))

            parsed_levels.extend(rotated_levels)
            
            to_rotate = rotated_levels

    # FIXME: add reflections?

    # FIXME: add inverses?

    # calculate probabilities[None]
    total_weights = 0
    weights = {}
    for width, height, objects in parsed_levels:
        for obj in objects:
            total_weights += 1
            weights[obj] = weights.get(obj,0)+1

    probabilities[None] = (total_weights, [(w, obj) for obj, w in weights.iteritems()])

    for dx, dy in directions:
        total_weights = {}
        weights = {}
        
        for width, height, objects in parsed_levels:
            if dx == -1:
                start_points = [(width-1, y) for y in range(height)]
            elif dx == 1:
                start_points = [(0, y) for y in range(height)]
            elif dy == -1:
                start_points = [(x, height-1) for x in range(width)]
            elif dy == 1:
                start_points = [(x, 0) for x in range(width)]

            for sx, sy in start_points:
                while True:
                    nx = sx + dx
                    ny = sy + dy
                    if not (0 <= nx < width and 0 <= ny < height):
                        break

                    sobj = objects[sy*width + sx]
                    nobj = objects[ny*width + nx]
                    
                    total_weights[sx] = total_weights.get(sx, 0) + 1
                    weights[sx, sy] = weights.get((sx, sy), 0) + 1

                    sx = nx
                    sy = ny

        for obj, total in total_weights.iteritems():
            probabilities[obj, (dx,dy)] = (total, [])

        for (sobj, nobj), weight in weights.iteritems():
            probabilities[sobj, (dx,dy)][1].append((weight, nobj))

    return probabilities

if sys.argv[1] == 'bitmap':
    width = int(sys.argv[2])
    height = int(sys.argv[3])

    probabilities = {}
    probabilities[None] = (2, ((1,'.'), (1,'#')))
    for d in directions:
        probabilities['.', d] = (10, ((1,'#'),(9,'.')))
        probabilities['#', d] = (10, ((1,'.'),(9,'#')))

    values = generate_map(width, height, probabilities)

    print_map(width, height, values)
elif sys.argv[1] == 'puzzlescript':
    width = int(sys.argv[2])
    height = int(sys.argv[3])
    
    level_text = sys.stdin.read()

    probabilities = parse_puzzlescript_levels(level_text)

    values = generate_map(width, height, probabilities)

    print_map(width, height, values)

