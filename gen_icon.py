from PIL import Image, ImageDraw

SS = 4  # supersample factor
S = 512 * SS
BG = (77, 10, 20, 255)      # #4D0A14 dark cherry
FG = (0, 0, 0, 255)         # negra
radius = 112 * SS
sw = 56 * SS                # stroke width
r = sw // 2                 # round cap/join radius

img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# rounded square background
d.rounded_rectangle([0, 0, S - 1, S - 1], radius=radius, fill=BG)

# W polyline points (scaled)
pts = [(120, 168), (192, 352), (256, 236), (320, 352), (392, 168)]
pts = [(x * SS, y * SS) for x, y in pts]

# draw segments
for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
    d.line([(x1, y1), (x2, y2)], fill=FG, width=sw)

# round caps/joins via circles at each vertex
for (x, y) in pts:
    d.ellipse([x - r, y - r, x + r, y + r], fill=FG)

# downsample (rounded, transparent corners) — para favicon / uso en la web
for size, name in [(512, "wzlab-icon-512.png"), (192, "wzlab-icon-192.png")]:
    img.resize((size, size), Image.LANCZOS).save(name)
    print("wrote", name)

# apple-touch-icon: cuadrado OPACO full-bleed (iOS aplica su propio redondeo)
flat = Image.new("RGBA", (S, S), BG)
df = ImageDraw.Draw(flat)
for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
    df.line([(x1, y1), (x2, y2)], fill=FG, width=sw)
for (x, y) in pts:
    df.ellipse([x - r, y - r, x + r, y + r], fill=FG)
flat.resize((180, 180), Image.LANCZOS).convert("RGB").save("apple-touch-icon.png")
print("wrote apple-touch-icon.png")
