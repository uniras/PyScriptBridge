import reflex as rx
import pysbridge as pys


class PyScriptComponent(pys.Script):
    # Override the script method to define the PyScript code.
    async def script(self):
        import js  # type: ignore
        js.console.log("Hello from PyScript!")


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        # Initialize the PyScript environment.
        pys.Init.create(),
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Welcome to Reflex!", size="9"),
            PyScriptComponent.create(),
        ),
    )


app = rx.App()
app.add_page(index)
