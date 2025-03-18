import pygame as pg

pg.init()
screen = pg.display.set_mode((500, 400))
pg.display.set_caption("Visualização de Fontes")

# Lista de fontes para testar
font_names = ["Arial", "Courier", "Comic Sans MS", "Consolas", "Georgia",
              "Impact", "Tahoma", "Times New Roman", "Verdana"]

screen.fill((30, 30, 30))
y = 10  # Posição inicial

for font_name in font_names:
    try:
        font = pg.font.SysFont(font_name, 30)
        text_surface = font.render(font_name, True, (255, 255, 255))
        screen.blit(text_surface, (10, y))
        y += 40  # Espaçamento entre as fontes
    except:
        print(f"Fonte {font_name} não disponível.")

pg.display.flip()

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

pg.quit()