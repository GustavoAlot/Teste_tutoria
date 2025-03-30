import math
from pygame import Rect

# Configuracoes da Tela
WIDTH = 800              # Largura da janela
HEIGHT = 512             # Altura da janela
TILE_SIZE = 32           # Tamanho de cada tile no mapa

# Variaveis Globais
game_state = "menu"      # Estado atual do jogo: "menu" ou "playing"
sound_on = True          # Flag para controle de som (ligado/desligado)
show_intro = True        # Flag para exibir o popup de instrucoes iniciais
show_win_popup = False   # Flag para exibir o popup de vitoria

# Define o volume da música de fundo (0.0 a 1.0)
music.set_volume(0.2)

# Define o volume dos efeitos sonoros individuais
sounds.jump.set_volume(0.2)
sounds.death.set_volume(0.2)

# Botoes do Menu (Actors)
start_button = Actor("painel_retangulo", center=(400, 170))
toggle_button = Actor("painel_retangulo", center=(400, 270))
exit_button = Actor("painel_retangulo", center=(400, 370))

# Mapa do Nivel: cada string e uma linha; cada caractere representa um tile
level_map = [
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "A......................................................................................................................................................................A",
    "A............................................C.........................................................................................................................A",
    "A......................................................................................................................................................................A",
    "A............................................C.........................................................................................................................A",
    "A......................................W........................................................................................................................H......A",
    "A............................................C.........................................................................................................................A",
    "A.................................................................................................................................B....................................A",
    "A.................................W..........C...............................X....................................................B......................G.G.G.G.G.G.G.A",
    "A.............WWWW.................................W..W...W..W...W.........X......................................................B...B................G...............A",
    "A............................G.G.............C.....W..W...W..W...W...........X..................W.......W.............................B..............G.T.T.T.T.T.T.T.T.A",
    "A..................................................WWWW...WWWW...WWWW.......................W.........................................B................................A",
    "A.......WW...SSS........G.G..SSSSSSSSSSS...................................E.X.................SSSSSSSSSSSSSSS.......B......................B......G.T.T.T.T.T.T.T.T.T.A",
    "A....................................................................................................................B......................B..........................A",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
]

# Calcula a largura total do nivel (em pixels)
level_width = len(level_map[0]) * TILE_SIZE

# Lista de caracteres que representam tiles solidos (para colisao)
solid_tiles = ["T", "G", "A", "C", "X", "H", "W"]
enemy_tiles = ["E"]    # Caractere que indica inimigo (tanque)
enemies = []           # Lista para armazenar os inimigos

# ----------------------------------------
# Classe EnemyBee (inimigo: abelha)
# ----------------------------------------
class EnemyBee:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.direction = 1      # 1 = direita, -1 = esquerda
        self.speed = 40         # Velocidade (pixels por segundo)
        self.max_distance = 100 # Distancia maxima para mudar de direcao
        self.start_x = x        # Posicao inicial (para medir a distancia)
        self.timer = 0          # Timer para animacao do sprite
        self.frame = 0          # Frame atual da animacao

        self.actor = Actor("abelha_indo1", (x, y))  # Actor para desenhar a abelha

    def update(self, dt):
        # Atualiza a posicao horizontal
        self.x += self.direction * self.speed * dt
        # Inverte a direcao se a distancia maxima for atingida
        if abs(self.x - self.start_x) > self.max_distance:
            self.direction *= -1

        # Atualiza o timer para a animacao
        self.timer += dt
        if self.timer > 0.2:
            self.timer = 0
            self.frame = (self.frame + 1) % 2  # Alterna entre 2 frames

        # Atualiza a imagem do actor com base no frame atual
        self.actor.image = f"abelha_indo{self.frame + 1}"
        self.actor.x = self.x

    def draw(self, camera_x):
        # Ajusta a posicao do actor em relacao a camera e desenha
        self.actor.pos = (self.x - camera_x, self.y)
        self.actor.draw()

    def get_rect(self):
        # Retorna a hitbox da abelha (ajustada)
        return Rect(self.x - 16, self.y - 16, 36, 32)

