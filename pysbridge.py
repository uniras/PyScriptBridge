import reflex as rx
from reflex.utils import imports


class InitPyScript(rx.Fragment):
    """
    Component that initializes PyScript.
    """

    @classmethod
    def create(cls, auto_ready: bool = True, version: str = "2025.3.1") -> rx.Fragment:
        """
        Add a component to the page that initializes PyScript.

        Uses a Promise named globalThis.pyScriptReady to defer function calls from Reflex until PyScript has finished initializing.
        Normally, this is resolved by PyScript’s done event.
        However, in cases where the event does not fire—such as in py-game mode or when the PyScript code is running in an infinite loop—you should
        set auto_ready to False and manually call js.pyScriptReady.resolve() at the appropriate time in your PyScript code.

        :param auto_ready: Whether to automatically resolve pyScriptReady when the PyScript execution completes.
        :param version: PyScript version
        """
        return super().create(
            rx.Script.create(
                src=f"https://pyscript.net/releases/{version}/core.js",
                custom_attrs={"type": "module"},
                strategy="beforeInteractive",
            ),
            rx.Script.create(
                f"""
                globalThis.pyScriptReady = (() => {{
                    let resolve;
                    const promise = new Promise((res) => resolve = res);
                    return {{ promise, resolve }};
                }})();

                if ({'true' if auto_ready else 'false'}) {{
                    addEventListener("py:done", globalThis.pyScriptReady.resolve, {{ once: true }});
                    addEventListener("mpy:done", globalThis.pyScriptReady.resolve, {{ once: true }});
                }}
                """,
                custom_attrs={"type": "module"},
                strategy="beforeInteractive",
            ),
        )


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


def define_useState(var_name: str, initial_value: any = None, prefix: str = "") -> str:
    """
    Define useState and register it in globalThis so that it can be accessed from PyScript.

    :param var_name: Variable name of useState
    :param initial_value: Initial value of useState, or null if none is specified.
    :param prefix: Prefix to be assigned when registering a global variable.
    """
    initial_value = sanitize_value(initial_value)
    return f"""
        var [{var_name}, set{var_name.capitalize()}] = useState({initial_value});
        globalThis.{prefix}{var_name} = {var_name};
        globalThis.{prefix}set{var_name.capitalize()} = set{var_name.capitalize()};
    """


def define_useRef(ref_name: str, ref_var: any = None, prefix: str = "") -> str:
    """
    Define useRef and register it in globalThis so that it can be accessed from PyScript.

    :param ref_name: Variable name of useRef
    :param ref_var: Initial value of useRef, or null if none is specified.
    :param prefix: Prefix to be assigned when registering a global variable.
    """
    ref_var = sanitize_value(ref_var)
    return f"""
        var {ref_name} = useRef({ref_var});
        globalThis.{prefix}{ref_name} = {ref_name};
    """


def define_useEffect(effect_func: str, effect_vars: list[str] = None) -> str:
    """
    Sets up useEffect so that its logic can be implemented as a function defined in PyScript.

    :param effect_func: Function name to call from useEffect
    :param effect_vars: Dependencies of useEffect
    """
    return f"""
        useEffect(() => {{
            async function runEffect() {{
                await globalThis.pyScriptReady.promise;
                globalThis.{effect_func}();
            }}
            runEffect();
        }}{', [' + ', '.join(effect_vars) + ']' if effect_vars is not None else ''});
    """


def call_pyscript_func(func_name: str, *args) -> rx.event.EventSpec:
    """
    Calling a PyScript function as a callback.
    Note: PyScript will throw an error if the number of arguments does not match between the caller and the target function.

    :param func_name: PyScript function name
    :param args: Arguments to be passed to the PyScript function.
    """
    return rx.call_script(
        f"""
            (async () => {{
                await globalThis.pyScriptReady.promise;
                globalThis.{func_name}({', '.join(args)});
            }})();
        """
    )
