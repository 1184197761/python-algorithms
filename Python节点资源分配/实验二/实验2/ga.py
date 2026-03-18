#!/usr/bin/env python
# coding: utf-8

# # 资源分配问题

# In[1]:


import numpy as np
import random
import math
import copy


# 
# 定义两个类，node表示节点类， net表示线网类

# In[2]:


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


# ## 定义函数
# ### 文件信息读取
# 读取文件，取得节点资源信息

# In[3]:


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


# 读取文件，取得线网信息

# In[4]:



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


# ### 定义分配函数fenpeiMethod
# 这里仅仅用于demo，采用随机分配

# In[5]:


def fenpeiMethod(vertex, nosFPGA, vertexname, nets):
    return randomFenpei(vertex, nosFPGA,vertexname, nets)

def randomFenpei(vertex, nosFPGA, vertexname, nets):
    nosnode = len(vertex)
    copy_nets = copy.deepcopy(nets)
    fenpei=[]
    for i in range(nosnode):
        fenpei.append(np.random.randint(nosFPGA))
    F = [[] for i in range(nosFPGA)]
    for i in range(nosnode):
        F[fenpei[i]].append(i)
        vertex[vertexname[i]].assignment = fenpei[i]
        for onenet in copy_nets:
            if vertexname[i] in onenet.nodelist:
                onenet.assignment.add(fenpei[i])
    return F,copy_nets


# ### 定义写文件函数writeResult

# In[6]:


def writeResult(F,vertexname):
    nosFPGA = len(F)
    for fpga in range(nosFPGA):
        f.write("F"+str(fpga))
        for onenode in F[fpga]:
            f.write(" "+vertexname[onenode])
        f.write("\n")


# ### 定义资源差异函数 ziyuanCal
# 计算不同板的资源 Z为一个列表里面分别对应四块FPGA板子上的资源 最后写入文件时调用np.std求方差

# In[7]:


def ziyuanCal(F):
    nosFPGA = len(F)
    Z = []
    for i in range(nosFPGA):
        list1 = []
        for index in F[i]:
            for j in vertex:
                if(j == vertexname[index]):
                    list1.append(vertex[j].ziyuan)
        Z.append(sum(list1))
    return Z


# ### 定义板间连线计算函数 linkCal
# 计算FPGA板间连线的总和

# In[8]:


def linkCal(nets,nosFPGA):
    L = [0 for i in range(nosFPGA)]
    for onenet in nets:
        if len(onenet.assignment)==1:
            continue
        for fpgaInd in onenet.assignment:
            L[fpgaInd] += 1
    return L


# ### 清空分配信息
# 包括节点和线网中的分配信息

# In[9]:


def clearAssignInfo(vertex,vertexname,nets):
    for nodeInd in range(len(vertexname)):
        vertex[vertexname[nodeInd]].assignment = None
    for onenet in nets:
        onenet.assignment = set()


# In[10]:


# 产生N个染色体的初始群体,保存在pop里
# 每个染色体代表资源分配问题的某一个解
def initPop(N):
    pop = []
    pop_nets = []
    for i in range(N): #使用随机函数生成N个染色体
        item = fenpeiMethod(vertex,nosFPGA,vertexname,nets)
        pop.append(item[0])
        pop_nets.append(item[1])
    return pop,pop_nets


# In[11]:


# 计算方差
def calVariance(pop):
    variance = []
    for oneSituation in pop:
        variance.append(np.std(ziyuanCal(oneSituation)))
    return variance


# In[12]:


# 计算板间连线
def calLinkSum(pop_nets):
    linkSum = []
    for oneSituation in pop_nets:
        linkSum.append(sum(linkCal(oneSituation,nosFPGA)))
    return linkSum


# In[13]:


# 根据所有染色体分别代表衡量分配好坏的值，计算各个染色体的适应值fitness
def calFitness(lst):
    fitness = []
    for i in lst:
        fitness.append(1/i)
    return fitness


# In[14]:


# 寻找最高适应值的染色体返回其在Pop中对应的下标及方差
def findBest(pop,fitness):
    f = max(fitness)
    ind = fitness.index(f)
    bst = pop[ind]
    return [bst,f,ind]


# In[15]:


#第一个问题的选择算法
# 根据染色体的适应值，按照一定的概率，生成新一代染色体群体newpop
def chooseNewP1(pop,fitness):
    ranNum = random.randint(1,N) #生成随机数
    sumFitness = sum(fitness)    #生成适应性的总和 不使用平均值与单个染色体进行比对 以防进入局部最优解 
    newPop = copy.copy(pop)      #复制染色体集进行选择, 此处数组0是因为在vp中浅拷贝列表会生成一个元组
    for i in range(ranNum):
        del newPop[100 - ranNum: 100]  
        newPop.extend(initPop(ranNum)[0])
        newFitness = calFitness(calVariance(newPop))
        if(sum(newFitness) > sumFitness): #若新的染色体表现更好 则选择新生成的染色体
            pop = newPop
            fitness = newFitness
            break
    return pop,fitness


