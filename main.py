import pygame as pg
import json
from balao import Enemy
from mundo import World
from arqueiro import Turret
from botoes import Button
import config as c


pg.init()


clock = pg.time.Clock()

#crian a janela do jogo
screen = pg.display.set_mode((c.LARGURA_TELA + c.PAINEL_LATERAL, c.ALTURA_TELA))
pg.display.set_caption("Tower Defence")
help_screen_stage = 1

#variaveis do jogo
game_over = False
game_outcome = 0# -1 é derrota e 1 é vitoria
level_started = False
last_enemy_spawn = pg.time.get_ticks()
placing_turrets = False
selected_turret = None
game_paused = False  
pause_button_clicked = False
#carregando imagens

map_image = pg.image.load('levels/novosNiveis/level.png').convert_alpha()
map_image2 = pg.image.load('levels/novosNiveis/level2.png').convert_alpha()
map_image3 = pg.image.load('levels/novosNiveis/level3.png').convert_alpha()


#arqueiros spritesheets
turret_spritesheets = []
for x in range(1, c.NIVEL_ARQUEIRO + 1):
  turret_sheet = pg.image.load(f'assets/images/turrets/Arqueiro_Atirando_{x}.png').convert_alpha()
  turret_spritesheets.append(turret_sheet)
  
#imagem do arqueiro para o cursor do mouse
cursor_turret = pg.image.load('assets/images/turrets/Arqueiro_Menu.png').convert_alpha()

#monstros
enemy_images = {
  "weak": pg.image.load('assets/images/enemies/alien1.png').convert_alpha(),
  "medium": pg.image.load('assets/images/enemies/alien2.png').convert_alpha(),
  "strong": pg.image.load('assets/images/enemies/alien3.png').convert_alpha(),
  "elite": pg.image.load('assets/images/enemies/alien4.png').convert_alpha(),
  "god": pg.image.load('assets/images/enemies/alien5.png').convert_alpha()
}

#carregando imagens
sidebar_background = pg.image.load('assets/images/gui/Moldura_Menu.png').convert_alpha()
buy_turret_image = pg.image.load('assets/images/buttons/novaCompra.png').convert_alpha()
nova_compra_image = pg.image.load('assets/images/buttons/novaCompra.png').convert_alpha()
cancel_image = pg.image.load('assets/images/buttons/cancel.png').convert_alpha()
upgrade_turret_image = pg.image.load('assets/images/buttons/Botao_Upgrade.png').convert_alpha()
begin_image = pg.image.load('assets/images/buttons/Botao_fase.png').convert_alpha()
restart_image = pg.image.load('assets/images/buttons/restart.png').convert_alpha()
fast_forward_image = pg.image.load('assets/images/buttons/fast_forward.png').convert_alpha()
pause_image = pg.image.load('assets/images/buttons/pause_button.png').convert_alpha()
heart_image = pg.image.load("assets/images/gui/heart.png").convert_alpha()
coin_image = pg.image.load("assets/images/gui/coin.png").convert_alpha()
logo_image = pg.image.load("assets/images/gui/logo.png").convert_alpha()
ajuda_image = pg.image.load('assets/images/buttons/ajuda.png').convert_alpha()
back_image = pg.image.load('assets/images/buttons/back.png').convert_alpha()
intro_image = pg.image.load('assets/images/intro.jpeg').convert_alpha()
informacao_tela1 = pg.image.load('assets/images/intro1.png').convert_alpha()
informacao_tela2 = pg.image.load('assets/images/intro2.png').convert_alpha()
informacao_tela3 = pg.image.load('assets/images/intro3.png').convert_alpha()
informacao_tela4 = pg.image.load('assets/images/intro4.png').convert_alpha()

#sons
shot_fx = pg.mixer.Sound('assets/audio/shot.wav')
shot_fx.set_volume(0.5)


#carregando json de dados
with open('levels/novosNiveis/level.tmj') as file:
  world_data = json.load(file)

with open('levels/novosNiveis/level2.tmj') as file:
  world_data_2 = json.load(file)

with open('levels/novosNiveis/level3.tmj') as file:
  world_data_3 = json.load(file) 
  
  
   
#definindo fontes
text_font = pg.font.SysFont("Consolas", 24, bold = True)
large_font = pg.font.SysFont("Consolas", 36)


