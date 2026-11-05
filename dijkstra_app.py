import heapq
import math
import time
import tkinter as tk
from collections import deque
from dataclasses import dataclass, field
from tkinter import ttk, messagebox
from typing import Dict, List, Optional, Tuple

GEO = {
    "Львів": (24.03, 49.84), "Луцьк": (25.34, 50.75), "Рівне": (26.25, 50.62),
    "Тернопіль": (25.59, 49.55), "Івано-Франківськ": (24.71, 48.92), "Ужгород": (22.30, 48.62),
    "Чернівці": (25.94, 48.29), "Хмельницький": (27.00, 49.42), "Житомир": (28.66, 50.25),
    "Вінниця": (28.47, 49.23), "Київ": (30.52, 50.45), "Чернігів": (31.29, 51.49),
    "Суми": (34.80, 50.91), "Полтава": (34.55, 49.59), "Харків": (36.23, 49.99),
    "Луганськ": (39.30, 48.57), "Донецьк": (37.80, 48.02), "Маріуполь": (37.55, 47.10),
    "Дніпро": (35.05, 48.46), "Запоріжжя": (35.14, 47.84), "Мелітополь": (35.37, 46.84),
    "Кривий Ріг": (33.39, 47.91), "Кропивницький": (32.26, 48.51), "Черкаси": (32.06, 49.44),
    "Одеса": (30.73, 46.48), "Миколаїв": (32.00, 46.97), "Херсон": (32.62, 46.64),
    "Сімферополь": (34.10, 44.95), "Севастополь": (33.52, 44.62),
}

ROADS = [
    ("Вінниця", "Житомир", 127), ("Вінниця", "Київ", 267), ("Вінниця", "Кропивницький", 320),
    ("Вінниця", "Миколаїв", 428), ("Вінниця", "Одеса", 423), ("Вінниця", "Черкаси", 341),
    ("Вінниця", "Чернівці", 276), ("Дніпро", "Донецьк", 248), ("Дніпро", "Запоріжжя", 85),
    ("Дніпро", "Кропивницький", 244), ("Дніпро", "Кривий Ріг", 146), ("Дніпро", "Полтава", 160),
    ("Дніпро", "Харків", 218), ("Донецьк", "Луганськ", 156), ("Донецьк", "Маріуполь", 113),
    ("Донецьк", "Харків", 294), ("Запоріжжя", "Мелітополь", 125), ("Івано-Франківськ", "Тернопіль", 133),
    ("Івано-Франківськ", "Ужгород", 293), ("Київ", "Житомир", 140), ("Київ", "Полтава", 340),
    ("Київ", "Суми", 333), ("Київ", "Черкаси", 189), ("Київ", "Чернігів", 148),
    ("Кропивницький", "Полтава", 246), ("Луганськ", "Харків", 325), ("Львів", "Івано-Франківськ", 134),
    ("Львів", "Луцьк", 151), ("Львів", "Рівне", 211), ("Львів", "Тернопіль", 127),
    ("Львів", "Ужгород", 268), ("Львів", "Чернівці", 268), ("Мелітополь", "Маріуполь", 192),
    ("Мелітополь", "Сімферополь", 250), ("Миколаїв", "Херсон", 69), ("Рівне", "Житомир", 188),
    ("Рівне", "Луцьк", 73), ("Рівне", "Тернопіль", 155), ("Харків", "Полтава", 143),
    ("Херсон", "Мелітополь", 231), ("Хмельницький", "Вінниця", 119), ("Хмельницький", "Житомир", 183),
    ("Хмельницький", "Рівне", 194), ("Хмельницький", "Тернопіль", 112), ("Хмельницький", "Чернівці", 187),
    ("Суми", "Харків", 184), ("Черкаси", "Полтава", 233), ("Полтава", "Суми", 175),
    ("Чернігів", "Суми", 306), ("Сімферополь", "Севастополь", 81),
]


