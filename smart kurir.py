import pygame
from tkinter import Tk, filedialog

# Inisialisasi Pygame
pygame.init()

# Fungsi untuk memuat gambar peta dari file
def load_map():
    root = Tk()
    root.withdraw()  # Sembunyikan jendela utama Tkinter
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])  
    if file_path:  # Jika pengguna memilih file
        return pygame.image.load(file_path)
    return None

# Muat peta awal (opsional, bisa None)
map_image = None

# Ukuran layar default
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Smart Kurir")

# Warna latar belakang
WHITE = (255, 255, 255)

# Tombol Load Peta
button_color = (100, 200, 100)
button_rect = pygame.Rect(50, 50, 200, 50)
font = pygame.font.Font(None, 36)
button_text = font.render("Load Map", True, (255, 255, 255))

# Loop utama
running = True
while running:
    screen.fill(WHITE)  # Bersihkan layar
    
    # Gambar tombol
    pygame.draw.rect(screen, button_color, button_rect)
    screen.blit(button_text, (button_rect.x + 50, button_rect.y + 10))

    # Tampilkan gambar peta jika sudah dimuat
    if map_image:
        screen.blit(map_image, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                map_image = load_map()  # Muat gambar baru

    pygame.display.update()

pygame.quit()
