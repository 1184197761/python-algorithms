
from random import random, sample, shuffle
from re import finditer, match, search
from matplotlib.patches import Circle, Polygon, Rectangle
from matplotlib.pyplot import figure, show
from numpy import array, concatenate, cos, cumsum, inf, mean, radians, reshape, sin
from numpy.random import rand,choice
from time import time


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


class Individ():
    def __init__(self, gene1, gene2):
        self.gene1 = gene1
        self.gene2 = gene2
        self.area = 0
        self.length = 0
        self.fitness = 0

    def getArea(self):
        vertexs = [vertex for module in modules.values()
                   for vertex in module.bound]  # 获取所有模块顶点列表
        vertexs = array(vertexs)  # 顶点列表转np数组
        width, height = vertexs.max(0)-vertexs.min(0)  # 获取矩形宽高
        self.area = width*height

    def getFitness(self):
        self.fitness = 10**6/(indiv.area+indiv.length/10)

    def getLength(self):
        self.length = 0
        for link in links:  # 遍历线网列表
            nx, ny = mean(concatenate(link.ports), 0)  # 获取线网中心点
            for port in link.ports:  # 遍历线网端口
                px, py = mean(port, 0)  # 获取端口中心点
                self.length += ((nx-px)**2+(ny-py)**2)**0.5  # 添加走线长度到线网总长

    def setLayout(self):  # 更新模块
        levels = [Level(0, 500, 0)]  # 水平线段列表
        minLevel = levels[0]  # 最低水平线段
        minDex = 0  # 最低水平线段索引
        ordMods = [modules[id] for id in self.gene1]
        for index, module in enumerate(ordMods):
            length = minLevel.x[1]-minLevel.x[0]
            while length < min(module.size):  # 当最低水平线长小于矩形宽度
                for fitMod in ordMods[index:]:
                    if length > min(fitMod.size):
                        ordMods.remove(fitMod)
                        ordMods.insert(index, fitMod)
                        module = fitMod
                        break
                if length > min(module.size):
                    break
                # 相邻水平线段高度
                leftH = levels[minDex-1].y if minDex > 0 else inf
                rightH = levels[minDex +
                                1].y if minDex < len(levels)-1 else inf
                if leftH < rightH:  # 左邻线段低于右邻线段
                    levels[minDex-1].x[1] = minLevel.x[1]  # 延长线段长度
                else:
                    levels[minDex+1].x[0] = minLevel.x[0]
                levels.remove(minLevel)  # 移除最低水平线段
                minLevel = min(levels, key=lambda level: level.y)  # 获取最低水平线段
                length = minLevel.x[1]-minLevel.x[0]
                minDex = levels.index(minLevel)  # 获取最低水平线段索引
            width, height = module.size
            lowLeft = module.lowLeft
            if length > height > width or width > length > height:
                angle = self.gene2[index]
                if angle == 1:
                    pivot = lowLeft+[width/2, width/2]
                else:
                    pivot = lowLeft+[height/2, height/2]  # 获取旋转点使旋转后左下顶点不变
                for vertex in module.bound:
                    vertex[:] = rotateVertex(vertex, pivot, angle)
                for port in module.ports:
                    for vertex in port:
                        vertex[:] = rotateVertex(
                            vertex, pivot, angle)
                module.size = width, height = height, width
            shift = [minLevel.x[0], minLevel.y]-lowLeft  # 获取偏移量
            module.bound = [vertex+shift for vertex in module.bound]  # 移动模块边界
            for port in module.ports:
                for vertex in port:
                    vertex += shift  # 移动端口
            module.lowLeft += shift
            newLevel = Level(minLevel.x[0], minLevel.x[0]+width, minLevel.y +
                             height)  # 获取新水平线段
            minLevel.x[0] += width  # 最低水平线段从左缩短
            levels.insert(minDex, newLevel)  # 插入新水平线段到最低水平线段前
            minDex += 1  # 最低水平线段索引自增


def rotateVertex(vertex, center, angle):  # 旋转顶点
    rad = -radians(angle*90)  # 旋转角度转弧度
    s, c = sin(rad), cos(rad)  # 正余弦值
    dx, dy = vertex-center  # 顶点-中心点偏移量
    return center+[c*dx-s*dy, c*dy+s*dx]  # 返回新顶点


