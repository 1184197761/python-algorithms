import numpy as np
import copy
from time import time
import numpy as np
import random

class node():
    def __init__(self, ind=None, name=None, ziyuan=None, assignment=None):
        self.id = ind
        self.name = name
        self.ziyuan = ziyuan         # 节点所用资源的列表(在当前题目要求下，资源总和即可，不需要列表)
        self.assignment = assignment # 节点被分配到的FPGA序号
        self.net = []               # 节点所属线网的序号列表

class net():
    def __init__(self, nodelist=None):
        self.nodelist = nodelist        # 线网中的节点的列表，此列表中每个元素是节点的名字
        self.assignment = set()    # 线网中的节点被分配到的FPGA的集合， 此集合中每个元素是FPGA的序号

def readNodeFile(filename):
    f = open(filename)
    vertex = {}        # 字典
    vertexname=[]      # 列表
    ind = 0
    for line in f:
        list1 = line.split()
        nm = list1[0]
        vertexname.append(nm)
        ziyuan = list(map(int, list1[-10:]))
        vertex[nm] = node(ind, nm, sum(ziyuan))
        ind += 1
    f.close()
    return vertex,vertexname

def readNetFile(filename,vertex):
    f = open(filename)
    linestack=[]
    for line in f:
        linestack.append(line.split())
    nets=[]
    nodelist=[]
    ind=0
    while linestack!=[]:
        line = linestack.pop()
        nodelist.append(line[0])
        if 's' in line:
            nets.append(net(nodelist))
            for node in nodelist:
                vertex[node].net.append(ind)
            nodelist=[]
            ind += 1
    f.close()
    return nets

def fenpeiMethod(vertex, nosFPGA,vertexname):
    return randomFenpei(vertex, nosFPGA,vertexname)

def randomFenpei(vertex, nosFPGA,vertexname):
    nosnode = len(vertex)
    fenpei=[]
    for i in range(nosnode):
        fenpei.append(np.random.randint(nosFPGA))
    F = [[] for i in range(nosFPGA)]
    for i in range(nosnode):
        F[fenpei[i]].append(i)
        vertex[vertexname[i]].assignment = fenpei[i]
        for onenet in nets:
            if vertexname[i] in onenet.nodelist:
                onenet.assignment.add(fenpei[i])
    return F

def writeResult(F,vertexname):
    nosFPGA = len(F)
    for fpga in range(nosFPGA):
        f.write("F"+str(fpga))
        for onenode in F[fpga]:
            f.write(" "+vertexname[onenode])
        f.write("\n")

def ziyuanCal(F,vertex,vertexname):
    nosFPGA = len(F)
    Z = []
    for i in range(nosFPGA):
        list1 = F[i]
        sumzy = 0
        for ind in list1:
            sumzy += vertex[vertexname[ind]].ziyuan
        Z.append(sumzy)
    return Z

###############遗传算法#################
#   初始化群体,
##  每一个染色体都为一个解，每个资源节点都被分别分配到四块FPGA中
def initPop(N, nosFPGA, vertex, vertexname):
    nosnode = len(vertex)
    pop = np.zeros((N, nosnode), int)   #FPGA节点分配矩阵 染色体
    for i in range(N):
        F = randomFenpei(vertex, nosFPGA, vertexname)
        for j in range(nosnode):
            pop[i][j] = vertex[vertexname[j]].assignment
    return pop

#   计算pop中每个染色体的四个FPGA上的资源和
def Popziyuan(pop, vertex, N, nosFPGA):
    nosnode = len(vertex)
    rang = np.zeros((N, nosFPGA), int)  #资源和矩阵
    poptemp = []
    for i in range(N):
        poptemp = pop[i, :]
        F = [[] for i in range(nosFPGA)]
        for j in range(nosnode):
            F[poptemp[j]].append(j)
        Z = ziyuanCal(F, vertex, vertexname)
        for j in range(nosFPGA):
            rang[i][j] = Z[j]
    return rang

