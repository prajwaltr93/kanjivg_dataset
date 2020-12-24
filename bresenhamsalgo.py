#filename : bresenhamsalgo.py
#author : PRAJWAL T R
#date last modified : Mon Jul  13 11:09:55 2020
#comments :

'''
    given two points generates intermediate points with range +2, -2
'''

def getPoints(x0, y0, x1, y1):
    point_list = [] # final point list to return

    # if slope is negative
    def plotLineLow(x0,y0, x1,y1):
        dx = x1 - x0
        dy = y1 - y0
        yi = 1
        if dy < 0 :
            yi = -1
            dy = -dy
        D = 2*dy - dx # accumulate error
        y = y0

        for x in range(x0, x1 +1):
            point_list.append([x, y])
            if D > 0:
                y = y + yi
                D = D - 2*dx
            D = D + 2*dy

    # if slope is positive
    def plotLineHigh(x0,y0, x1,y1):
        dx = x1 - x0
        dy = y1 - y0
        xi = 1
        if dx < 0 :
            xi = -1
            dx = -dx
        D = 2*dx - dy # accumulate error
        x = x0

        for y in range(y0, y1+1):
            point_list.append([x, y])
            if D > 0:
                x = x + xi
                D = D - 2*dy
            D = D + 2*dx

    if abs(y1 - y0) < abs(x1 - x0):
        if x0 > x1:
            plotLineLow(x1, y1, x0, y0)
            point_list = point_list[::-1]
        else:
            plotLineLow(x0, y0, x1, y1)
    else:
        if y0 > y1 :
            plotLineHigh(x1, y1, x0, y0)
            point_list = point_list[::-1]
        else :
            plotLineHigh(x0, y0, x1, y1)

    if len(point_list) % 2 == 0: # if even number of points exist, then append last point
        return [point_list[i] for i in range(0, len(point_list),2)] + [point_list[-1]]
    return [point_list[i] for i in range(0, len(point_list), 2)] # else stride with step 2 skipping intermediate points and return
