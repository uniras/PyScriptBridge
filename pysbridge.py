import reflex as rx
from reflex.utils import imports
from typing import Any


PYS_TYPES = ["py", "mpy", "py-game"]
PYS_DEF_VERSION = "2025.3.1"


class Init(rx.Script):
    """
    Component that initializes PyScript.
    """

    @classmethod
    def create(cls, version: str = PYS_DEF_VERSION) -> rx.Script:
        """
        Add a component to the page that initializes PyScript.

        :param version: PyScript version
        """
        return super().create(
            src=f"https://pyscript.net/releases/{version}/core.js",
            custom_attrs={"type": "module"},
            strategy="beforeInteractive",
        )

    def add_imports(self) -> imports.ImportDict:
        """
        Add the import statement for the pysbridge.js file to be used in the component.
        """
        return {"": ["public/pysbridge.js"]}


class Script(rx.Script):
    """
    Component that loads external PyScript files.
    """

    @classmethod
    def create(
        cls, src: str | None = None, script_type: str = "mpy", script_config: str = "{}"
    ) -> rx.Script:
        """
        Add a component to the page that loads external PyScript files.

        :param src: PyScript file path
        :param script_type: PyScript type ("py", "mpy", "py-game")
        :param script_config: PyScript config
        """

        if script_type not in PYS_TYPES:
            raise ValueError(
                f"Invalid type '{script_type}'. Valid types are: {', '.join(PYS_TYPES)}"
            )

        if src is None:
            code = Script.generate_script(cls)
            return super().create(
                code,
                custom_attrs={"type": script_type, "config": script_config},
            )
        else:
            return super().create(
                src=src,
                custom_attrs={"type": script_type, "config": script_config},
            )

    @classmethod
    def generate_script(cls, script_class: type, indent: int = 0) -> str:
        if not hasattr(script_class, "script"):
            raise AttributeError(
                "Script not found. Please define the 'script' method to generate the script."
            )

        import inspect
        import ast
        import textwrap

        # Get the source code of the script
        source = inspect.getsource(script_class.script)
        source = textwrap.dedent(source)  # delete leading whitespace

        # Parse the source code into an AST
        parsed = ast.parse(source)
        func_node = parsed.body[0]  # get the first node (function definition)

        # Get the function body
        body_nodes = func_node.body  # type: ignore

        # Convert the AST back to source code
        body_code = "\n".join([ast.unparse(stmt) for stmt in body_nodes])

        # indent the code
        if indent > 0:
            body_code = textwrap.indent(body_code, " " * indent)

        return body_code


class PyGame:
    """
    Component that execute PyGame script.
    """

    def __init__(self):
        """
        Initialize a PyGame object.
        """
        raise NotImplementedError(
            "PyGame class cannot be instantiated directly. Use the create method instead."
        )

    @classmethod
    def create(
        cls,
        src: str | None = None,
        config: str = "{}",
        target: str = "canvas",
        canvas_auto_create: bool = True,
    ) -> rx.el.Div:
        """
        Add a component to the page that executes PyGame script.

        :param src: PyScript file path
        :param config: PyScript config
        :param target: Target canvas element ID
        :param canvas_auto_create: Whether to automatically create a canvas element
        """

        if src is None:
            code = Script.generate_script(cls)
            script = rx.Script.create(
                code,
                custom_attrs={"type": "py-game", "config": config},
            )
        else:
            script = rx.Script.create(
                src=src,
                custom_attrs={"type": "py-game", "config": config},
            )

        children = (script,)

        if canvas_auto_create:
            children = (rx.el.canvas(id=target),) + children

        return rx.el.Div.create(*children)


class Var(rx.Var):
    """
    Alias for rx.Var to be used in PyScriptBridge.
    """

    def __init__(self, name: str, pysid: str = ""):
        """
        Initialize a Var object.

        :param name: Variable name
        :param pysid: PyScriptBridge ID
        """
        super().__init__(self.name(name, pysid))

    @classmethod
    def sanitize_pysid(cls, pysid: str) -> str:
        """
        Sanitize the PyScriptBridge ID.

        :param pysid: PyScriptBridge ID
        """
        import re

        return re.sub(r"[^a-zA-Z0-9_]", "", pysid)

    @classmethod
    def name(cls, name: str, pysid: str | None = None) -> str:
        """
        Create a variable name for PyScriptBridge.

        :param name: Variable name
        :param pysid: PyScriptBridge ID
        """
        return f"{name}{cls.sanitize_pysid(pysid)}" if pysid else name


