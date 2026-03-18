
from copy import deepcopy
from datetime import datetime as dt
from matplotlib import rcParams
from matplotlib.patches import Circle, Polygon, Rectangle
from matplotlib.pyplot import figure, savefig, show, tight_layout
from numpy import array, concatenate, cos, cumsum, inf, mean, radians, reshape, sin
from numpy.random import rand, choice, shuffle, random
from os import makedirs
from re import finditer, match, search
from time import time


class Module():   # 模块类
    def __init__(self, bound, size, lowLeft):
        self.bound = bound  # 模块边界
        self.size = size  # 模块长宽
        self.lowLeft = lowLeft  # 模块左下点
        self.ports = []  # 模块端口列表
        self.angle = 0  # 模块旋转量
        self.mirror = False  # 模块镜像量


class Level():  # 水平线类
    def __init__(self, start, end, height):
        self.x0 = start  # 水平线起点
        self.x1 = end  # 水平线终点
        self.y = height  # 水平线高度


class Individ():  # 染色体类
    def __init__(self, genes):
        self.genes = genes  # 基因列表
        self.area = 0  # 版图面积
        self.length = 0  # 线网总长
        self.fitness = 0  # 适应值

    def placeMods(self):  # 摆放模块
        levels = [Level(0, orgS**0.5, 0)]  # 初始化水平线段列表
        minLevel = levels[0]  # 初始化最低水平线段
        minDex = 0  # 初始化最低水平线段索引
        ordMods = [modules[id] for id in self.genes[0]]  # 解码模块序列
        for index, module in enumerate(ordMods):  # 遍历模块序列
            length = minLevel.x1-minLevel.x0  # 获取最低水平线段长度
            while length < min(module.size):  # 当模块放不下
                for newMod in ordMods[index+1:]:  # 搜索靠后的模块
                    if length > min(newMod.size):  # 若新模块放得下
                        ordMods.remove(newMod)  # 将新模块移动到当前模块前
                        ordMods.insert(index, newMod)
                        module = newMod  # 将新模块作为当前模块
                        break  # 结束搜索
                if length > min(module.size):  # 若当前模块放得下
                    break  # 不再提升水平线高度
                # 初始化相邻水平线段高度，用于提升最低水平线段
                leftH = levels[minDex-1].y if minDex > 0 else inf  # 边缘为无穷高
                rightH = levels[minDex+1].y if minDex < len(levels)-1 else inf
                if leftH < rightH:  # 若左邻线段低于右邻线段
                    levels[minDex-1].x1 = minLevel.x1  # 向右延长左邻线段
                else:  # 否则
                    levels[minDex+1].x0 = minLevel.x0  # 向左延长右邻线段
                levels.remove(minLevel)  # 移除当前最低水平线段
                minLevel = min(levels, key=lambda level: level.y)  # 获取最低水平线段
                length = minLevel.x1-minLevel.x0  # 更新水平线段长度
                minDex = levels.index(minLevel)  # 更新最低水平线段索引
            width, height = module.size  # 模块宽高
            lowLeft = module.lowLeft  # 模块左下点
            # 若竖放模块可以横放或横放模块只能竖放
            if length > height > width or width > length > height:
                angle = self.genes[1][index]  # 获取编码对应旋转量
                if angle == 1:  # 旋转90°
                    pivot = lowLeft+[width/2, width/2]  # 获取旋转点使左下顶点不变
                else:  # 旋转270°
                    pivot = lowLeft+[height/2, height/2]  # 同上
                for vertex in module.bound:  # 旋转模块
                    vertex[:] = rotateVertex(vertex, pivot, angle)
                for port in module.ports:  # 旋转端口
                    for vertex in port:  # 切片后可进行原址修改
                        vertex[:] = rotateVertex(vertex, pivot, angle)
                module.size = width, height = height, width  # 宽高对调
                module.angle = (module.angle+angle) % 4  # 更新旋转量
            if self.genes[2][index]:  # 若模块镜像为真
                axis = lowLeft[0]+width/2  # 对称轴
                module.bound = [[2*axis-x, y]  # 水平翻转模块
                                for [x, y] in module.bound]
                for port in module.ports:  # 水平翻转端口
                    for vertex in port:  # 索引可进行原址修改
                        vertex[0] = 2*axis-vertex[0]
                module.mirror = not module.mirror  # 镜像取反
            shift = [minLevel.x0, minLevel.y]-lowLeft  # 获取偏移量
            module.bound = [vertex+shift for vertex in module.bound]  # 移动模块
            for port in module.ports:  # 移动模块端口
                for vertex in port:  # 自增运算可进行原址修改
                    vertex += shift
            module.lowLeft += shift  # 更新左下顶点
            # 根据最低水平线段和新模块初始化新水平线段
            newLevel = Level(minLevel.x0, minLevel.x0+width, minLevel.y+height)
            minLevel.x0 += width  # 最低水平线段从左缩短
            levels.insert(minDex, newLevel)  # 插入新水平线段到最低水平线段前
            minDex += 1  # 更新最低水平线段索引

    def saveResult(self):
        vertexs = array([vertex for module in modules.values()
                         for vertex in module.bound])  # 获取所有模块顶点列表
        width, height = vertexs.max(0)-vertexs.min(0)  # 获取最小矩形宽高
        self.area = width*height  # 保存版图面积
        self.length = 0  # 初始化线网长度
        for link in links:  # 遍历线网列表
            nx, ny = mean(concatenate(link), 0)  # 获取线网中心点
            for port in link:  # 遍历线网端口
                px, py = mean(port, 0)  # 获取端口中心点
                self.length += ((nx-px)**2+(ny-py)**2)**0.5  # 添加两点距离到线网长度
        self.fitness = 10**6/(self.area+self.length/10)  # 保存适应值


