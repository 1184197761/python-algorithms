import numpy as np
import math
import re
import matplotlib.pyplot as plt
import matplotlib.patches as pth
import shapely.geometry.polygon as plg
import copy as cp


class module():
    def __init__(self, id, bound, ports):
        self.id = id
        self.bound = bound
        self.ports = ports


class linkNet():
    def __init__(self, id, ports):
        self.id = id
        self.ports = ports


def update():
    for mod in mods.values():
        shift = np.random.randint(-50, 50, 2)
        mirror = np.random.randint(2)
        angle = np.random.randint(4)
        center = np.mean(mod.bound, 0)
        if shift.all():
            mod.bound = [vertex+shift for vertex in mod.bound]
            mod.ports = [[vertex+shift for vertex in port]
                         for port in mod.ports]
        if mirror:
            mod.bound = [2*center-vertex for vertex in mod.bound]
            mod.ports = [[2*center-vertex for vertex in port]
                         for port in mod.ports]
        if angle:
            mod.bound = [rotate(vertex, center, angle) for vertex in mod.bound]
            mod.ports = [[rotate(vertex, center, angle) for vertex in port]
                         for port in mod.ports]


def rotate(vertex, center, angle):
    rad = -math.radians(angle*90)
    sin, cos = np.sin(rad), np.cos(rad)
    dx, dy = vertex-center
    return center + [cos*dx-sin*dy, cos*dy+sin*dx]


def checkOverlap():
    for index, mod1 in enumerate(mods.values()):
        shmod1 = plg.Polygon(mod1.bound)
        for mod2 in list(mods.values())[index+1:]:
            shmod2 = plg.Polygon(mod2.bound)
            if shmod1.intersection(shmod2):
                print('重叠模块：', mod1.id, '-', mod2.id)


def readMods():
    modInfo = 'contest_cases/Ports_area_etc_input_1.txt'
    mods = {}
    mod = module(None, [], [])
    with open(modInfo, 'r') as file:
        for line in reversed(file.readlines()):
            match re.match('\w', line).group():
                case 'P':
                    port = [float(match.group())
                            for match in re.finditer('-?\d+\.\d', line)]
                    mod.ports.append(np.reshape(port, (-1, 2)))
                case 'B':
                    bound = [float(match.group())
                             for match in re.finditer('-?\d+\.\d', line)]
                    mod.bound = np.reshape(bound, (-1, 2))
                case 'M':
                    mod.id = int(re.search('\d+', line).group())
                    mods[mod.id] = cp.copy(mod)
                    mod.ports = []
                # case 'A':
                #     area = [float(match.group())
                #             for match in re.finditer('-?\d+\.\d', line)]
    return mods


def readLinks():
    linkInfo = 'contest_cases/Ports_link_input.txt_1.txt'
    links = []
    link = linkNet(None, [])
    with open(linkInfo, 'r') as file:
        for line in file:
            match re.match('\D', line).group():
                case 'L':
                    link.id = int(re.search('\d+', line).group())
                case 'M':
                    modIds = [int(match.group())
                              for match in re.finditer('\d+', line)]
                    portIds = [int(match.group())
                               for match in re.finditer('\d', file.readline())]
                    for modId, portId in zip(modIds, portIds):
                        port = mods[modId].ports[portId-1]
                        link.ports.append(port)
                    links.append(cp.copy(link))
                    link.ports = []
    return links


def plotLinks():
    for link in links:
        netCenter = np.mean(np.concatenate(link.ports), 0)
        color = np.random.rand(3)
        for port in link.ports:
            portCenter = np.mean(port, 0)
            x = [netCenter[0], portCenter[0]]
            y = [netCenter[1], portCenter[1]]
            axes.plot(x, y, color=color)
        x, y = netCenter
        axes.text(x, y, link.id, color=color)


def plotMods():
    for mod in mods.values():
        poly = pth.Polygon(mod.bound)
        poly.set_color('white')
        axes.add_patch(poly)
        for port in mod.ports:
            poly = pth.Polygon(port)
            poly.set_color(np.random.rand(4))
            axes.add_patch(poly)
        x, y = np.mean(mod.bound, 0)
        circle = pth.Circle((x, y))
        axes.add_patch(circle)
        axes.text(x, y, mod.id)


def plotRect():
    vertexs = [vertex for mod in mods.values() for vertex in mod.bound]
    vertexs = np.array(vertexs)
    vertex1, vertex2 = vertexs.min(axis=0), vertexs.max(axis=0)
    xy, [width, height] = vertex1, vertex2-vertex1
    axes.add_patch(pth.Rectangle(xy, width, height))

    # area = np.reshape(area, (-1, 2))
    # LDx, LDy = area.min(axis=0)
    # RUx, RUy = area.max(axis=0)
    # axes.set_xbound(LDx, RUx)
    # axes.set_ybound(LDy, RUy)

    return width*height


if __name__ == '__main__':
    mods = readMods()
    links = readLinks()
    figure = plt.figure()

    axes = figure.add_subplot(121, aspect='equal')
    orgArea = plotRect()
    plotMods()
    plotLinks()

    update()
    checkOverlap()

    axes = figure.add_subplot(122, aspect='equal')
    newArea = plotRect()
    plotMods()
    plotLinks()

    print('版图面积：%d->%d' % (orgArea, newArea))
    plt.show()
