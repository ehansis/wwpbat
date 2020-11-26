"""White Wall Photo Book Alignment Tool"""

import sys
import shutil
import json
from pathlib import Path

from datetime import datetime


# ## Settings start ###

# Automatically make a timestamped backup of the project file before modifying it?
do_backup = True

# minimum spacing between pictures, in mm
spacing = 10

# margin around the page border in addition to picture spacing margin, in mm
page_margin = 5

# number of grid rectangles along horizontal and vertical axis (on a single page)
grid_n = 6

# preference for outer page edges in snapping (reduction of delta, in mm)
outer_pref = 5

# ## Settings end ###


# noinspection DuplicatedCode
def position_picture(element, page):
    # page properties (excluding margin)
    page_width = page["size"]["width"]
    page_height = page["size"]["height"]
    is_double_page = abs(page_width / page_height - 2) < 0.2

    grid_spacing_x = (page_width * (0.5 if is_double_page else 1) - 2 * page_margin) / grid_n
    grid_spacing_y = (page_height - 2 * page_margin) / grid_n

    # picture dimensions and outer edges
    width = element["size"]["width"]
    height = element["size"]["height"]
    left = element["position"]["x"] - 0.5 * width
    right = element["position"]["x"] + 0.5 * width
    top = element["position"]["y"] - 0.5 * height
    bottom = element["position"]["y"] + 0.5 * height
    aspect = element["picture"]["dimension"]["width"] / element["picture"]["dimension"]["height"]

    # boundaries of single page (depending on image position)
    page_t = page_margin
    page_b = page_height - page_margin
    if is_double_page:
        if element["position"]["x"] <= page_width / 2:
            page_l = page_margin
            page_r = page_width / 2 - page_margin
        else:
            page_l = page_width / 2 + page_margin
            page_r = page_width - page_margin
    else:
        page_l = page_margin
        page_r = page_width - page_margin

    # helper function: compute distance to next grid line (incl. margin) and snapping penalty
    def grid_delta(pos, grid_spacing, margin):
        line_n = int((pos + margin) / grid_spacing + 0.5)
        d = pos - line_n * grid_spacing
        penalty = abs(d + margin)
        if line_n == 0 or line_n == grid_n:
            penalty -= outer_pref
        return d, penalty

    # offsets from image edges to nearest grid lines;
    sp = spacing * 0.5
    grid_delta_l, penalty_l = grid_delta(left - page_l, grid_spacing_x, -sp)
    grid_delta_r, penalty_r = grid_delta(right - page_l, grid_spacing_x, sp)
    grid_delta_t, penalty_t = grid_delta(top - page_t, grid_spacing_y, -sp)
    grid_delta_b, penalty_b = grid_delta(bottom - page_t, grid_spacing_y, sp)

    # use dimension with lower total offset for image sizing, snap the other to top, bottom or center
    if (
        penalty_l + penalty_r
        <= penalty_t + penalty_b
    ):
        print(f"\tLaying out {element['id']} with horizontal sizing")
        left_new = left - grid_delta_l
        right_new = right - grid_delta_r
        width_new = right_new - left_new
        height_new = width_new / aspect

        delta_t = top - page_t - sp
        delta_b = bottom - page_b + sp
        page_center_y = 0.5 * (page_t + page_b)
        delta_center = element["position"]["y"] - page_center_y

        if abs(delta_center) < min(abs(delta_t), abs(delta_b)):
            top_new = page_center_y - 0.5 * height_new
            bottom_new = page_center_y + 0.5 * height_new
        elif abs(delta_t) < abs(delta_b):
            top_new = page_t
            bottom_new = top_new + height_new
        else:
            bottom_new = page_b
            top_new = bottom_new - height_new
    else:
        print(f"\tLaying out {element['id']} with vertical sizing")
        top_new = top - grid_delta_t
        bottom_new = bottom - grid_delta_b
        height_new = bottom_new - top_new
        width_new = aspect * height_new

        delta_l = left - page_l
        delta_r = right - page_r
        page_center_x = 0.5 * (page_l + page_r)
        delta_center = element["position"]["x"] - page_center_x

        if abs(delta_center) < min(abs(delta_l), abs(delta_r)):
            left_new = page_center_x - 0.5 * width_new
            right_new = page_center_x + 0.5 * width_new
        elif abs(delta_l) < abs(delta_r):
            left_new = page_l
            right_new = left_new + width_new
        else:
            right_new = page_r
            left_new = right_new - width_new

    # set element position, shrink image to apply margin (0.5 spacing on all sides)
    element["position"]["x"] = 0.5 * (left_new + right_new)
    element["position"]["y"] = 0.5 * (top_new + bottom_new)
    element["size"]["width"] = width_new - spacing
    element["size"]["height"] = height_new - spacing

    # remove any cropping
    if "cropping" in element:
        del element["cropping"]


if len(sys.argv) != 2:
    print("Usage: python wwpbat.py <project file>.json")
    exit(1)

project_path = Path(sys.argv[1])
assert project_path.exists(), f"Cannot find project file {project_path}!"

# parse the project
with open(project_path) as f:
    book = json.load(f)

# position the images, skip the first page (the cover)
for pg in book["pages"][1:]:
    for layer in pg["layers"]:
        for el in layer["elements"]:
            # only modify pictures
            if el["type"] == "PICTURE":
                position_picture(el, pg)


if do_backup:
    # make a backup
    backup_path = project_path.parent / (
        project_path.stem + f"___{str(datetime.now().timestamp())}{project_path.suffix}"
    )
    print(f"Backing up project file to {backup_path}")
    shutil.copy(project_path, backup_path)


# store output
with open(project_path, "w") as f:
    json.dump(book, f, indent=4)