def rotateVertex(vertex, center, angle):  # 旋转顶点
    rad = -radians(angle*90)  # 旋转角度转弧度
    s, c = sin(rad), cos(rad)  # 正余弦值
    dx, dy = vertex-center  # 顶点-中心点偏移量
    return center+[c*dx-s*dy, c*dy+s*dx]  # 返回新顶点


def readMods():  # 读取模块信息
    moduleInfo = 'contest_cases/Ports_Area_etc_input_' + \
        str(caseId)+'.txt'  # 模块文件名
    with open(moduleInfo, 'r') as file:  # 以只读方式打开模块文件
        for line in file:  # 遍历文本行
            if match('M', line):  # 跳至Module行
                id = int(search('\d+', line).group())  # 获取模块编号
                bound = [float(match.group())  # 获取边界数据
                         for match in finditer('-?\d+\.\d', file.readline())]
                vertexs = reshape(bound, (-1, 2))  # 格式化为顶点列表
                lowLeft, topRight = vertexs.min(0), vertexs.max(0)  # 获取对角坐标
                module = Module(vertexs, topRight-lowLeft, lowLeft)  # 初始化模块
                for _ in range(3):  # 遍历端口数据
                    bound = [float(match.group())  # 获取边界数据
                             for match in finditer('-?\d+\.\d', file.readline())]
                    module.ports.append(reshape(bound, (-1, 2)))  # 添加到模块端口列表
                modules[id] = module  # 以模块编号为键添加模块到模块字典


def readLinks():  # 获取线网信息
    linkInfo = 'contest_cases/Ports_link_input.txt_' + \
        str(caseId)+'.txt'  # 线网文件名
    with open(linkInfo, 'r') as file:  # 以只读方式打开线网文件
        for _ in file:
            link = []  # 初始化空列表
            modIds = [int(match.group())  # 获取模块编号列表
                      for match in finditer('\d+', file.readline())]
            portIds = [int(match.group())  # 获取端口编号列表
                       for match in finditer('\d', file.readline())]
            for modId, portId in zip(modIds, portIds):  # 遍历模块-端口编号列表
                link.append(modules[modId].ports[portId-1])  # 添加模块端口到线网
            links.append(link)  # 添加线网到线网列表


