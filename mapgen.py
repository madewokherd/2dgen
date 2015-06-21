# coding=utf8

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

