import math
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, simpledialog


# ================== Utility ==================

def float_input(entry, name):
    val = entry.get().strip()
    if val == "":
        raise ValueError
    try:
        return float(val)
    except ValueError:
        messagebox.showerror("Input Error", f"Please enter a valid number for {name}.")
        raise


# ================== Whiteboard (pen/erase/color/text) ==================

class WhiteboardFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        top_bar = ttk.Frame(self)
        top_bar.pack(side="top", fill="x", pady=2)

        self.mode_var = tk.StringVar(value="pen")
        ttk.Radiobutton(top_bar, text="Pen", value="pen", variable=self.mode_var).pack(side="left", padx=2)
        ttk.Radiobutton(top_bar, text="Eraser", value="eraser", variable=self.mode_var).pack(side="left", padx=2)
        ttk.Radiobutton(top_bar, text="Text", value="text", variable=self.mode_var).pack(side="left", padx=2)

        ttk.Label(top_bar, text="Color:").pack(side="left", padx=(10, 2))
        self.color_btn = ttk.Button(top_bar, text="Pick", command=self.choose_color)
        self.color_btn.pack(side="left", padx=2)

        ttk.Label(top_bar, text="Width:").pack(side="left", padx=(10, 2))
        self.width_scale = ttk.Scale(top_bar, from_=1, to=10, orient="horizontal")
        self.width_scale.set(2)
        self.width_scale.pack(side="left", padx=2)

        clear_btn = ttk.Button(top_bar, text="Clear", command=self.clear_board)
        clear_btn.pack(side="right", padx=4)

        self.canvas = tk.Canvas(self, bg="white", cursor="pencil")
        self.canvas.pack(fill="both", expand=True)

        self.old_x = None
        self.old_y = None
        self.pen_color = "black"

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def choose_color(self):
        color = colorchooser.askcolor(initialcolor=self.pen_color)[1]
        if color:
            self.pen_color = color

    def on_click(self, event):
        mode = self.mode_var.get()
        if mode == "text":
            # Ask text once at the click position
            text = simpledialog.askstring("Text", "Enter text:")
            if text:
                self.canvas.create_text(event.x, event.y, text=text,
                                        fill=self.pen_color, anchor="nw")
        else:
            self.old_x, self.old_y = event.x, event.y

    def on_drag(self, event):
        mode = self.mode_var.get()
        if mode == "text":
            return
        if self.old_x is not None and self.old_y is not None:
            width = self.width_scale.get()
            color = "white" if mode == "eraser" else self.pen_color
            self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                    fill=color, width=width,
                                    capstyle=tk.ROUND, smooth=True)
            self.old_x, self.old_y = event.x, event.y

    def on_release(self, event):
        self.old_x, self.old_y = None, None

    def clear_board(self):
        self.canvas.delete("all")


# ================== Preview canvas (2D/3D per shape) ==================

class ShapePreviewCanvas(tk.Canvas):
    def __init__(self, parent, width=400, height=400, bg="#050716", **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg,
                         highlightthickness=1, highlightbackground="#24253a", **kwargs)
        self.mode = "cube"  # default
        self.angle_x = 0.02
        self.angle_y = 0.03
        self.angle_z = 0.01

        s = 1
        self.cube_vertices = [
            [-s, -s, -s],
            [ s, -s, -s],
            [ s,  s, -s],
            [-s,  s, -s],
            [-s, -s,  s],
            [ s, -s,  s],
            [ s,  s,  s],
            [-s,  s,  s],
        ]
        self.cube_edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]

        self.after(30, self.animate)

    def set_shape(self, shape_key):
        # Map shape key to preview mode
        if shape_key in ("circle", "sector"):
            self.mode = "circle"
        elif shape_key in ("rectangle", "parallelogram", "trapezium"):
            self.mode = "rectangle"
        elif shape_key == "square":
            self.mode = "square"
        elif shape_key in ("ellipse",):
            self.mode = "ellipse"
        elif shape_key in ("Rhombus",):
            self.mode = "Rhombus"

        else:
            self.mode = "cube"  # default 3D-style preview

    def rotate(self, v, ax, ay, az):
        x, y, z = v
        cosx, sinx = math.cos(ax), math.sin(ax)
        y, z = y * cosx - z * sinx, y * sinx + z * cosx
        cosy, siny = math.cos(ay), math.sin(ay)
        x, z = x * cosy + z * siny, -x * siny + z * cosy
        cosz, sinz = math.cos(az), math.sin(az)
        x, y = x * cosz - y * sinz, x * sinz + y * cosz
        return [x, y, z]

    def project(self, v):
        w = int(self.cget("width"))
        h = int(self.cget("height"))
        fov = 200
        dist = 4
        x, y, z = v
        factor = fov / (dist + z)
        x = x * factor + w / 2
        y = -y * factor + h / 2
        return (x, y)

    def draw_cube(self):
        rotated = [self.rotate(v, self.angle_x, self.angle_y, self.angle_z) for v in self.cube_vertices]
        projected = [self.project(v) for v in rotated]
        for e in self.cube_edges:
            p1 = projected[e[0]]
            p2 = projected[e[1]]
            self.create_line(p1[0], p1[1], p2[0], p2[1], fill="#00ffcc", width=2)
        self.create_text(10, 10, anchor="nw", text="3D Solid Preview", fill="#ffffff",
                         font=("Segoe UI", 10))

    def draw_circle(self):
        w = int(self.cget("width"))
        h = int(self.cget("height"))
        r = min(w, h) * 0.3
        cx, cy = w // 2, h // 2
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         outline="#00ffcc", width=3)
        self.create_text(10, 10, anchor="nw", text="Circle Preview", fill="#ffffff",
                         font=("Segoe UI", 10))

    def draw_square(self):
        w = int(self.cget("width"))
        h = int(self.cget("height"))
        s = min(w, h) * 0.5
        cx, cy = w // 2, h // 2
        self.create_rectangle(cx - s/2, cy - s/2, cx + s/2, cy + s/2,
                              outline="#00ffcc", width=3)
        self.create_text(10, 10, anchor="nw", text="Square Preview", fill="#ffffff",
                         font=("Segoe UI", 10))

    def draw_rectangle(self):
        w = int(self.cget("width"))
        h = int(self.cget("height"))
        rw = w * 0.6
        rh = h * 0.4
        cx, cy = w // 2, h // 2
        self.create_rectangle(cx - rw/2, cy - rh/2, cx + rw/2, cy + rh/2,
                              outline="#00ffcc", width=3)
        self.create_text(10, 10, anchor="nw", text="Rectangle Preview", fill="#ffffff",
                         font=("Segoe UI", 10))

    def draw_ellipse(self):
        w = int(self.cget("width"))
        h = int(self.cget("height"))
        rw = w * 0.6
        rh = h * 0.4
        cx, cy = w // 2, h // 2
        self.create_oval(cx - rw/2, cy - rh/2, cx + rw/2, cy + rh/2,
                         outline="#00ffcc", width=3)
        self.create_text(10, 10, anchor="nw", text="Ellipse Preview", fill="#ffffff",
                         font=("Segoe UI", 10))
    
    def draw_Rhombus(self):
          w= int(self.cget("width"))
          w = int(self.cget("width"))
          h = int(self.cget("height"))
          rw = w * 0.6 
          rh = h * 0.4
          cx, cy = w // 2, h // 2

    # four points of a rhombus (diamond) centered at (cx, cy)
          points = [
        cx, cy - rh/2,   # top
        cx + rw/2, cy,   # right
        cx, cy + rh/2,   # bottom
        cx - rw/2, cy    # left
         ]

          self.create_polygon(
         points,
         outline="#00ffcc",
         width=3,
         fill=""  # or some color if you want it filled
          )
          self.create_text(10, 10, anchor="nw",
                     text="Rhombus Preview",
                     fill="#ffffff",
                     font=("Segoe UI", 10))


        
    def animate(self):
        self.delete("all")
        if self.mode == "circle":
            self.draw_circle()
        elif self.mode == "square":
            self.draw_square()
        elif self.mode == "rectangle":
            self.draw_rectangle()
        elif self.mode == "ellipse":
            self.draw_ellipse()
        elif self.mode=="Rhombus":
            self.draw_Rhombus()
        else:
            self.draw_cube()
        # rotate slightly only in cube mode
        if self.mode == "cube":
            self.angle_x += 0.01
            self.angle_y += 0.015
            self.angle_z += 0.008
        self.after(30, self.animate)


