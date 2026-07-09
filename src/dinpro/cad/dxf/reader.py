from dinpro.cad.base.entity import Block, Circle, Layer, Line, Polyline, Text


class DXFReader:
    SECTION_MARKER = "SECTION"
    ENTITY_MARKER = "ENTITY"
    EOF_MARKER = "EOF"

    def __init__(self) -> None:
        self._entities: dict[str, list] = {
            "LINE": [],
            "POLYLINE": [],
            "LWPOLYLINE": [],
            "CIRCLE": [],
            "TEXT": [],
            "MTEXT": [],
        }
        self._blocks: list[Block] = []
        self._layers: list[Layer] = []
        self._tables_parsed = False

    def parse(self, path: str) -> None:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        self._parse_lines(lines)

    def _parse_lines(self, lines: list[str]) -> None:
        i = 0
        n = len(lines)
        while i + 1 < n:
            code_str = lines[i].strip()
            value = lines[i + 1].rstrip("\n\r")
            if code_str == "0" and value == "SECTION":
                i += 2
                code_str = lines[i].strip()
                section_name = lines[i + 1].rstrip("\n\r")
                i += 2
                section_data = self._read_section(lines, i)
                self._process_section(section_name, section_data)
                i = section_data[1] if isinstance(section_data, tuple) else i + 1
                continue
            i += 1

    def _read_section(self, lines: list[str], start: int) -> tuple[list[tuple[int, str]], int]:
        data: list[tuple[int, str]] = []
        i = start
        while i + 1 < len(lines):
            code_str = lines[i].strip()
            value = lines[i + 1].rstrip("\n\r")
            if value == "ENDSEC" or value == "EOF":
                return (data, i + 2)
            code = int(code_str) if code_str.lstrip("-").isdigit() else 0
            data.append((code, value))
            i += 2
        return (data, i)

    def _process_section(self, name: str, data: tuple[list[tuple[int, str]], int]) -> None:
        pairs = data[0]
        if name == "TABLES":
            self._parse_tables(pairs)
        elif name == "ENTITIES":
            self._parse_entities(pairs)
        elif name == "BLOCKS":
            self._parse_block_entities(pairs)

    def _parse_tables(self, pairs: list[tuple[int, str]]) -> None:
        i = 0
        while i < len(pairs):
            code, value = pairs[i]
            if value == "LAYER" and i + 1 < len(pairs):
                i += 1
                layer_data = []
                while i < len(pairs):
                    c, v = pairs[i]
                    if c == 0 and v in ("LAYER", "ENDTAB", "TABLE"):
                        if layer_data:
                            self._layers.append(self._make_layer(layer_data))
                        if v in ("ENDTAB", "TABLE"):
                            break
                        layer_data = []
                    else:
                        layer_data.append((c, v))
                    i += 1
            i += 1

    def _make_layer(self, data: list[tuple[int, str]]) -> Layer:
        d = dict(data)
        color_map = {0: 7, 1: 7, 2: 3, 3: 2, 4: 6, 5: 5, 6: 4, 7: 7}
        color = int(d.get(62, "7"))
        return Layer(
            name=d.get(2, "0"),
            color=color_map.get(abs(color), 7),
            linetype=d.get(6, "Continuous"),
            locked=color < 0,
            frozen=False,
        )

    def _parse_entities(self, pairs: list[tuple[int, str]]) -> None:
        self._parse_entity_list(pairs, self._entities)

    def _parse_block_entities(self, pairs: list[tuple[int, str]]) -> None:
        self._parse_entity_list(pairs, None)

    def _parse_entity_list(self, pairs: list[tuple[int, str]], target: dict | None) -> None:
        i = 0
        while i < len(pairs):
            code, value = pairs[i]
            if code == 0:
                entity_types = frozenset({
                    "LINE", "CIRCLE", "TEXT", "MTEXT", "POLYLINE",
                    "LWPOLYLINE", "VERTEX", "SEQEND", "BLOCK",
                    "ENDBLK", "INSERT", "ATTDEF", "ATTRIB",
                })
                if value in entity_types:
                    entity_pairs = [(code, value)]
                    i += 1
                    while i < len(pairs):
                        ec, ev = pairs[i]
                        if ec == 0:
                            break
                        entity_pairs.append((ec, ev))
                        i += 1
                    self._process_entity(entity_pairs, target)
                    continue
            i += 1

    def _process_entity(self, pairs: list[tuple[int, str]], target: dict | None) -> None:
        if not pairs:
            return
        etype = pairs[0][1]
        d = dict(pairs[1:])

        if etype == "LINE" and target is not None:
            entity = Line(
                layer=d.get(8, "0"),
                color=int(d.get(62, "256")),
                linetype=d.get(6, "BYLAYER"),
                start=(float(d.get(10, "0")), float(d.get(20, "0")), float(d.get(30, "0"))),
                end=(float(d.get(11, "0")), float(d.get(21, "0")), float(d.get(31, "0"))),
            )
            entity.length = self._compute_length_3d(entity.start, entity.end)
            target.setdefault("LINE", []).append(entity)

        elif etype == "LWPOLYLINE" and target is not None:
            vertices = self._extract_lwvertices(pairs)
            entity = Polyline(
                layer=d.get(8, "0"),
                color=int(d.get(62, "256")),
                linetype=d.get(6, "BYLAYER"),
                elevation=float(d.get(38, "0")),
                closed=d.get(70, "0") == "1",
                vertices=[(v[0], v[1], self._get_z(v, float(d.get(38, "0")))) for v in vertices],
            )
            target.setdefault("LWPOLYLINE", []).append(entity)

        elif etype == "POLYLINE" and target is not None:
            verts, closed = self._collect_polyline_vertices(pairs)
            entity = Polyline(
                layer=d.get(8, "0"),
                color=int(d.get(62, "256")),
                linetype=d.get(6, "BYLAYER"),
                elevation=float(d.get(38, "0")),
                closed=closed or d.get(70, "0") in ("1", "129", "193"),
                vertices=verts,
            )
            target.setdefault("POLYLINE", []).append(entity)

        elif etype == "CIRCLE" and target is not None:
            entity = Circle(
                layer=d.get(8, "0"),
                color=int(d.get(62, "256")),
                center=(float(d.get(10, "0")), float(d.get(20, "0")), float(d.get(30, "0"))),
                radius=float(d.get(40, "0")),
            )
            target.setdefault("CIRCLE", []).append(entity)

        elif etype in ("TEXT", "MTEXT") and target is not None:
            entity = Text(
                layer=d.get(8, "0"),
                color=int(d.get(62, "256")),
                content=d.get(1, ""),
                insertion=(float(d.get(10, "0")), float(d.get(20, "0")), float(d.get(30, "0"))),
                height=float(d.get(40, "2.5")),
                rotation=float(d.get(50, "0")),
                is_mtext=(etype == "MTEXT"),
            )
            target.setdefault(etype, []).append(entity)

    def _extract_lwvertices(self, pairs: list[tuple[int, str]]) -> list[tuple[float, float, float]]:
        vertices: list[tuple[float, float, float]] = []
        i = 1
        while i < len(pairs):
            code, value = pairs[i]
            if code == 10:
                x = float(value)
                y = float(pairs[i + 1][1]) if i + 1 < len(pairs) else 0.0
                z = 0.0
                vertices.append((x, y, z))
                i += 1
            i += 1
        return vertices

    def _collect_polyline_vertices(
        self, pairs: list[tuple[int, str]]
    ) -> tuple[list[tuple[float, float, float]], bool]:
        vertices: list[tuple[float, float, float]] = []
        closed = False
        for i, (code, value) in enumerate(pairs):
            if code == 0 and value == "VERTEX":
                vpairs = []
                j = i + 1
                while j < len(pairs):
                    vc, vv = pairs[j]
                    if vc == 0:
                        break
                    vpairs.append((vc, vv))
                    j += 1
                vd = dict(vpairs)
                vertices.append((
                    float(vd.get(10, "0")),
                    float(vd.get(20, "0")),
                    float(vd.get(30, "0")),
                ))
            if code == 70 and value == "1":
                closed = True
        return vertices, closed

    def _compute_length_3d(
        self, p1: tuple[float, float, float], p2: tuple[float, float, float]
    ) -> float:
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dz = p2[2] - p1[2]
        return (dx * dx + dy * dy + dz * dz) ** 0.5

    def get_entities(self, etype: str, layer: str | None = None) -> list:
        results = list(self._entities.get(etype, []))
        if layer:
            results = [e for e in results if e.layer == layer]
        return results

    def get_layers(self) -> list[Layer]:
        if not self._tables_parsed:
            if not self._layers:
                self._layers.append(Layer(name="0"))
            self._tables_parsed = True
        return list(self._layers) if self._layers else [Layer(name="0")]

    def get_blocks(self, name: str | None = None) -> list[Block]:
        if name:
            return [b for b in self._blocks if b.name == name]
        return list(self._blocks)

    @staticmethod
    def _get_z(vertex: tuple[float, float, float], default: float) -> float:
        if len(vertex) >= 3:
            return vertex[2]
        return default
