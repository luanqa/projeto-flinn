import pygame as pg
import math
import config as c
from arqueiro_data import TURRET_DATA

class Turret(pg.sprite.Sprite):
  def __init__(self, sprite_sheets, tile_x, tile_y, shot_fx):
    pg.sprite.Sprite.__init__(self)
    self.upgrade_level = 1
    self.range = TURRET_DATA[self.upgrade_level - 1].get("range")
    self.cooldown = TURRET_DATA[self.upgrade_level - 1].get("cooldown")
    self.last_shot = pg.time.get_ticks()
    self.selected = False
    self.target = None

    #position variables
    self.tile_x = tile_x
    self.tile_y = tile_y
    #calculate center coordinates
    self.x = (self.tile_x + 0.5) * c.TAMANHO_BLOCO
    self.y = (self.tile_y + 0.5) * c.TAMANHO_BLOCO
    #shot sound effect
    self.shot_fx = shot_fx

    #animation variables
    self.sprite_sheets = sprite_sheets
    self.animation_list = self.load_images(self.sprite_sheets[self.upgrade_level - 1])
    self.frame_index = 0
    self.update_time = pg.time.get_ticks()

    #update image
    self.angle = 90
    self.original_image = self.animation_list[self.frame_index]
    self.image = pg.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect()
    self.rect.center = (self.x, self.y)

    #create transparent circle showing range
    self.range_image = pg.Surface((self.range * 2, self.range * 2))
    self.range_image.fill((0, 0, 0))
    self.range_image.set_colorkey((0, 0, 0))
    pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
    self.range_image.set_alpha(100)
    self.range_rect = self.range_image.get_rect()
    self.range_rect.center = self.rect.center

  def load_images(self, sprite_sheet):
    #extract images from spritesheet
    size = sprite_sheet.get_height()
    animation_list = []
    for x in range(c.ANIMATION_STEPS):
      temp_img = sprite_sheet.subsurface(x * size, 0, size, size)
      animation_list.append(temp_img)
    return animation_list

  def update(self, enemy_group, world):
    #if target picked, play firing animation
    if self.target:
      self.play_animation()
    else:
      #search for new target once turret has cooled down
      if pg.time.get_ticks() - self.last_shot > (self.cooldown / world.game_speed):
        if(world.level == 4):
          self.pick_target_level4(enemy_group)
        else:
          self.pick_target(enemy_group)
 
  def pick_target(self, enemy_group):
      # Mapear tipos de inimigos para cada nível de torre
      type = {
          1: "weak",    # Nível 1 só ataca inimigos "weak"
          2: "medium",  # Nível 2 só ataca inimigos "medium"
          3: "strong",  # Nível 3 só ataca inimigos "strong"
          4: "elite"    # Nível 4 também ataca apenas inimigos "elite"
      }

      # Verifica o tipo de inimigo que pode ser atacado pelo nível atual
      valid_enemy_type = type.get(self.upgrade_level, "strong")  # Padrão é "strong" para nível 4

      x_dist = 0
      y_dist = 0

      # Iterar sobre os inimigos para achar um alvo válido
      for enemy in enemy_group:
          # Verifica se o inimigo é do tipo "god", qualquer torre pode atacar ele
          if enemy.type == "god":
              x_dist = enemy.pos[0] - self.x
              y_dist = enemy.pos[1] - self.y
              dist = math.sqrt(x_dist ** 2 + y_dist ** 2)

              # Se o inimigo estiver dentro do alcance, é escolhido como alvo
              if dist < self.range:
                  self.target = enemy
                  self.angle = math.degrees(math.atan2(-y_dist, x_dist))
                  # Dano ao inimigo
                  self.target.health -= c.DANO
                  # Reproduzir o efeito sonoro
                  self.shot_fx.play()
                  break

          # Se o inimigo não for "god", verifica se a torre pode atacar o inimigo de acordo com seu tipo
          elif enemy.health > 0 and enemy.type == valid_enemy_type:
              x_dist = enemy.pos[0] - self.x
              y_dist = enemy.pos[1] - self.y
              dist = math.sqrt(x_dist ** 2 + y_dist ** 2)

              # Se o inimigo estiver dentro do alcance, é escolhido como alvo
              if dist < self.range:
                  self.target = enemy
                  self.angle = math.degrees(math.atan2(-y_dist, x_dist))
                  # Dano ao inimigo
                  self.target.health -= c.DANO
                  # Reproduzir o efeito sonoro
                  self.shot_fx.play()
                  break
  def pick_target_level4(self, enemy_group):
    #find an enemy to target
    x_dist = 0
    y_dist = 0
    #check distance to each enemy to see if it is in range
    for enemy in enemy_group:
      if enemy.health > 0:
        x_dist = enemy.pos[0] - self.x
        y_dist = enemy.pos[1] - self.y
        dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
        if dist < self.range:
          self.target = enemy
          self.angle = math.degrees(math.atan2(-y_dist, x_dist))
          #damage enemy
          self.target.health -= c.DANO
          #play sound effect
          self.shot_fx.play()
          break
  
  def play_animation(self):
    #update image
    self.original_image = self.animation_list[self.frame_index]
    #check if enough time has passed since the last update
    if pg.time.get_ticks() - self.update_time > c.ANIMATION_DELAY:
      self.update_time = pg.time.get_ticks()
      self.frame_index += 1
      #check if the animation has finished and reset to idle
      if self.frame_index >= len(self.animation_list):
        self.frame_index = 0
        #record completed time and clear target so cooldown can begin
        self.last_shot = pg.time.get_ticks()
        self.target = None

  def upgrade(self):
    self.upgrade_level += 1
    self.range = TURRET_DATA[self.upgrade_level - 1].get("range")
    self.cooldown = TURRET_DATA[self.upgrade_level - 1].get("cooldown")
    #upgrade turret image
    self.animation_list = self.load_images(self.sprite_sheets[self.upgrade_level - 1])
    self.original_image = self.animation_list[self.frame_index]

    #upgrade range circle
    self.range_image = pg.Surface((self.range * 2, self.range * 2))
    self.range_image.fill((0, 0, 0))
    self.range_image.set_colorkey((0, 0, 0))
    pg.draw.circle(self.range_image, "grey100", (self.range, self.range), self.range)
    self.range_image.set_alpha(100)
    self.range_rect = self.range_image.get_rect()
    self.range_rect.center = self.rect.center

  def draw(self, surface):
    self.image = pg.transform.rotate(self.original_image, self.angle - 90)
    self.rect = self.image.get_rect()
    self.rect.center = (self.x, self.y)
    surface.blit(self.image, self.rect)
    if self.selected:
      surface.blit(self.range_image, self.range_rect)