class RotatingCubeCanvas(tk.Canvas):
    def __init__(self, parent, width=400, height=400, bg="#050716", **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg,
                         highlightthickness=1, highlightbackground="#24253a", **kwargs)
        s = 1
        self.vertices = [
            [-s, -s, -s],
            [ s, -s, -s],
            [ s,  s, -s],
            [-s,  s, -s],
            [-s, -s,  s],
            [ s, -s,  s],
            [ s,  s,  s],
            [-s,  s,  s],
        ]
        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
        self.angle_x = 0.02
        self.angle_y = 0.03
        self.angle_z = 0.01
        self.after(30, self.animate)

    def rotate(self, v, ax, ay, az):
        x, y, z = v
        cosx, sinx = math.cos(ax), math.sin(ax)
        y, z = y * cosx - z * sinx, y * sinx + z * cosx
        cosy, siny = math.cos(ay), math.sin(ay)
        x, z = x * cosy + z * siny, -x * siny + z * cosy
        cosz, sinz = math.cos(az), math.sin(az)
        x, y = x * cosz - y * sinz, x * sinz + y * cosz
        return [x, y, z]

    def project(self, v):
        w = int(self.cget("width"))
        h = int(self.cget("height"))
        fov = 200
        dist = 4
        x, y, z = v
        factor = fov / (dist + z)
        x = x * factor + w / 2
        y = -y * factor + h / 2
        return (x, y)

    def animate(self):
        rotated = [self.rotate(v, self.angle_x, self.angle_y, self.angle_z) for v in self.vertices]
        projected = [self.project(v) for v in rotated]

        self.delete("all")
        for e in self.edges:
            p1 = projected[e[0]]
            p2 = projected[e[1]]
            self.create_line(p1[0], p1[1], p2[0], p2[1], fill="#00ffcc", width=2)
        self.create_text(10, 10, anchor="nw", text="3D Preview", fill="#ffffff",
                         font=("Segoe UI", 10))
        self.after(30, self.animate)


# ================== Shape Frames ==================

class CircleFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Circle", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self, text="Radius:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.radius_entry = ttk.Entry(self)
        self.radius_entry.grid(row=1, column=1, padx=5, pady=5)

        self.var_area = tk.BooleanVar(value=True)
        self.var_circ = tk.BooleanVar(value=True)
        self.var_diam = tk.BooleanVar(value=True)

        ttk.Checkbutton(self, text="Area", variable=self.var_area).grid(row=2, column=0, sticky="w", padx=5)
        ttk.Checkbutton(self, text="Circumference", variable=self.var_circ).grid(row=2, column=1, sticky="w", padx=5)
        ttk.Checkbutton(self, text="Diameter", variable=self.var_diam).grid(row=3, column=0, sticky="w", padx=5)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=4, column=0, columnspan=2, pady=10)
        self.output = tk.Text(self, height=6, width=40, state="disabled")
        self.output.grid(row=5, column=0, columnspan=2, pady=5, padx=5)

    def calculate(self):
        try:
            r = float_input(self.radius_entry, "radius")
        except ValueError:
            return
        lines = []
        if self.var_area.get():
            lines.append(f"Area = πr² = {math.pi * r ** 2:.4f}")
        if self.var_circ.get():
            lines.append(f"Circumference = 2πr = {2 * math.pi * r:.4f}")
        if self.var_diam.get():
            lines.append(f"Diameter = 2r = {2 * r:.4f}")
        self._show(lines)

    def _show(self, lines):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines) if lines else "Select at least one option.")
        self.output.config(state="disabled")


class RectangleFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Rectangle", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self, text="Length:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(self, text="Breadth:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.length_entry = ttk.Entry(self)
        self.breadth_entry = ttk.Entry(self)
        self.length_entry.grid(row=1, column=1, padx=5, pady=5)
        self.breadth_entry.grid(row=2, column=1, padx=5, pady=5)

        self.var_area = tk.BooleanVar(value=True)
        self.var_per = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Area", variable=self.var_area).grid(row=3, column=0, sticky="w", padx=5)
        ttk.Checkbutton(self, text="Perimeter", variable=self.var_per).grid(row=3, column=1, sticky="w", padx=5)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=4, column=0, columnspan=2, pady=10)
        self.output = tk.Text(self, height=6, width=40, state="disabled")
        self.output.grid(row=5, column=0, columnspan=2, pady=5, padx=5)

    def calculate(self):
        try:
            l = float_input(self.length_entry, "length")
            b = float_input(self.breadth_entry, "breadth")
        except ValueError:
            return
        lines = []
        if self.var_area.get():
            lines.append(f"Area = l × b = {l * b:.4f}")
        if self.var_per.get():
            lines.append(f"Perimeter = 2(l + b) = {2 * (l + b):.4f}")
        self._show(lines)

    def _show(self, lines):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines) if lines else "Select at least one option.")
        self.output.config(state="disabled")


class SquareFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Square", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self, text="Side:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.side_entry = ttk.Entry(self)
        self.side_entry.grid(row=1, column=1, padx=5, pady=5)

        self.var_area = tk.BooleanVar(value=True)
        self.var_per = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Area", variable=self.var_area).grid(row=2, column=0, sticky="w", padx=5)
        ttk.Checkbutton(self, text="Perimeter", variable=self.var_per).grid(row=2, column=1, sticky="w", padx=5)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=3, column=0, columnspan=2, pady=10)
        self.output = tk.Text(self, height=6, width=40, state="disabled")
        self.output.grid(row=4, column=0, columnspan=2, pady=5, padx=5)

    def calculate(self):
        try:
            a = float_input(self.side_entry, "side")
        except ValueError:
            return
        lines = []
        if self.var_area.get():
            lines.append(f"Area = a² = {a * a:.4f}")
        if self.var_per.get():
            lines.append(f"Perimeter = 4a = {4 * a:.4f}")
        self._show(lines)

    def _show(self, lines):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines) if lines else "Select at least one option.")
        self.output.config(state="disabled")


class RhombusFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Rhombus", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self, text="Diagonal 1:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(self, text="Diagonal 2:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(self, text="Side (for perimeter):").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.d1_entry = ttk.Entry(self)
        self.d2_entry = ttk.Entry(self)
        self.side_entry = ttk.Entry(self)
        self.d1_entry.grid(row=1, column=1, padx=5, pady=5)
        self.d2_entry.grid(row=2, column=1, padx=5, pady=5)
        self.side_entry.grid(row=3, column=1, padx=5, pady=5)

        self.var_area = tk.BooleanVar(value=True)
        self.var_per = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Area", variable=self.var_area).grid(row=4, column=0, sticky="w", padx=5)
        ttk.Checkbutton(self, text="Perimeter", variable=self.var_per).grid(row=4, column=1, sticky="w", padx=5)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=5, column=0, columnspan=2, pady=10)
        self.output = tk.Text(self, height=6, width=40, state="disabled")
        self.output.grid(row=6, column=0, columnspan=2, pady=5, padx=5)

    def calculate(self):
        lines = []
        try:
            if self.var_area.get():
                d1 = float_input(self.d1_entry, "diagonal 1")
                d2 = float_input(self.d2_entry, "diagonal 2")
                lines.append(f"Area = 1/2 d1 d2 = {0.5 * d1 * d2:.4f}")
            if self.var_per.get():
                a = float_input(self.side_entry, "side")
                lines.append(f"Perimeter = 4a = {4 * a:.4f}")
        except ValueError:
            return
        self._show(lines)

    def _show(self, lines):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines) if lines else "Select at least one option.")
        self.output.config(state="disabled")


class TriangleFrame(ttk.Frame):
    def float_input(entry, name):
     value = entry.get().strip()

     if not value:
            raise ValueError(f"{name} is empty")
     return float(value)
 
class TriangleFrame(ttk.Frame):
    import tkinter as tk
from tkinter import ttk
import math


def float_input(entry):
    return float(entry.get().strip())


class TriangleFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        ttk.Label(self, text="3D Triangle Calculator",
                  font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=10
        )

        # ---------- INPUTS ----------
        ttk.Label(self, text="Base:").grid(row=1, column=0, sticky="e")
        self.base_entry = ttk.Entry(self)
        self.base_entry.insert(0, "6")
        self.base_entry.grid(row=1, column=1)

        ttk.Label(self, text="Height:").grid(row=2, column=0, sticky="e")
        self.height_entry = ttk.Entry(self)
        self.height_entry.insert(0, "5")
        self.height_entry.grid(row=2, column=1)

        ttk.Label(self, text="Side a:").grid(row=3, column=0, sticky="e")
        ttk.Label(self, text="Side b:").grid(row=4, column=0, sticky="e")
        ttk.Label(self, text="Side c:").grid(row=5, column=0, sticky="e")

        self.a_entry = ttk.Entry(self)
        self.b_entry = ttk.Entry(self)
        self.c_entry = ttk.Entry(self)

        self.a_entry.insert(0, "6")
        self.b_entry.insert(0, "5")
        self.c_entry.insert(0, "7")

        self.a_entry.grid(row=3, column=1)
        self.b_entry.grid(row=4, column=1)
        self.c_entry.grid(row=5, column=1)

        ttk.Button(self, text="Calculate & Animate",
                   command=self.calculate_and_start)\
            .grid(row=6, column=0, columnspan=2, pady=8)

        # ---------- OUTPUT ----------
        self.output = tk.Text(self, height=6, width=38, state="disabled")
        self.output.grid(row=7, column=0, columnspan=2, pady=5)

        # ---------- CANVAS ----------
        self.canvas = tk.Canvas(self, width=300, height=220, bg="white")
        self.canvas.grid(row=0, column=2, rowspan=8, padx=10)

        # animation
        self.angle = 0
        self.running = False

    # ---------- DRAW 3D TRIANGLE ----------
    def draw_triangle_3d(self, base, height):
        self.canvas.delete("all")

        scale = 100 / max(base, height)
        b = base * scale
        h = height * scale
        depth = 40

        cx, cy = 150, 120
        dx = depth * math.cos(self.angle)
        dy = depth * math.sin(self.angle)

        # front
        x1, y1 = cx, cy - h/2
        x2, y2 = cx - b/2, cy + h/2
        x3, y3 = cx + b/2, cy + h/2

        # back
        x1b, y1b = x1 + dx, y1 + dy
        x2b, y2b = x2 + dx, y2 + dy
        x3b, y3b = x3 + dx, y3 + dy

        self.canvas.create_polygon(x1, y1, x2, y2, x3, y3,
                                   outline="blue", width=2)
        self.canvas.create_polygon(x1b, y1b, x2b, y2b, x3b, y3b,
                                   outline="gray", dash=(4, 2))

        self.canvas.create_line(x1, y1, x1b, y1b)
        self.canvas.create_line(x2, y2, x2b, y2b)
        self.canvas.create_line(x3, y3, x3b, y3b)

    # ---------- CALCULATE ----------
    def calculate_and_start(self):
        try:
            base = float_input(self.base_entry)
            height = float_input(self.height_entry)
            a = float_input(self.a_entry)
            b = float_input(self.b_entry)
            c = float_input(self.c_entry)
        except ValueError:
            return

        # calculations
        area = 0.5 * base * height
        perimeter = a + b + c

        # Heron's formula
        s = perimeter / 2
        val = s * (s-a) * (s-b) * (s-c)
        area_heron = math.sqrt(val) if val > 0 else 0

        # output
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert(
            "end",
            f"Area (½·b·h) = {area:.4f}\n"
            f"Perimeter = {perimeter:.4f}\n"
            f"Area (Heron) = {area_heron:.4f}"
        )
        self.output.config(state="disabled")

        # start animation
        self.running = True
        self.animate()

    # ---------- ANIMATION LOOP ----------
    def animate(self):
        if not self.running:
            return

        base = float_input(self.base_entry)
        height = float_input(self.height_entry)

        self.draw_triangle_3d(base, height)
        self.angle += 0.05

        self.after(50, self.animate)


# ---------- MAIN ----------
root = tk.Tk()
root.title("3D Triangle Calculator")

TriangleFrame(root).pack(padx=10, pady=10)

root.mainloop()



class PentagonFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Regular Pentagon", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self, text="Side:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(self, text="Apothem:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.side_entry = ttk.Entry(self)
        self.apo_entry = ttk.Entry(self)
        self.side_entry.grid(row=1, column=1, padx=5, pady=5)
        self.apo_entry.grid(row=2, column=1, padx=5, pady=5)

        self.var_area = tk.BooleanVar(value=True)
        self.var_per = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Area", variable=self.var_area).grid(row=3, column=0, sticky="w", padx=5)
        ttk.Checkbutton(self, text="Perimeter", variable=self.var_per).grid(row=3, column=1, sticky="w", padx=5)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=4, column=0, columnspan=2, pady=8)
        self.output = tk.Text(self, height=6, width=40, state="disabled")
        self.output.grid(row=5, column=0, columnspan=2, pady=5, padx=5)

    def calculate(self):
        lines = []
        try:
            side = float_input(self.side_entry, "side")
            apo = float_input(self.apo_entry, "apothem")
        except ValueError:
            return
        if self.var_area.get():
            area = 0.5 * (5 * side) * apo
            lines.append(f"Area = 1/2 · P · apothem = {area:.4f}")
        if self.var_per.get():
            per = 5 * side
            lines.append(f"Perimeter = 5a = {per:.4f}")
        self._show(lines)

    def _show(self, lines):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines) if lines else "Select at least one option.")
        self.output.config(state="disabled")


class CubeFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Cube", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self, text="Side:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.a_entry = ttk.Entry(self)
        self.a_entry.grid(row=1, column=1, padx=5, pady=5)

        self.var_tsa = tk.BooleanVar(value=True)
        self.var_vol = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Surface Area", variable=self.var_tsa).grid(row=2, column=0, sticky="w", padx=5)
        ttk.Checkbutton(self, text="Volume", variable=self.var_vol).grid(row=2, column=1, sticky="w", padx=5)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=3, column=0, columnspan=2, pady=8)
        self.output = tk.Text(self, height=6, width=40, state="disabled")
        self.output.grid(row=4, column=0, columnspan=2, pady=5, padx=5)

    def calculate(self):
        try:
            a = float_input(self.a_entry, "side")
        except ValueError:
            return
        lines = []
        if self.var_tsa.get():
            lines.append(f"TSA = 6a² = {6 * a * a:.4f}")
        if self.var_vol.get():
            lines.append(f"Volume = a³ = {a ** 3:.4f}")
        self._show(lines)

    def _show(self, lines):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines) if lines else "Select at least one option.")
        self.output.config(state="disabled")


class CuboidFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Cuboid", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self, text="Length:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(self, text="Breadth:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(self, text="Height:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.l_entry = ttk.Entry(self)
        self.b_entry = ttk.Entry(self)
        self.h_entry = ttk.Entry(self)
        self.l_entry.grid(row=1, column=1, padx=5, pady=5)
        self.b_entry.grid(row=2, column=1, padx=5, pady=5)
        self.h_entry.grid(row=3, column=1, padx=5, pady=5)

        self.var_tsa = tk.BooleanVar(value=True)
        self.var_vol = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Surface Area", variable=self.var_tsa).grid(row=4, column=0, sticky="w", padx=5)
        ttk.Checkbutton(self, text="Volume", variable=self.var_vol).grid(row=4, column=1, sticky="w", padx=5)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=5, column=0, columnspan=2, pady=8)
        self.output = tk.Text(self, height=6, width=40, state="disabled")
        self.output.grid(row=6, column=0, columnspan=2, pady=5, padx=5)

    def calculate(self):
        try:
            l = float_input(self.l_entry, "length")
            b = float_input(self.b_entry, "breadth")
            h = float_input(self.h_entry, "height")
        except ValueError:
            return
        lines = []
        if self.var_tsa.get():
            tsa = 2 * (l * b + b * h + h * l)
            lines.append(f"TSA = 2(lb + bh + hl) = {tsa:.4f}")
        if self.var_vol.get():
            lines.append(f"Volume = lbh = {l * b * h:.4f}")
        self._show(lines)

    def _show(self, lines):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines) if lines else "Select at least one option.")
        self.output.config(state="disabled")


class CylinderFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Cylinder", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self, text="Radius:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(self, text="Height:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.r_entry = ttk.Entry(self)
        self.h_entry = ttk.Entry(self)
        self.r_entry.grid(row=1, column=1, padx=5, pady=5)
        self.h_entry.grid(row=2, column=1, padx=5, pady=5)

        self.var_tsa = tk.BooleanVar(value=True)
        self.var_vol = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Surface Area (TSA)", variable=self.var_tsa).grid(row=3, column=0, sticky="w", padx=5)
        ttk.Checkbutton(self, text="Volume", variable=self.var_vol).grid(row=3, column=1, sticky="w", padx=5)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=4, column=0, columnspan=2, pady=8)
        self.output = tk.Text(self, height=6, width=40, state="disabled")
        self.output.grid(row=5, column=0, columnspan=2, pady=5, padx=5)

    def calculate(self):
        try:
            r = float_input(self.r_entry, "radius")
            h = float_input(self.h_entry, "height")
        except ValueError:
            return
        lines = []
        if self.var_tsa.get():
            tsa = 2 * math.pi * r * (r + h)
            lines.append(f"TSA = 2πr(r + h) = {tsa:.4f}")
        if self.var_vol.get():
            lines.append(f"Volume = πr²h = {math.pi * r * r * h:.4f}")
        self._show(lines)

    def _show(self, lines):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines) if lines else "Select at least one option.")
        self.output.config(state="disabled")


class SphereFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Sphere", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self, text="Radius:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.r_entry = ttk.Entry(self)
        self.r_entry.grid(row=1, column=1, padx=5, pady=5)

        self.var_sa = tk.BooleanVar(value=True)
        self.var_vol = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Surface Area", variable=self.var_sa).grid(row=2, column=0, sticky="w", padx=5)
        ttk.Checkbutton(self, text="Volume", variable=self.var_vol).grid(row=2, column=1, sticky="w", padx=5)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=3, column=0, columnspan=2, pady=8)
        self.output = tk.Text(self, height=6, width=40, state="disabled")
        self.output.grid(row=4, column=0, columnspan=2, pady=5, padx=5)

    def calculate(self):
        try:
            r = float_input(self.r_entry, "radius")
        except ValueError:
            return
        lines = []
        if self.var_sa.get():
            lines.append(f"Surface area = 4πr² = {4 * math.pi * r * r:.4f}")
        if self.var_vol.get():
            lines.append(f"Volume = 4/3 πr³ = {(4 / 3) * math.pi * r ** 3:.4f}")
        self._show(lines)

    def _show(self, lines):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines) if lines else "Select at least one option.")
        self.output.config(state="disabled")


class ConeFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Cone", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self, text="Radius:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(self, text="Height:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.r_entry = ttk.Entry(self)
        self.h_entry = ttk.Entry(self)
        self.r_entry.grid(row=1, column=1, padx=5, pady=5)
        self.h_entry.grid(row=2, column=1, padx=5, pady=5)

        self.var_tsa = tk.BooleanVar(value=True)
        self.var_vol = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Surface Area (TSA)", variable=self.var_tsa).grid(row=3, column=0, sticky="w", padx=5)
        ttk.Checkbutton(self, text="Volume", variable=self.var_vol).grid(row=3, column=1, sticky="w", padx=5)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=4, column=0, columnspan=2, pady=8)
        self.output = tk.Text(self, height=6, width=40, state="disabled")
        self.output.grid(row=5, column=0, columnspan=2, pady=5, padx=5)

    def calculate(self):
        try:
            r = float_input(self.r_entry, "radius")
            h = float_input(self.h_entry, "height")
        except ValueError:
            return
        lines = []
        l = math.sqrt(r * r + h * h)
        if self.var_tsa.get():
            tsa = math.pi * r * (r + l)
            lines.append(f"TSA = πr(r + l) (l={l:.4f}) = {tsa:.4f}")
        if self.var_vol.get():
            lines.append(f"Volume = 1/3 πr²h = {(math.pi * r * r * h / 3):.4f}")
        self._show(lines)

    def _show(self, lines):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines) if lines else "Select at least one option.")
        self.output.config(state="disabled")


class HemisphereFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Hemisphere", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self, text="Radius:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.r_entry = ttk.Entry(self)
        self.r_entry.grid(row=1, column=1, padx=5, pady=5)

        self.var_tsa = tk.BooleanVar(value=True)
        self.var_vol = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Surface Area (TSA)", variable=self.var_tsa).grid(row=2, column=0, sticky="w", padx=5)
        ttk.Checkbutton(self, text="Volume", variable=self.var_vol).grid(row=2, column=1, sticky="w", padx=5)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=3, column=0, columnspan=2, pady=8)
        self.output = tk.Text(self, height=6, width=40, state="disabled")
        self.output.grid(row=4, column=0, columnspan=2, pady=5, padx=5)

    def calculate(self):
        try:
            r = float_input(self.r_entry, "radius")
        except ValueError:
            return
        lines = []
        if self.var_tsa.get():
            lines.append(f"TSA = 3πr² = {3 * math.pi * r * r:.4f}")
        if self.var_vol.get():
            lines.append(f"Volume = 2/3 πr³ = {(2 / 3) * math.pi * r ** 3:.4f}")
        self._show(lines)

    def _show(self, lines):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines) if lines else "Select at least one option.")
        self.output.config(state="disabled")


class PrismFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Prism (Triangular base)", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self, text="Triangle base (b):").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(self, text="Triangle height:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(self, text="Prism height:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.b_entry = ttk.Entry(self)
        self.h_base_entry = ttk.Entry(self)
        self.h_prism_entry = ttk.Entry(self)
        self.b_entry.grid(row=1, column=1, padx=5, pady=2)
        self.h_base_entry.grid(row=2, column=1, padx=5, pady=2)
        self.h_prism_entry.grid(row=3, column=1, padx=5, pady=2)

        ttk.Label(self, text="Triangle side a:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(self, text="Triangle side b:").grid(row=5, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(self, text="Triangle side c:").grid(row=6, column=0, sticky="e", padx=5, pady=2)
        self.a_entry = ttk.Entry(self)
        self.b2_entry = ttk.Entry(self)
        self.c_entry = ttk.Entry(self)
        self.a_entry.grid(row=4, column=1, padx=5, pady=2)
        self.b2_entry.grid(row=5, column=1, padx=5, pady=2)
        self.c_entry.grid(row=6, column=1, padx=5, pady=2)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=7, column=0, columnspan=2, pady=8)
        self.output = tk.Text(self, height=7, width=40, state="disabled")
        self.output.grid(row=8, column=0, columnspan=2, pady=5, padx=5)

    def calculate(self):
        try:
            b = float_input(self.b_entry, "triangle base")
            h_base = float_input(self.h_base_entry, "triangle height")
            h_prism = float_input(self.h_prism_entry, "prism height")
            a1 = float_input(self.a_entry, "side a")
            a2 = float_input(self.b2_entry, "side b")
            a3 = float_input(self.c_entry, "side c")
        except ValueError:
            return
        base_area = 0.5 * b * h_base
        volume = base_area * h_prism
        per_base = a1 + a2 + a3
        tsa = 2 * base_area + per_base * h_prism
        lines = [
            f"Base area = 1/2·b·h = {base_area:.4f}",
            f"Volume = base_area·H = {volume:.4f}",
            f"TSA = 2·base_area + P_base·H = {tsa:.4f}",
        ]
        self._show(lines)

    def _show(self, lines):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines))
        self.output.config(state="disabled")


class PyramidFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Square Pyramid", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self, text="Base side (a):").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(self, text="Height (h):").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(self, text="Slant height (l):").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.a_entry = ttk.Entry(self)
        self.h_entry = ttk.Entry(self)
        self.l_entry = ttk.Entry(self)
        self.a_entry.grid(row=1, column=1, padx=5, pady=2)
        self.h_entry.grid(row=2, column=1, padx=5, pady=2)
        self.l_entry.grid(row=3, column=1, padx=5, pady=2)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=4, column=0, columnspan=2, pady=8)
        self.output = tk.Text(self, height=7, width=40, state="disabled")
        self.output.grid(row=5, column=0, columnspan=2, pady=5, padx=5)

    def calculate(self):
        try:
            a = float_input(self.a_entry, "base side")
            h = float_input(self.h_entry, "height")
            l = float_input(self.l_entry, "slant height")
        except ValueError:
            return
        base_area = a * a
        volume = (1 / 3) * base_area * h
        per_base = 4 * a
        tsa = base_area + 0.5 * per_base * l
        lines = [
            f"Base area = a² = {base_area:.4f}",
            f"Volume = 1/3·base_area·h = {volume:.4f}",
            f"TSA = base_area + 1/2·P_base·l = {tsa:.4f}",
        ]
        self._show(lines)

    def _show(self, lines):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines))
        self.output.config(state="disabled")


class TrapeziumFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Trapezium", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self, text="Parallel side a:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(self, text="Parallel side b:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(self, text="Height (h):").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.a_entry = ttk.Entry(self)
        self.b_entry = ttk.Entry(self)
        self.h_entry = ttk.Entry(self)
        self.a_entry.grid(row=1, column=1, padx=5, pady=2)
        self.b_entry.grid(row=2, column=1, padx=5, pady=2)
        self.h_entry.grid(row=3, column=1, padx=5, pady=2)

        ttk.Label(self, text="Side c:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(self, text="Side d:").grid(row=5, column=0, sticky="e", padx=5, pady=2)
        self.c_entry = ttk.Entry(self)
        self.d_entry = ttk.Entry(self)
        self.c_entry.grid(row=4, column=1, padx=5, pady=2)
        self.d_entry.grid(row=5, column=1, padx=5, pady=2)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=6, column=0, columnspan=2, pady=8)
        self.output = tk.Text(self, height=7, width=40, state="disabled")
        self.output.grid(row=7, column=0, columnspan=2, pady=5, padx=5)

    def calculate(self):
        try:
            a = float_input(self.a_entry, "side a")
            b = float_input(self.b_entry, "side b")
            h = float_input(self.h_entry, "height")
            c = float_input(self.c_entry, "side c")
            d = float_input(self.d_entry, "side d")
        except ValueError:
            return
        area = 0.5 * (a + b) * h
        per = a + b + c + d
        lines = [
            f"Area = 1/2(a + b)h = {area:.4f}",
            f"Perimeter = a + b + c + d = {per:.4f}",
        ]
        self._show(lines)

    def _show(self, lines):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines))
        self.output.config(state="disabled")


class ParallelogramFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Parallelogram", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self, text="Base:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(self, text="Height:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.base_entry = ttk.Entry(self)
        self.height_entry = ttk.Entry(self)
        self.base_entry.grid(row=1, column=1, padx=5, pady=2)
        self.height_entry.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(self, text="Side1:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(self, text="Side2:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        self.s1_entry = ttk.Entry(self)
        self.s2_entry = ttk.Entry(self)
        self.s1_entry.grid(row=3, column=1, padx=5, pady=2)
        self.s2_entry.grid(row=4, column=1, padx=5, pady=2)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=5, column=0, columnspan=2, pady=8)
        self.output = tk.Text(self, height=7, width=40, state="disabled")
        self.output.grid(row=6, column=0, columnspan=2, pady=5, padx=5)

    def calculate(self):
        try:
            base = float_input(self.base_entry, "base")
            height = float_input(self.height_entry, "height")
            s1 = float_input(self.s1_entry, "side1")
            s2 = float_input(self.s2_entry, "side2")
        except ValueError:
            return
        area = base * height
        per = 2 * (s1 + s2)
        lines = [
            f"Area = base·height = {area:.4f}",
            f"Perimeter = 2(side1 + side2) = {per:.4f}",
        ]
        self._show(lines)

    def _show(self, lines):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines))
        self.output.config(state="disabled")


class EllipseFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Ellipse", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self, text="Semi-major axis (a):").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(self, text="Semi-minor axis (b):").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.a_entry = ttk.Entry(self)
        self.b_entry = ttk.Entry(self)
        self.a_entry.grid(row=1, column=1, padx=5, pady=2)
        self.b_entry.grid(row=2, column=1, padx=5, pady=2)

        self.var_area = tk.BooleanVar(value=True)
        self.var_per = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Area", variable=self.var_area).grid(row=3, column=0, sticky="w", padx=5)
        ttk.Checkbutton(self, text="Approx. Perimeter", variable=self.var_per).grid(row=3, column=1, sticky="w", padx=5)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=4, column=0, columnspan=2, pady=8)
        self.output = tk.Text(self, height=6, width=40, state="disabled")
        self.output.grid(row=5, column=0, columnspan=2, pady=5, padx=5)

    def calculate(self):
        try:
            a = float_input(self.a_entry, "a")
            b = float_input(self.b_entry, "b")
        except ValueError:
            return
        lines = []
        if self.var_area.get():
            lines.append(f"Area = πab = {math.pi * a * b:.4f}")
        if self.var_per.get():
            peri = 2 * math.pi * math.sqrt((a * a + b * b) / 2)
            lines.append(f"Approx perimeter ≈ 2π√((a²+b²)/2) = {peri:.4f}")
        self._show(lines)

    def _show(self, lines):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines) if lines else "Select at least one option.")
        self.output.config(state="disabled")


class SectorFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Sector of Circle", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self, text="Radius:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(self, text="Angle (degrees):").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.r_entry = ttk.Entry(self)
        self.theta_entry = ttk.Entry(self)
        self.r_entry.grid(row=1, column=1, padx=5, pady=2)
        self.theta_entry.grid(row=2, column=1, padx=5, pady=2)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=3, column=0, columnspan=2, pady=8)
        self.output = tk.Text(self, height=7, width=40, state="disabled")
        self.output.grid(row=4, column=0, columnspan=2, pady=5, padx=5)

    def calculate(self):
        try:
            r = float_input(self.r_entry, "radius")
            theta = float_input(self.theta_entry, "angle")
        except ValueError:
            return
        area = (theta / 360) * math.pi * r * r
        arc = (theta / 360) * 2 * math.pi * r
        perim = 2 * r + arc
        lines = [
            f"Area = (θ/360)·πr² = {area:.4f}",
            f"Arc length = (θ/360)·2πr = {arc:.4f}",
            f"Perimeter of sector = 2r + arc = {perim:.4f}",
        ]
        self._show(lines)

    def _show(self, lines):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines))
        self.output.config(state="disabled")


class ParabolaFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Parabola (standard)", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self, text="a in y²=4ax or x²=4ay:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.a_entry = ttk.Entry(self)
        self.a_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Button(self, text="Calculate", command=self.calculate).grid(row=2, column=0, columnspan=2, pady=8)
        self.output = tk.Text(self, height=7, width=40, state="disabled")
        self.output.grid(row=3, column=0, columnspan=2, pady=5, padx=5)

    def calculate(self):
        try:
            a = float_input(self.a_entry, "a")
        except ValueError:
            return
        lines = [
            f"Focus (horizontal): (a, 0) = ({a:.4f}, 0)",
            f"Directrix (horizontal): x = {-a:.4f}",
            f"Latus rectum length = 4a = {4 * a:.4f}",
        ]
        self._show(lines)

    def _show(self, lines):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n".join(lines))
        self.output.config(state="disabled")

# ================== Main App ==================

class GeometryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Geometry Calculator - Dark Star Pro")
        self.geometry("1200x700")
        self.configure(bg="#02030a")

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#02030a")
        self.style.configure("TLabel", background="#02030a", foreground="#f0f0f0")
        self.style.configure("TButton", background="#141627", foreground="#f0f0f0")
        self.style.map("TButton", background=[("active", "#1e2140")])

        self.create_star_background()
        self.create_layout()

    def create_star_background(self):
        bg_canvas = tk.Canvas(self, bg="#02030a", highlightthickness=0)
        bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        import random
        for _ in range(140):
            x = random.randint(0, 1200)
            y = random.randint(0, 700)
            r = random.choice([1, 1, 2])
            color = random.choice(["#ffffff", "#a0c4ff", "#c4f1ff"])
            bg_canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")

        self.overlay = tk.Frame(self, bg="#02030a")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

    def create_layout(self):
        header = tk.Label(
            self.overlay,
            text="★ Geometry Calculator  ★",
            font=("Segoe UI", 45, "bold"),
            fg="#ecedf3",
            bg="#00139f",
        )
        header.pack(pady=10)

        subtitle = tk.Label(
            self.overlay,
            text="Aditya sharma",
            font=("Segoe UI", 10),
            fg="#000000",
            bg="#cdcdd0",
        )
        subtitle.pack(pady=2)

        main_frame = ttk.Frame(self.overlay)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        menu_frame = ttk.Frame(main_frame)
        menu_frame.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(menu_frame, text="Shapes", font=("Segoe UI", 12, "bold")).pack(pady=5)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True)

        self.tabs = ttk.Notebook(right_frame)
        self.tabs.pack(fill="both", expand=True)

        self.calc_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.calc_tab, text="Calculator")

        self.calc_left = ttk.Frame(self.calc_tab)
        self.calc_left.pack(side="left", fill="y", padx=10, pady=10)

        self.preview_canvas = ShapePreviewCanvas(self.calc_tab)
        self.preview_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.whiteboard_tab = WhiteboardFrame(self.tabs)
        self.tabs.add(self.whiteboard_tab, text="Whiteboard")

        self.current_shape_frame = None

        def add_btn(name, key, cmd):
            btn = ttk.Button(menu_frame, text=name,
                             command=lambda: (self.preview_canvas.set_shape(key), cmd()))
            btn.pack(fill="x", pady=2)

        # 2D shapes
        add_btn("Circle", "circle", self.show_circle)
        add_btn("Rectangle", "rectangle", self.show_rectangle)
        add_btn("Square", "square", self.show_square)
        add_btn("Rhombus", "rhombus", self.show_rhombus)
        add_btn("Triangle", "triangle", self.show_triangle)
        add_btn("Pentagon", "pentagon", self.show_pentagon)
        add_btn("Parallelogram", "parallelogram", self.show_parallelogram)
        add_btn("Trapezium", "trapezium", self.show_trapezium)
        add_btn("Ellipse", "ellipse", self.show_ellipse)
        add_btn("Sector", "sector", self.show_sector)
        add_btn("Parabola", "parabola", self.show_parabola)

        ttk.Label(menu_frame, text="3D Solids", font=("Segoe UI", 12, "bold")).pack(pady=(10, 4))
        add_btn("Cube", "cube", self.show_cube)
        add_btn("Cuboid", "cuboid", self.show_cuboid)
        add_btn("Cylinder", "cylinder", self.show_cylinder)
        add_btn("Sphere", "sphere", self.show_sphere)
        add_btn("Cone", "cone", self.show_cone)
        add_btn("Hemisphere", "hemisphere", self.show_hemisphere)
        add_btn("Prism", "prism", self.show_prism)
        add_btn("Pyramid", "pyramid", self.show_pyramid)

        # Default
        self.preview_canvas.set_shape("circle")
        self.show_circle()

    def clear_current_shape_frame(self):
        if self.current_shape_frame is not None:
            self.current_shape_frame.destroy()
            self.current_shape_frame = None

    # Show methods (same as before; just call frames)
    def show_circle(self):
        self.clear_current_shape_frame()
        self.current_shape_frame = CircleFrame(self.calc_left)
        self.current_shape_frame.pack(fill="both", expand=True)

    def show_rectangle(self):
        self.clear_current_shape_frame()
        self.current_shape_frame = RectangleFrame(self.calc_left)
        self.current_shape_frame.pack(fill="both", expand=True)

    def show_square(self):
        self.clear_current_shape_frame()
        self.current_shape_frame = SquareFrame(self.calc_left)
        self.current_shape_frame.pack(fill="both", expand=True)

    def show_rhombus(self):
        self.clear_current_shape_frame()
        self.current_shape_frame = RhombusFrame(self.calc_left)
        self.current_shape_frame.pack(fill="both", expand=True)

    def show_triangle(self):
        self.clear_current_shape_frame()
        self.current_shape_frame = TriangleFrame(self.calc_left)
        self.current_shape_frame.pack(fill="both", expand=True)

    def show_pentagon(self):
        self.clear_current_shape_frame()
        self.current_shape_frame = PentagonFrame(self.calc_left)
        self.current_shape_frame.pack(fill="both", expand=True)

    def show_cube(self):
        self.clear_current_shape_frame()
        self.current_shape_frame = CubeFrame(self.calc_left)
        self.current_shape_frame.pack(fill="both",expand=True)

    def show_cuboid(self):
        self.clear_current_shape_frame()
        self.current_shape_frame = CuboidFrame(self.calc_left)
        self.current_shape_frame.pack(fill="both",expand=True)

    def show_cylinder(self):
        self.clear_current_shape_frame()
        self.current_shape_frame = CylinderFrame(self.calc_left)
        self.current_shape_frame.pack(fill="both",expand=True)

    def show_sphere(self):
        self.clear_current_shape_frame()
        self.current_shape_frame = SphereFrame(self.calc_left)
        self.current_shape_frame.pack(fill="both",expand=True)

    def show_cone(self):
        self.clear_current_shape_frame()
        self.current_shape_frame = ConeFrame(self.calc_left)
        self.current_shape_frame.pack(fill="both",expand=True)

    def show_hemisphere(self):
        self.clear_current_shape_frame()
        self.current_shape_frame = HemisphereFrame(self.calc_left)
        self.current_shape_frame.pack(fill="both",expand=True)

    def show_prism(self):
        self.clear_current_shape_frame()
        self.current_shape_frame = PrismFrame(self.calc_left)
        self.current_shape_frame.pack(fill="both",expand=True)

    def show_pyramid(self):
        self.clear_current_shape_frame()
        self.current_shape_frame = PyramidFrame(self.calc_left)
        self.current_shape_frame.pack(fill="both",expand=True)

    def show_trapezium(self):
        self.clear_current_shape_frame()
        self.current_shape_frame = TrapeziumFrame(self.calc_left)
        self.current_shape_frame.pack(fill="both",expand=True)

    def show_parallelogram(self):
        self.clear_current_shape_frame()
        self.current_shape_frame = ParallelogramFrame(self.calc_left)
        self.current_shape_frame.pack(fill="both",expand=True)

    def show_ellipse(self):
        self.clear_current_shape_frame()
        self.current_shape_frame = EllipseFrame(self.calc_left)
        self.current_shape_frame.pack(fill="both",expand=True)

    def show_sector(self):
        self.clear_current_shape_frame()
        self.current_shape_frame = SectorFrame(self.calc_left)
        self.current_shape_frame.pack(fill="both",expand=True)

    def show_parabola(self):
        self.clear_current_shape_frame()
        self.current_shape_frame = ParabolaFrame(self.calc_left)
        self.current_shape_frame.pack(fill="both",expand=True)


if __name__ == "__main__":
    app = GeometryApp()
    app.mainloop()
