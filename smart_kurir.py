import cv2
import numpy as np
import heapq
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import tkinter as tk
from tkinter import Button, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

class SmartCourierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Courier - Final Version")

        self.original_image = None  
        self.binary_image = None    
        self.start = None
        self.end = None
        self.path = None
        self.animation = None
        self.paused = False
        self.current_frame = 0

        self.setup_gui()

    def setup_gui(self):
        Button(self.root, text="Load Map", command=self.load_map).pack(pady=5)
        Button(self.root, text="Randomize Positions", command=self.randomize_positions).pack(pady=5)
        Button(self.root, text="Start/Resume", command=self.start_or_resume_animation).pack(pady=5)
        Button(self.root, text="Stop", command=self.stop_animation).pack(pady=5)
        Button(self.root, text="Reset Cat Position", command=self.reset_animation).pack(pady=5)
        Button(self.root, text="Exit", command=self.root.quit).pack(pady=5)

        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def load_map(self):
        file_path = filedialog.askopenfilename(title="Select Map Image", 
                                               filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            try:
                self.original_image = cv2.imread(file_path, cv2.IMREAD_COLOR)
                if self.original_image is None:
                    raise FileNotFoundError(f"Image '{file_path}' not found!")

                self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)

                h, w = self.original_image.shape[:2]
                if not (1000 <= w <= 1500 and 700 <= h <= 1000):
                    raise ValueError("Ukuran peta harus 1000–1500px (lebar) dan 700–1000px (tinggi)")

                self.binary_image = cv2.inRange(self.original_image, (90, 90, 90), (150, 150, 150))

                self.ax.clear()
                self.ax.imshow(self.original_image, origin="upper")
                self.canvas.draw()
                print("Map loaded successfully.")

            except Exception as e:
                print(f"Error: {e}")

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

    def plot_flag_icon(self, image_path, coord, zoom=0.05):
        try:
            img = plt.imread(image_path)
            imagebox = OffsetImage(img, zoom=zoom)
            ab = AnnotationBbox(imagebox, (coord[1], coord[0]), frameon=False)
            self.ax.add_artist(ab)
        except Exception as e:
            print(f"Error loading flag icon: {e}")

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

            if self.animation:
                self.animation.event_source.stop()
                self.animation = None

            self.ax.clear()
            self.ax.imshow(self.original_image, origin="upper")

            self.plot_flag_icon("flag_yellow.png", self.start)
            self.plot_flag_icon("flag_red.png", self.end)

            self.triangle = self.ax.text(self.start[1], self.start[0], '▲', fontsize=22, 
                                         color='red', ha='center', va='center')
            self.canvas.draw()
            self.current_frame = 0
            self.paused = False

        except Exception as e:
            print(f"Error: {e}")

    def start_or_resume_animation(self):
        if not self.path:
            print("Error: Randomize positions first!")
            return

        if self.paused and self.animation:
            self.paused = False
            self.animation.event_source.start()
        else:
            self.paused = False
            step_size = 3

            def update(frame):
                if self.paused:
                    return self.triangle,

                idx = min(self.current_frame, len(self.path) - 1)
                y, x = self.path[idx]
                self.triangle.set_position((x, y))

                if idx < len(self.path) - 1:
                    next_idx = min(self.current_frame + step_size, len(self.path) - 1)
                    self.triangle.set_text(self.get_triangle_symbol(self.path[idx], self.path[next_idx]))

                self.current_frame += step_size
                if self.current_frame >= len(self.path):
                    self.animation.event_source.stop()
                return self.triangle,

            self.animation = animation.FuncAnimation(
                self.fig,
                update,
                frames=range(0, len(self.path), step_size),
                interval=1,
                blit=True,
                repeat=False
            )
            self.canvas.draw()

    def stop_animation(self):
        if self.animation:
            self.paused = True
            self.animation.event_source.stop()

    def reset_animation(self):
        if not self.path:
            print("Error: Tidak ada jalur untuk di-reset!")
            return

        try:
            if self.animation:
                self.animation.event_source.stop()
                self.animation = None

            self.ax.clear()
            self.ax.imshow(self.original_image, origin="upper")

            self.plot_flag_icon("flag_yellow.png", self.start)
            self.plot_flag_icon("flag_red.png", self.end)

            self.triangle = self.ax.text(self.start[1], self.start[0], '▲', fontsize=22,
                                         color='red', ha='center', va='center')

            self.canvas.draw()

            self.current_frame = 0
            self.paused = True
            print("Kurir kembali ke titik awal. Tekan Start/Resume untuk melanjutkan.")

        except Exception as e:
            print(f"Error during reset: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartCourierApp(root)
    root.mainloop()
