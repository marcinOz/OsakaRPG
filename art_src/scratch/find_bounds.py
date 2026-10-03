from PIL import Image
im = Image.open('art_src/reference.jpg').convert('RGB')
W, H = im.size
px = im.load()

def bright_cyan(p):
    r, g, b = p
    return g > 150 and b > 150 and r > 100 and (r + g + b) > 450

approx = {
    'danny': (30, 165, 145, 295), 'alior': (355, 165, 475, 295), 'lisu': (680, 165, 800, 295),
    'barti': (30, 355, 145, 485), 'oziem': (355, 355, 475, 485), 'luki': (680, 355, 800, 485),
}
for k, (x0, y0, x1, y1) in approx.items():
    cols = []
    for x in range(x0, x1):
        c = sum(bright_cyan(px[x, y]) for y in range(y0, y1))
        cols.append((c, x))
    rows = []
    for y in range(y0, y1):
        c = sum(bright_cyan(px[x, y]) for x in range(x0, x1))
        rows.append((c, y))
    cs = sorted(cols, reverse=True)[:6]
    rs = sorted(rows, reverse=True)[:6]
    print(k, 'cols', sorted([x for c, x in cs]), [c for c, x in cs], 'rows', sorted([y for c, y in rs]), [c for c, y in rs])