def plotLinks():  # 绘制线网
    length = 0  # 线网长度
    for index, link in enumerate(links):  # 遍历线网列表
        nx, ny = mean(concatenate(link), 0)  # 获取线网中心点
        rands = rand(3)  # 生成随机数列表
        for port in link:  # 遍历线网端口
            px, py = mean(port, 0)  # 获取端口中心点
            axes.plot([nx, px], [ny, py], color=rands)  # 绘制随机颜色线网分支
            length += ((nx-px)**2+(ny-py)**2)**0.5  # 添加两点距离到线网长度
        axes.text(nx, ny, index+1, color=rands)  # 打印相同颜色的线网编号
    return length  # 返回线网总长


def plotMods():  # 绘制模块
    vertexs = array([vertex for module in modules.values()
                     for vertex in module.bound])  # 获取所有模块顶点列表
    lowLeft, topRight = vertexs.min(0), vertexs.max(0)  # 获取最小矩形对角坐标
    width, height = topRight-lowLeft  # 获取最小矩形宽高
    axes.add_patch(Rectangle(lowLeft, width, height))  # 添加矩形
    for id, module in modules.items():  # 遍历模块列表
        poly = Polygon(module.bound, color='white')  # 创建模块边界白色多边形
        axes.add_patch(poly)  # 添加多边形
        for port in module.ports:  # 遍历模块端口列表
            poly = Polygon(port, color=rand(4))  # 创建端口边界随机颜色多边形
            axes.add_patch(poly)  # 添加多边形
        x, y = mean(module.bound, 0)  # 获取模块中心点
        axes.add_patch(Circle((x, y)))  # 创建并添加模块中心圆点
        axes.text(x, y, id)  # 打印模块编号
    return width*height  # 返回矩形面积


def initPop():  # 初始化种群
    for _ in range(NP):  # 根据种群规模循环编码个体基因
        order = list(range(1, len(modules)+1))  # 模块摆放顺序
        angle = choice([1, 3], len(modules))  # 模块旋转量列表
        mirror = choice([0, 1], len(modules))  # 模块镜像量列表
        pop.append(Individ([order, angle, mirror]))  # 添加个体到种群


def screenPop():  # 筛选种群个体
    sumFit = cumsum([indiv.fitness for indiv in pop])  # 生成累加适应值列表（轮盘）
    rand = random()*sumFit[-1:-1]  # 生成随机数（轮盘指针）
    for indiv1 in pop:  # 遍历种群个体
        for index, indiv2 in enumerate(pop):  # 遍历新的个体（轮盘转圈）
            # 若轮盘指针指向新个体且新个体适应值较大
            if rand < sumFit[index] and indiv1.fitness < indiv2.fitness:
                pop.remove(indiv1)  # 淘汰当前个体
                pop.append(indiv2)  # 克隆新的个体
                break  # 轮盘停止转动


def crossPop():  # 种群个体交配
    for indiv1 in pop[:int(NP/2)]:  # 遍历雄性个体
        indiv2 = choice(pop[int(NP/2):])  # 寻找配偶
        if random() < PC:  # 求偶成功，进行染色体顺序交叉
            for gene1, gene2 in zip(indiv1.genes, indiv2.genes):  # 遍历双方三段基因
                index1, index2 = sorted(choice(len(modules), 2))  # 生成随机交叉点
                child1 = gene1[index1:index2]  # 截取基因1片段为子片段1
                child2 = gene2[index1:index2]  # 截取基因2片段为子片段2
                gene2 = [id for id in gene2 if id not in child1]  # 只保留非重复基因编码
                gene2[index1:index1] = child1  # 在交叉位置插入子片段
                gene1 = [id for id in gene1 if id not in child2]  # 等效为剔除重复基因编码
                gene1[index1:index1] = child2  # 切片以实现列表插入


