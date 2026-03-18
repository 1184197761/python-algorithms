import numpy as np
import re
import math
import matplotlib.pyplot as plt
import matplotlib.patches as pth
import shapely.geometry.polygon as plg
# import copy


class Module():
    def __init__(self, id):
        self.id = id
        self.bound = []
        self.ports = []


class Port():
    def __init__(self, bound):
        self.bound = bound
        self.linkId = None


def updateMods():
    for module in modules.values():
        shift = np.random.randint(-50, 50, 2)
        mirror = np.random.randint(2)
        angle = np.random.randint(4)
        center = np.mean(module.bound, 0)
        if shift.all():
            module.bound = [vertex+shift for vertex in module.bound]
            for port in module.ports:
                port.bound = [vertex+shift for vertex in port.bound]
        if mirror:
            module.bound = [2*center-vertex for vertex in module.bound]
            for port in module.ports:
                port.bound = [2*center-vertex for vertex in port.bound]
        if angle:
            module.bound = [rotateVertex(vertex, center, angle)
                            for vertex in module.bound]
            for port in module.ports:
                port.bound = [rotateVertex(vertex, center, angle)
                              for vertex in port.bound]


def rotateVertex(vertex, center, angle):
    rad = -math.radians(angle*90)
    sin, cos = np.sin(rad), np.cos(rad)
    dx, dy = vertex-center
    return center + [cos*dx-sin*dy, cos*dy+sin*dx]


def checkOverlap():
    for index, module1 in enumerate(modules.values()):
        shmodule1 = plg.Polygon(module1.bound)
        for module2 in list(modules.values())[index+1:]:
            shmodule2 = plg.Polygon(module2.bound)
            if shmodule1.intersection(shmodule2):
                print('重叠模块：', module1.id, '-', module2.id)


def readMods():
    moduleInfo = 'contest_cases/Ports_area_etc_input_1.txt'
    # module = Module()
    # with open(moduleInfo, 'r') as file:
    #     for line in reversed(file.readlines()):
    #         match re.match('\w', line).group():
    #             case 'P':
    #                 bound = [float(match.group())
    #                          for match in re.finditer('-?\d+\.\d', line)]
    #                 port = Port(np.reshape(bound, (-1, 2)))
    #                 module.ports.append(port)
    #             case 'B':
    #                 bound = [float(match.group())
    #                          for match in re.finditer('-?\d+\.\d', line)]
    #                 module.bound = np.reshape(bound, (-1, 2))
    #             case 'M':
    #                 module.id = int(re.search('\d+', line).group())
    #                 modules[module.id] = copy.copy(module)
    #                 module.ports = []
    with open(moduleInfo, 'r') as file:
        for line in file:
            if not re.match('M', line):
                continue
            module = Module(int(re.search('\d+', line).group()))
            bound = [float(match.group())
                     for match in re.finditer('-?\d+\.\d', file.readline())]
            module.bound = np.reshape(bound, (-1, 2))
            for _ in range(3):
                bound = [float(match.group())
                         for match in re.finditer('-?\d+\.\d', file.readline())]
                module.ports.append(Port(np.reshape(bound, (-1, 2))))
            modules[module.id] = module


def readLinks():
    linkInfo = 'contest_cases/Ports_link_input.txt_1.txt'
    with open(linkInfo, 'r') as file:
        for line in file:
            # match re.match('\D', line).group():
            #     case 'L':
            #         linkId = int(re.search('\d+', line).group())
            #     case 'M':
            #         moduleIds = [int(match.group())
            #                         for match in re.finditer('\d+', line)]
            #         portIds = [int(match.group())
            #                     for match in re.finditer('\d', file.readline())]
            #         for moduleId, portId in zip(moduleIds, portIds):
            #             modules[moduleId].ports[3-portId].link = linkId
            linkId = int(re.search('\d+', line).group())
            moduleIds = [int(match.group())
                         for match in re.finditer('\d+', file.readline())]
            portIds = [int(match.group())
                       for match in re.finditer('\d', file.readline())]
            for moduleId, portId in zip(moduleIds, portIds):
                modules[moduleId].ports[portId-1].linkId = linkId


def plotLinks():
    links = [[] for _ in range(8)]
    for module in modules.values():
        for port in module.ports:
            if port.linkId:
                links[port.linkId-1].append(port.bound)
    for index, link in enumerate(links):
        netCenter = np.mean(np.concatenate(link), 0)
        rands = np.random.rand(3)
        for port in link:
            portCenter = np.mean(port, 0)
            x = [netCenter[0], portCenter[0]]
            y = [netCenter[1], portCenter[1]]
            axes.plot(x, y, color=rands)
        x, y = netCenter
        axes.text(x, y, index+1, color=rands)


def plotMods():
    for module in modules.values():
        poly = pth.Polygon(module.bound)
        poly.set_color('white')
        axes.add_patch(poly)
        for port in module.ports:
            poly = pth.Polygon(port.bound)
            poly.set_color(np.random.rand(4))
            axes.add_patch(poly)
        x, y = np.mean(module.bound, 0)
        circle = pth.Circle((x, y))
        axes.add_patch(circle)
        axes.text(x, y, module.id)


def plotRect():
    vertexs = [vertex for module in modules.values()
               for vertex in module.bound]
    vertexs = np.array(vertexs)
    vertex1, vertex2 = vertexs.min(axis=0), vertexs.max(axis=0)
    xy, [width, height] = vertex1, vertex2-vertex1
    axes.add_patch(pth.Rectangle(xy, width, height))

    return width*height


if __name__ == '__main__':
    modules = {}
    readMods()
    readLinks()
    figure = plt.figure()
    axes = figure.add_subplot(121, aspect=1)
    orgArea = plotRect()
    plotMods()
    plotLinks()
    updateMods()
    checkOverlap()
    axes = figure.add_subplot(122, aspect=1)
    newArea = plotRect()
    plotMods()
    plotLinks()
    print('版图面积前后比：%.2f' % (newArea/orgArea))
    plt.show()