# In[16]:


#第二个问题的选择算法
# 根据染色体的适应值，按照一定的概率，生成新一代染色体群体newpop
def chooseNewP2(pop,fitness):
    ranNum = random.randint(1,N) #生成随机数
    sumFitness = sum(fitness)    #生成适应性的总和 不使用平均值与单个染色体进行比对 以防进入局部最优解 
    newPop = copy.copy(pop)      #复制染色体集进行选择, 此处数组0是因为在vp中浅拷贝列表会生成一个元组
    for i in range(ranNum):
        del newPop[100 - ranNum: 100]  
        newPop.extend(initPop(ranNum)[0])
        fake_pop_nets = updateNets(newPop)  #这里必须使用一个伪pop_nets，经过选择后才能决定他是否能够选择为真的nets
        newFitness = calFitness(calLinkSum(fake_pop_nets))
        if(sum(newFitness) > sumFitness): #若新的染色体表现更好 则选择新生成的染色体
            pop = newPop
            fitness = newFitness
            break
    return pop,fitness


# ### 交叉生成新群体

# In[17]:


def crossPop(pop,pc):
    lst=list(range(N))
    np.random.shuffle(lst)
    i = 0
    while i < 4: #实测此处如果 i 取到 4以上直接跑崩 遗传算法太吃资源了 不信可以改一下
        rval = np.random.rand()
        j = np.random.randint(int(N/2),N)
        if rval > pc:
            continue
            
        partner1 = copy.copy(pop[lst[i]])
        partner2 = copy.copy(pop[lst[j]])
        OVpartner1 = copy.copy(sum(partner1, []))  # 把处理的二维数据转换成一维属于以便于交叉
        OVpartner2 = copy.copy(sum(partner2, []))
        divIndex1 = []  # 记录下分离前的分离索引
        divIndex2 = []
        index1 = 0;
        index2 = 0;
        for i in range(nosFPGA):
            divIndex1.append(len(partner1[i]))
        for i in range(nosFPGA):
            divIndex2.append(len(partner2[i]))
        
#         print(partner1)
#         print(OVpartner1)
        child1,child2 = genecross(OVpartner1,OVpartner2)
        
        
        # 化为二维数组
        newChild1 = []
        newChild2 = []
        for i in range(nosFPGA):
            index1 += divIndex1[i]
            index2 += divIndex1[i]
            newChild1.append(child1[index1 - divIndex1[i]: index1])
            newChild2.append(child2[index2 - divIndex2[i]: index2])
        pop[lst[i]] = copy.copy(newChild1)
        pop[lst[j]] = copy.copy(newChild2)
        i = i+1
    return pop


# ### 生成两个子染色体

# In[18]:


# 生成两个子染色体child1,child2
def genecross(partner1,partner2):
    length = len(partner1)	
    idx1=0
    idx2=0
    while idx1==idx2:
        idx1 = random.randint(0,length-1)
        idx2 = random.randint(0,length-1)
    ind1 = min(idx1,idx2)
    ind2 = max(idx1,idx2)
    
    child1 = copy.copy(partner1)
    child2 = copy.copy(partner2)
    
    tem1 = copy.copy(child1[ind1:ind2])
    tem2 = copy.copy(child2[ind1:ind2])
    
    if (tem1==tem2):
        return [child1,child2]
    if set(tem1)==set(tem2):
        child1[ind1:ind2] = tem2
        child2[ind1:ind2] = tem1
        return [child1,child2]
        
    temdff1 = set(tem1).difference(set(tem2)) #排序后不一样的元素
    temdff2 = set(tem2).difference(set(tem1))

    #此处改写了源程序中TSP算法的源码，优化了代码
    try:
        for i in range(len(temdff1)):
            child1[child1.index(list(temdff2)[i])]=list(temdff1)[i]
            child2[child2.index(list(temdff1)[i])]=list(temdff2)[i]
    except:
        return [partner1,partner2]
    
    child1[ind1:ind2] = tem2
    child2[ind1:ind2] = tem1
    return [child1,child2]


# ### 变异

# In[19]:


#通过变异的方式生成新群体 
#每一次变异很大概率得到更优染色体
def mutPop(pop,pw):
    for i in range(N):
        rval = random.random()
        if rval > pw:
            continue
        F = copy.copy(pop[i])
        var = ziyuanCal(F)
        minIndex = var.index(min(var))
        maxIndex = var.index(max(var))
        changeLen = int(min(len(F[minIndex]), len(F[maxIndex]))/3)
        F[minIndex][0: changeLen], F[maxIndex][0: changeLen] = F[maxIndex][0: changeLen],F[minIndex][0: changeLen]
        pop[i] = F
    return pop


# In[20]:


# 根据现有pop更新对应的线网pop用于后续计算板间连线
def updateNets(pop):
    pop_nets = []
    for i in range(N):
        copy_nets = copy.deepcopy(nets)
        for i in range(len(vertex)):
            for onenet in copy_nets:
                if vertexname[i] in onenet.nodelist:
                    onenet.assignment.add(vertex[vertexname[i]].assignment)   
        pop_nets.append(copy_nets)
    return pop_nets


