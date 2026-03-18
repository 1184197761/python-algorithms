# %% [markdown]
#  # 资源分配问题

# %% [markdown]
# ## 包导入

# %%
from numpy import cumsum
from time import time
import random as rd

# %% [markdown]
#  ## 类定义

# %%


class node():  # 节点类
    def __init__(self, name=None, resourse=None):  # 初始化节点
        self.name = name  # 名称
        self.resourse = resourse  # 资源
        self.nets = set()  # 网络集合

# %% [markdown]
#  ## 函数定义
#  ### 读取文件信息
#

# %%


def readNodeInfo():  # 读取节点信息
    with open("design.are") as file:  # 打开节点文件
        nodes = {}  # 创建节点字典
        for line in file:  # 按行遍历文件
            name = line.split()[0]  # 取当前行首字符为节点名
            nodes[name] = node(name)  # 新建节点键值到字典
    return nodes  # 返回字典


# %%
def readNetInfo():  # 读取网络信息
    names = []  # 同网络节点名称列表
    with open("design.net") as file:
        for line in file:
            if 's' in line.split():  # 当前行中包含网络首节点s
                for name in names:  # 将之前节点映射到前首节点网络
                    nodes[name].nets.add(names[0])
                names.clear()  # 清空已映射节点
            names.append(line.split()[0])  # 添加当前行的节点
        nodes[name].nets.add(names[0])  # 将剩余节点映射到当前网络


# %% [markdown]
#  ### 定义分配函数

# %%
def allocation():  # 分配单个染色体
    return [rd.randint(0, NF-1) for _ in nodes]  # 返回映射所有节点fpga号的随机染色体编码

# %% [markdown]
#  ### 定义结果函数

# %%


def writeResult():  # 输出分配结果
    buffer = ''  # 临时字符串
    for fpga in range(NF):  # 遍历4个fpga
        buffer += 'F'+str(fpga)+' '  # 添加fpga编号
        for index, node in enumerate(nodes.values()):  # 遍历所有节点
            if best[index] == fpga:  # 若节点通过最佳染色体映射为当前fpga号
                buffer += node.name+' '  # 添加当前节点名称
        buffer += '\n'
    print(buffer)  # 打印最优fpga节点分配结果
    buffer += str(minLink)  # 添加最优板间连线结果
    with open("./result.res", 'w') as file:  # 打开结果文件
        file.write(buffer)  # 写入最优结果


# %% [markdown]
#  ### 定义资源差异函数

# %%
def resourseCal():
    return 0

# %% [markdown]
#  ### 定义板间连线函数

# %%


def linkCal(ind):  # 计算FPGA板间连线总和
    link = 0  # 初始化连线数量
    fpgaNets = [set() for _ in range(NF)]  # 4个fpga的网络集合列表
    for index, node in enumerate(nodes.values()):  # 遍历所有节点
        fpgaNets[ind[index]] |= node.nets  # 将节点网络添加到通过染色体映射的fpga网络
    for index, net1 in enumerate(fpgaNets):  # 遍历所有fpga网络
        for net2 in fpgaNets[index+1:]:  # 遍历之后的fpga网络
            link += len(net1 & net2)  # 两板相同网络数即为板间连线数
    return link


# %% [markdown]
# ### 定义适应值函数

# %%
def fitnessCal():  # 计算每个个体的适应性
    fitness = []  # 初始化适应值列表
    for link in links:
        try:  # 捕获异常
            fitness.append(1/link)  # 适应值与连线数成反比
        except ZeroDivisionError:  # 零除错误（此时达到最优解）
            fitness.append(float('inf'))  # 适应值为正无穷
    return fitness


# %% [markdown]
# ### 定义筛选函数

# %%
def screenPop():  # 筛选种群个体
    sumFit = cumsum(fitness)  # 计算累加适应值列表（生成轮盘）
    for i, ind1 in enumerate(pop):  # 遍历每个个体
        for j, ind2 in enumerate(pop):  # 遍历新的个体（轮盘转圈）
            if rd.random() < sumFit[j] and fitness[i] < fitness[j]:  # 若轮盘选中个体适应值较大
                ind1 = ind2  # 以新个体淘汰当前个体
                break  # 轮盘停止转动


# %% [markdown]
# ### 定义交叉函数

# %%
def crossPop():  # 种群个体交配
    for i in range(int(NP/2)):  # 遍历雄性个体
        j = rd.randint(int(NP/2), NP-1)  # 寻找配偶
        if rd.random() < PC:  # 求偶成功
            index = rd.randint(1, len(nodes))  # 染色体交叉点
            child1 = pop[i][:index]+pop[j][index:]  # 子染色体
            child2 = pop[j][:index]+pop[i][index:]  # 或子代个体
            pop[i], pop[j] = child1, child2  # 牺牲父代，保留子代


# %% [markdown]
# ### 定义变异函数

# %%
def mutatePop():  # 种群个体变异
    for ind in pop:
        if rd.random() < PW:  # 触发变异
            # gene1, gene2 = rd.sample(ind, 2)  # 浅拷贝，无法修改原值
            # gene1, gene2 = gene2, gene1
            # i, j = rd.sample(range(len(ind)), 2)
            # ind[i], ind[j] = ind[j], ind[i]  # 索引，可以修改原值
            rd.shuffle(ind)  # 超级变异


# %% [markdown]
#  ## 执行代码

# %% [markdown]
# ### 设定参数

# %%
NF = 4  # FPGA数量
MI = 10**3  # 最大迭代次数
PC = 0.2  # 交叉概率
PW = 0.1  # 变异概率
NP = 100  # 染色体规模

# %% [markdown]
# ### 遗传算法

# %%
nodes = readNodeInfo()  # 读取节点文件
readNetInfo()  # 读取线网文件
pop = [allocation() for _ in range(NP)]  # 初始化N个体种群
tstart = time()  # 开始计时
for iter in range(MI):  # 种群迭代
    links = [linkCal(ind) for ind in pop]  # 板间连线总和列表
    fitness = fitnessCal()  # 个体适应值列表
    maxLink, minLink = max(links), min(links)  # 最大、最小连线总和
    index1 = links.index(minLink)  # 最大连线总和索引
    index2 = links.index(maxLink)  # 最小连线总和索引
    best = pop[index1]  # 最佳适应性个体
    screenPop()  # 筛选种群个体
    crossPop()  # 种群个体交配
    mutatePop()  # 种群个体变异
    pop[index2] = best  # 淘汰最差并保留最佳适应性个体
    if not iter % (MI/10) or not minLink:  # 迭代进度达到设置的10%或最优结果
        print('迭代次数：%3d\t时间：%.2fs\t板间连线：%2d' %
              (iter+1, time()-tstart, minLink))
        if not minLink:  # 达到最优板间连线总和
            break  # 停止迭代
print('最小连线：%3d\t适应值：%f\t分配关系：' % (minLink, fitness[index1]))
writeResult()
