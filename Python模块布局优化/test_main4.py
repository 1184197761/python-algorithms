import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib.patches as pth
import shapely.geometry.polygon as plg
# import copy


class Module():  # 模块类
    def __init__(self, id):
        self.id = id  # 模块编号
        self.bound = []  # 模块边界
        self.ports = []  # 模块端口列表


class Port():  # 端口类
    def __init__(self, bound):
        self.bound = bound  # 端口边界
        self.linkId = None  # 端口线网编号


def updateMods():  # 更新模块
    for module in modules.values():  # 遍历模块值列表
        shift = np.random.randint(-50, 50, 2)  # 偏移量
        mirror = np.random.randint(2)  # 镜像量
        angle = np.random.randint(4)  # 旋转量
        center = np.mean(module.bound, 0)  # 中心点
        Mirror[module.id-1] = mirror   # 保存镜像量
        Angle[module.id-1] = angle     # 保存旋转量
        if shift.all():  # 若偏移量非零
            module.bound = [vertex+shift for vertex in module.bound]  # 移动模块
            for port in module.ports:  # 遍历模块端口
                port.bound = [vertex+shift for vertex in port.bound]  # 移动端口
        if mirror:  # 若镜像量非零
            module.bound = [[2*center[0]-x, y] for [x, y] in module.bound]  # 镜像模块
            for port in module.ports:
                port.bound = [[2*center[0]-x, y] for [x, y] in port.bound]  # 镜像端口
        if angle:  # 若旋转量非零
            module.bound = [rotateVertex(vertex, center, angle)
                            for vertex in module.bound]  # 旋转模块
            for port in module.ports:
                port.bound = [rotateVertex(vertex, center, angle)
                              for vertex in port.bound]  # 旋转端口
        center = np.mean(module.bound, 0)
        Center[module.id-1][0] = center[0]   # 保存中心点x位置
        Center[module.id-1][1] = center[1]   # 保存中心点y位置
    return Mirror, Angle, Center


def rotateVertex(vertex, center, angle):  # 旋转顶点
    rad = -np.radians(angle*90)  # 旋转角度转弧度
    sin, cos = np.sin(rad), np.cos(rad)  # 正余弦值
    dx, dy = vertex-center  # 顶点-中心点偏移量
    return center+[cos*dx-sin*dy, cos*dy+sin*dx]  # 返回新顶点

def saveresult(Mirror, Angle, Center):  # 保存更新模块结果
    file = open("result1.txt", 'w')
    sortmodule = np.zeros(len(modules))
    for module in modules.values():  # 模块列表排序
        sortmodule[module.id-1] = module.id
    for module_num in sortmodule:  # 遍历模块序号
        module_num = int(module_num)
        file.write("Module:" + str(module_num) + "\n")
        if Mirror[module_num-1]:    # 镜像
            if Angle[module_num-1] == 0:
                file.write("Orient:" + "MX")
            elif Angle[module_num-1] == 1:
                file.write("Orient:" + "MXR90")
            elif Angle[module_num-1] == 2:
                file.write("Orient:" + "MY")
            elif Angle[module_num-1] == 3:
                file.write("Orient:" + "MYR90")
        else:   # 无镜像
            file.write("Orient:" + "R" + str(int(Angle[module_num-1]*90)))
        file.write("\n")
        file.write("Offset:" + str(Center[module_num-1]))
        file.write("\n")
        file.write("\n")


def checkOverlap():  # 检查重叠
    for index, module1 in enumerate(modules.values()):  # 遍历模块列表
        polygon1 = plg.Polygon(module1.bound)  # 根据模块1边界创建多边形1
        for module2 in list(modules.values())[index+1:]:  # 遍历未遍历模块列表
            polygon2 = plg.Polygon(module2.bound)  # 根据模块2边界创建多边形2
            if polygon1.intersection(polygon2):  # 若两多边形存在交叉区域
                print('重叠模块：', module1.id, '-', module2.id)


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
                module = Module(int(re.search('\d+', line).group()))  # 初始化模块
                bound = [float(match.group())  # 获取边界数据
                         for match in re.finditer('-?\d+\.\d', file.readline())]
                module.bound = np.reshape(bound, (-1, 2))  # 格式化为模块边界
                for _ in range(3):  # 遍历端口数据
                    bound = [float(match.group())  # 获取边界数据
                             for match in re.finditer('-?\d+\.\d', file.readline())]
                    # 格式化为端口边界以创建端口类对象并添加到模块
                    module.ports.append(Port(np.reshape(bound, (-1, 2))))
                modules[module.id] = module  # 以模块编号为键添加模块到模块字典