# In[21]:


#满足要求
def satified(fitness):
    return 0


# ## 执行代码
# 读取文件

# In[22]:


# 读取节点文件
filename = "./contest/testdata-0/design.are"
vertex,vertexname = readNodeFile(filename)


# In[23]:


# 读取线网文件
filename = "./contest/testdata-0/design.net"
nets = readNetFile(filename,vertex)


# 设定参数

# In[24]:


nosFPGA = 4 	# FPGA的个数
N = 100		# 染色体群体规模
MAXITER = 2	# 最大循环次数 不超过100不然资源不够
pc = 0.9		# 交叉概率
pw = 0.1		# 变异概率


# 把结果文件打开

# 第1种情况：

# In[25]:


filename = "./result.res"
f = open(filename,'w')
clearAssignInfo(vertex,vertexname,nets)
pop = initPop(N)[0]               #pop初始化种群
variance = calVariance(pop)    #计算所有情况的方差
fitness = calFitness(variance) #计算出所有情况下的适应值
iter=0
while iter < MAXITER:
    iter = iter+1
    pop,fitness = chooseNewP1(pop,fitness)  #选择
    pop = crossPop(pop, pc)                #交叉
    pop = mutPop(pop, pw)                  #变异
    pop[0] = findBest(pop,fitness)[0] #保留最强一代
    
    if satified(fitness):             #满足某个要求可以推出
        break
writeResult(pop[0],vertexname)
f.write(str(np.std(ziyuanCal(pop[0])))+"\n")
print(calVariance(pop)[0])
print(sum(ziyuanCal(pop[0])))         #用于第三问


# 第2种情况：

# In[26]:


clearAssignInfo(vertex,vertexname,nets)
pop, pop_nets = initPop(N)               #pop初始化种群\
linkSum = calLinkSum(pop_nets)           #计算所有情况的板连接
fitness = calFitness(linkSum)            #计算出所有情况下的适应值
iter=0
index = 0                     #用于标注最优解在pop中的序号
maxFitness = 0                #记录最大适应值
while iter < MAXITER:
    iter = iter+1
    pop,fitness = chooseNewP2(pop,fitness)  #选择
    pop = crossPop(pop, pc)                #交叉
    pop = mutPop(pop, pw)                  #变异
    pop_nets = updateNets(pop)             #更新连接图
    

    linkSum = calLinkSum(pop_nets)           #计算所有情况的板连接
    fitness = calFitness(linkSum)            #计算出所有情况下的适应值
    pop[0],maxFitness,index = findBest(pop,fitness) #保留最强一代
    pop_nets[0] = pop_nets[index]
    
    if satified(fitness):             #满足某个要求可以推出
        break
writeResult(pop[0],vertexname)
f.write(str(calLinkSum(pop_nets)[0])+"\n")
print('t2')
print(calLinkSum(pop_nets)[0])


# In[27]:


#删除不符合要求项
def filterPop(pop):
    for i in range(N):
        for j in ziyuanCal(pop[i]):
            if(Zmin<= j <= Zmax):
                pop[i] = []                #删除不符合要求项
    return pop

#补充染色体
def supply(pop):
    for i in range(N):
        if(pop[i] == []):
            pop[i] = fenpeiMethod(vertex, nosFPGA, vertexname, nets)[0] #随机补全
    pop_nets = updateNets(pop)             #更新连接图
    return pop


# 第3种情况：

# In[28]:


Zm = 497/4
Zmax = Zm * 1.1
Zmin = Zm * 0.9
clearAssignInfo(vertex,vertexname,nets)
pop, pop_nets = initPop(N)               #pop初始化种群\
linkSum = calLinkSum(pop_nets)           #计算所有情况的板连接
fitness = calFitness(linkSum)            #计算出所有情况下的适应值
iter=0
index = 0                     #用于标注最优解在pop中的序号
maxFitness = 0                #记录最大适应值
while iter < MAXITER:
    iter = iter+1
    pop,fitness = chooseNewP2(pop,fitness)  #选择
    pop = crossPop(pop, pc)                #交叉
    pop = mutPop(pop, pw)                  #变异
    pop_nets = updateNets(pop)             #更新连接图
    linkSum = calLinkSum(pop_nets)           #计算所有情况的板连接
    fitness = calFitness(linkSum)            #计算出所有情况下的适应值
    pop = filterPop(pop)                   #筛选
    
    pop[0],maxFitness,index = findBest(pop,fitness) #保留最强一代
    pop_nets[0] = pop_nets[index]
    
    pop = supply(pop)                      #补充以至于进入下一次循环有充足染色体进化
    
    if satified(fitness):             #满足某个要求可以推出
        break
writeResult(pop[0],vertexname)
f.write(str(calLinkSum(pop_nets)[0])+"\n")
print(calLinkSum(pop_nets)[0])
print(ziyuanCal(pop[index]))           #看看是否满足题目要求


# 关闭文件

# In[29]:


f.close()

