import sys
from heapq import heappush, heappop

class Node():
    def __init__(self, state, parent, action, cost=0, priority=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost 
        self.priority = priority  

    def __lt__(self, other):
        return self.priority < other.priority

class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier.pop()
            return node

class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier.pop(0)
            return node

class PriorityFrontier(StackFrontier):

    def __init__(self):
        self.frontier = []
        self.entry_finder = {}
        self.counter = 0

    def add(self, node):
        heappush(self.frontier, node)

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = heappop(self.frontier)
            return node

class Maze():

    def __init__(self, filename):

        
        with open(filename) as f:
            contents = f.read()

        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.solution = None

    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()

    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    def heuristic(self, state):
        (x1, y1) = state
        (x2, y2) = self.goal
        return abs(x1 - x2) + abs(y1 - y2)

    def solve(self, algorithm="DFS"):

        self.num_explored = 0

        start = Node(state=self.start, parent=None, action=None, cost=0)
        if algorithm == "DFS":
            frontier = StackFrontier()
        elif algorithm == "BFS":
            frontier = QueueFrontier()
        elif algorithm == "A*":
            frontier = PriorityFrontier()
            start.priority = self.heuristic(start.state)
        else:
            raise ValueError("Algoritmo no soportado")

        frontier.add(start)

        self.explored = set()

        while True:

            if frontier.empty():
                raise Exception("no solution")

            node = frontier.remove()
            self.num_explored += 1

            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            self.explored.add(node.state)

            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action, cost=node.cost + 1)
                    if algorithm == "A*":
                        child.priority = child.cost + self.heuristic(child.state)
                    frontier.add(child)

    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw
        cell_size = 50
        cell_border = 2

        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                if col:
                    fill = (40, 40, 40)

                elif (i, j) == self.start:
                    fill = (255, 0, 0)

                elif (i, j) == self.goal:
                    fill = (0, 171, 28)

                elif solution is not None and show_solution and (i, j) in solution:
                    fill = (220, 235, 113)

                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                else:
                    fill = (237, 240, 252)

                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        img.save(filename)

def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python maze.py maze.txt")

    m = Maze(sys.argv[1])
    print("Laberinto:")
    m.print()

    print("Seleccione el algoritmo de búsqueda:")
    print("1. DFS (Búsqueda en Profundidad)")
    print("2. BFS (Búsqueda en Anchura)")
    print("3. A*")
    choice = input("Ingrese el número correspondiente al algoritmo: ")

    if choice == "1":
        algorithm = "DFS"
    elif choice == "2":
        algorithm = "BFS"
    elif choice == "3":
        algorithm = "A*"
    else:
        sys.exit("Selección inválida")

    print(f"Resolviendo el laberinto usando {algorithm}...")
    try:
        m.solve(algorithm=algorithm)
    except Exception as e:
        sys.exit(str(e))

    print("Estados explorados:", m.num_explored)
    print("Solución:")
    m.print()
    m.output_image("maze.png", show_explored=True)
    print("Imagen de la solución guardada como maze.png")

if __name__ == "__main__":
    main()