def mutatePop():  # 种群个体变异
    for indiv in pop:  # 遍历种群个体
        if random() < PW:  # 触发变异，进行基因突变
            shuffle(indiv.genes[0])  # 打乱摆放顺序基因
            index1, index2 = sorted(choice(len(modules), 2))  # 随机变异片段截点
            indiv.genes[1][index1:index2] = choice(
                [1, 3], index2-index1)  # 替换为随机旋转量片段
            indiv.genes[2][index1:index2] = choice(
                [0, 1], index2-index1)  # 替换为随机镜像量片段


def saveSolution():  # 保存摆放解法
    with open(path+'/result'+str(caseId)+'.txt', 'w') as file:  # 以写入模式打开结果文件
        ordMods = [modules[id+1] for id in range(len(modules))]  # 正序模块列表
        for id, module in enumerate(ordMods):  # 遍历模块列表
            center = list(map(int, mean(module.bound, 0)))  # 获取模块中心点
            angle = module.angle  # 获取模块旋转量
            file.write('Module: M%d\n' % (id+1))  # 写入模块id
            mirrors = ['MX', 'MXR90', 'MY', 'MYR90']  # 镜像名列表
            # 根据旋转量和镜像量生成模块朝向字符串
            orient = mirrors[angle] if module.mirror else 'R'+str(angle*90)
            file.write('Orient: '+orient+'\n')  # 写入模块朝向
            file.write('Offset: '+str(center)+'\n')  # 写入模块中心点
    savefig(path+'/figure'+str(caseId), bbox_inches='tight')  # 保存画布


if __name__ == '__main__':
    MI = 100  # 最大迭代次数
    PC = 0.5  # 交叉概率
    PW = 0.1  # 变异概率
    NP = 10  # 染色体规模

    path = 'contest_cases/'+dt.now().strftime("%Y_%m_%d_%H_%M_%S")  # 结果路径
    makedirs(path)  # 根据结果路径创建文件夹

    for caseId in range(1, 4):  # 遍历三个案例
        modules = {}  # 模块字典
        links = []  # 线网列表
        levels = []  # 水平线列表
        pop = []  # 种群个体列表
        bests = []  # 最佳个体列表

        readMods()  # 读取模块
        readLinks()  # 读取线网
        initPop()  # 初始化种群

        rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 设置中文字体
        fig = figure(figsize=(15, 5))  # 设置画布
        fig.canvas.set_window_title('案例'+str(caseId)+'优化对比')  # 设置标题

        axes = fig.add_subplot(121, aspect=1, title='初始布局')  # 子图1
        orgS = plotMods()  # 初始版图面积
        orgL = plotLinks()  # 初始线网长度

        tstart = time()  # 开始计时
        for iter in range(MI):  # 遗传迭代
            for indiv in pop:  # 遍历种群个体
                indiv.placeMods()  # 解码个体基因
                indiv.saveResult()
            best = max(pop, key=lambda indiv: indiv.fitness)  # 当前最佳个体
            bests.append(deepcopy(best))  # 添加到最佳个体列表
            screenPop()  # 筛选种群个体
            crossPop()  # 种群个体交配
            mutatePop()  # 种群个体变异
            print('迭代次数：%3d  时间：%.2fs  版图面积：%d  线网长度：%d  适应值：%f' %
                  (iter+1, time()-tstart, best.area, best.length, best.fitness))
        best = max(bests, key=lambda indiv: indiv.fitness)  # 历史最佳个体
        best.placeMods()  # 解码最佳个体基因

        axes = fig.add_subplot(122, aspect=1, title='最终布局')  # 子图2
        plotMods()  # 绘制模块
        plotLinks()  # 绘制线网

        print('版图面积新旧比：%d/%d=%.2f  线网总长新旧比：%d/%d=%.2f  适应值：%f' %
              (best.area, orgS, best.area/orgS, best.length, orgL, best.length/orgL, best.fitness))
        tight_layout()  # 紧凑布局
        print('正在保存案例%d结果...' % (caseId))
        saveSolution()  # 保存摆放结果
        print('保存成功，显示结果')
        show()  # 显示画布窗口
