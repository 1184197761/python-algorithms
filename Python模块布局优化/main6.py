import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib.patches as pth
import shapely.geometry.polygon as plg
# import copy


class Link():
    def __init__(self):
        self.ports = []


class Module():  # 模块类
    def __init__(self):
        self.bound = []  # 模块边界
        self.ports = []  # 模块端口列表
        self.size = []
        self.lowLeft = []


class Level():
    def __init__(self, start, end, height):
        self.x = [start, end]
        self.y = height


def updateMods():  # 更新模块
    levels = [Level(0, 400, 0)]  # 水平线段列表
    minLevel = levels[0]  # 最低水平线段
    minDex = 0  # 最低水平线段索引
    ordMods = [modules[id+1] for id in range(16)]
    for module in ordMods:
        length = minLevel.x[1]-minLevel.x[0]
        width, height = module.size
        lowLeft = module.lowLeft
        while length < min(width, height):  # 当最低水平线长小于矩形宽度
            leftH = levels[minDex-1].y if minDex > 0 else np.inf  # 相邻水平线段高度
            rightH = levels[minDex+1].y if minDex < len(levels)-1 else np.inf
            if leftH < rightH:  # 左邻线段低于右邻线段
                levels[minDex-1].x[1] = minLevel.x[1]  # 延长线段长度
            else:
                levels[minDex+1].x[0] = minLevel.x[0]
            levels.remove(minLevel)  # 移除最低水平线段
            minLevel = min(levels, key=lambda level: level.y)  # 获取最低水平线段
            length = minLevel.x[1]-minLevel.x[0]
            minDex = levels.index(minLevel)  # 获取最低水平线段索引
        if length > height > width or width > length > height:
            pivot = lowLeft+[width/2, width/2]  # 获取旋转点使旋转后左下顶点不变
            for vertex in module.bound:
                vertex[:] = rotateVertex(vertex, pivot, 1)  # 旋转模块90°
            for port in module.ports:
                for vertex in port:
                    vertex[:] = rotateVertex(vertex, pivot, 1)  # 旋转端口90°
            width, height = height, width
        shift = [minLevel.x[0], minLevel.y] - lowLeft  # 获取偏移量
        module.bound = [vertex+shift for vertex in module.bound]  # 移动模块边界
        for port in module.ports:
            for vertex in port:
                vertex += shift  # 移动端口
        newLevel = Level(minLevel.x[0], minLevel.x[0]+width, minLevel.y +
                         height)  # 获取新水平线段
        minLevel.x[0] += width  # 最低水平线段从左缩短
        levels.insert(minDex, newLevel)  # 插入新水平线段到最低水平线段前
        minDex += 1  # 最低水平线段索引自增


def rotateVertex(vertex, center, angle):  # 旋转顶点
    rad = -np.radians(angle*90)  # 旋转角度转弧度
    sin, cos = np.sin(rad), np.cos(rad)  # 正余弦值
    dx, dy = vertex-center  # 顶点-中心点偏移量
    return center+[cos*dx-sin*dy, cos*dy+sin*dx]  # 返回新顶点


def checkOverlap():  # 检查重叠
    for index, [id1, module1] in enumerate(modules.items()):  # 遍历模块列表
        polygon1 = plg.Polygon(module1.bound)  # 根据模块1边界创建多边形1
        for id2, module2 in list(modules.items())[index+1:]:  # 遍历未遍历模块列表
            polygon2 = plg.Polygon(module2.bound)  # 根据模块2边界创建多边形2
            if polygon1.intersection(polygon2):  # 若两多边形存在交叉区域
                print('重叠模块：', id1, '-', id2)


def readMods():  # 读取模块信息
    moduleInfo = 'contest_cases/Ports_Area_etc_input_1.txt'  # 模块文件名
    with open(moduleInfo, 'r') as file:  # 以只读方式打开模块文件
        # # 替代方案
        # module = Module(None)  # 初始化模块类对象
        # for line in reversed(file.readlines()):  # 倒序遍历文本行
        #     match re.match('\w', line).group():  # 匹配第一个字母
        #         case 'P':  # Port开头
        #             bound = [float(match.group())  # 获取边界数据
        #                      for match in re.finditer('-?\d+\.\d', line)]
        #             port = Port(np.reshape(bound, (-1, 2)))  # 格式化为边界以创建端口类对象
        #             module.ports.append(port)  # 添加端口到模块
        #         case 'B':  # Boundary开头
        #             bound = [float(match.group())  # 获取边界数据
        #                      for match in re.finditer('-?\d+\.\d', line)]
        #             module.bound = np.reshape(bound, (-1, 2))  # 格式化为模块边界
        #         case 'M':  # Module开头
        #             module.id = int(re.search('\d+', line).group())  # 获取模块编号
        #             modules[module.id] = copy.copy(module)  # 以模块编号为键浅拷贝到模块字典
        #             module.ports = []  # 清空模块端口
        for line in file:  # 遍历文本行
            if re.match('M', line):  # 跳至Module行
                module = Module()  # 初始化模块
                id = int(re.search('\d+', line).group())
                bound = [float(match.group())  # 获取边界数据
                         for match in re.finditer('-?\d+\.\d', file.readline())]
                vertexs = np.reshape(bound, (-1, 2))
                lowLeft, topRight = vertexs.min(axis=0), vertexs.max(axis=0)
                module.bound = vertexs  # 格式化为模块边界
                module.size = topRight - lowLeft
                module.lowLeft = lowLeft
                for _ in range(3):  # 遍历端口数据
                    bound = [float(match.group())  # 获取边界数据
                             for match in re.finditer('-?\d+\.\d', file.readline())]
                    # 格式化为端口边界以创建端口类对象并添加到模块
                    module.ports.append(np.reshape(bound, (-1, 2)))
                modules[id] = module  # 以模块编号为键添加模块到模块字典


