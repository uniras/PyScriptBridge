import reflex as rx
import pysbridge as pys


# A simple counter component that runs entirely on the frontend using PyScript.
class SimpleCounterComponent(pys.Bridge):
    # Override the script method to define the PyScript code.
    async def script(self, pys, js, proxy):
        # Increments the useState counter by 1 and updates the element referenced by useRef.
        def increment_counter():
            pys.set_state("counter", pys.state("counter") + 1)
            pys.ref("text_ref").current.innerHTML = f"Count: {pys.state('counter') + 1}  using useRef and innerHTML"

        # Called via useEffect when the counter value changes, this function updates the page title.
        def change_title():
            js.document.title = f"Counter: {pys.state('counter')} - Reflex PyScript Example"

        # Register functions in js(globalThis) to be called from reflex
        pys.add_func("increment_counter", proxy(increment_counter))
        pys.add_func("change_title", proxy(change_title))

    # Hook relationships are defined by overriding the add_hooks method.
    def add_hooks(self) -> list[str | rx.Var]:
        return [
            # UseState to record counter values.
            self.use_state("counter", 0),
            # UseRef to hold DOM elements.
            self.use_ref("text_ref"),
            # Call PyScript functions when the counter value changes with useEffect. wait for the promise to resolve before calling the function.
            self.use_effect("change_title", [self.var("counter")]),
        ]

    # Override the create method to define the component's structure.
    @classmethod
    def create(cls):
        # Generate a unique pysid for each instance of the component.(Global pysid is empty string)
        pysid = cls.generate_pysid()

        # Create a Reflex and PyScriptBridge component with the pysid.
        return super().create(
            rx.vstack(
                # Use pys.Var to pass useState values to components.
                rx.heading(f"Count: {pys.Var('counter', pysid)} (Using useState)", size="5"),
                rx.button(
                    "Increment",
                    # Call PyScript functions when you click a button. wait for the "CounterTest" promise to resolve before calling the function.
                    on_click=cls.call_func("increment_counter", f"{pysid}")
                ),
                rx.text(
                    "This is a simple counter example using PyScript.",
                    font_size="2xl",
                    # Register a reference to this element in useRef.
                    custom_attrs={"ref": f"{pys.Var('text_ref', pysid)}"},
                ),
                spacing="5",
                justify="center",
            ),
            data_pysid=pysid,
        )


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        # Initialize the PyScript environment.
        pys.Init.create(),
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Welcome to Reflex!", size="9"),
            SimpleCounterComponent.create(),
            SimpleCounterComponent.create(),
        ),
    )


app = rx.App()
app.add_page(index)
