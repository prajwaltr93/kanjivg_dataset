#filename : extract_kanjivg.py
#author : PRAJWAL T R
#date last modified : Mon Oct 12 20:40:12 2020
#comments :

# imports
from os import walk
from svg.path import parse_path
import re

# constants and magic numbers
d_regex = re.compile(r'\sd="(.*)"/>') # find d attribute of path element
traverse_path = './kanji/'
offset_x = 4
offset_y = 4
out_path = './kanji_modified/'
m_line = " M %d, %d "
l_line = " L %d, %d "
svg_start_line = "<svg xmlns='http://www.w3.org/2000/svg' \nxmlns:xlink='http://www.w3.org/1999/xlink' \n"
min_x = 0
min_y = 0
WIDTH = 100
HEIGHT = 100
NUM_SEGMENTS = 3 # actual segments -= 1
step = 0.5 # intecrement t in terms of

# helper functions
def offset(x,y):
    # offset x, y to move image horizontally and vertically
    return(x-offset_x, y-offset_y)

def rem_dup(points):
    # remove redundant adjacent points
    se = []
    for ind in range(len(points)-1):
        if points[ind] != points[ind + 1]:
            se.append(points[ind])
    se.append(points[-1])
    return se

def write_stroke(point_list, write_fd):
    # remove duplicate cordinates
    point_list = rem_dup(point_list) # REMOVE adjacent duplicate
    # write line (x,y) and (x1, y1) using M L commands
    write_fd.write(m_line % point_list[0]) # first is M command
    for point in point_list[1:]:
        write_fd.write(l_line % point)
    point_list = [] # clear contents

# iterate over files
if __name__ == "__main__":
    _, _, filelist = next(walk(traverse_path))
    for file in filelist:
        svg_string = open(traverse_path + file, 'r')
        write_fd = open(out_path + file, 'w')
        # prep output svg file
        write_fd.write(svg_start_line) #write first line
        write_fd.write(f"viewBox = \'{min_x} {min_y} {WIDTH} {HEIGHT}\' >\n")
        d_paths = []
        # findall d paths in svg file
        for line in svg_string:
            d = d_regex.findall(line)
            if d: # if line has path with d attribute
                d_paths.append(re.sub(r'[.]\d+',r'', d[0])) # remove decimal part of cordinates

        # process d atttributes and convert bezeir curves to lines
        for d in d_paths:
            curve_objects = parse_path(d) # individual curve
            points = [ ]
            for curve in curve_objects[1:]: # ignore fist M command
                t = 0.0
                for x in range(0,NUM_SEGMENTS): # 0.0 <= t <= 1.0
                    p = curve.point(t)
                    points.append(offset(int(p.real), int(p.imag)))
                    t += step # step
            # write individual stroke in terms of path
            write_fd.write("<path d = '")
            write_stroke(points, write_fd)
            write_fd.write("' fill='none' stroke='black' />\n")
        # all strokes written
        write_fd.write("</svg>")
        write_fd.close()
