from typing import Any
from tkinter import Tk, Canvas, mainloop, PhotoImage, TclError
from Map import Map
from Hub import Connection, Hub


class Graphics:
    __graphics: Any = None
    __nb_drones_at_hub: dict[str, int] = {}

    def __new__(cls) -> Any:
        if cls.__graphics is None:
            cls.__graphics = object.__new__(cls)
        return cls.__graphics

    @staticmethod
    def calculate_window(drone_map: Map, scale: int,
                         margin: int, radius: int) -> tuple[int, int]:
        """calculates the window size"""
        height: int = 0
        width: int = 0
        for hub in drone_map.hubs:
            hx = hub.x * scale + margin
            hy = hub.y * scale + margin
            if hx > width:
                width = hx
            if hy > height:
                height = hy
        return (height + radius + 15, width + radius + 15)

    @staticmethod
    def move(canvas: Canvas, id: int, cx: int, cy: int) -> None:
        """function for moving thee drones to de new space"""
        canvas.coords(id, cx, cy)

    def animate(
            self, root: Tk, canvas: Canvas, drone_map: Map, turn: int,
            turn_id: int, drone_ids: list[int],
            drone_text_ids: list[int], scale: int = 220, margin: int = 100,
            id_location: int = 58) -> None:
        """function for making the animation of the drones moving

        Args:
        - root (Tk): the root representing the tkinter object
        - canvas (Canvas): the window where the objects are gonna be displayed
        - turn (int): it represents the turn that is being played at the moment
        - turn_id (int): the id of the text that displays the turn
        - drone_ids (list[int]): the ids of the drones to be displayed
        - drone_text_ids (list[int]): the ids of the text that represent the
                                        id of the drones
        - scale (int): the scale of the objects
        - margin (int): margin to the edge of the window
        - id_location (int): a number for mocing the text representing the id
                            of the drone id texts

        This function iterates on the solution to make the animation of that
        solution by mocing the specified drones
        """
        ct = drone_map.constraint_tree
        solutions: list[tuple] = ct.solutions
        if turn == ct.cost + 1:
            return
        for drone, paths in solutions:
            if len(paths) == 0:
                continue
            if paths[0][1] != turn:
                continue
            path = paths.pop(0)
            dest_hub = drone_map.get_hub(path[0])
            actual_hub: Hub = path[2].other_hub(dest_hub)
            actual_hub.move_to(drone.get_id(), dest_hub)
            dest_id = self.__nb_drones_at_hub[dest_hub.name]
            canvas.itemconfig(dest_id, text=len(dest_hub.drones))
            if actual_hub.name != "Wait":
                actual_id = self.__nb_drones_at_hub[actual_hub.name]
                canvas.itemconfig(actual_id, text=len(actual_hub.drones))
            cx = dest_hub.x * scale + margin
            cy = dest_hub.y * scale + margin
            self.move(canvas, drone_ids[drone.get_id()], cx, cy)
            self.move(
                canvas, drone_text_ids[drone.get_id()],
                cx, cy + id_location)

        canvas.itemconfig(turn_id, text=f"Turn: {turn}")
        turn += 1
        root.after(1000, self.animate, root, canvas, drone_map,
                   turn, turn_id, drone_ids, drone_text_ids)

    def initialize_graphics(
            self, drone_map: Map, height: int = 700, width: int = 700,
            scale: int = 220, margin: int = 100, radius: int = 50) -> None:
        """Function for creating the graphic representation

        Args:
        - drone_map(Map): the map to be represented as graphics
        - height(int): the height of the window
        - width(int): the width of the window
        - scale(int): the scale of the objects
        - margin(int): margin to the edge of the window
        - radiuse(int): radius of the objects in the window to specify the size

        This function creates all the 3 essential objects to create the map:
        - the drones
        - the hubs
        - the connections

        And display them in a tkinter window and make the animation based on
        the solution the drone_map has
        """
        root = Tk()
        height, width = self.calculate_window(drone_map, scale, margin, radius)
        connections: set[Connection] = set()
        C = Canvas(root, bg="white", height=height, width=width)
        for hub in drone_map.hubs:
            cx = hub.x * scale + margin
            cy = hub.y * scale + margin
            try:
                C.create_oval(
                    cx - radius, cy - radius, cx + radius, cy + radius,
                    fill=hub.color, outline="grey")
            except TclError as e:
                print(f"{e}")
                C.create_oval(
                    cx - radius, cy - radius, cx + radius, cy + radius,
                    fill="grey", outline="grey")
            C.create_text(cx, cy - radius - 10,
                          text=hub.name, fill="black", font=("Arial", 8))
            nb_of_drones: int = C.create_text(cx, cy, text=len(hub.drones),
                                              fill="black", font=("Arial", 8))
            C.tag_raise(nb_of_drones)
            self.__nb_drones_at_hub.update(
                {hub.name: nb_of_drones})
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
        drones: list[int] = []
        drones_text: list[int] = []
        img = PhotoImage(file="drone.png")
        for i in range(drone_map.nb_drones):
            drone = C.create_image(
                drone_map.start_hub.x * scale + margin,
                drone_map.start_hub.y * scale + margin, image=img)
            C.tag_lower(drone)
            drones.append(drone)
            drone_text = C.create_text(
                drone_map.start_hub.x * scale + margin,
                drone_map.start_hub.y * scale + margin + radius + 8,
                text=f"id: {i} ", font=("Arial", 8))
            C.tag_raise(drone_text)
            drones_text.append(drone_text)
        turn_id: int = C.create_text(width/2, 15, text="Turn: 0")
        C.pack()
        root.after(500, self.animate, root, C,
                   drone_map, 0, turn_id, drones, drones_text, scale, margin)
        mainloop()
