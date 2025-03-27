import cv2
import numpy as np
import heapq
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import tkinter as tk
from tkinter import Button, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SmartCourierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Courier - High Speed")

        # Initialize variables
        self.binary_image = None
        self.start = None
        self.end = None
        self.path = None
        self.animation = None
        self.paused = False
        self.current_frame = 0

        # GUI Setup
        self.setup_gui()

    def setup_gui(self):
        # Create buttons
        Button(self.root, text="Load Map", command=self.load_map).pack(pady=5)
        Button(self.root, text="Randomize Positions", command=self.randomize_positions).pack(pady=5)
        Button(self.root, text="Start/Resume", command=self.start_or_resume_animation).pack(pady=5)
        Button(self.root, text="Stop", command=self.stop_animation).pack(pady=5)
        Button(self.root, text="Exit", command=self.root.quit).pack(pady=5)

        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def load_map(self):
        file_path = filedialog.askopenfilename(title="Select Map Image", 
                                             filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            try:
                self.binary_image = self.load_image(file_path)
                self.ax.clear()
                self.ax.imshow(self.binary_image, cmap="gray", origin="upper")
                self.canvas.draw()
                print("Map loaded successfully.")
            except Exception as e:
                print(f"Error: {e}")

    def load_image(self, image_path):
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image '{image_path}' not found!")

        if image.shape[1] < 1000 or image.shape[1] > 1500 or image.shape[0] < 700 or image.shape[0] > 1000:
            raise ValueError("Map size must be between 1000x700 and 1500x1000 pixels!")

        binary_image = cv2.inRange(image, (90, 90, 90), (150, 150, 150))
        return binary_image

    def get_random_point(self, binary_image):
        white_pixels = np.column_stack(np.where(binary_image > 0))
        if len(white_pixels) == 0:
            raise ValueError("No valid road areas found on the map!")
        return tuple(white_pixels[random.randint(0, len(white_pixels) - 1)])

    def dijkstra(self, binary_image, start, end):
        rows, cols = binary_image.shape
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] 
        queue = [(0, start)]
        visited = set()
        parent = {start: None}

        while queue:
            cost, current = heapq.heappop(queue)
            if current in visited:
                continue
            visited.add(current)

            if current == end:
                break

            for dx, dy in directions:
                neighbor = (current[0] + dx, current[1] + dy)
                if (0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and
                        binary_image[neighbor] > 0 and neighbor not in visited):
                    heapq.heappush(queue, (cost + 1, neighbor))
                    if neighbor not in parent:
                        parent[neighbor] = current

        path = []
        step = end
        while step is not None:
            path.append(step)
            step = parent.get(step)

        if len(path) == 1:
            raise ValueError("No path found from start to finish!")

        return path[::-1]

    def get_triangle_symbol(self, p1, p2):
        dy, dx = p2[0] - p1[0], p2[1] - p1[1]
        if abs(dx) > abs(dy): 
            return '▶' if dx > 0 else '◀' 
        else:  
            return '▲' if dy < 0 else '▼'

    def randomize_positions(self):
        if self.binary_image is None:
            print("Error: Load map first!")
            return

        try:
            self.start = self.get_random_point(self.binary_image)
            self.end = self.get_random_point(self.binary_image)
            while self.start == self.end:
                self.end = self.get_random_point(self.binary_image)

            self.path = self.dijkstra(self.binary_image, self.start, self.end)
            print(f"Start: {self.start}, End: {self.end}")
            print(f"Path found! Length: {len(self.path)} steps")

            # Clear previous animation
            if self.animation:
                self.animation.event_source.stop()

            # Draw new positions
            self.ax.clear()
            self.ax.imshow(self.binary_image, cmap="gray", origin="upper")
            self.ax.plot(self.start[1], self.start[0], "yo", label="Start")
            self.ax.plot(self.end[1], self.end[0], "ro", label="End")
            self.triangle = self.ax.text(self.start[1], self.start[0], '▲', fontsize=22, 
                                        color='red', ha='center', va='center')
            self.ax.legend()
            self.canvas.draw()
            self.current_frame = 0
            self.paused = False

        except Exception as e:
            print(f"Error: {e}")

    def start_or_resume_animation(self):
        if not self.path:
            print("Error: Randomize positions first!")
            return

        if self.paused:
            # Resume animation
            self.paused = False
            self.animation.event_source.start()
        else:
            # Start new animation with ultra-fast speed
            self.paused = False
            
            def update(frame):
                if self.paused:
                    return self.triangle,

                idx = min(self.current_frame, len(self.path) - 1)
                y, x = self.path[idx]
                self.triangle.set_position((x, y))

                if idx < len(self.path) - 1:
                    self.triangle.set_text(self.get_triangle_symbol(self.path[idx], self.path[idx + 1]))

                self.current_frame += 1
                if self.current_frame >= len(self.path):
                    self.animation.event_source.stop()
                return self.triangle,

            # Ultra-fast animation settings (5ms interval)
            self.animation = animation.FuncAnimation(
                self.fig, 
                update, 
                frames=len(self.path), 
                interval=5,  # Extreme speed (original: 50ms)
                blit=True, 
                repeat=False
            )
            self.canvas.draw()

    def stop_animation(self):
        if self.animation:
            self.paused = True
            self.animation.event_source.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartCourierApp(root)
    root.mainloop()
