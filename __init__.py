"""String Join (Multi): une muchos strings con un delimitador configurable.

- Entradas dinámicas (Autogrow): al conectar "string0" aparece "string1", etc. (hasta 100).
- Cada entrada acepta también listas de strings (is_input_list), que se aplanan.
- El delimitador admite secuencias de escape: \\n, \\t, \\r, \\\\.
"""
from typing_extensions import override

from comfy_api.latest import ComfyExtension, io


def _flatten(value):
    if value is None:
        return
    if isinstance(value, (list, tuple)):
        for v in value:
            yield from _flatten(v)
    else:
        yield str(value)


def _first(value, default):
    if isinstance(value, (list, tuple)):
        return value[0] if value else default
    return default if value is None else value


def _unescape(s: str) -> str:
    out, i = [], 0
    escapes = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\"}
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s) and s[i + 1] in escapes:
            out.append(escapes[s[i + 1]])
            i += 2
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


class StringJoinMulti(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        # Todas las entradas opcionales (min=0): si el nodo de origen está muteado o en bypass
        # el frontend quita el enlace y ese string simplemente no cuenta.
        template = io.Autogrow.TemplatePrefix(
            input=io.String.Input("string", optional=True),
            prefix="string",
            min=0,
            max=100,
        )
        return io.Schema(
            node_id="StringJoinMulti",
            display_name="String Join (Multi)",
            category="utils/string",
            search_aliases=["join", "concat", "concatenate", "implode"],
            description="Concatena todos los strings conectados (y listas de strings) separados por el delimitador.",
            is_input_list=True,
            inputs=[
                io.String.Input("delimiter", default=", ",
                                tooltip="Separador. Admite \\n, \\t, \\r y \\\\."),
                io.Boolean.Input("skip_empty", default=True,
                                 tooltip="Omite strings vacíos (o sólo espacios)."),
                io.Boolean.Input("strip", default=False,
                                 tooltip="Quita espacios al principio y final de cada string."),
                io.Autogrow.Input("strings", template=template, optional=True),
            ],
            outputs=[io.String.Output(display_name="STRING")],
        )

    @classmethod
    def execute(cls, delimiter, skip_empty, strip, strings=None) -> io.NodeOutput:
        delimiter = _unescape(str(_first(delimiter, ", ")))
        skip_empty = bool(_first(skip_empty, True))
        strip = bool(_first(strip, False))

        parts = []
        # Autogrow llega como dict {string0: ..., string1: ...}; ordenar por índice numérico
        if isinstance(strings, dict):
            keys = sorted(strings, key=lambda k: int(k[len("string"):]) if k[len("string"):].isdigit() else 1 << 30)
            values = [strings[k] for k in keys]
        else:
            values = strings
        for s in _flatten(values):
            if strip:
                s = s.strip()
            if skip_empty and not s.strip():
                continue
            parts.append(s)
        return io.NodeOutput(delimiter.join(parts))


class StringJoinExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [StringJoinMulti]


async def comfy_entrypoint() -> StringJoinExtension:
    return StringJoinExtension()