def readLinks():  # 获取线网信息
    linkInfo = 'contest_cases/Ports_link_input.txt_1.txt'  # 线网文件名
    with open(linkInfo, 'r') as file:  # 以只读方式打开线网文件
        for _ in file:
            # # 替代方案
            # match re.match('\D', line).group():  # 匹配非数字字符
            #     case 'L':  # Link开头
            #         linkId = int(re.search('\d+', line).group())  # 获取线网编号
            #     case 'M':  # Mx开头
            #         modIds = [int(match.group())  # 获取模块编号列表
            #                   for match in re.finditer('\d+', line)]
            #         portIds = [int(match.group())  # 获取端口编号列表
            #                    for match in re.finditer('\d', file.readline())]
            #         for modId, portId in zip(modIds, portIds):  # 遍历模块-端口列表
            #             # 绑定线网编号到对应的模块端口
            #             modules[modId].ports[3-portId].linkId = linkId
            link = Link()
            modIds = [int(match.group())  # 获取模块编号列表
                      for match in re.finditer('\d+', file.readline())]
            portIds = [int(match.group())  # 获取端口编号列表
                       for match in re.finditer('\d', file.readline())]
            for modId, portId in zip(modIds, portIds):  # 遍历模块-端口列表
                link.ports.append(modules[modId].ports[portId-1])  # 绑定模块端口到线网
            links.append(link)


def plotLinks():  # 绘制线网
    length = 0  # 线网总长
    for index, link in enumerate(links):  # 遍历线网列表
        nx, ny = np.mean(np.concatenate(link.ports), 0)  # 获取线网中心点
        rands = np.random.rand(3)  # 随机数列表
        for port in link.ports:  # 遍历线网端口
            px, py = np.mean(port, 0)  # 获取端口中心点
            axes.plot([nx, px], [ny, py], color=rands)  # 绘制随机颜色的线网分支
            length += ((nx-px)**2+(ny-py)**2)**0.5  # 添加走线长度到线网总长
        axes.text(nx, ny, index+1, color=rands)  # 打印相同颜色的线网编号
    return length  # 返回线网总长


def plotMods():  # 绘制模块
    vertexs = [vertex for module in modules.values()
               for vertex in module.bound]  # 获取所有模块顶点列表
    vertexs = np.array(vertexs)  # 顶点列表转np数组
    lowLeft, topRight = vertexs.min(axis=0), vertexs.max(axis=0)  # 获取对角坐标
    width, height = topRight-lowLeft  # 获取矩形宽高
    axes.add_patch(pth.Rectangle(lowLeft, width, height))  # 添加矩形
    for id, module in modules.items():  # 遍历模块列表
        poly = pth.Polygon(module.bound, color='white')  # 根据模块边界创建白色多边形
        axes.add_patch(poly)  # 添加多边形
        for port in module.ports:  # 遍历模块端口列表
            # 根据端口边界创建随机颜色多边形
            poly = pth.Polygon(port, color=np.random.rand(4))
            axes.add_patch(poly)  # 添加多边形
        x, y = np.mean(module.bound, 0)  # 获取模块中心点
        axes.add_patch(pth.Circle((x, y)))  # 添加模块圆点
        axes.text(x, y, id)  # 打印模块编号
    return width*height  # 返回矩形面积


if __name__ == '__main__':
    modules = {}  # 模块字典
    links = []
    levels = []
    readMods()  # 读取模块
    readLinks()  # 读取线网
    figure = plt.figure()  # 画布
    axes = figure.add_subplot(121, aspect=1)  # 子图1
    orgS = plotMods()  # 初始版图面积
    orgL = plotLinks()  # 初始线网长度
    updateMods()  # 更新模块
    checkOverlap()  # 检查重叠
    axes = figure.add_subplot(122, aspect=1)  # 子图2
    newS = plotMods()  # 最终版图面积
    newL = plotLinks()  # 最终线网总长
    print('版图面积新旧比：%d/%d=%.2f' % (newS, orgS, newS/orgS))
    print('线网总长新旧比：%d/%d=%.2f' % (newL, orgL, newL/orgL))
    plt.show()  # 显示画布
