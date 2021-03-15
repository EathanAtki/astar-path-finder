import pygame
import math
from queue import PriorityQueue

WIDTH = 1000
WIN = pygame.display.set_mode((WIDTH,WIDTH))
pygame.display.set_caption("Path Finder")

RED = (74,71,163)
GREEN = (167,197,235)
BLUE = (0,0,255)
YELLOW = (0,132,135)
WHITE = (65,60,105)
BLACK = (255,255,255)
PURPLE = (112,159,176)
ORANGE = (225,165,0)
GREY = (128,128,128)
TURQUOISE = (64,224,208)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row*width
        self.y = col*width
        self.color = WHITE
        self.neighbours = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return  self.row, self.col
    
    # Get Methods
    def is_exhausted(self):
        return self.color == RED
    
    def is_accessible(self):
        return self.color == GREEN
    
    def is_partician(self):
        return self.color == BLACK
    
    def is_start(self):
        return self.color == ORANGE
    
    def is_end(self):
        return self.color == TURQUOISE
    
    def reset(self):
        self.color = WHITE

    # Set Methods
    def set_exhausted(self):
        self.color = RED
    
    def set_accessible(self):
        self.color = GREEN
    
    def set_partition(self):
        self.color = BLACK
    
    def set_start(self):
        self.color = ORANGE
    
    def set_end(self):
        self.color = TURQUOISE
    
    def set_path(self):
        self.color = PURPLE
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbours(self, grid):
        self.neighbours = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_partician(): #Check Down Neighbour
            self.neighbours.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_partician():#Check Up Neighbour
            self.neighbours.append(grid[self.row - 1][self.col])

        if self.col > 0 and not grid[self.row][self.col - 1].is_partician():#Check Left Neighbour
            self.neighbours.append(grid[self.row][self.col - 1])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_partician():#Check Right Neighbour
            self.neighbours.append(grid[self.row][self.col + 1])


    def __lt__(self, other):
        return False

def heuristic(p1,p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1-x2)+abs(y1-y2)

def reconstruct_path(came_from,current,draw):
    while current in came_from:
        current = came_from[current]
        current.set_path()
        draw()



def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = heuristic(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.set_end()
            return True

        for neighbour in current.neighbours:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + heuristic(neighbour.get_pos(), end.get_pos())
                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.set_accessible()
            
        draw()

        if current != start:
            current.set_exhausted()

    return False




def create_grid(rows, width):
    grid = []
    difference = width//rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, difference, rows)
            grid[i].append(node)

    return grid

def draw_grid(win, rows, width):
    difference = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*difference), (width, i*difference))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*difference, 0), (j*difference, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update();

def get_click_pos(pos, rows, width):
    difference = width // rows
    y, x  = pos
    row = y // difference
    col = x // difference
    return row, col

def main(win, width):
    ROWS = 50
    grid = create_grid(ROWS, WIDTH)

    start = None
    end = None

    run = True
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_click_pos(pos, ROWS, width)
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.set_start()
                elif not end and node != start:
                    end = node
                    end.set_end()

                elif node != end and node != start:
                    node.set_partition()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_click_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbours(grid)

                    algorithm(lambda:draw(win, grid, ROWS, width), grid, start, end )

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = create_grid(ROWS, width)

    pygame.quit()  

main(WIN, WIDTH)