def readLinks():  # 获取线网信息
    linkInfo = 'contest_cases/Ports_link_input.txt_1.txt'  # 线网文件名
    with open(linkInfo, 'r') as file:  # 以只读方式打开线网文件
        for line in file:
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
            linkId = int(re.search('\d+', line).group())  # 获取线网编号
            modIds = [int(match.group())  # 获取模块编号列表
                      for match in re.finditer('\d+', file.readline())]
            portIds = [int(match.group())  # 获取端口编号列表
                       for match in re.finditer('\d', file.readline())]
            for modId, portId in zip(modIds, portIds):  # 遍历模块-端口列表
                modules[modId].ports[portId-1].linkId = linkId  # 绑定线网编号到模块端口


def plotLinks():  # 绘制线网
    links = [[] for _ in range(8)]  # 线网列表
    length = 0  # 线网总长
    for module in modules.values():  # 遍历模块列表
        for port in module.ports:  # 遍历端口列表
            if port.linkId:  # 若端口已绑定线网编号
                links[port.linkId-1].append(port.bound)  # 添加端口边界到对应线网
    for index, link in enumerate(links):  # 遍历线网列表
        nx, ny = np.mean(np.concatenate(link), 0)  # 获取线网中心点
        rands = np.random.rand(3)  # 随机数列表
        for port in link:  # 遍历线网端口
            px, py = np.mean(port, 0)  # 获取端口中心点
            axes.plot([nx, px], [ny, py], color=rands)  # 绘制随机颜色的线网分支
            length += ((nx-px)**2+(ny-py)**2)**0.5  # 添加走线长度到线网总长
        axes.text(nx, ny, index+1, color=rands)  # 打印相同颜色的线网编号
    return length  # 返回线网总长


def plotMods():  # 绘制模块
    for module in modules.values():  # 遍历模块列表
        poly = pth.Polygon(module.bound, color='white')  # 根据模块边界创建白色多边形
        axes.add_patch(poly)  # 添加多边形
        for port in module.ports:  # 遍历模块端口列表
            # 根据端口边界创建随机颜色多边形
            poly = pth.Polygon(port.bound, color=np.random.rand(4))
            axes.add_patch(poly)  # 添加多边形
        x, y = np.mean(module.bound, 0)  # 获取模块中心点
        axes.add_patch(pth.Circle((x, y)))  # 添加模块圆点
        axes.text(x, y, module.id)  # 打印相同颜色的模块编号


def plotRect():  # 绘制最小矩形
    vertexs = [vertex for module in modules.values()
               for vertex in module.bound]  # 获取所有模块顶点列表
    vertexs = np.array(vertexs)  # 顶点列表转np数组
    vertex1, vertex2 = vertexs.min(axis=0), vertexs.max(axis=0)  # 获取对角坐标
    width, height = vertex2-vertex1  # 获取矩形宽高
    axes.add_patch(pth.Rectangle(vertex1, width, height))  # 添加矩形
    return width*height  # 返回矩形面积


if __name__ == '__main__':
    modules = {}  # 模块字典
    readMods()  # 读取模块
    readLinks()  # 读取线网

    Mirror = np.zeros(len(modules))     # 所有模块的镜像量
    Angle = np.zeros(len(modules))  # 所有模块的旋转量
    Center = np.zeros((len(modules),2))     # 所有模块的中心点

    figure = plt.figure()  # 画布
    axes = figure.add_subplot(121, aspect=1)  # 子图1
    orgS = plotRect()  # 初始版图面积
    plotMods()  # 绘制模块
    orgSL = plotLinks()  # 初始线网长度
    updateMods()  # 更新模块
    checkOverlap()  # 检查重叠
    axes = figure.add_subplot(122, aspect=1)  # 子图2
    saveresult(Mirror, Angle, Center)   # 保存更新后的模块数据
    newS = plotRect()  # 最终版图面积
    plotMods()
    newSL = plotLinks()  # 最终线网长度
    print('版图面积新旧比：%d/%d=%.2f' % (newS, orgS, newS/orgS))
    print('线网总长新旧比：%d/%d=%.2f' % (newSL, orgSL, newSL/orgSL))
    #print(Mirror)      #debug
    #print(Angle)
    #print(Center)
    plt.show()  # 显示画布
