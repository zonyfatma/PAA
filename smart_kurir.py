import cv2
import numpy as np
import heapq
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.spatial import distance

def load_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Error: Gambar '{image_path}' tidak ditemukan!")

    _, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV) 
    return binary_image

def select_points(image):
    points = []

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((y, x))  
            if len(points) == 2:
                cv2.destroyAllWindows()

    temp_img = image.copy()
    cv2.imshow("Pilih start dan finish (klik 2 titik)", temp_img)
    cv2.setMouseCallback("Pilih start dan finish (klik 2 titik)", click_event)
    cv2.waitKey(0)

    if len(points) < 2:
        raise ValueError("Error: Harap pilih dua titik!")

    return points[0], points[1]

def find_nearest_valid_point(binary_image, point):
    if binary_image[point] > 0:  
        return point

    white_pixels = np.column_stack(np.where(binary_image > 0))  
    nearest_index = distance.cdist([point], white_pixels).argmin()
    return tuple(white_pixels[nearest_index]) 

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

def animate_path(binary_image, path):
    fig, ax = plt.subplots()
    ax.imshow(binary_image, cmap="gray", origin="upper")

    triangle = ax.text(path[0][1], path[0][0], '▲', fontsize=12, color='green', ha='center', va='center')

    step_size = max(1, len(path) // 300)

    def update(frame):
        idx = min(frame * step_size, len(path) - 1)
        y, x = path[idx]
        triangle.set_position((x, y))

        if idx < len(path) - 1:
            triangle.set_text(get_triangle_symbol(path[idx], path[idx + 1]))

        return triangle,

    ani = animation.FuncAnimation(fig, update, frames=(len(path) // step_size), interval=5, blit=True, repeat=False)
    plt.show()

if __name__ == "__main__":
    image_path = "jalan.png"
    try:
        binary_image = load_image(image_path)
        print("Pilih titik start dan finish di gambar.")
        start, end = select_points(binary_image)

        start = find_nearest_valid_point(binary_image, start)
        end = find_nearest_valid_point(binary_image, end)
        print(f"Start: {start}, Finish: {end}")

        path = dijkstra(binary_image, start, end)
        print(f"Jalur ditemukan! Panjang jalur: {len(path)}")
        animate_path(binary_image, path)

    except FileNotFoundError as e:
        print(e)
    except ValueError as e:
        print(e)