def readMods():  # 读取模块信息
    moduleInfo = 'contest_cases/Ports_Area_etc_input_1.txt'  # 模块文件名
    with open(moduleInfo, 'r') as file:  # 以只读方式打开模块文件
        # # 替代方案
        # module = Module(None)  # 初始化模块类对象
        # for line in reversed(file.readlines()):  # 倒序遍历文本行
        #     match match('\w', line).group():  # 匹配第一个字母
        #         case 'P':  # Port开头
        #             bound = [float(match.group())  # 获取边界数据
        #                      for match in finditer('-?\d+\.\d', line)]
        #             port = Port(reshape(bound, (-1, 2)))  # 格式化为边界以创建端口类对象
        #             module.ports.append(port)  # 添加端口到模块
        #         case 'B':  # Boundary开头
        #             bound = [float(match.group())  # 获取边界数据
        #                      for match in finditer('-?\d+\.\d', line)]
        #             module.bound = reshape(bound, (-1, 2))  # 格式化为模块边界
        #         case 'M':  # Module开头
        #             module.id = int(search('\d+', line).group())  # 获取模块编号
        #             modules[module.id] = copy.copy(module)  # 以模块编号为键浅拷贝到模块字典
        #             module.ports = []  # 清空模块端口
        for line in file:  # 遍历文本行
            if match('M', line):  # 跳至Module行
                module = Module()  # 初始化模块
                id = int(search('\d+', line).group())
                bound = [float(match.group())  # 获取边界数据
                         for match in finditer('-?\d+\.\d', file.readline())]
                vertexs = reshape(bound, (-1, 2))
                lowLeft, topRight = vertexs.min(axis=0), vertexs.max(axis=0)
                module.bound = vertexs  # 格式化为模块边界
                module.size = topRight - lowLeft
                module.lowLeft = lowLeft
                for _ in range(3):  # 遍历端口数据
                    bound = [float(match.group())  # 获取边界数据
                             for match in finditer('-?\d+\.\d', file.readline())]
                    # 格式化为端口边界以创建端口类对象并添加到模块
                    module.ports.append(reshape(bound, (-1, 2)))
                modules[id] = module  # 以模块编号为键添加模块到模块字典


def readLinks():  # 获取线网信息
    linkInfo = 'contest_cases/Ports_link_input.txt_1.txt'  # 线网文件名
    with open(linkInfo, 'r') as file:  # 以只读方式打开线网文件
        for _ in file:
            # # 替代方案
            # match match('\D', line).group():  # 匹配非数字字符
            #     case 'L':  # Link开头
            #         linkId = int(search('\d+', line).group())  # 获取线网编号
            #     case 'M':  # Mx开头
            #         modIds = [int(match.group())  # 获取模块编号列表
            #                   for match in finditer('\d+', line)]
            #         portIds = [int(match.group())  # 获取端口编号列表
            #                    for match in finditer('\d', file.readline())]
            #         for modId, portId in zip(modIds, portIds):  # 遍历模块-端口列表
            #             # 绑定线网编号到对应的模块端口
            #             modules[modId].ports[3-portId].linkId = linkId
            link = Link()
            modIds = [int(match.group())  # 获取模块编号列表
                      for match in finditer('\d+', file.readline())]
            portIds = [int(match.group())  # 获取端口编号列表
                       for match in finditer('\d', file.readline())]
            for modId, portId in zip(modIds, portIds):  # 遍历模块-端口列表
                link.ports.append(modules[modId].ports[portId-1])  # 绑定模块端口到线网
            link.center = mean(concatenate(link.ports), 0)
            links.append(link)


def plotLinks():  # 绘制线网
    length = 0  # 线网总长
    for index, link in enumerate(links):  # 遍历线网列表
        nx, ny = mean(concatenate(link.ports), 0)  # 获取线网中心点
        rands = rand(3)  # 随机数列表
        for port in link.ports:  # 遍历线网端口
            px, py = mean(port, 0)  # 获取端口中心点
            axes.plot([nx, px], [ny, py], color=rands)  # 绘制随机颜色的线网分支
            length += ((nx-px)**2+(ny-py)**2)**0.5  # 添加走线长度到线网总长
        axes.text(nx, ny, index+1, color=rands)  # 打印相同颜色的线网编号
    return length  # 返回线网总长