#   计算rang中每个染色体所代表的资源的方差
def calziyuan(rang, N):
    var = {}
    for i in range(N):
        X = rang[i]
        var[i] = np.var(X)
    return var

#   根据所有染色体分别的方差，计算各个染色体的适应值fitness
def calfitness(var):
    fitness = {}
    for i in range(len(var)):
        fitness[i] = 1.0 / var[i]
    fitness = [x[1] for x in sorted(fitness.items())]  # 将fitness字典按顺序转化成数组
    return fitness

#   根据染色体群体rang已经对应的适应值fitness
#   找到最高的适应值f，以及对应的染色体bst和其在pop中的编号/下标ind
def findBest(pop,fitness):
    f = np.n=max(fitness)
    ind = np.asarray(np.where(fitness == f)).flatten()
    bst = pop[ind, :]
    return bst

def satified(fitness):
    return 0

#   根据交叉概率pc，以及各染色体的适应值fitness，通过交叉的方式生成新群体
#   #SelfAdj = 1时为自适应，否则取固定的交叉概率pc
def crossPop(pop, pc, fitness, SelfAdj):
    N, nosnode = np.shape(pop)
    lst = list(range(N))
    np.random.shuffle(lst)

    fm = np.max(fitness)
    fa = np.mean(fitness)
    k1 = pc
    k2 = pc
    i = 0
    while i < int(N/2):
        # 生成一个随机数，与pc进行比较，当随机数小于pc则进行交叉操作
        rval = np.random.rand()
        # 生成一个50-100之间的整数j，父亲1是前半段族群的染色体，父亲2是后半段族群的染色体
        j = np.random.randint(int(N/2), N)
        # 固定交叉概率pc，或自适应交叉概率
        if SelfAdj == 1:
            fprime = np.max(fitness[i], fitness)
            if fprime>fa:
                pc = k1*(fm-fprime) / (fm-fa)
            else:
                pc = k2
        if rval > pc:
            continue
        # 满足交叉条件
        # 生成交叉父亲
        partner1 = copy.copy(pop[lst[i], :])
        partner2 = copy.copy(pop[lst[j], :])
        # 若父亲1和2完全相等，则进行下一次循环
        if (partner1 == partner2).all():
            continue
        # 进行交叉，调用genercross函数
        child1, child2 = genecross(partner1, partner2)
        pop[lst[i], :] = copy.copy(child1)
        pop[lst[j], :] = copy.copy(child2)
        i = i+1
#   父染色体partner1,partner2，通过交叉方式
#   生成两个子染色体child1,child2
def genecross(partner1, partner2):
    length = len(partner1)
    idx1 = 0
    idx2 = 0
    while idx1 == idx2:
        idx1 = random.randint(0, length-1)
        idx2 = random.randint(0, length-1)
    ind1 = min(idx1, idx2)
    ind2 = max(idx1, idx2)

    child1 = copy.copy(partner1)
    child2 = copy.copy(partner2)

    tem1 = copy.copy(child1[ind1:ind2])
    tem2 = copy.copy(child2[ind1:ind2])

    if (tem1 == tem2).all():
        return [child1, child2]
    if set(tem1) == set(tem2):
        child1[ind1:ind2] = tem2
        child2[ind1:ind2] = tem1
        return [child1, child2]

    child1[ind1:ind2] = tem2
    child2[ind1:ind2] = tem1
    return [child1, child2]        ##有疑问？

# 根据变异概率pw，以及各染色体的适应值fitness，通过变异的方式生成新群体
# #SelfAdj = 1时为自适应，否则取固定的变异概率pw
def mutPop(pop, pw, fitness, SelfAdj):
    N, nc = np.shape(pop)

    fm = max(fitness)
    fa = np.mean(fitness)
    k3 = pw
    k4 = pw

    for i in range(N):
        rval = random.random()
        if SelfAdj == 1:
            if fitness[i] > fa:
                pw = k3 * (fm - fitness[i]) / (fm - fa)
            else:
                pw = k4
        if rval > pw:
            continue
        pop[i, :] = np.asarray(mutDistGene(pop[i, :], pw))
