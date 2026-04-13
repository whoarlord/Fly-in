from typing import Any
from tkinter import Tk, Canvas, mainloop
from Map import Map
from Hub import Connection


class Graphics:
    __graphics: Any = None
    __nb_drones_at_hub: list[int] = []

    def __new__(cls) -> Any:
        if cls.__graphics is None:
            cls.__graphics = object.__new__(cls)
        return cls.__graphics

    @staticmethod
    def calculate_window(drone_map: Map, scale, margin, radius) -> tuple[int]:
        height: int = 0
        width: int = 0
        for hub in drone_map.hubs:
            hx = hub.x * scale + margin
            hy = hub.y * scale + margin
            if hx > width:
                width = hx
            if hy > height:
                height = hy
        return tuple([height + radius + 15, width + radius + 15])

    def initialize_graphics(
            self, drone_map: Map, height=700, width=700, scale=220,
            margin=110, radius=50):
        root = Tk()
        height, width = self.calculate_window(drone_map, scale, margin, radius)
        connections: set[Connection] = set()
        C = Canvas(root, bg="white", height=height, width=width)
        for hub in drone_map.hubs:
            cx = hub.x * scale + margin
            cy = hub.y * scale + margin
            C.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                          fill=hub.color, outline="grey")
            C.create_text(cx, cy - radius - 10,
                          text=hub.name, fill="black", font=("Arial", 8))
            nb_of_drones: int = C.create_text(cx, cy, text=len(hub.drones),
                                              fill="black", font=("Arial", 8))
            C.tag_raise(nb_of_drones)
            self.__nb_drones_at_hub.append(nb_of_drones)
            connections |= set(hub.connections)
        for connection in connections:
            lx1 = connection.edge_1.x * scale + margin
            ly1 = connection.edge_1.y * scale + margin
            lx2 = connection.edge_2.x * scale + margin
            ly2 = connection.edge_2.y * scale + margin
            C.tag_lower(C.create_line(lx1, ly1, lx2, ly2, fill="black"))
            tx = (lx1 + lx2) / 2
            ty = (ly1 + ly2) / 2 - 15
            C.tag_raise(
                C.create_text(
                    tx, ty, text=f"capacity: {connection.max_link_capacity} ",
                    fill="#003087", font=("Arial", 8)))
        C.pack()
        mainloop()
