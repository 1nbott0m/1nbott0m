"""Render the profile animation. Requires Pillow; run from the repository root."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT
OUT.mkdir(exist_ok=True)
W, H = 1100, 660
BG = '#0d0d12'
PINK = '#E8A0BF'
WHITE = '#F1E9EE'
MUTED = '#ACA0AD'
FONT = next((p for p in [
    Path('/System/Library/Fonts/Menlo.ttc'),
    Path('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')
] if p.exists()), None)
if FONT is None:
    raise SystemExit('Install DejaVu Sans Mono or set FONT to a monospace font.')

def font(size):
    return ImageFont.truetype(str(FONT), size)

def text(draw, xy, value, size=20, fill=WHITE):
    draw.text(xy, value, font=font(size), fill=fill)

# Pixel emblem based on the user's reference: an outlined file with a sad face.
MASK = [
    '00111111100000', '00100000100000', '00100000111000',
    '00100000001000', '00101000101000', '00101000001000',
    '00100000001000', '00100111101000', '00101000101000',
    '00100000001000', '00111111111000', '00000000000000',
]

def frame(t):
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    # Deliberately quiet background: scan lines never cross the main text.
    for y in range(0, H, 5):
        d.line((0, y, W, y), fill='#111017')
    d.rounded_rectangle((22, 22, W-23, H-23), radius=18, fill=BG, outline='#44313F', width=2)
    d.line((23, 77, W-24, 77), fill='#44313F')
    for x, color in [(49, PINK), (70, '#886576'), (91, '#4C3A47')]:
        d.ellipse((x, 46, x+9, 55), fill=color)
    text(d, (120, 39), '1nbott0m@macbook  ~  /identity', 17, MUTED)
    text(d, (877, 39), 'LOCAL SESSION', 15, PINK)

    text(d, (55, 105), 'PERSONAL FILE  /  001', 16, PINK)
    text(d, (53, 135), '1nbott0m', 67)
    d.rectangle((57, 224, 104, 228), fill=PINK)
    text(d, (120, 215), 'YAN  /  INFORMATION SECURITY STUDENT', 20, PINK)

    # All actual bio information is inside the animation.
    rows = [
        ('FOCUS', 'Understanding security products'),
        ('LEARNING', 'Rust / Linux / Git'),
        ('LOCATION', 'Moscow / UTC+3'),
        ('DEVICE', 'MacBook Pro / Apple M2'),
        ('SYSTEM', 'macOS / 24 GB RAM / 1 TB SSD'),
    ]
    for idx, (label, value) in enumerate(rows):
        y = 289 + idx * 43
        text(d, (56, y), label, 17, MUTED)
        progress = min(1, max(0, (t - .55 - idx*.38) / .55))
        visible = value[:int(len(value) * progress)]
        text(d, (213, y-1), visible, 19)
        if 0 < progress < 1:
            x = 213 + d.textlength(visible, font=font(19))
            d.rectangle((x+3, y+2, x+12, y+22), fill=PINK)

    d.line((770, 280, 770, 501), fill='#332632')
    # Brief displacement on the decorative icon only.
    glitch = (t < .3 or 7.0 < t < 7.25 or 12 < t < 12.18)
    for yy, row in enumerate(MASK):
        offset = 5 if glitch and yy % 3 == 0 else 0
        for xx, pixel in enumerate(row):
            if pixel == '1':
                x, y = 827+xx*12+offset, 302+yy*12
                d.rectangle((x, y, x+9, y+9), fill=PINK if yy % 3 else '#BD809F')
    text(d, (833, 469), '[ KEEP LEARNING ]', 15, MUTED)
    d.rounded_rectangle((54, 540, 1045, 598), radius=7, fill='#18131B', outline='#3E2B3A')
    status = '> loading identity...' if t < 2.8 else '> learning in public. building from the inside.'
    text(d, (72, 558), status, 18, PINK)
    if int(t*2) % 2 == 0:
        x = 72+d.textlength(status, font=font(18))
        d.rectangle((x+10, 560, x+19, 580), fill=PINK)
    text(d, (56, 615), 'RUST  +  SYSTEMS  +  CURIOSITY', 12, MUTED)
    text(d, (872, 615), 'SIGNAL / ONLINE', 12, PINK)
    return im

if __name__ == '__main__':
    # 14-second loop with 10+ seconds of completely readable profile data.
    frames = [frame(i/10) for i in range(140)]
    frames[60].save(OUT / 'identity.png')
    palette = frames[60].quantize(colors=64)
    frames = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    frames[0].save(OUT / 'identity.gif', save_all=True, append_images=frames[1:],
                   duration=100, loop=0, optimize=True, disposal=1)
    print(f'Created {OUT / "identity.gif"}')
