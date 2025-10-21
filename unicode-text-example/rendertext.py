#!/usr/bin/env python3
# rendertext.py
# Render a single-line input into a black bitmap (max 720x1280) with white text,
# using Noto Sans SemiBold at nominal 48px. Lines wrap at spaces; if a single word
# is wider than the allowed line width it will be broken between characters.

from PIL import Image, ImageDraw, ImageFont
import os
import sys
import argparse

MAX_W, MAX_H = 720, 1280
MIN_IMG_W, MIN_IMG_H = 640, 320
DEFAULT_FONT_SIZE = 48
MIN_FONT_SIZE = 24 # vision models do poorly at very small sizes
MARGIN = 15
LINE_SPACING_FACTOR = 0.18  # fraction of font size added to each line

def load_semibold_font(base_dir, size):
    path = os.path.join(base_dir, "static", "NotoSans-SemiBold.ttf")
    return ImageFont.truetype(path, size)

def wrap_single_line(text, draw, font, avail_width):
    """Wrap a single-line input so no word extends past avail_width.
    Break words between characters if they are individually longer than avail_width."""
    if avail_width <= 0:
        return [text]  # fallback
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        if cur == "":
            candidate = w
        else:
            candidate = cur + " " + w
        bbox = draw.textbbox((0,0), candidate, font=font)
        if bbox[2] - bbox[0] <= avail_width:
            cur = candidate
        else:
            # candidate doesn't fit
            if cur:  # flush current line
                lines.append(cur)
                cur = ""
            # Now place w: if w fits on its own, put it as new cur; else break w into pieces
            bbox_w = draw.textbbox((0,0), w, font=font)
            if bbox_w[2] - bbox_w[0] <= avail_width:
                cur = w
            else:
                # break w into char-chunks that fit
                chunk = ""
                for ch in w:
                    test = chunk + ch
                    if draw.textbbox((0,0), test, font=font)[2] - draw.textbbox((0,0), test, font=font)[0] <= avail_width:
                        chunk = test
                    else:
                        if chunk == "":  # single char doesn't fit (shouldn't happen), force it
                            lines.append(ch)
                        else:
                            lines.append(chunk)
                            chunk = ch
                if chunk:
                    cur = chunk
    if cur != "":
        lines.append(cur)
    # preserve trailing single-space behavior: if input had trailing space, keep an empty line? not necessary here
    return lines

def measure_lines(lines, draw, font):
    ascent, descent = font.getmetrics()
    line_height = ascent + descent + int(font.size * LINE_SPACING_FACTOR)
    max_w = 0
    for L in lines:
        bbox = draw.textbbox((0,0), L or " ", font=font)
        w_px = bbox[2] - bbox[0]
        if w_px > max_w: max_w = w_px
    total_h = line_height * len(lines)
    return max_w, total_h, line_height

def make_text_image(text):
    """ Make an image containing the given text as per above """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_size = DEFAULT_FONT_SIZE

    # We will attempt to fit; if too tall, downsize until MIN_FONT_SIZE, else truncate last line with ellipsis.
    while True:
        font = load_semibold_font(base_dir, font_size)
        tmp = Image.new("RGB", (10,10))
        draw_tmp = ImageDraw.Draw(tmp)
        avail_w = MAX_W - 2 * MARGIN
        lines = wrap_single_line(text, draw_tmp, font, avail_w)
        measured_w, measured_h, line_h = measure_lines(lines, draw_tmp, font)
        img_w = min(MAX_W, measured_w + 2 * MARGIN)
        img_h = measured_h + 2 * MARGIN

        if img_h <= MAX_H or font_size <= MIN_FONT_SIZE:
            break
        font_size -= 2

    # If still too tall, truncate lines and add ellipsis on last line
    if img_h > MAX_H:
        max_lines = max(1, (MAX_H - 2 * MARGIN) // line_h)
        lines = lines[:max_lines]
        # add ellipsis, shortening last line as needed
        last = lines[-1]
        ell = "…"
        tmp = Image.new("RGB", (10,10))
        draw_tmp = ImageDraw.Draw(tmp)
        while draw_tmp.textbbox((0,0), last + ell, font=font)[2] - draw_tmp.textbbox((0,0), last + ell, font=font)[0] > avail_w:
            if not last:
                last = ""
                break
            last = last[:-1]
        lines[-1] = last + ell
        measured_w, measured_h, line_h = measure_lines(lines, draw_tmp, font)
        img_w = min(MAX_W, measured_w + 2 * MARGIN)
        img_h = min(MAX_H, measured_h + 2 * MARGIN)

    # The safer checker dislikes images that are too small, so make sure it's big enough
    if img_w < MIN_IMG_W:
        img_w = MIN_IMG_W
    if img_h < MIN_IMG_H:
        img_h = MIN_IMG_H
    img = Image.new("RGB", (int(img_w), int(img_h)), "black")
    draw = ImageDraw.Draw(img)
    y = MARGIN
    for L in lines:
        draw.text((MARGIN, y), L, font=font, fill="white")
        y += line_h
    # frame the text, to make sure de-letterboxing doesn't cut down the size below the minimum
    draw.rectangle([0, 0, img_w-1, img_h-1], fill=None, outline=(128, 192, 64, 255))

    return img

def render(text, out_path="out.png"):
    img = make_text_image(text)
    img.save(out_path)
    return out_path

def main():
    """ usage: rendertext.py [-o filename.png] 'Some input text' """
    p = argparse.ArgumentParser()
    p.add_argument("text", nargs="?", help="Text to render; if omitted, read from stdin")
    p.add_argument("-o", "--out", default="out.png")
    args = p.parse_args()
    if args.text:
        text = args.text
    else:
        text = sys.stdin.read().rstrip("\n")
    out = render(text, args.out)
    print(out)

if __name__ == "__main__":
    main()

