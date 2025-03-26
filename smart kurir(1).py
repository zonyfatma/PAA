import cv2
import numpy as np
import heapq
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.spatial import distance
import random
import tkinter as tk
from tkinter import Button, filedialog


def load_image():
    global binary_image, image_path
    image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if not image_path:
        return
    
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Gambar tidak ditemukan!")
        return

    if image.shape[1] < 1000 or image.shape[1] > 1500 or image.shape[0] < 700 or image.shape[0] > 1000:
        print("Error: Ukuran peta tidak sesuai!")
        return

    binary_image = cv2.inRange(image, (90, 90, 90), (150, 150, 150))
    print("Peta berhasil dimuat.")


def get_random_point(binary_image):
    white_pixels = np.column_stack(np.where(binary_image > 0))
    if len(white_pixels) == 0:
        raise ValueError("Error: Tidak ada area jalan yang valid pada peta!")
    return tuple(white_pixels[random.randint(0, len(white_pixels) - 1)])


def dijkstra(binary_image, start, end):
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
        raise ValueError("Error: Tidak ada jalur dari start ke finish!")

    return path[::-1]


def get_triangle_symbol(p1, p2):
    dy, dx = p2[0] - p1[0], p2[1] - p1[1]
    if abs(dx) > abs(dy):
        return '▶' if dx > 0 else '◀'
    else:
        return '▲' if dy < 0 else '▼'


def animate_path(binary_image, path, start, end):
    fig, ax = plt.subplots()
    ax.imshow(binary_image, cmap="gray", origin="upper")
    ax.plot(start[1], start[0], "yo", label="Source (Start)")
    ax.plot(end[1], end[0], "ro", label="Destination (Finish)")

    triangle = ax.text(path[0][1], path[0][0], '▲', fontsize=24, color='red', ha='center', va='center')

    step_size = max(1, len(path) // 300)

    def update(frame):
        idx = min(frame * step_size, len(path) - 1)
        y, x = path[idx]
        triangle.set_position((x, y))
        
        if idx < len(path) - 1:
            triangle.set_text(get_triangle_symbol(path[idx], path[idx + 1]))

        return triangle,

    ani = animation.FuncAnimation(fig, update, frames=(len(path) // step_size), interval=5, blit=True, repeat=False)
    ax.legend()
    plt.show()


def randomize_positions():
    global start, end
    if binary_image is None:
        print("Error: Peta belum dimuat!")
        return
    
    start = get_random_point(binary_image)
    end = get_random_point(binary_image)
    while start == end:
        end = get_random_point(binary_image)
    print(f"Source: {start}, Destination: {end}")
    
    path = dijkstra(binary_image, start, end)
    print(f"Jalur ditemukan! Panjang jalur: {len(path)}")
    animate_path(binary_image, path, start, end)


if __name__ == "__main__":
    binary_image = None
    root = tk.Tk()
    root.title("Smart Courier")

    Button(root, text="Load Map", command=load_image).pack(pady=10)
    Button(root, text="Acak Kurir dan Tujuan", command=randomize_positions).pack(pady=10)
    Button(root, text="Keluar", command=root.destroy).pack(pady=10)

    root.mainloop()