@dataclass
class Edge:
    u: str
    v: str
    w: float
    directed: bool = False

    def connects(self, a: str, b: str) -> bool:
        return {self.u, self.v} == {a, b}


class Graph:
    def __init__(self) -> None:
        self.pos: Dict[str, Tuple[float, float]] = {}
        self.edges: List[Edge] = []

    @classmethod
    def ukraine(cls, width: int = 1000, height: int = 640) -> "Graph":
        g = cls()
        lon0, lon1, lat0, lat1 = 21.8, 40.4, 44.2, 51.9
        k = (width - 80) / (lon1 - lon0)
        for name, (lon, lat) in GEO.items():
            g.pos[name] = (40 + (lon - lon0) * k, 30 + (lat1 - lat) * k / 0.67)
        for u, v, w in ROADS:
            g.edges.append(Edge(u, v, w))
        return g

    def add_vertex(self, name: str, x: float, y: float) -> None:
        self.pos[name] = (x, y)

    def remove_vertex(self, name: str) -> None:
        self.pos.pop(name, None)
        self.edges = [e for e in self.edges if name not in (e.u, e.v)]

    def find_edge(self, a: str, b: str) -> Optional[Edge]:
        return next((e for e in self.edges if e.connects(a, b)), None)

    def add_edge(self, u: str, v: str, w: float, directed: bool = False) -> Edge:
        e = Edge(u, v, w, directed)
        self.edges.append(e)
        return e

    def remove_edge(self, a: str, b: str) -> bool:
        e = self.find_edge(a, b)
        if e:
            self.edges.remove(e)
        return e is not None

    def adjacency(self) -> Dict[str, List[Tuple[str, float]]]:
        adj: Dict[str, List[Tuple[str, float]]] = {n: [] for n in self.pos}
        for e in self.edges:
            adj[e.u].append((e.v, e.w))
            if not e.directed:
                adj[e.v].append((e.u, e.w))
        return adj

    def weight_between(self, a: str, b: str) -> Optional[float]:
        best = None
        for e in self.edges:
            if (e.u == a and e.v == b) or (not e.directed and e.u == b and e.v == a):
                best = e.w if best is None else min(best, e.w)
        return best


@dataclass
class SearchResult:
    algorithm: str
    found: bool = False
    path: List[str] = field(default_factory=list)
    distance: float = 0.0
    dist: Dict[str, float] = field(default_factory=dict)
    prev: Dict[str, Optional[str]] = field(default_factory=dict)
    events: List[tuple] = field(default_factory=list)   
    order: List[str] = field(default_factory=list)
    cycles: int = 0         
    relaxations: int = 0
    improvements: int = 0
    time_ms: float = 0.0


class ShortestPathSearch:
    name = "?"

    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def _restore(self, prev: Dict[str, Optional[str]], target: str) -> List[str]:
        path, cur = [], target
        while cur is not None:
            path.append(cur)
            cur = prev.get(cur)
        return list(reversed(path))

    def search(self, start: str, target: str) -> SearchResult:
        raise NotImplementedError


class DijkstraSearch(ShortestPathSearch):
    name = "dijkstra"

    def search(self, start: str, target: str) -> SearchResult:
        res = SearchResult(self.name)
        t0 = time.perf_counter()
        adj = self.graph.adjacency()
        dist = {n: math.inf for n in adj}
        prev: Dict[str, Optional[str]] = {n: None for n in adj}
        dist[start] = 0.0
        heap = [(0.0, start)]
        done = set()
        res.events.append(("push", start, 0.0))
        while heap:
            d, u = heapq.heappop(heap)
            if u in done:
                continue
            done.add(u)
            res.cycles += 1
            res.order.append(u)
            res.events.append(("extract", u, d))
            if u == target:
                break
            for v, w in adj[u]:
                res.relaxations += 1
                if v in done:
                    res.events.append(("skip", u, v, d + w))
                    continue
                if d + w < dist[v]:
                    dist[v] = d + w
                    prev[v] = u
                    res.improvements += 1
                    heapq.heappush(heap, (dist[v], v))
                    res.events.append(("improve", u, v, dist[v]))
                else:
                    res.events.append(("keep", u, v, d + w))
        res.dist, res.prev = dist, prev
        if dist.get(target, math.inf) < math.inf:
            res.found, res.distance = True, dist[target]
            res.path = self._restore(prev, target)
        res.time_ms = (time.perf_counter() - t0) * 1000.0
        return res