# ----------------------------------------
# Classe Bullet (bala)
# ----------------------------------------
class Bullet:
    def __init__(self, x, y, angle):
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.actor = Actor("bala", (x, y))  # Actor para desenhar a bala
        self.angle = angle      # Angulo de movimento (graus)
        self.speed = 200        # Velocidade (pixels por segundo)
        self.life_timer = 0     # Timer para controlar o tempo de vida

    def update(self, dt):
        # Incrementa o timer de vida usando dt
        self.life_timer += dt

        # Se a bala existir por mais de 5 segundos, nao atualiza
        if self.life_timer > 5:
            return

        # Calcula o deslocamento com base no angulo (convertido para radianos)
        rad = math.radians(self.angle)
        dx = math.cos(rad) * self.speed * dt
        dy = math.sin(rad) * self.speed * dt
        self.pos_x += dx
        self.pos_y += dy
        self.actor.pos = (self.pos_x, self.pos_y)

    def draw(self, camera_x):
        # Ajusta o angulo e a posicao do actor em relacao a camera e desenha
        self.actor.angle = self.angle
        self.actor.pos = (self.pos_x - camera_x, self.pos_y)
        self.actor.draw()

    def get_rect(self):
        # Retorna a hitbox da bala
        return Rect(self.pos_x - 4, self.pos_y - 4, 8, 8)

    def is_expired(self):
        # A bala e expirada se existir por mais de 5 segundos
        return self.life_timer > 5

# ----------------------------------------
# Classe EnemyTank (inimigo: tanque)
# ----------------------------------------
class EnemyTank:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.can_shoot = True   # Flag para controlar o disparo

        self.angle = 0          # Angulo atual do canhao
        self.angle_speed = 0.5  # Velocidade de variacao do angulo
        self.max_angle = 90     # Angulo maximo permitido
        self.min_angle = -90    # Angulo minimo permitido
        self.moving_up = True   # Indica se o canhao esta se movendo para cima

        # Actors para o corpo e o canhao do tanque
        self.body = Actor("corpo_tank", (x, y))
        self.cannon = Actor("cano_tank", (x, y - 8))
        self.bullets = []       # Lista de balas disparadas

        self.waiting_after_shot = False  # Flag para pausa apos disparar
        self.pause_timer = 0             # Timer da pausa apos disparo

    def shoot(self):
        # Calcula a posicao inicial da bala com base no angulo do canhao
        rad = math.radians(180 + self.angle)
        bullet_x = self.x + math.cos(rad) * 20
        bullet_y = self.y - 8 + math.sin(rad) * 20
        self.bullets.append(Bullet(bullet_x, bullet_y, 180 + self.angle))

    def update(self, dt):
        # Se estiver em pausa apos disparar, decrementa o timer
        if self.waiting_after_shot:
            self.pause_timer -= dt
            if self.pause_timer <= 0:
                self.waiting_after_shot = False
            else:
                self.cannon.angle = 180 + self.angle
                return

        # Oscila o angulo do canhao entre min_angle e max_angle
        if self.moving_up:
            self.angle -= self.angle_speed
            if self.angle <= self.min_angle:
                self.moving_up = False
        else:
            self.angle += self.angle_speed
            if self.angle >= self.max_angle:
                self.moving_up = True

        # Atualiza o angulo do canhao (apontando para a esquerda)
        self.cannon.angle = 180 + self.angle

        # Dispara uma bala quando o canhao estiver alinhado (angulo = 0)
        if int(self.angle) == 0 and self.can_shoot:
            self.shoot()
            self.waiting_after_shot = True
            self.pause_timer = 1.0  # Pausa de 1 segundo apos disparo
            self.can_shoot = False

        # Permite disparo se o angulo nao for 0 e nao estiver em pausa
        if int(self.angle) != 0 and not self.waiting_after_shot:
            self.can_shoot = True

        # Atualiza as balas e remove as que estiverem expiradas
        for bullet in self.bullets:
            bullet.update(dt)
        self.bullets = [b for b in self.bullets if not b.is_expired()]

    def draw(self, camera_x):
        # Calcula a posicao do tanque relativa a camera
        offset_x = self.x - camera_x
        self.body.pos = (offset_x, self.y)
        self.cannon.pos = (offset_x, self.y - 8)
        self.body.draw()
        self.cannon.draw()
        # Desenha as balas disparadas
        for bullet in self.bullets:
            bullet.draw(camera_x)

