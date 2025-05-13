import reflex as rx
import pysbridge as pys


# A simple counter component that runs entirely on the frontend using PyScript.
class SimpleCounterComponent(pys.UseHooksComponent):
    @classmethod
    def create(cls):
        return super().create(
            # Write PyScript code inline. (Alternatively, you can use the ExternalPyScript component to execute code from an external file.)
            pys.InlinePyScript.create(
                """
                import js

                # Increments the useState counter by 1 and updates the element referenced by useRef.
                def increment_counter():
                    js.pys_set("counter", js.pys_get("counter") + 1)
                    js.pys_ref("text_ref").current.innerHTML = f"Count: {js.pys_get('counter') + 1}  using useRef and innerHTML"

                # Called via useEffect when the counter value changes, this function updates the page title.
                def change_title():
                    js.document.title = f"Counter: {js.pys_get('counter')} - Reflex PyScript Example"

                # Register functions in js(globalThis) to be called from reflex
                js.pys_func("increment_counter", increment_counter)
                js.pys_func("change_title", change_title)

                # Now that the function is registered, resolve "CouterTest" Promise
                js.pys_resolve("CounterTest")
                """
            ),
            rx.vstack(
                # Use rx.Var to pass useState values to components.
                rx.heading(f"Count: {rx.Var('counter')} (Using useState)", size="5"),
                rx.button(
                    "Increment",
                    # Call PyScript functions when you click a button. wait for the "CounterTest" promise to resolve before calling the function.
                    on_click=pys.call_func("increment_counter", "CounterTest"),
                ),
                rx.text(
                    "This is a simple counter example using PyScript.",
                    font_size="2xl",
                    # Register a reference to this element in useRef.
                    custom_attrs={"ref": f"{rx.Var('text_ref')}"},
                ),
                spacing="5",
                justify="center",
                min_height="85vh",
            ),
        )

    # Hook relationships are defined by overriding the add_hooks method.
    def add_hooks(self) -> list[str | rx.Var]:
        return [
            # UseState to record counter values.
            pys.use_state("counter", 0),
            # UseRef to hold DOM elements.
            pys.use_ref("text_ref"),
            # Call PyScript functions when the counter value changes with useEffect. wait for the "CounterTest" promise to resolve before calling the function.
            pys.use_effect("change_title", "CounterTest", ["counter"]),
        ]


def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.container(
        pys.InitPyScript.create(),
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("Welcome to Reflex!", size="9"),
            SimpleCounterComponent.create(),
        ),
    )


app = rx.App()
app.add_page(index)
