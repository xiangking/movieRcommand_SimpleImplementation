#coding= utf-8

from pprint import pprint
from math import sqrt
import pickle


#数据读取函数
def readData(file, n=0, transf=False):

    dataStore = []
    #使用迭代器来读取一行
    for line in file:
        #丢弃换行
        line=line.strip('\n')
        #以::作为分割标志分割
        temp = line.split("::")
        if transf:
            temp[n-1] = float(temp[n-1])
        #将其放到data上
        dataStore.append(temp[:n])

    return dataStore


#相似度的衡量*************************************************************************************************************
# 欧几里得距离
# 输入： prefs：类似于critics的二维数组；
#       person1：指定的用户；
#       person2：其他用户；
# 返回： 欧几里得距离

def sim_distance(prefs, person1, person2):
    '欧几里得距离计算函数'

    si = {} #相似度
    #迭代用户的每一步项目ID字典（在本例中就是电影）
    for itemId in prefs[person1]:
        #如果该电影ID在另一个用户的项目字典中
        if itemId in prefs[person2]:
            #那么将这个项目ID的相似度加1
            si[itemId] = 1

    #如果遍历结束还是没有相同的项目，返回0
    if len(si) == 0: return 0

    #定义不断加合的平方差
    sum_of_squares = 0.0

    # 计算距离
    # for item in si:
    # sum_of_squares =  pow(prefs[person1][item] - prefs[person2][item],2) + sum_of_squares
    # sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2) for item in prefs[person1] if item in prefs[person2]])

    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2) for item in si])

    return 1 / (1 + sqrt(sum_of_squares))



# 皮尔逊相关度
# 输入： prefs：类似于critics的二维数组；
#       p1：指定的用户；
#       p2：其他用户；
# 返回： 皮尔逊相关度

def sim_pearson(prefs, p1, p2):
    '皮尔逊相关度计算函数'

    si = {} #相似度
    # 迭代用户的每一步项目ID字典（在本例中就是电影）
    for item in prefs[p1]:
        # 如果该项目ID在另一个用户的项目字典中
        if item in prefs[p2]:
            si[item] = 1

    # 如果遍历结束还是没有相同的项目，返回0
    if len(si) == 0: return 0


    #计算它们相同项目的个数
    n = len(si)

    #将一个用户中每一个与另一个用户相同的项目找出来，然后将它们全部加和
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    #将一个用户中每一个与另一个用户相同的项目找出来，然后将它们的平方全部加和
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])

    #将两个用户间相同的项目找出来，然后将它们相乘
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])


    num = pSum - (sum1 * sum2 / n)

    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    # 计算结束

    #然后den为0，就返回0
    if den == 0: return 0

    r = num / den

    return r


#数据处理*************************************************************************************************************


#生成二维字典
# 输入：  Data 评分数据表[（用户ID，电影ID，评分，时间）,... ] 或者 电影表[（电影ID，电影名，类型）,... ]
# 返回：  {用户ID：{电影ID：评分}} 或者 {电影ID：{电影名：类型}}

def buildInherentDict(Data):
    'buildInherentDict用以生成二维字典'
    user_Mrate_dic={}

    for lineData in Data:
        # 用户对电影的评分表,形式是 {用户ID：{电影ID：评分}}
        # 如果该用户不在字典中，那么添加该用户
        if lineData[0] in user_Mrate_dic:
            user_Mrate_dic[lineData[0]][lineData[1]] = lineData[2]

        # 如果该用户已经在字典中那么就要{电影ID：评分}添加上去
        else:
             user_Mrate_dic[lineData[0]] = {}
             user_Mrate_dic[lineData[0]][lineData[1]] = lineData[2]

    # 返回：{用户ID：{电影ID：评分}}
    return user_Mrate_dic




# 转换功能的函数，将基于用户的转换成基于物品的列表
#从这里的角度来说，prefs应该是基于用户的列表
# 输入： prefs：类似于critics的二维字典；
# 返回： 返回基于物品的列表{项目：{人：评分}}表

def transformPrefs(prefs):
    '构建{项目：{人：评分}}形式的二维字典'
    itemList = {}

    for person in prefs:
        for item in prefs[person]:
            # 如果这个项目还没有被登记过，那么就登记它到itemList字典中

             if not itemList.has_key(item):
                itemList[item] = dict()

             # 将人的评分加入字典中
             itemList[item][person] = prefs[person][item]

    # 返回基于物品的列表
    return itemList



