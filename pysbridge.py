import reflex as rx
from reflex.utils import imports


class InitPyScript(rx.Fragment):
    """
    Component that initializes PyScript.
    """

    @classmethod
    def create(cls, version: str = "2025.3.1") -> rx.Fragment:
        """
        Add a component to the page that initializes PyScript.

        :param version: PyScript version
        """
        return super().create(
            rx.Script.create(
                src=f"https://pyscript.net/releases/{version}/core.js",
                custom_attrs={"type": "module"},
                strategy="beforeInteractive",
            ),
        )

    def add_imports(self) -> imports.ImportDict:
        """
        Add the import statement for the pysbridge.js file to be used in the component.
        """
        return {"": ["public/pysbridge.js"]}


class InlinePyScript(rx.Script):
    """
    Inline PyScript code writing component.
    """

    @classmethod
    def create(cls, code: str, type: str = "mpy", config: str = "{}") -> rx.Script:
        """
        Add a component to the page that writes PyScript code inline.

        :param code: PyScript code
        :param type: PyScript type (py, mpy, py-game)
        :param config: PyScript configuration
        """
        from textwrap import dedent

        formatted_code = dedent(code).strip() + "\n"

        return super().create(
            formatted_code,
            custom_attrs={"type": type, "config": config},
        )


class ExternalPyScript(rx.Script):
    """
    Component that reads and executes PyScript code from an external Python file.
    """

    @classmethod
    def create(cls, src: str, type: str = "mpy", config: str = "{}") -> rx.Script:
        """
        PyScript code is read from an external Python file and executed.

        :param src: Path to the Python file containing the PyScript code
        :param type: PyScript type (py, mpy, py-game)
        :param config: PyScript configuration
        """
        return super().create(
            src=src,
            custom_attrs={"type": type, "config": config},
        )


class BasicHooksImport:
    """
    Class that defines methods to import Hooks for use with Reflex.

    Inherit this class if you want to use Hooks in Reflex or PyScript components.
    """

    def add_imports(self) -> imports.ImportDict:
        """
        Add the import statement for the Hooks to be used in the component.
        """
        return {
            "react": [
                imports.ImportVar(tag="useState"),
                imports.ImportVar(tag="useRef"),
                imports.ImportVar(tag="useEffect"),
            ]
        }


class UseHooksComponent(BasicHooksImport, rx.Fragment):
    """
    Base class for components that use Hooks.
    """

    pass


def sanitize_value(data: any) -> str:
    """
    Returns "null" if the value is None. If the value is a string, it escapes the string and wraps it in double quotes.
    """
    return (
        "null"
        if data is None
        else f'"{data.replace("\\", "\\\\").replace('"', '\\"')}"' if isinstance(data, str) else str(data)
    )


def use_state(var_name: str, initial_value: any = None) -> str:
    """
    Define useState and register it in globalThis so that it can be accessed from PyScript.

    :param var_name: Variable name of useState
    :param initial_value: Initial value of useState, or null if none is specified.
    """
    initial_value = sanitize_value(initial_value)
    return f"""
        var [{var_name}, set{var_name.capitalize()}] = useState({initial_value});
        globalThis.pys_register_state("{var_name}", {var_name}, set{var_name.capitalize()});
    """


def use_ref(ref_name: str, ref_value: any = None) -> str:
    """
    Define useRef and register it in globalThis so that it can be accessed from PyScript.

    :param ref_name: Variable name of useRef
    :param ref_value: Initial value of useRef, or null if none is specified.
    """
    ref_value = sanitize_value(ref_value)
    return f"""
        var {ref_name} = useRef({ref_value});
        globalThis.pys_register_ref("{ref_name}", {ref_name});
    """


def use_effect(effect_func: str, promiseName: str, effect_vars: list[str] = None) -> str:
    """
    Sets up useEffect so that its logic can be implemented as a function defined in PyScript.

    :param effect_func: Function name to call from useEffect
    :param promiseName: Name of the promise to wait for
    :param effect_vars: Dependencies of useEffect
    """
    return f"""
        useEffect(() => {{
            (async () => {{
                await globalThis.pys_call_func("{effect_func}", "{promiseName}");
            }})();
        }}{', [' + ', '.join(effect_vars) + ']' if effect_vars is not None else ''});
    """


def call_func(func_name: str, promiseName: str, *args) -> rx.event.EventSpec:
    """
    Calling a PyScript function as a callback.
    Note: PyScript will throw an error if the number of arguments does not match between the caller and the target function.

    :param func_name: PyScript function name
    :param promiseName: Name of the promise to wait for
    :param args: Arguments to be passed to the PyScript function.
    """
    return rx.call_script(
        f"""
            (async () => {{
                await globalThis.pys_call_func("{func_name}", "{promiseName}", {', '.join([sanitize_value(arg) for arg in args])});
            }})();
        """
    )