def plotMods():  # 绘制模块
    vertexs = [vertex for module in modules.values()
               for vertex in module.bound]  # 获取所有模块顶点列表
    vertexs = array(vertexs)  # 顶点列表转np数组
    lowLeft, topRight = vertexs.min(axis=0), vertexs.max(axis=0)  # 获取对角坐标
    width, height = topRight-lowLeft  # 获取矩形宽高
    axes.add_patch(Rectangle(lowLeft, width, height))  # 添加矩形
    for id, module in modules.items():  # 遍历模块列表
        poly = Polygon(module.bound, color='white')  # 根据模块边界创建白色多边形
        axes.add_patch(poly)  # 添加多边形
        for port in module.ports:  # 遍历模块端口列表
            # 根据端口边界创建随机颜色多边形
            poly = Polygon(port, color=rand(4))
            axes.add_patch(poly)  # 添加多边形
        x, y = mean(module.bound, 0)  # 获取模块中心点
        axes.add_patch(Circle((x, y)))  # 添加模块圆点
        axes.text(x, y, id)  # 打印模块编号
    return width*height  # 返回矩形面积


def initPop():
    for _ in range(NP):
        gene1 = list(range(1, len(modules)+1))
        gene2 = choice([1, 3], len(modules))
        pop.append(Individ(gene1, gene2))


def screenPop():  # 筛选种群个体
    # 计算累加适应值列表（生成轮盘）
    sumFit = cumsum([indiv.fitness for indiv in pop])
    for indiv1 in pop:  # 遍历每个个体
        for index, indiv2 in enumerate(pop):  # 遍历新的个体（轮盘转圈）
            # 若轮盘选中个体适应值较大
            if random() < sumFit[index] and indiv1.fitness < indiv2.fitness:
                pop.remove(indiv2)
                pop.append(indiv1)  # 以新个体淘汰当前个体
                break  # 轮盘停止转动



def crossPop():  # 种群个体交配
    for indiv1 in pop[:int(NP/2)]:  # 遍历雄性个体
        indiv2 = choice(pop[int(NP/2):])  # 寻找配偶
        gene1, gen2 = indiv1.gene1, indiv2.gene2
        if random() < PC:  # 求偶成功
            index1, index2 = sorted(choice(16, 2))
            child1 = gene1[index1:index2]
            child2 = gen2[index1:index2]
            gen2 = [id for id in gen2 if id not in child1]
            gen2[index1:index1] = child1  # 切片实现列表插入
            gene1 = [id for id in gene1 if id not in child2]
            gene1[index1:index1] = child2


def mutatePop():  # 种群个体变异
    for indiv in pop:
        if random() < PW:  # 触发变异
            shuffle(indiv.gene1)  # 超级变异
            indiv.gene2 = choice([1, 3], len(modules))


if __name__ == '__main__':
    MI = 100  # 最大迭代次数
    PC = 0.5  # 交叉概率
    PW = 0.1  # 变异概率
    NP = 10  # 染色体规模

    modules = {}  # 模块字典
    links = []
    levels = []
    pop = []

    readMods()  # 读取模块
    readLinks()  # 读取线网
    initPop()  # 初始化种群

    figure = figure()  # 画布
    axes = figure.add_subplot(121, aspect=1)  # 子图1
    orgS = plotMods()  # 初始版图面积
    orgL = plotLinks()  # 初始线网长度

    tstart = time()  # 开始计时
    for iter in range(MI):
        for indiv in pop:
            indiv.setLayout()
            indiv.getArea()
            indiv.getLength()
            indiv.getFitness()
        best = max(pop, key=lambda indiv: indiv.fitness)
        worst = min(pop, key=lambda indiv: indiv.fitness)
        screenPop()  # 筛选种群个体
        crossPop()  # 种群个体交配
        mutatePop()  # 种群个体变异
        # worst = best  # 淘汰最差并保留最佳适应性个体
        pop.append(best)
        pop.remove(worst)
        print('迭代次数：%3d  时间：%.2fs  版图面积：%d  线网长度：%d  适应值：%f' %
              (iter+1, time()-tstart, best.area, best.length, best.fitness))
    axes = figure.add_subplot(122, aspect=1)  # 子图2
    newS = plotMods()  # 最终版图面积
    newL = plotLinks()  # 最终线网总长
    print('版图面积新旧比：%d/%d=%.2f' % (newS, orgS, newS/orgS))
    print('线网总长新旧比：%d/%d=%.2f' % (newL, orgL, newL/orgL))
    show()  # 显示画布