# ----------------------------------------
# Carrega os inimigos do mapa
# ----------------------------------------
for row_idx, row in enumerate(level_map):
    for col_idx, char in enumerate(row):
        x = col_idx * TILE_SIZE
        y = row_idx * TILE_SIZE

        if char == "E":
            # Cria um tanque inimigo se o caractere for 'E'
            enemies.append(EnemyTank(x + TILE_SIZE // 2, y + TILE_SIZE))
        elif char == "B":
            # Cria uma abelha inimiga se o caractere for 'B'
            enemies.append(EnemyBee(x + TILE_SIZE // 2, y + TILE_SIZE // 2))

# ----------------------------------------
# Funcoes auxiliares para colisao no mapa
# ----------------------------------------
def is_solid(col, row):
    # """
    # Verifica se o tile na posicao (col, row) e solido.
    # """
    if 0 <= row < len(level_map) and 0 <= col < len(level_map[0]):
        return level_map[row][col] in solid_tiles
    return False

def get_tile_rect(col, row):
    # """
    # Retorna o retangulo (hitbox) correspondente a um tile.
    # """
    return Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE * 4, TILE_SIZE)

# ----------------------------------------
# Classe Hero (personagem do jogador)
# ----------------------------------------
class Hero:
    def __init__(self):
        self.x = 100           # Posicao inicial x
        self.y = 200           # Posicao inicial y
        self.vx = 0            # Velocidade horizontal
        self.vy = 0            # Velocidade vertical
        self.speed = 4         # Velocidade de movimento
        self.jump_power = -12  # Potencia do pulo (valor negativo para subir)
        self.gravity = 0.5     # Aceleracao da gravidade
        self.actor = Actor("platformchar_idle", (self.x, self.y))
        # Frames para animacao de diferentes estados
        self.idle_frames = ["platformchar_idle", "platformchar_happy"]
        self.run_frames = ["platformchar_walk1", "platformchar_walk2"]
        self.jump_frames = ["platformchar_jump"]
        self.state = "idle"    # Estado atual: idle, running ou jumping
        self.current_frame_index = 0  # Frame atual da animacao
        self.frame_timer = 0   # Timer para controle da animacao
        self.frame_delay = 0.15  # Delay entre frames

    def get_rect(self):
        # """
        # Retorna a hitbox do hero.
        # """
        return Rect(self.x - 20, self.y - 16, 48, 64)

    def check_bullet_collision(self, bullets):
        # """
        # Verifica colisao entre o hero e as balas.
        # """
        hero_rect = self.get_rect()
        for bullet in bullets:
            if hero_rect.colliderect(bullet.get_rect()):
                self.respawn()
                break

    def update(self, dt):
        keys = keyboard
        # Verifica se o hero alcancou o objetivo do nivel
        if self.check_goal():
            print("Nivel completo!")
            music.stop()

        self.vx = 0
        # Move para a esquerda se a tecla esquerda estiver pressionada
        if keys.left:
            self.vx = -self.speed
        # Move para a direita se a tecla direita estiver pressionada
        if keys.right:
            self.vx = self.speed
        # Pula se a tecla de espaco estiver pressionada e o hero estiver no chao
        if keys.space and self.on_ground():
            self.y -= 1
            colidiu = self.check_collision()
            self.y += 1
            if not colidiu:
                self.vy = self.jump_power
                if sound_on:
                    sounds.jump.play()

        # Aplica a gravidade
        self.vy += self.gravity

        # Movimento horizontal: atualiza a posicao incrementalmente para detectar colisao
        move_x = int(self.vx)
        sign_x = int(math.copysign(1, move_x)) if move_x != 0 else 0
        for _ in range(abs(move_x)):
            self.x += sign_x
            if self.check_collision():
                self.x -= sign_x
                break

        # Movimento vertical: atualiza a posicao incrementalmente para detectar colisao
        move_y = int(self.vy)
        sign_y = int(math.copysign(1, move_y)) if move_y != 0 else 0
        for _ in range(abs(move_y)):
            self.y += sign_y
            if self.check_collision():
                self.y -= sign_y
                self.vy = 0
                break

        # Verifica colisao com inimigos (abelhas)
        for enemy in enemies:
            if isinstance(enemy, EnemyBee):
                if self.get_rect().colliderect(enemy.get_rect()):
                    self.respawn()

        # Atualiza o estado do hero: "jumping" se nao estiver no chao, "running" se estiver se movendo, senao "idle"
        new_state = "jumping" if not self.on_ground() else ("running" if self.vx != 0 else "idle")
        if new_state != self.state:
            self.state = new_state
            self.current_frame_index = 0
            self.frame_timer = 0

        # Atualiza a animacao do hero com base no estado atual
        frame_list = self.idle_frames if self.state == "idle" else self.run_frames if self.state == "running" else self.jump_frames
        self.frame_timer += dt
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.current_frame_index = (self.current_frame_index + 1) % len(frame_list)
        self.actor.image = frame_list[self.current_frame_index]

        # Verifica colisao com tiles de espinhos (se houver)
        if self.check_spike_collision():
            self.respawn()

    def check_collision(self):
        # """
        # Verifica se o hero colide com tiles solidos.
        # """
        hero_rect = self.get_rect()
        left = (hero_rect.left) // TILE_SIZE - 1
        right = (hero_rect.right) // TILE_SIZE + 1
        top = (hero_rect.top) // TILE_SIZE - 1
        bottom = (hero_rect.bottom) // TILE_SIZE + 1
        for row in range(top, bottom + 1):
            for col in range(left, right + 1):
                if is_solid(col, row):
                    if hero_rect.colliderect(get_tile_rect(col, row)):
                        return True
        return False

    def check_spike_collision(self):
        # """
        # Verifica se o hero colide com tiles de espinhos.
        # """
        hero_rect = self.get_rect()
        left = (hero_rect.left) // TILE_SIZE - 1
        right = (hero_rect.right) // TILE_SIZE + 1
        top = (hero_rect.top) // TILE_SIZE - 1
        bottom = (hero_rect.bottom) // TILE_SIZE + 1
        for row in range(top, bottom + 1):
            for col in range(left, right + 1):
                if 0 <= row < len(level_map) and 0 <= col < len(level_map[0]):
                    if level_map[row][col] == "S":
                        if hero_rect.colliderect(get_tile_rect(col, row)):
                            return True
        return False

    def respawn(self):
        # """
        # Reinicia o hero para a posicao inicial.
        # """
        self.x = 100
        self.y = 200
        self.vx = 0
        self.vy = 0
        if sound_on:
            sounds.death.play()
        print("Hero reiniciado no inicio.")

    def check_goal(self):
        # """
        # Verifica se o hero alcancou o objetivo do nivel.
        # Ex: colidindo com um tile especifico (coluna 161).
        # """
        hero_rect = self.get_rect()
        left = hero_rect.left // TILE_SIZE - 1
        right = hero_rect.right // TILE_SIZE + 1
        top = hero_rect.top // TILE_SIZE - 1
        bottom = hero_rect.bottom // TILE_SIZE + 1
        for row in range(top, bottom + 1):
            for col in range(left, right + 1):
                if 0 <= row < len(level_map) and 0 <= col < len(level_map[0]):
                    if col == 161:
                        if self.get_rect().colliderect(get_tile_rect(col, row)):
                            global show_win_popup
                            show_win_popup = True
                            return True
        return False

    def on_ground(self):
        # """
        # Verifica se o hero esta no chao.
        # Isto e feito movendo o hero 1 pixel para baixo e verificando colisao.
        # """
        self.y += 1
        collision = self.check_collision()
        self.y -= 1
        return collision

    def draw(self, camera_x):
        # """
        # Desenha o hero na tela, ajustando a posicao em relacao a camera.
        # Tambem desenha um retangulo vermelho representando a hitbox (para debug).
        # """
        self.actor.pos = (self.x - camera_x, self.y)
        self.actor.draw()
        #screen.draw.rect(self.get_rect().move(-camera_x, 0), (255, 0, 0))

# Cria a instancia do hero
hero = Hero()

# ----------------------------------------
# Funcao principal de desenho
# ----------------------------------------
def draw():
    if game_state == "menu":
        draw_menu()  # Desenha o menu principal
    elif game_state == "playing":
        screen.fill((135, 206, 235))  # Preenche o fundo com azul (como o ceu)
        # Calcula a posicao da camera com base no hero
        camera_x = hero.x - (WIDTH // 2)
        camera_x = clamp(camera_x, 0, level_width - WIDTH)
        draw_level(camera_x)  # Desenha os tiles do nivel
        hero.draw(camera_x)   # Desenha o hero
        # Desenha todos os inimigos
        for enemy in enemies:
            enemy.draw(camera_x)

        # Exibe o popup de instrucoes
        if show_intro:
            screen.draw.filled_rect(Rect(150, 100, 500, 300), (0, 0, 0))
            screen.draw.text("Controles:\n\nSetas = mover\nEspaco = pular\n\nObjetivo: Alcancar o bloco de madeira\nao topo do morro de terra!\n\n[Pressione qualquer tecla]",
                               center=(400, 250), color="white", fontsize=28)

        # Exibe o popup de vitoria
        if show_win_popup:
            screen.draw.filled_rect(Rect(150, 100, 500, 300), (0, 0, 0))
            screen.draw.text("Parabens!\nVoce alcancou o fim.\n\n[Pressione Enter para voltar ao menu]",
                               center=(400, 250), color="white", fontsize=28)

# ----------------------------------------
# Funcao para tratar cliques do mouse
# ----------------------------------------
def on_mouse_down(pos):
    global game_state, sound_on
    if game_state == "menu":
        if start_button.collidepoint(pos):
            reset_level()  # Reinicia a fase antes de começar a jogar
            game_state = "playing"
            if sound_on:
                music.play("bgm")
        elif toggle_button.collidepoint(pos):
            sound_on = not sound_on
            if sound_on:
                music.play("bgm")
            else:
                music.stop()
        elif exit_button.collidepoint(pos):
            exit()



def reset_level():
    global hero, enemies, show_win_popup, show_intro
    # Reinicializa o herói
    hero = Hero()
    
    # Reinicializa a lista de inimigos
    enemies = []
    for row_idx, row in enumerate(level_map):
        for col_idx, char in enumerate(row):
            x = col_idx * TILE_SIZE
            y = row_idx * TILE_SIZE
            if char == "E":
                enemies.append(EnemyTank(x + TILE_SIZE // 2, y + TILE_SIZE))
            elif char == "B":
                enemies.append(EnemyBee(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
    
    # Reseta os popups
    show_win_popup = False
    show_intro = True



# ----------------------------------------
# Funcao para reiniciar a musica de fundo
# ----------------------------------------
def on_music_end():
    if game_state == "playing" and sound_on:
        music.play("bgm")

# ----------------------------------------
# Funcao utilitaria para limitar valores
# ----------------------------------------
def clamp(value, min_value, max_value):
    # """
    # Retorna o valor limitado entre min_value e max_value.
    # """
    return max(min_value, min(max_value, value))

# ----------------------------------------
# Funcao para tratar pressionamento de teclas
# ----------------------------------------
def on_key_down(key):
    global show_intro, show_win_popup, game_state
    if show_intro:
        show_intro = False  # Fecha o popup de instrucoes
    elif show_win_popup and key == keys.RETURN:
        show_win_popup = False
        game_state = "menu"

# ----------------------------------------
# Mapeamento de caractere de tile para nome da imagem
# ----------------------------------------
def tile_char_to_image(char):
    # """
    # Retorna o nome da imagem correspondente ao caractere do mapa.
    # """
    return {
        "T": "bloco_terra",
        "G": "bloco_grama",
        "M": "bloco_marrom",
        "A": "bloco_amarelo",
        "C": "bloco_cinza",
        "X": "tijolo_cinza",
        "H": "bloco_tabuas",
        "W": "plataforma_madeira",
        "S": "espinhos_para_cima"
    }.get(char, None)

# ----------------------------------------
# Funcao para desenhar os tiles do nivel
# ----------------------------------------
def draw_level(camera_x):
    # """
    # Percorre o level_map e desenha cada tile, ajustando a posicao pela camera.
    # Tambem desenha o retangulo de hitbox de cada tile (para debug).
    # """
    for row_idx, row in enumerate(level_map):
        for col_idx, tile_char in enumerate(row):
            img = tile_char_to_image(tile_char)
            if img:
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                screen_x = x - camera_x
                screen.blit(img, (screen_x, y))
                # Desenha a hitbox do tile (para debug)
                rect = get_tile_rect(col_idx, row_idx)
                # screen.draw.rect(rect.move(-camera_x, 0), (255, 0, 0))

# ----------------------------------------
# Funcao para desenhar o menu principal
# ----------------------------------------
def draw_menu():
    # """
    # Desenha o menu principal com botoes e textos.
    # """
    screen.fill((30, 30, 30))  # Fundo escuro para o menu
    start_button.draw()
    toggle_button.draw()
    exit_button.draw()
    screen.draw.text("Start Game", center=start_button.center, color="white", fontsize=30)
    sound_text = "Sound ON" if sound_on else "Sound OFF"
    screen.draw.text(sound_text, center=toggle_button.center, color="white", fontsize=30)
    screen.draw.text("Exit", center=exit_button.center, color="white", fontsize=30)

# ----------------------------------------
# Funcao principal de atualizacao do jogo
# ----------------------------------------
def update(dt):
    if game_state == "playing":
        hero.update(dt)
        # Atualiza os inimigos (especialmente os tanques, que podem disparar balas)
        for enemy in enemies:
            enemy.update(dt)
            # Verifica se o hero colide com as balas dos tanques
            if isinstance(enemy, EnemyTank):
                hero.check_bullet_collision(enemy.bullets)
