# coding=utf8

import random
import sys

random.seed()

def gen_maze(nodes, node_edges):
    result_edges = set()
    result_nodes = set()

    remaining_nodes = set(nodes)

    node = random.choice(tuple(nodes))
    result_nodes.add(node)
    remaining_nodes.remove(node)

    while remaining_nodes:
        # do a loop-erased random walk from a random node outside our tree to one inside it
        walk_nodes = []
        seen_nodes = set()

        node = random.choice(tuple(remaining_nodes))
        walk_nodes.append(node)
        seen_nodes.add(node)

        while node not in result_nodes:
            # follow a random edge
            node = random.choice(tuple(node_edges[node]))

            # if we created a loop, erase it
            if node in seen_nodes:
                while walk_nodes[-1] != node:
                    seen_nodes.remove(walk_nodes.pop(-1))
                continue

            # add this node to our list
            walk_nodes.append(node)
            seen_nodes.add(node)

        # now add the walk to our result
        result_nodes.update(walk_nodes)
        remaining_nodes.difference_update(walk_nodes)
        for i in range(0, len(walk_nodes)-1):
            result_edges.add((walk_nodes[i], walk_nodes[i+1]))
        

    return result_edges

def gen_grid_maze(width, height):
    nodes = set((x, y) for x in range(width) for y in range(height))
    edges = {}
    for x in range(0, width):
        for y in range(0, height):
            edges[x, y] = nodes.intersection(((x-1, y), (x+1, y), (x, y-1), (x, y+1)))

    return gen_maze(nodes, edges)

def print_grid_maze(width, height, edges):
    LEFT = 1
    RIGHT = 2
    UP = 4
    DOWN = 8

    box_chars = u' ╴╶─╵┘└┴╷┐┌┬│┤├┼'

    for y in range(height):
        for x in range(width):
            ch = 0
            if ((x, y), (x-1, y)) in edges or ((x-1, y), (x, y)) in edges:
                ch += LEFT
            if ((x, y), (x+1, y)) in edges or ((x+1, y), (x, y)) in edges:
                ch += RIGHT
            if ((x, y), (x, y-1)) in edges or ((x, y-1), (x, y)) in edges:
                ch += UP
            if ((x, y), (x, y+1)) in edges or ((x, y+1), (x, y)) in edges:
                ch += DOWN

            sys.stdout.write(box_chars[ch])
        sys.stdout.write('\n')
    sys.stdout.flush()

if __name__ == '__main__':
    print_grid_maze(10, 10, gen_grid_maze(10, 10))

