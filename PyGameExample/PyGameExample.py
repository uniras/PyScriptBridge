import reflex as rx
import pysbridge as pys


class PyGameComponent(pys.PyGame):
    # Override the script method to define the PyGame code.
    async def script(self):
        import pygame  # type: ignore
        import asyncio

        pygame.init()

        screen = pygame.display.set_mode((500, 500))
        fps = 60
        counter = 0
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((0, 0, 0))
            pygame.draw.circle(screen, (255, 0, 0), (100 + counter, 250), 50)
            counter += 1
            counter %= 300
            pygame.display.flip()

            # PyScript requires async.sleep to return control to the browser
            await asyncio.sleep(1 / fps)

        pygame.quit()


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        # Initialize the PyScript environment.
        pys.Init.create(),
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Welcome to Reflex!", size="9"),
            PyGameComponent.create(),
        ),
    )


app = rx.App()
app.add_page(index)