# 在pop的资源分配中，对每一个染色体节点的所分配的FPGA号进行变异，改变为其他的FPGA
def mutDistGene(gene, pw):
    choose=np.random.rand()
    isornot=choose=np.random.rand()
    nosnode = len(gene)
    if choose < 0.33:#两点互换
        for i in range(int(nosnode/2)):
            if isornot< pw:
                ind1 = np.random.randint(0,nosnode,1)
                ind2 = np.random.randint(0,nosnode,1)
                gene[ind1],gene[ind2]=gene[ind2],gene[ind1]
    elif choose > 0.67:#相邻互换
        for i in range(int(nosnode/2)):
            if isornot < pw:
                ind1 = np.random.randint(0,nosnode,1)
                gene[ind1],gene[ind1+1]=gene[ind1+1],gene[ind1]
    else:#区间反转
        for i in range(10):
            if isornot < pw:
                ind1 = np.random.randint(0, nosnode, 1)
                ind2 = np.random.randint(0, nosnode, 1)
                reverse(gene[ind1:ind2])
    return gene
# 反转函数
def reverse(slice):
    list=[]
    for i in len(slice):
        list.append(slice.pop())
    return list

#   根据染色体的适应值，按照一定的概率，生成新一代染色体群体newpop
def chossNewP(pop, fitness):
    N, nosnode = np.shape(pop)
    x = []
    lst = np.zeros([N, 1])
    for i in range(N):
        rval = np.random.rand()
        for j in range(N-1, -1, -1):
            if rval > fitness[j]:
                lst[i] = j
                break
    pop = pop[list(lst.flatten().astype(np.uint8)), :]
# 测试
# 读取节点文件
filename = "design.are"
vertex, vertexname = readNodeFile(filename)
# 读取线网文件
filename = "design.net"
nets = readNetFile(filename, vertex)

# 超参数设置
nosFPGA = 4
N = 100
pc = 0.80
pw = 0.25
SelfAdj = 0
MAXITER = 10**3	# 最大循环次数
#   步骤1，产生N个染色体的初始群体保存在pop中
pop = initPop(N, nosFPGA, vertex, vertexname)
iter = 0
tstart = time()
while iter <= MAXITER+1:
    iter = iter +1

    rang = Popziyuan(pop, vertex, N, nosFPGA)   #计算每个染色体对应的资源和
    var = calziyuan(rang, N)                    #步骤2：计算每个染色体对应的资源方差
    fitness = calfitness(var)               #   计算每个染色体的适应值
    bst = findBest(pop, fitness)  #   找到当前种群中，适应度最高的个体

    # 步骤三：如果满足某些标准，算法停止
    if satified(fitness):
        break

    chossNewP(pop, fitness)   #否则，选取一个新的群体
    crossPop(pop, pc, fitness, SelfAdj)         #步骤四：交叉产生新染色体
    mutPop(pop, pw, fitness, SelfAdj)           #步骤五：基因变异
    pop[0, :] = bst[0, :]                     #保留每一代中适应值最高的
    if np.mod(iter, MAXITER / 10) == 1:
        titer = time()
        print("iter = %d after running %d seconds with var=%f" % (
        iter, int(titer - tstart),var[0]))

best = pop[0, :]

filename = "./result.res"
f = open(filename, 'w')
str0 = 'F1'
str1 = 'F2'
str2 = 'F3'
str3 = 'F4'
for i, node in enumerate(best):
    if node == 0:
        str0 = str0 + " " + vertex[vertexname[i]].name
    elif node == 1:
        str1 = str1 + " " + vertex[vertexname[i]].name
    elif node == 2:
        str2 = str2 + " " + vertex[vertexname[i]].name
    else:
        str3 = str3 + " " + vertex[vertexname[i]].name

f.write(str0 + "\n")
f.write(str1 + "\n")
f.write(str2 + "\n")
f.write(str3 + "\n")
f.write(str(var[0])+"\n")
f.close()

