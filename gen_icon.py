import math
from PIL import Image, ImageDraw

SS = 4
S = 512 * SS
BG = (78, 27, 46, 255)      # #4E1B2E dark cherry
FG = (0, 0, 0, 255)
radius = 112 * SS

# --- W afilada estilo Zenix: polilínea con offset perpendicular, miter y puntas ---
P = [(112, 150), (196, 360), (256, 230), (316, 360), (400, 150)]  # nodos centro
HW = 30        # media-anchura del trazo
TIP = 30       # cuánto sobresalen las puntas de las puntas superiores
MITER_MAX = 120

def unit(ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy)
    return dx / L, dy / L

def offset_pts(side):
    # side=+1 una orilla, -1 la otra. Normal izquierda = (-dy,dx)
    segdir = [unit(*P[i], *P[i + 1]) for i in range(len(P) - 1)]
    segnrm = [(-d[1] * side, d[0] * side) for d in segdir]
    pts = []
    for i in range(len(P)):
        if i == 0:
            n = segnrm[0]
            pts.append((P[i][0] + n[0] * HW, P[i][1] + n[1] * HW))
        elif i == len(P) - 1:
            n = segnrm[-1]
            pts.append((P[i][0] + n[0] * HW, P[i][1] + n[1] * HW))
        else:
            # miter: interseccion de las dos orillas offset
            n1, n2 = segnrm[i - 1], segnrm[i]
            a = (P[i][0] + n1[0] * HW, P[i][1] + n1[1] * HW)
            d1 = segdir[i - 1]
            b = (P[i][0] + n2[0] * HW, P[i][1] + n2[1] * HW)
            d2 = segdir[i]
            # resolver a + t*d1 = b + s*d2
            den = d1[0] * (-d2[1]) - d1[1] * (-d2[0])
            if abs(den) < 1e-6:
                pts.append(a)
            else:
                t = ((b[0] - a[0]) * (-d2[1]) - (b[1] - a[1]) * (-d2[0])) / den
                mx, my = a[0] + d1[0] * t, a[1] + d1[1] * t
                # clamp longitud del miter
                vx, vy = mx - P[i][0], my - P[i][1]
                ml = math.hypot(vx, vy)
                if ml > MITER_MAX:
                    mx = P[i][0] + vx / ml * MITER_MAX
                    my = P[i][1] + vy / ml * MITER_MAX
                pts.append((mx, my))
    return pts

right = offset_pts(+1)
left = offset_pts(-1)

# apices puntiagudos en las dos puntas superiores
d0 = unit(*P[0], *P[1]); apex0 = (P[0][0] - d0[0] * TIP, P[0][1] - d0[1] * TIP)
d4 = unit(*P[4], *P[3]); apex4 = (P[4][0] - d4[0] * TIP, P[4][1] - d4[1] * TIP)

poly = [apex0] + right + [apex4] + left[::-1]
poly_ss = [(x * SS, y * SS) for x, y in poly]

img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle([0, 0, S - 1, S - 1], radius=radius, fill=BG)
d.polygon(poly_ss, fill=FG)

for size, name in [(512, "wzlab-icon-512.png"), (192, "wzlab-icon-192.png")]:
    img.resize((size, size), Image.LANCZOS).save(name)
    print("wrote", name)

flat = Image.new("RGBA", (S, S), BG)
ImageDraw.Draw(flat).polygon(poly_ss, fill=FG)
flat.resize((180, 180), Image.LANCZOS).convert("RGB").save("apple-touch-icon.png")
print("wrote apple-touch-icon.png")

# imprimir puntos para el SVG (escala 512)
print("SVG_POINTS=" + " ".join(f"{x:.1f},{y:.1f}" for x, y in poly))
