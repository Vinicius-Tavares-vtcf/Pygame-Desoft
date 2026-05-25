# Pygame-Desoft
# Jogo Pygame Disciplina de Design de Software
# ## Como rodar
# 1. Instala as dependências:
# pip install -r requirements.txt
# 2. Roda o jogo:
# python jogo.py


Projeto: O Coliseu

O Coliseu é um jogo de sobrevivência em arena feito com Pygame. O jogador enfrenta ondas de inimigos cada vez mais fortes, coleta moedas, compra e evolui armas como espada, arco e cajado, e tenta sobreviver até enfrentar o Minotauro. Após derrotar o chefe, o jogo entra em uma fase final mais intensa, com inimigos espaciais, waves crescentes e maior dificuldade. As pontuações são salvas em um ranking com as melhores partidas.


Nome dos Integrantes:
Vinícius Tavares Cunha Fernandes
Judáh Eliezer Levy
Rafael Novak Alberto
Luis Fernando Luz

Link do Vídeo Apresentando o Jogo: [text](https://youtu.be/y1V23r4ElmA)
Como rodar o jogo
1. Instalar as bibliotecas necessárias

Antes de executar o jogo, é necessário instalar as dependências do projeto.

No terminal, execute:

pip install -r requirements.txt

Ou instalar manualmente:

pip install pygame opencv-python

Bibliotecas utilizadas
pygame → engine principal do jogo
opencv-python (cv2) → reprodução dos vídeos de transição

2. Executar o jogo

Depois das dependências instaladas, basta rodar o arquivo principal:

python jogo.py
Estrutura importante

O projeto utiliza:

jogo.py → arquivo principal
game_screen.py → gameplay
sprites.py → classes do jogador, inimigos e projéteis
assets_loader.py → carregamento das imagens, sons e vídeos
pasta assets/ → imagens, músicas, sons e vídeos

Controles do jogo

WASD -- Movimentação
Mouse esquerdo -- Atacar / atirar
Mouse Direito -- Atirar flecha, quando equipada
E -- Interagir / abrir loja
Enter -- Sair da partida
1 / 2 / 3 -- Equipar armas
Shift + 1/2/3 -- Melhorar armas


Utilizamos IA como ferramenta de apoio para debugging, implementação de algumas mecânicas específicas (como flechas, pontuação e ajustes de HUD) e auxílio em Git/merge. A estrutura principal, organização do projeto e desenvolvimento geral do jogo foram feitos pela equipe.

A maior parte do código foi feito pelos integrantes da equipe, mas a Inteligência Artificial foi utilizada para aprimorar a lógica do código e execução das funcionalidades.
A seguir, é mostrada as partes principais do jogo que utilizamos IA para aprimorar.

1. Sistema de ataque à distância (Arco/Flechas)(80% de IA)

Criação de projéteis (flechas)
Movimento da flecha em direção ao mouse
Rotação correta da imagem da flecha
Colisão com inimigos
Remoção da flecha ao sair da arena
Separação entre ataque e ataque à distância
Correção do problema em que flechas não apareciam
Correção do dano contra magos
Ajustes de renderização/desenho das flechas

2. Sistema de pontuação (20% feito de IA)

Variável player.score
Pontuação acumulativa independente das moedas
Exibição de pontos na HUD
Correção de sobreposição visual do HUD

3. Correções de HUD/interface (20% feito de IA)

Vida
Moedas
Pontos
Arma equipada
Correção de textos sobrepostos

4. Direção do ataque pelo mouse (15% feito por IA)

Direções diagonais
Correção de orientação de ataques
Compatibilidade com flechas e ataques 

5. Correção da orientação das magias do mago

Criação das Classes: (60% feito com ajuda de IA)
Inimigo
Minotauro
MageSpell
Mago
MagoEvo
MagoSpace
O que foi discutido/ajustado:
Problema da animação da bola de fogo sempre horizontal
Rotação da magia conforme direção do movimento

6. Sistema de áudio (40% feita de IA)

Função _play_sound()
Reprodução simultânea de sons
Sons especiais para chefes


8. Sistema de loja e upgrades (80% feito de IA)

Evolução:
fogo
espacial
Atalhos de teclado da loja
Aplicação de upgrades nas armas

9. Balanceamento e progressão de fases (30% feito de IA)

Tempo até evolução das arenas
Tempo até boss
Spawn por fases
Sistema de waves
Congelamento de waves
Progressão temporal

Aqui tem um link do histórico do Chat GPT com algumas funcionalidades que foram implementadas com a ajuda dele: https://chatgpt.com/share/e/6a145e4e-97d0-8008-a36a-28d55ce57281

Sprites:
As imagens do cajado, arco, espada, mago, esqueleto, lobisomem foram retiradas do site https://itch.io/game-assets/free

AS imagens do Minotauro e feitiços do Mago foram retiradas do site https://opengameart.org/

As imagens da arena(coliseu), imagens dos personagens e aramas evoluídas, totem de cura, Leão e sprite do jogador(romano) foram feitas com a IA Nano Banana Pro. Utilizamos essa IA para deixar as imagens retiradas dos repositórios pixelizadas