# 寻找最近邻（可以用来寻找用户和用户之间最接近的人还可以用来寻找物品和物品之间最接近的物品）
# 输入： prefs：类似于critics的二维数组；
#       person：指定的用户；
#       n：所推荐的用户的个数，即找到最相似的几个用户；
#       similarity：使用的度量相似度的公式；
# 返回： 最近邻

def topMatches(prefs, person, n=5, similarity=sim_distance):
    '推荐的用户，也就是一般书上的最近邻'

    #先for other in prefs：得到其他用户ID
    #if other != person：判断不是与指定用户是同一个人
    #计算它们的相似度，scores的形式是[（相似度，用户ID）]
    scores = [(similarity(prefs, person, other), other) for other in prefs if other != person]
    scores.sort(reverse=True)

    #返回相似度最高的几个（相似度，项目（或者用户））
    return scores[0:n]



# 构建基于物品相似度相似矩阵，也就是基于每个项目的评价，判断他们之间的相似度
#从这里的角度来说，prefs应该是基于用户的列表
# 输入： prefs：类似于critics的二维字典；
#       n: 寻找几个最接近的
# 返回： 构建基于物品相似度数据集{项目：[（相似度，项目），......]}

def calculateSimilarItems(prefs, n=20):
    result = {}
    itemPrefs = transformPrefs(prefs)

    #从基于物品的列表中取得得到每一个键值，也就是项目
    for item in itemPrefs:

        #使用寻找最近邻的方法来找到相似的物品
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_pearson)

        result[item] = scores
    #关于物品相似度的二维字典
    return result




#额外功能*******************************************************************************************************************


# 得到所需要得本地储存格式的数据表
# 输入：  itemList： 物品的列表{项目：{人：评分}}
#        movieDict：电影列表{电影ID：{电影名：类型}}
# 返回：  { 电影ID: [电影名，评分，电影类型，评分人数],... }

def averageMovie(itemList, movieDict):
    '得到所需要得本地储存格式的数据表'

    averageRate = {} #平均评分存放表
    rateNum = {}     #评分人数存放表

    idmovieRate = {} #最终存放表

    # 从物品列表中得到键（对字典使用for遍历获得的是键，不是其对于的东西）
    for movie in itemList:
        # 如果该电影不在averageRate表中，则averageRate和rateNum表都创建新的一项
        if movie not in averageRate:
            averageRate[movie] = 0
            rateNum[movie] = 0

        # 得到该movie所对于的用户评分表，累计
        for user in itemList[movie]:
            averageRate[movie] += itemList[movie][user]
            rateNum[movie] += 1

    # 得到平均评分表
    for movie in averageRate:
        averageRate[movie] = averageRate[movie] / rateNum[movie]


    # 将未有人评分的电影加入表中，并制成新表{ 电影ID: [电影名，评分，电影类型，评分人数],... }
    for movie in movieDict:
        # 如果未有用户评分，则将其的得分记为-1
        if movie not in averageRate:
            temp = -1
            rateNumber = 0

        # 否则就按实际记入
        else:
            temp = averageRate[movie]
            rateNumber = rateNum[movie]

        # 添加一项加入新表
        for movieName in movieDict[movie]:
            idmovieRate[movie] = [movieName, movieDict[movie][movieName], temp, rateNumber]

    # 使用lambda和sorted进行排序，按分数从高到低
    idmovieRate = sorted(idmovieRate.items(),key= lambda item: item[1][2], reverse=True)

    # 返回{ 电影ID: [电影名，评分，电影类型，评分人数],... }
    return idmovieRate


#预加载数据*******************************************************************************************************************


# open函数打开.DAT文件
fileMovie = open("/Users/macbook/PycharmProjects/Project/DataMovie/movies.dat", 'r')
fileRating = open("/Users/macbook/PycharmProjects/Project/DataMovie/ratings.dat", 'r')

# 使用read读数数据
movieData = readData(fileMovie, n=3) #[(电影ID，电影名称，电影类型]
ratingData = readData(fileRating,n=3, transf=True) #[(用户ID，电影ID，评分）,......]


inherentDict =  buildInherentDict(ratingData)
movieDict = buildInherentDict(movieData)

list = transformPrefs(inherentDict)

# 得到最近使用带平均分的表，将它的名字记为数据库表
averageList = averageMovie(list,movieDict)

## 取出保存的相似矩阵
pkl_file = open('/Users/macbook/PycharmProjects/Project/DataMovie/sim_itemVector2.pkl','rb')
sim_itemVector = pickle.load(pkl_file)