class BfsSearch(ShortestPathSearch):
    name = "bfs"

    def search(self, start: str, target: str) -> SearchResult:
        res = SearchResult(self.name)
        t0 = time.perf_counter()
        adj = self.graph.adjacency()
        prev: Dict[str, Optional[str]] = {start: None}
        q = deque([start])
        res.events.append(("push", start, 0.0))
        found = start == target
        while q and not found:
            u = q.popleft()
            res.cycles += 1
            res.order.append(u)
            res.events.append(("extract", u, 0.0))
            for v, w in adj[u]:
                res.relaxations += 1
                if v not in prev:
                    prev[v] = u
                    q.append(v)
                    res.events.append(("improve", u, v, 0.0))
                    if v == target:
                        found = True
                        break
        res.prev = prev
        if found or start == target:
            res.found = True
            res.path = self._restore(prev, target)
            res.distance = sum(self.graph.weight_between(a, b) or 0 for a, b in zip(res.path, res.path[1:]))
        res.time_ms = (time.perf_counter() - t0) * 1000.0
        return res


ALGORITHMS = {
    "dijkstra": ("Алгоритм Дейкстри (за відстанню, км)", DijkstraSearch),
    "bfs": ("Пошук у ширину (за кількістю ребер, для порівняння)", BfsSearch),
}

C_UNSEEN, C_QUEUE, C_CURRENT, C_DONE = "#dfe6ee", "#f5d76e", "#e8743b", "#8aa6c1"
C_START, C_TARGET, C_PATH, C_EDGE = "#2e86de", "#c0392b", "#27ae60", "#9aa5b1"
EDIT_MODES = {
    "view": "Перегляд (без редагування)",
    "move": "Перемістити місто (тягнути)",
    "add_vertex": "Додати місто (клік по вільному місцю)",
    "del_vertex": "Видалити місто (клік по ньому)",
    "add_edge": "Додати ребро/дугу (клік 2 міст, вага з поля)",
    "del_edge": "Видалити ребро/дугу (клік 2 міст)",
    "set_weight": "Змінити вагу (клік 2 міст, вага з поля)",
    "toggle_arc": "Ребро ↔ дуга (клік 2 міст)",
}
R = 8


class DijkstraApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Лаб. №5 — Алгоритм Дейкстри: автомобільні шляхи України")
        root.geometry("1400x940")
        self.graph = Graph.ukraine()
        self.state: Dict[str, str] = {}
        self.labels: Dict[str, float] = {}
        self.hl_edges: set = set()
        self.path_edges: set = set()
        self.active_edge: Optional[Tuple[str, str]] = None
        self.result: Optional[SearchResult] = None
        self.animating, self.job = False, None
        self.first: Optional[str] = None
        self.drag: Optional[str] = None
        self.start_name, self.target_name = "Львів", "Харків"
        self._build()
        self._redraw()

    def _build(self) -> None:
        main = ttk.Frame(self.root); main.pack(fill="both", expand=True)
        panel = ttk.Frame(main, padding=10); panel.pack(side="left", fill="y")
        ttk.Label(panel, text="Керування пошуком", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 6))
        ttk.Label(panel, text="Алгоритм").pack(anchor="w")
        self.algo_combo = ttk.Combobox(panel, state="readonly", width=42, values=[v[0] for v in ALGORITHMS.values()])
        self.algo_combo.set(ALGORITHMS["dijkstra"][0]); self.algo_combo.pack(anchor="w", pady=(0, 6))
        ttk.Label(panel, text="Відправна точка").pack(anchor="w")
        self.start_combo = ttk.Combobox(panel, state="readonly", width=42); self.start_combo.pack(anchor="w", pady=(0, 6))
        ttk.Label(panel, text="Цільова точка").pack(anchor="w")
        self.target_combo = ttk.Combobox(panel, state="readonly", width=42); self.target_combo.pack(anchor="w", pady=(0, 6))
        ttk.Button(panel, text="⇄ Поміняти місцями", command=self._swap).pack(fill="x", pady=2)
        ttk.Label(panel, text="Затримка між кроками, мс").pack(anchor="w", pady=(6, 0))
        self.delay_var = tk.IntVar(value=250)
        ttk.Scale(panel, from_=1000, to=0, orient="horizontal", variable=self.delay_var).pack(fill="x")
        self.instant = tk.BooleanVar(value=False)
        ttk.Checkbutton(panel, text="Миттєво (без анімації)", variable=self.instant).pack(anchor="w")
        self.show_w = tk.BooleanVar(value=True)
        ttk.Checkbutton(panel, text="Показувати ваги ребер (км)", variable=self.show_w, command=self._redraw).pack(anchor="w", pady=(0, 6))
        ttk.Button(panel, text="▶ Запустити пошук", command=self.run).pack(fill="x", pady=2)
        ttk.Button(panel, text="⏹ Зупинити анімацію", command=self.stop).pack(fill="x", pady=2)
        ttk.Button(panel, text="Порівняти Дейкстру і BFS", command=self.compare).pack(fill="x", pady=2)
        ttk.Button(panel, text="Відстані від відправної точки до всіх міст", command=self.all_dist).pack(fill="x", pady=2)
        ttk.Button(panel, text="Відновити початковий граф", command=self.reset_graph).pack(fill="x", pady=2)

        box = ttk.LabelFrame(panel, text="Ручне редагування графа", padding=6); box.pack(fill="x", pady=6)
        self.edit_combo = ttk.Combobox(box, state="readonly", width=42, values=list(EDIT_MODES.values()))
        self.edit_combo.set(EDIT_MODES["view"]); self.edit_combo.pack(fill="x")
        self.edit_combo.bind("<<ComboboxSelected>>", lambda e: self._edit_changed())
        f = ttk.Frame(box); f.pack(fill="x", pady=4)
        ttk.Label(f, text="Назва нового міста:").grid(row=0, column=0, sticky="w")
        self.name_entry = ttk.Entry(f, width=18); self.name_entry.grid(row=0, column=1, padx=4)
        ttk.Label(f, text="Вага ребра, км:").grid(row=1, column=0, sticky="w")
        self.weight_entry = ttk.Entry(f, width=18); self.weight_entry.insert(0, "100"); self.weight_entry.grid(row=1, column=1, padx=4)
        self.new_arc = tk.BooleanVar(value=False)
        ttk.Checkbutton(box, text="нове ребро створювати як дугу (клік 1 → клік 2)", variable=self.new_arc).pack(anchor="w")
        self.hint = tk.StringVar(value="")
        ttk.Label(box, textvariable=self.hint, wraplength=330, foreground="#8a4b00").pack(anchor="w")
        self.status = tk.StringVar(value="Готово.")
        ttk.Label(panel, textvariable=self.status, wraplength=340, foreground="#333").pack(anchor="w", pady=4)

        leg = ttk.LabelFrame(panel, text="Умовні позначення", padding=6); leg.pack(fill="x", pady=4)
        for col, txt in [(C_START, "відправна точка"), (C_TARGET, "цільова точка"), (C_UNSEEN, "ще не досягнуте місто"),
                         (C_QUEUE, "у черзі (є попередня мітка відстані)"), (C_CURRENT, "розкривається зараз"),
                         (C_DONE, "остаточна мітка (розкрите)"), (C_PATH, "найкоротший шлях")]:
            row = ttk.Frame(leg); row.pack(anchor="w")
            sw = tk.Canvas(row, width=14, height=14, highlightthickness=0)
            sw.create_oval(1, 1, 13, 13, fill=col, outline="#666"); sw.pack(side="left", padx=4)
            ttk.Label(row, text=txt).pack(side="left")

        self.canvas = tk.Canvas(main, bg="white", width=1000, height=840)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Button-1>", self._press)
        self.canvas.bind("<B1-Motion>", self._motion)
        self.canvas.bind("<ButtonRelease-1>", lambda e: setattr(self, "drag", None))
        self._refresh_combos(reset=True)


    def algo_key(self) -> str:
        return next((k for k, v in ALGORITHMS.items() if v[0] == self.algo_combo.get()), "dijkstra")

    def edit_key(self) -> str:
        return next((k for k, v in EDIT_MODES.items() if v == self.edit_combo.get()), "view")

    def _refresh_combos(self, reset: bool = False) -> None:
        names = sorted(self.graph.pos)
        self.start_combo["values"] = names; self.target_combo["values"] = names
        s, t = self.start_combo.get(), self.target_combo.get()
        self.start_combo.set(self.start_name if reset else (s if s in names else (names[0] if names else "")))
        self.target_combo.set(self.target_name if reset else (t if t in names else (names[-1] if names else "")))

    def _swap(self) -> None:
        s, t = self.start_combo.get(), self.target_combo.get()
        self.start_combo.set(t); self.target_combo.set(s); self._redraw()

    def _edit_changed(self) -> None:
        self.first = None
        hints = {"add_vertex": "Введіть назву й клацніть по вільному місцю полотна.",
                 "del_vertex": "Клацніть по місту, яке треба видалити (разом з усіма його дорогами).",
                 "add_edge": "Введіть вагу, клацніть по двох містах.",
                 "del_edge": "Клацніть по двох містах, між якими треба прибрати дорогу.",
                 "set_weight": "Введіть нову вагу й клацніть по двох містах існуючої дороги.",
                 "toggle_arc": "Клацніть по двох містах дороги: ребро стане дугою в напрямку кліків; "
                               "повтор у тому ж порядку повертає ребро; у зворотному — змінює напрям дуги.",
                 "move": "Тягніть місто мишею."}
        self.hint.set(hints.get(self.edit_key(), ""))

    def _reset_view(self) -> None:
        self.state, self.labels, self.hl_edges, self.path_edges, self.active_edge = {}, {}, set(), set(), None
        self.result = None

    def reset_graph(self) -> None:
        self.stop(); self.graph = Graph.ukraine(); self._reset_view()
        self._refresh_combos(reset=True); self.status.set("Відновлено початковий граф: 29 міст, 50 доріг."); self._redraw()

    def _city_at(self, x: float, y: float) -> Optional[str]:
        best, bd = None, None
        for n, (cx, cy) in self.graph.pos.items():
            d = math.hypot(cx - x, cy - y)
            if d <= R + 6 and (bd is None or d < bd):
                best, bd = n, d
        return best

    def _weight(self) -> Optional[float]:
        try:
            w = float(self.weight_entry.get().replace(",", "."))
            return w if w > 0 else None
        except ValueError:
            return None

    def _press(self, e) -> None:
        mode, g = self.edit_key(), self.graph
        if mode == "view":
            return
        city = self._city_at(e.x, e.y)
        if mode == "move":
            self.drag = city; return
        if mode == "add_vertex":
            if city:
                self.hint.set("Тут уже є місто."); return
            name = self.name_entry.get().strip() or f"Місто {len(g.pos) + 1}"
            if name in g.pos:
                self.hint.set("Місто з такою назвою вже існує."); return
            g.add_vertex(name, e.x, e.y); self.name_entry.delete(0, tk.END)
            self._after_edit(f"Додано місто «{name}». Усього міст: {len(g.pos)}.")
            return
        if city is None:
            self.hint.set("Клацніть точно по місту."); return
        if mode == "del_vertex":
            g.remove_vertex(city); self._after_edit(f"Місто «{city}» видалено разом з усіма дорогами: "
                                                    f"{len(g.pos)} міст, {len(g.edges)} доріг.")
            return
        if self.first is None:
            self.first = city; self.hint.set(f"Обрано «{city}». Клацніть друге місто."); return
        a, b, self.first = self.first, city, None
        if a == b:
            self.hint.set("Потрібні два різних міста."); return
        edge = g.find_edge(a, b)
        if mode == "add_edge":
            w = self._weight()
            if w is None: self.hint.set("Некоректна вага."); return
            if edge: self.hint.set("Дорога між цими містами вже існує."); return
            g.add_edge(a, b, w, self.new_arc.get())
            self._after_edit(f"Додано {'дугу' if self.new_arc.get() else 'ребро'} {a}–{b}, {w:g} км.")
        elif mode == "del_edge":
            if not edge: self.hint.set("Такої дороги немає."); return
            g.edges.remove(edge); self._after_edit(f"Дорогу {a}–{b} видалено: залишилось {len(g.edges)} доріг.")
        elif mode == "set_weight":
            w = self._weight()
            if not edge or w is None: self.hint.set("Немає дороги або некоректна вага."); return
            edge.w = w; self._after_edit(f"Вагу дороги {a}–{b} змінено на {w:g} км.")
        elif mode == "toggle_arc":
            if not edge: self.hint.set("Такої дороги немає."); return
            if not edge.directed:
                edge.directed, edge.u, edge.v = True, a, b; msg = f"Ребро {a}–{b} перетворено на дугу {a} → {b}."
            elif (edge.u, edge.v) == (a, b):
                edge.directed = False; msg = f"Дугу {a} → {b} перетворено назад на ребро."
            else:
                edge.u, edge.v = a, b; msg = f"Напрям дуги змінено: {a} → {b}."
            self._after_edit(msg)

    def _motion(self, e) -> None:
        if self.edit_key() == "move" and self.drag:
            self.graph.pos[self.drag] = (e.x, e.y); self._redraw()

    def _after_edit(self, msg: str) -> None:
        self._reset_view(); self._refresh_combos(); self.status.set(msg); self.hint.set(""); self._redraw()

    def _redraw(self) -> None:
        cv, g = self.canvas, self.graph
        cv.delete("all")
        s, t = self.start_combo.get(), self.target_combo.get()
        for ed in g.edges:
            if ed.u not in g.pos or ed.v not in g.pos:
                continue
            (x1, y1), (x2, y2) = g.pos[ed.u], g.pos[ed.v]
            key = frozenset((ed.u, ed.v))
            color, width = C_EDGE, 1.3
            if key in self.hl_edges: color, width = "#5d6d7e", 2
            if key in self.path_edges: color, width = C_PATH, 4
            if self.active_edge and key == frozenset(self.active_edge): color, width = C_CURRENT, 3
            kw = dict(fill=color, width=width)
            if ed.directed:
                dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy) or 1
                x2, y2 = x2 - dx / L * R, y2 - dy / L * R
                kw.update(arrow=tk.LAST, arrowshape=(14, 16, 6))
            cv.create_line(x1, y1, x2, y2, **kw)
            if self.show_w.get():
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                cv.create_text(mx, my, text=f"{ed.w:g}", font=("Segoe UI", 7), fill="#a04000")
        for n, (x, y) in g.pos.items():
            st = self.state.get(n, "unseen")
            fill = {"unseen": C_UNSEEN, "queue": C_QUEUE, "current": C_CURRENT, "done": C_DONE, "path": C_PATH}[st]
            outline, wd = "#555", 1
            if n == s: outline, wd = C_START, 3
            if n == t: outline, wd = C_TARGET, 3
            cv.create_oval(x - R, y - R, x + R, y + R, fill=fill, outline=outline, width=wd)
            cv.create_text(x, y + R + 8, text=n, font=("Segoe UI", 8, "bold"))
            if n in self.labels and self.labels[n] < math.inf:
                cv.create_text(x, y - R - 7, text=f"{self.labels[n]:g}", font=("Segoe UI", 8, "bold"), fill="#1b4f72")

    def stop(self) -> None:
        self.animating = False
        if self.job:
            try: self.root.after_cancel(self.job)
            except Exception: pass
            self.job = None

    def run(self) -> None:
        self.stop()
        s, t = self.start_combo.get(), self.target_combo.get()
        if s not in self.graph.pos or t not in self.graph.pos:
            messagebox.showwarning("Увага", "Оберіть існуючі відправну й цільову точки."); return
        res = ALGORITHMS[self.algo_key()][1](self.graph).search(s, t)
        self._reset_view(); self.result = res
        if self.instant.get():
            self._finish(res); return
        self.animating = True
        self._step(res, 0)

    def _step(self, res: SearchResult, i: int) -> None:
        if not self.animating:
            return
        if i >= len(res.events):
            self.animating = False; self._finish(res); return
        ev = res.events[i]
        kind = ev[0]
        for n, s_ in list(self.state.items()):
            if s_ == "current": self.state[n] = "done"
        self.active_edge = None
        if kind == "push":
            self.state[ev[1]] = "queue"; self.labels[ev[1]] = ev[2]
        elif kind == "extract":
            self.state[ev[1]] = "current"; self.labels[ev[1]] = ev[2] if res.algorithm == "dijkstra" else self.labels.get(ev[1], 0)
            self.status.set(f"Розкривається «{ev[1]}»" + (f", остаточна відстань {ev[2]:g} км." if res.algorithm == "dijkstra" else "."))
        elif kind in ("improve", "keep", "skip"):
            self.active_edge = (ev[1], ev[2])
            if kind == "improve":
                self.state[ev[2]] = "queue"
                if res.algorithm == "dijkstra": self.labels[ev[2]] = ev[3]
                self.hl_edges.add(frozenset((ev[1], ev[2])))
        self._redraw()
        self.job = self.root.after(max(1, int(self.delay_var.get())), lambda: self._step(res, i + 1))

    def _finish(self, res: SearchResult) -> None:
        self.state = {n: "done" for n in res.order}
        if res.algorithm == "dijkstra":
            self.labels = {n: d for n, d in res.dist.items() if d < math.inf}
        self.hl_edges, self.active_edge = set(), None
        self.path_edges = {frozenset(p) for p in zip(res.path, res.path[1:])} if res.found else set()
        for n in res.path:
            self.state[n] = "path"
        self._redraw(); self._result_window(res)

    def _result_window(self, res: SearchResult) -> None:
        w = tk.Toplevel(self.root); w.title("Результат пошуку"); w.geometry("640x560")
        f = ttk.Frame(w, padding=14); f.pack(fill="both", expand=True)
        ttk.Label(f, text="Шлях: " + ("ЗНАЙДЕНО" if res.found else "НЕ ЗНАЙДЕНО"), font=("Segoe UI", 14, "bold"),
                  foreground="#1e8449" if res.found else "#c0392b").pack(anchor="w")
        ttk.Label(f, text=ALGORITHMS[res.algorithm][0], font=("Segoe UI", 10, "italic")).pack(anchor="w")
        ttk.Separator(f).pack(fill="x", pady=6)
        info = [("Відправна точка", self.start_combo.get()), ("Цільова точка", self.target_combo.get()),
                ("Відстань найкоротшого шляху, км" if res.algorithm == "dijkstra" else "Відстань знайденого шляху, км",
                 f"{res.distance:g}" if res.found else "—"),
                ("Кількість міст на шляху", str(len(res.path)) if res.found else "—"),
                ("Кількість циклів (розкритих вершин)", str(res.cycles)),
                ("Кількість перевірених ребер", str(res.relaxations)),
                ("Кількість поліпшень міток", str(res.improvements) if res.algorithm == "dijkstra" else "—"),
                ("Граф", f"{len(self.graph.pos)} міст, {len(self.graph.edges)} доріг"),
                ("Час пошуку", f"{res.time_ms:.4f} мс")]
        for a, b in info:
            row = ttk.Frame(f); row.pack(fill="x", pady=2)
            ttk.Label(row, text=a + ":", width=40).pack(side="left"); ttk.Label(row, text=b, font=("Segoe UI", 9, "bold")).pack(side="left")
        ttk.Separator(f).pack(fill="x", pady=6)
        ttk.Label(f, text="Маршрут (міста від відправної до цільової точки):").pack(anchor="w")
        t = tk.Text(f, height=9, wrap="word")
        if res.found:
            lines = [f"{res.path[0]}"]
            acc = 0.0
            for a, b in zip(res.path, res.path[1:]):
                wgt = self.graph.weight_between(a, b) or 0; acc += wgt
                lines.append(f"→ {b}  (+{wgt:g} км, разом {acc:g} км)")
            t.insert("1.0", "\n".join(lines))
        else:
            t.insert("1.0", "шлях відсутній")
        t.configure(state="disabled"); t.pack(fill="both")
        ttk.Button(f, text="Закрити", command=w.destroy).pack(anchor="e", pady=8)

    def compare(self) -> None:
        s, t = self.start_combo.get(), self.target_combo.get()
        w = tk.Toplevel(self.root); w.title("Порівняння алгоритмів"); w.geometry("1100x260")
        f = ttk.Frame(w, padding=10); f.pack(fill="both", expand=True)
        cols = ("Алгоритм", "Знайдено", "Відстань, км", "Міст на шляху", "Циклів", "Ребер перевірено", "Шлях")
        tv = ttk.Treeview(f, columns=cols, show="headings", height=3)
        for c, wd in zip(cols, (210, 80, 100, 100, 70, 120, 420)):
            tv.heading(c, text=c); tv.column(c, width=wd, anchor="w" if c in ("Алгоритм", "Шлях") else "center")
        for k, (nm, cls) in ALGORITHMS.items():
            r = cls(self.graph).search(s, t)
            tv.insert("", "end", values=(nm.split(" (")[0], "так" if r.found else "ні", f"{r.distance:g}" if r.found else "—",
                                         len(r.path) if r.found else "—", r.cycles, r.relaxations, " → ".join(r.path) if r.found else "—"))
        tv.pack(fill="both", expand=True)

    def all_dist(self) -> None:
        s = self.start_combo.get()
        r = DijkstraSearch(self.graph).search(s, "\0")
        w = tk.Toplevel(self.root); w.title(f"Відстані від «{s}»"); w.geometry("420x640")
        tv = ttk.Treeview(w, columns=("c", "d", "p"), show="headings")
        for c, t_, wd in (("c", "Місто", 150), ("d", "Відстань, км", 100), ("p", "Попередник", 150)):
            tv.heading(c, text=t_); tv.column(c, width=wd, anchor="w")
        for n, d in sorted(r.dist.items(), key=lambda kv: kv[1]):
            tv.insert("", "end", values=(n, f"{d:g}" if d < math.inf else "недосяжне", r.prev.get(n) or "—"))
        tv.pack(fill="both", expand=True)


def main() -> None:
    root = tk.Tk()
    try:
        s = ttk.Style()
        if "clam" in s.theme_names(): s.theme_use("clam")
    except Exception:
        pass
    DijkstraApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