class Bridge(rx.Fragment):
    """
    Base class for components that use Hooks.
    """

    def __init__(self):
        """
        Initialize a Bridge object.
        """
        raise NotImplementedError(
            "Bridge class cannot be instantiated directly. Use the create method instead."
        )

    @classmethod
    def create(cls, *args, **kwargs):
        """
        Create a component that uses Hooks.

        :param args: Positional arguments
        :param kwargs: Keyword arguments
        """
        pysid = kwargs.get("data_pysid", "")
        if not isinstance(pysid, str):
            raise TypeError(f"Invalid type '{type(pysid)}'. pysid must be a string.")
        kwargs.pop("data_pysid", None)
        new_kwargs = {
            **kwargs,
            "key": pysid,
        }

        auto_resolve = kwargs.get("auto_resolve", True)

        pys_type = kwargs.get("pys_type", "mpy")
        if pys_type not in PYS_TYPES:
            raise ValueError(
                f"Invalid type '{pys_type}'. Valid types are: {', '.join(PYS_TYPES)}"
            )
        pys_config = kwargs.get("pys_config", "{}")
        pys_func = Var.name("__pys_func", pysid)
        pys_var = Var.name("__pys_var", pysid)
        res_code = f"{pys_var}.resolve()\n" if auto_resolve else ""
        pre_code = f'import js\n{pys_var} = js.PysBridge.get_pys_bridge("{pysid}")\n\nasync def {pys_func}(pys, js):\n'
        aft_code = f"\n\nawait {pys_func}({pys_var}, js)\n{res_code}{pys_var} = None\n{pys_func} = None\n"
        pys_code = Script.generate_script(cls, 4)
        pys_element = rx.script(
            f"{pre_code}{pys_code}{aft_code}",
            custom_attrs={"type": pys_type, "config": pys_config},
        )
        new_args = args + (pys_element,)

        return super().create(
            "",
            *new_args,
            **new_kwargs,
        )

    @classmethod
    def generate_pysid(cls) -> str:
        """
        Generate a unique pysid for the component.
        """
        import uuid

        return str(uuid.uuid4())

    @classmethod
    def sanitize_value(cls, data: Any) -> str:
        """
        Returns "null" if the value is None. If the value is a string, it escapes the string and wraps it in double quotes.
        """
        return (
            "null"
            if data is None
            else (
                f'"{data.replace("\\", "\\\\").replace('"', '\\"')}"'
                if isinstance(data, str)
                else str(data)
            )
        )

    @classmethod
    def call_func(cls, func_name: str, pysid: str = "", *args) -> rx.event.EventSpec:
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
                    await globalThis.PysBridge.get_pys_bridge("{pysid}").call_func("{func_name}", {', '.join([cls.sanitize_value(arg) for arg in args])});
                }})();
            """
        )

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

    def add_hooks(self) -> list[str | rx.Var]:
        """
        Define the hooks to be used in the component.
        """
        return [self.set_pysid_ref()]

    def set_pysid_ref(self) -> str:
        """
        Create a UUID reference for the component.
        """
        return f"""
            globalThis.PysBridge.create_pys_bridge("{self.key}");
        """

    def use_state(self, var_name: str, initial_value: Any = None) -> str:
        """
        Define useState and register it in globalThis so that it can be accessed from PyScript.

        :param var_name: Variable name of useState
        :param initial_value: Initial value of useState, or null if none is specified.
        """
        initial_value = self.sanitize_value(initial_value)
        return f"""
            var [{Var.name(var_name, self.key)}, set{Var.name(var_name.capitalize(), self.key)}] = useState({initial_value});
            globalThis.PysBridge.get_pys_bridge("{self.key}").add_state("{var_name}", {Var.name(var_name, self.key)}, set{Var.name(var_name.capitalize(), self.key)});
        """

    def use_ref(self, ref_name: str, ref_value: Any = None) -> str:
        """
        Define useRef and register it in globalThis so that it can be accessed from PyScript.

        :param ref_name: Variable name of useRef
        :param ref_value: Initial value of useRef, or null if none is specified.
        """
        ref_value = self.sanitize_value(ref_value)
        return f"""
            var {Var.name(ref_name, self.key)} = useRef({ref_value});
            globalThis.PysBridge.get_pys_bridge("{self.key}").add_ref("{ref_name}", {Var.name(ref_name, self.key)});
        """

    def use_effect(self, effect_func: str, effect_vars: list[str] | None = None) -> str:
        """
        Sets up useEffect so that its logic can be implemented as a function defined in PyScript.

        :param effect_func: Function name to call from useEffect
        :param effect_vars: Dependencies of useEffect
        """
        return f"""
            useEffect(() => {{
                (async () => {{
                    await globalThis.PysBridge.get_pys_bridge("{self.key}").call_func("{effect_func}");
                }})();
            }}{', [' + ', '.join(effect_vars) + ']' if effect_vars is not None else ''});
        """

    def var(self, var_name: str) -> str:
        """
        Get the value of a variable in PyScript.

        :param var_name: Variable name
        """
        return Var.name(var_name, self.key)