#escrever texto
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

def display_data():
  #desenha o painel lateral
  screen.blit(sidebar_background, (c.LARGURA_TELA, 0))
  draw_text("LEVEL: " + str(world.level), text_font, "grey100", c.LARGURA_TELA + 110, 50)
  screen.blit(heart_image, (c.LARGURA_TELA + 110, 70))
  draw_text("PV:" + str(world.health), text_font, "grey100", c.LARGURA_TELA + 140, 75)
  screen.blit(coin_image, (c.LARGURA_TELA + 220, 90))
  draw_text("MOEDAS:" + str(world.money), text_font, "grey100", c.LARGURA_TELA + 90, 95)
  

def create_turret(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TAMANHO_BLOCO
  mouse_tile_y = mouse_pos[1] // c.TAMANHO_BLOCO
  #calcula qual o bloco escolhido
  mouse_tile_num = (mouse_tile_y * c.COLUNAS) + mouse_tile_x
  #verifica se o bloco escolhido é caminho
  if world.tile_map[mouse_tile_num] == 7:
    #verifica se já há um arqueiro posicionado
    space_is_free = True
    for turret in turret_group:
      if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
        space_is_free = False
    #se é um espaço livre então é criado um arqueiro
    if space_is_free == True:
      new_turret = Turret(turret_spritesheets, mouse_tile_x, mouse_tile_y, shot_fx)
      turret_group.add(new_turret)
      #diminui 10 moedas
      world.money -= c.CUSTO

def select_turret(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TAMANHO_BLOCO
  mouse_tile_y = mouse_pos[1] // c.TAMANHO_BLOCO
  for turret in turret_group:
    if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
      return turret

def clear_selection():
  for turret in turret_group:
    turret.selected = False

#criando o mundo
world = World(world_data, map_image)
world.process_data()
world.process_enemies()
if world.waypoints_2:
  world.process_enemies()

#criando os grupos
enemy_group = pg.sprite.Group()
enemy_group_2 = pg.sprite.Group()
turret_group = pg.sprite.Group()

#criando os botoes
new_turrer_button = Button(c.LARGURA_TELA + 75, 300, nova_compra_image, True)
turret_button = Button(c.LARGURA_TELA + 90, 200, buy_turret_image, True)
cancel_button = Button(c.LARGURA_TELA + 90, 350, cancel_image, True)
upgrade_button = Button(c.LARGURA_TELA + 90, 400, upgrade_turret_image, True)
begin_button = Button(c.LARGURA_TELA + 30, 450, begin_image, True) 
restart_button = Button(c.LARGURA_TELA + 30, 550, restart_image, True)
fast_forward_button = Button(c.LARGURA_TELA + 30, 450, fast_forward_image, False)
pause_button = Button(c.LARGURA_TELA + 150, 450, pause_image, False)  # Botão de Pausar
ajuda_button = Button(c.LARGURA_TELA + 30, 500, ajuda_image, False)  # Botão de Ajuda
#back_button = Button(c.LARGURA_TELA + 150, 500, back_image, False)
back_button = Button(550, 625, back_image, False)

def informar2(lv):
    if lv == 1:
      screen.blit(informacao_tela1, (0, 0))
    if lv == 2:
      screen.blit(informacao_tela2, (0, 0))
    if lv == 3:
      screen.blit(informacao_tela3, (0, 0))
    if lv == 4:
      screen.blit(informacao_tela4, (0, 0))    
    iniciar_image = pg.image.load('assets/images/buttons/begin.png').convert_alpha()  # Botão de pausar
    iniciar_rect = iniciar_image.get_rect(center=(c.LARGURA_TELA // 2, c.ALTURA_TELA - 100))  # Ajustar a posição do botão
    # Checando se o botão de iniciar foi clicado
    screen.blit(iniciar_image, iniciar_rect)
    if iniciar_rect.collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]:
        return True  # Fechar a tela de informações e voltar para o jogo

    return False  # Caso contrário, continua mostrando a tela de informações





help_images = [
    pg.image.load('assets/images/ajuda1.png').convert_alpha(),
    pg.image.load('assets/images/ajuda2.png').convert_alpha(),
    pg.image.load('assets/images/ajuda3.png').convert_alpha(),
    pg.image.load('assets/images/ajuda4.png').convert_alpha()
]

# Carrega as imagens dos botões
button_images = [
    pg.image.load('assets/images/page1.png').convert_alpha(),
    pg.image.load('assets/images/page2.png').convert_alpha(),
    pg.image.load('assets/images/page3.png').convert_alpha(),
    pg.image.load('assets/images/page4.png').convert_alpha(),
    
]

# Cria os botões de navegação automaticamente
buttons = [
    pg.Rect(150 + i * 100, 625, button_images[i].get_width(), button_images[i].get_height())
    for i in range(4)
]

def show_help_screen():
    global help_screen_stage

    # Loop para manter a tela de ajuda ativa
    showing_help = True
    while showing_help:
        #screen.fill((0, 0, 0))  # Limpa a tela

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for i, button in enumerate(buttons):
                    if button.collidepoint(event.pos):
                        help_screen_stage = i + 1  # Atualiza para a página correta
                # Se clicar no botão de voltar, sai da tela de ajuda
                if back_button.draw(screen):  # Esse botão retorna ao jogo
                  return True  # Indica que deve voltar ao jogo

        # Exibe a tela de ajuda correspondente
        screen.blit(help_images[help_screen_stage - 1], (0, 0))

        # Desenha os botões
        for i, button in enumerate(buttons):
            screen.blit(button_images[i], (button.x, button.y))

        # Desenha o botão de voltar
        screen.blit(back_image, (back_button.rect.x, back_button.rect.y))

        pg.display.flip()  # Atualiza a tela

    return False  # Retorna para indicar que saiu da tela de ajuda

'''
def show_help_screen():
    global help_screen_stage
    pg1_image = pg.image.load('assets/images/page1.png').convert_alpha()
    pg2_image = pg.image.load('assets/images/page2.png').convert_alpha()
    pg3_image = pg.image.load('assets/images/page3.png').convert_alpha()
    pg4_image = pg.image.load('assets/images/page4.png').convert_alpha()
    
    # Criando os botões manualmente
    next_button = pg.Rect(150, 625, pg1_image.get_width(), pg1_image.get_height())
    next_button_2 = pg.Rect(250, 625, pg2_image.get_width(), pg2_image.get_height())
    next_button_3 = pg.Rect(350, 625, pg1_image.get_width(), pg1_image.get_height())
    next_button_4 = pg.Rect(450, 625, pg2_image.get_width(), pg2_image.get_height())

    # Capturar eventos de clique
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # Botão esquerdo do mouse
            if next_button.collidepoint(event.pos):
                help_screen_stage = 1  # Vai para a tela 1
            elif next_button_2.collidepoint(event.pos):
                help_screen_stage = 2  # Vai para a tela 2
            elif next_button_3.collidepoint(event.pos):
                help_screen_stage = 3  # Vai para a tela 3
            elif next_button_4.collidepoint(event.pos):
                help_screen_stage = 4  # Vai para a tela 4

    # Exibir a tela correspondente
    if help_screen_stage == 1:
       ajuda_1 = pg.image.load('assets/images/ajuda1.png').convert_alpha()
       screen.blit(ajuda_1, (0, 0))
    elif help_screen_stage == 2:
        # Exibir a imagem da segunda tela de ajuda
        ajuda_2 = pg.image.load('assets/images/ajuda2.png').convert_alpha()
        screen.blit(ajuda_2, (0, 0))
    elif help_screen_stage == 3:
        ajuda_3 = pg.image.load('assets/images/ajuda3.png').convert_alpha()
        screen.blit(ajuda_3, (0, 0))
    elif help_screen_stage == 4:     
        ajuda_4 = pg.image.load('assets/images/ajuda4.png').convert_alpha()
        screen.blit(ajuda_4, (0, 0))
    screen.blit(pg1_image, (next_button.x, next_button.y))
    screen.blit(pg2_image, (next_button_2.x, next_button_2.y))
    screen.blit(pg3_image, (next_button_3.x, next_button_3.y))
    screen.blit(pg4_image, (next_button_4.x, next_button_4.y))

    # Atualizar a tela
    if back_button.draw(screen):  # Esse botão retorna ao jogo
        return True  # Indica que deve voltar ao jogo
    return False  # Permanece na tela de ajuda
'''


run = True
intro_display_time = 3000  # Tempo para exibir a tela de introdução (em milissegundos)
intro_start_time = pg.time.get_ticks()  # Marca o tempo que a tela de introdução começou a ser exibida
in_help_screen = True  # Variável para controlar se estamos na tela de ajuda
in_informar1 = False
in_informar2 = False
in_informar3 = False
in_informar4 = False

while run:

  clock.tick(c.FPS)
  #########################
  # Tela de Introdução
  #########################
  if pg.time.get_ticks() - intro_start_time < intro_display_time:
    # Exibe a tela de introdução
    screen.blit(intro_image, (0, 0))
    pg.display.flip()
    continue  # Pula o resto do loop para não atualizar o jogo ainda
  display_data()
  #########################
  #     ATUALIZAÇAO       #
  #########################  
  if not game_paused and not in_help_screen:  # A tela de ajuda não pode ser atualizada enquanto o jogo está pausado
    if game_over == False:
        #checa se o jogador perdeu
        if world.health <= 0:
            game_over = True
            game_outcome = -1 #derrota
        #checa se o jogador ganhou
        if world.level > c.TOTAL_NIVEIS:
            game_over = True
            game_outcome = 1 #vitoria

    #atualizando grupos
    enemy_group.update(world)
    enemy_group_2.update(world)
    enemy_group_all = []
    enemy_group_all.extend(enemy_group)
    enemy_group_all.extend(enemy_group_2)
    turret_group.update(enemy_group_all, world)

    #selecionando torre
    if selected_turret:
        selected_turret.selected = True

  #########################
  #     DESENHANDO        #                     
  #########################

  #desenha o nivel
  world.draw(screen)

  #desenha os grupos
  enemy_group.draw(screen)
  enemy_group_2.draw(screen)
  for turret in turret_group:
    turret.draw(screen)
  
  
  if game_over == False:
    if in_help_screen:  # Quando na tela de ajuda
        if show_help_screen():  # Se o jogador clicar no botão de voltar
          in_help_screen = False  # Voltar para o jogo
               
    #checa se o nivel já começou ou não
    if level_started == False:
      
      if world.level == 1 and in_informar1 == False:
        if informar2(1):
            in_informar1 = True
            world.draw(screen)
      if world.level == 2 and in_informar2 == False:
        if informar2(2):
            in_informar2 = True
            world.draw(screen)
      if world.level == 3 and in_informar3 == False:
        if informar2(3):
            in_informar3 = True
            world.draw(screen)
      if world.level == 4 and in_informar4 == False:
        if informar2(4):
            in_informar4 = True
            world.draw(screen)
      if begin_button.draw(screen):
        level_started = True     
    else:
      world.game_speed = 1
      if fast_forward_button.draw(screen):
        world.game_speed = 2
        
      #gerar inimigos
      if pg.time.get_ticks() - last_enemy_spawn > c.ESPERA_SURGIMENTO:
        if world.waypoints_2:
          if world.spawned_enemies < len(world.enemy_list):
            enemy_type = world.enemy_list[world.spawned_enemies]
            enemy = Enemy(enemy_type, world.waypoints, enemy_images)
            enemy_group.add(enemy)
            world.spawned_enemies += 1
            last_enemy_spawn = pg.time.get_ticks()
            enemy_2 = Enemy(enemy_type, world.waypoints_2, enemy_images)
            enemy_group_2.add(enemy_2)
            world.spawned_enemies += 1
            last_enemy_spawn = pg.time.get_ticks()
        elif  (not world.waypoints_2):
          if world.spawned_enemies < len(world.enemy_list):
            enemy_type = world.enemy_list[world.spawned_enemies]
            enemy = Enemy(enemy_type, world.waypoints, enemy_images)
            enemy_group.add(enemy)
            enemy_group_2.add(enemy)
            world.spawned_enemies += 1
            last_enemy_spawn = pg.time.get_ticks()

  
    #checar se a wave acabou
    if world.check_level_complete() == True:
      world.money += c.RECOMPENSA_NIVEL
      world.level += 1
      level_started = False
      last_enemy_spawn = pg.time.get_ticks()
      if world.health <= 0:
        game_over = True
        game_outcome = -1
      if(world.level == 2):
        turret_group.empty()
        world = World(world_data_2, map_image2)
        world.level = 2
        world.process_data()
        world.money = 46
      if(world.level == 3):
        turret_group.empty()
        world = World(world_data_3, map_image3)
        world.level = 3
        world.process_data()
        world.process_enemies()
        world.money = 46
      if(world.level == 4):
        turret_group.empty()
        world = World(world_data_3, map_image3)
        world.level = 4
        world.process_data()
        world.process_enemies()
        world.money = 46
      if(world.level<5):
        world.process_enemies()
    screen.blit(coin_image, (c.LARGURA_TELA + 195, 330))
    draw_text("CUSTO:" + str(c.CUSTO), text_font, "grey100", c.LARGURA_TELA + 80, 335)

    if turret_button.draw(screen):
      placing_turrets = True
    #se estiver colocando arqueiros, mostra também o botão cancelar
    if placing_turrets == True:
      #mostra o cursor de arquerio 
      cursor_rect = cursor_turret.get_rect()
      cursor_pos = pg.mouse.get_pos()
      cursor_rect.center = cursor_pos
      if cursor_pos[0] <= c.LARGURA_TELA:
        screen.blit(cursor_turret, cursor_rect)
      if cancel_button.draw(screen):
        placing_turrets = False
    #se um arqueiro for selecionada, mostre o botão de upgrade
    if selected_turret:
      if selected_turret.upgrade_level < c.NIVEL_ARQUEIRO:
        #draw_text(str(c.CUSTO_UPGRADE), text_font, "grey100", c.LARGURA_TELA + 200, 250)
        #screen.blit(coin_image, (c.LARGURA_TELA + 240, 245))
        if upgrade_button.draw(screen):
          if world.money >= c.CUSTO_UPGRADE:
            selected_turret.upgrade()
            world.money -= c.CUSTO_UPGRADE
  else:
    pg.draw.rect(screen, "dodgerblue", (200, 200, 400, 200), border_radius = 30)
    if game_outcome == -1:
      draw_text("GAME OVER", large_font, "grey0", 310, 230)
    elif game_outcome == 1:
      draw_text("YOU WIN!", large_font, "grey0", 315, 230)
    #Reinicia o jogo
    if restart_button.draw(screen):
      game_over = False
      level_started = False
      placing_turrets = False
      selected_turret = None
      in_informar1 = False
      in_informar2 = False
      in_informar3 = False
      in_informar4 = False
      last_enemy_spawn = pg.time.get_ticks()
      world = World(world_data, map_image)
      world.process_data()
      world.process_enemies()
      enemy_group.empty()
      enemy_group_2.empty()
      turret_group.empty()
  
  # verifica se o jogo esta pausado
  if pause_button.draw(screen):
    if not pause_button_clicked: 
        game_paused = not game_paused 
        pause_button_clicked = True 

  if not pause_button.draw(screen):  #Sai do modo pausa
    pause_button_clicked = False

  if game_paused:  #Mostra a mensagem "PAUSADO" na tela
    draw_text("PAUSADO", pg.font.SysFont("Impact", 36), "red", c.LARGURA_TELA // 2 - 100, c.ALTURA_TELA // 2)
  
  # Adicionar lógica do botão "Ajuda"
  if ajuda_button.draw(screen):
    in_help_screen = True  # Quando o botão "Ajuda" for clicado, entra na tela de ajuda

  if in_help_screen:  # Quando na tela de ajuda
    if show_help_screen():  # Se o jogador clicar no botão de voltar
      in_help_screen = False  # Voltar para o jogo
 
  # Lógica de mouse e eventos
  for event in pg.event.get():
    if event.type == pg.QUIT:
      run = False
    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
      mouse_pos = pg.mouse.get_pos()
      if mouse_pos[0] < c.LARGURA_TELA and mouse_pos[1] < c.ALTURA_TELA:
        selected_turret = None
        clear_selection()
        if placing_turrets == True:
          if world.money >= c.CUSTO:
            create_turret(mouse_pos)
        else:
          selected_turret = select_turret(mouse_pos)
  pg.display.flip()

pg.quit()