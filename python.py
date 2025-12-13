from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

ground = Entity(
    model='plane',
    collider='box',
    scale=(20, 1, 20),
    texture='white_cube',
    texture_scale=(20, 20)
)

player = FirstPersonController()

cube = Entity(
    model='cube',
    color=color.azure,
    position=(0,1,3),
    collider='box'
)

def update():
    # game logic every frame
    if player.intersects(cube).hit:
        print("Touched the cube!")

app.run()
