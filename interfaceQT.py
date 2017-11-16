# -*- coding: utf-8 -*-


# 基本界面
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import*

from DataMovie.Support import *


# MyGui是使用界面
class MyGui(QDialog):

    #搜索功能
    def serchMovie(self):
        '搜索功能'

        flag = 0 #是否成功搜索到的标志：如果为1，则成功搜索到；否则，搜索失败

        # 清空原来的内容
        self.movieIDEdit.clear()
        self.movieNameEdit.clear()
        self.classEdit.clear()
        self.scoreEdit.clear()
        self.rateNumEdit.clear()

        # 从searchEdit搜索编辑处获得用户想要搜索的电影
        movie = self.searchEdit.text()
        # 将用户输入的内容在数据库表中查询
        # 如果存在，则将flag置为1，且将其显示出来，同时弹出信息框咨询是否加入收藏用以推荐
        # 否则，flag置为0
        for movieData in averageList:
            if movie == movieData[1][0]:
                flag = 1
                self.movieIDEdit.setText(movieData[0])
                self.movieNameEdit.setText(movieData[1][0])
                self.classEdit.setText(movieData[1][1])
                self.scoreEdit.setText(str(movieData[1][2]))
                self.rateNumEdit.setText(str(movieData[1][3]))
                # 消息框
                self.msg(self)

        # 如果flag为0，弹出警告
        if flag == 0:
            self.msgW(self)


    # 弹出的是否加入收藏的消息框
    def msg(self, event):
        '是否加入收藏的消息框'

        # 设计QMessageBox的内容
        # 用reply来接收用户所选择的选项
        reply = QMessageBox.question(self, 'Message', '是否加入收藏',
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        # 如果选项为是，则将用户所搜索的电影加入userFavorites用户收藏中
        if reply == QMessageBox.Yes:
            if self.movieIDEdit.text() in self.userFavorites:
                pass
            else:
                self.userFavorites.append(self.movieIDEdit.text())

            print self.userFavorites

        # 否则，如果该电影存在于用户收藏中就将其删去，不在的话就PASS
        else:
            if self.movieIDEdit.text() in self.userFavorites:
                self.userFavorites.remove(self.movieIDEdit.text())



    # 弹出警告框
    def msgW(self, event):
        '警告'
        QMessageBox.warning(self, 'Warning', '您输入的电影名有误')





    #推荐功能
    #本版本的推荐仅通过物品的相似度进行推荐，暂未使用用户评分机制
    def getRecommendedItems(self):

        # 电影的得分表
        scores = {}

        # items返回可遍历的（键，值）在这里是（电影，评分）
        for item in self.userFavorites:
            # 得到每一个（相似度，其他项目）
            if item not in sim_itemVector.keys():
                continue
            else:
                for (similarity, item2) in self.sim_itemVector[item]:
                # 如果这个项目已经在指定用户所拥有的列表里，舍弃这个项目（比如指定用户已经看过这部电影，那推荐也就没有意思）
                    if item2 in self.userFavorites: continue

                # 如果没有在指定用户的列表里，使用setdefault设置键item2，值为0
                    scores.setdefault(item2, 0)
                # 计算相似度*评分，并加合作为该项目的推荐度
                # （这里就是用户对这个项目的好感度怎么样*相似度；比如如果用户对一部电影很喜欢，那么对和它相似的电影可能也会很喜欢）
                    scores[item2] += similarity


        # 得到推荐的项目的得分
        rankings = [(score, item) for item, score in scores.items()]

        # Return the rankings from highest to lowest
        rankings.sort(reverse=True)

        # 如果推荐数大于5，则取前五个将其显示出来
        if len(rankings) > 5:
            # 清空rankingTabel
            self.rankingTabel.clear()
            # 重新设置标题
            self.rankingTabel.setHorizontalHeaderLabels(['电影', '相似度']) # 水平标题
            rankings = rankings[:5]

            # 由于rankings是使用的电影ID，这里将电影ID转化为电影名，并显示
            for i in range(0, 5):
                # 遍历averageList
                for movieData in averageList:
                    # 搜索到电影
                    if rankings[i][1] == movieData[0]:
                        # 控制评分的小数点，这里选择2
                        temp = str(round(rankings[i][0], 2))

                        #设置对齐格式，并显示
                        tempItem = QTableWidgetItem(movieData[1][0])
                        tempItem.setTextAlignment(Qt.AlignHCenter |  Qt.AlignVCenter)
                        self.rankingTabel.setItem(i, 0, QTableWidgetItem(movieData[1][0]))

                        tempItem = QTableWidgetItem(temp)
                        tempItem.setTextAlignment(Qt.AlignHCenter |  Qt.AlignVCenter)
                        self.rankingTabel.setItem(i, 1, tempItem)

        # 如果推荐数小于5，就不打算推荐
        else:
            pass

        # 返回推荐
        return rankings[:5]





    def __init__(self, parent = None):

        QWidget.__init__(self)

        self.userFavorites = [] #存放用户收藏
        self.sim_itemVector = sim_itemVector #得到相似矩阵
        self.averageList = averageList #得到数据库表


        # 得到排行榜所需数据
        def buildRateList(inherentData):
            rateList = []
            num = 0
            # 主要还是本地数据库中评分小于20个的电影去除
            for  movie in inherentData:
                if movie[1][3] < 20:
                    continue
                else:
                    temp = str(round(movie[1][2], 2)) #round函数控制小数点精度，str函数将浮点变为字符串
                    rateList.append([movie[1][0], temp])
                    num += 1

                #只选择5个评分最高的电影即可
                if num > 4:
                    break


            return rateList



        #界面布局********************************************************************************************************
        # 设置应用标题栏
        self.setWindowTitle("RecommendMovie")

        # 搜索结果区布局*************************
        # 界面设计
        movieIDLabel = QLabel('电影ID：')
        self.movieIDEdit = QLineEdit()
        movieNameLabel = QLabel('电影名：')
        self.movieNameEdit = QLineEdit()
        classLabel = QLabel('类型：')
        self.classEdit = QLineEdit()
        scoreLabel = QLabel('评分：')
        self.scoreEdit = QLineEdit()
        rateNumLabel = QLabel('评分人数：')
        self.rateNumEdit = QLineEdit()

        # 使用QGridLayout网格布局来进行布局
        self.serchResultLayout = QGridLayout()
        self.serchResultLayout.addWidget(movieIDLabel, 0, 0)
        self.serchResultLayout.addWidget(self.movieIDEdit, 0, 1)
        self.serchResultLayout.addWidget(movieNameLabel, 1, 0)
        self.serchResultLayout.addWidget(self.movieNameEdit, 1, 1)
        self.serchResultLayout.addWidget(classLabel, 2, 0)
        self.serchResultLayout.addWidget(self.classEdit, 2, 1)
        self.serchResultLayout.addWidget(scoreLabel, 3, 0)
        self.serchResultLayout.addWidget(self.scoreEdit, 3, 1)
        self.serchResultLayout.addWidget(rateNumLabel, 4, 0)
        self.serchResultLayout.addWidget(self.rateNumEdit, 4, 1)




        # 搜索推荐区域
        # 设置搜索推荐区域
        searchLabel = QLabel('电影名')
        self.searchEdit = QLineEdit() # 搜索输入栏

        # 搜索按钮，点击按钮就调用serchMovie方法进行搜索
        searchButton = QPushButton('搜索')
        searchButton.clicked.connect(self.serchMovie)

        # 推荐按钮，点击按钮就调用getRecommendedItems方法进行推荐
        recommendButton = QPushButton('推荐')
        recommendButton.clicked.connect(self.getRecommendedItems)

        # 冷启动：使用评分最高的5项作为推荐
        # 使用buildRateList函数得到rateList排行榜
        rateList = buildRateList(self.averageList)  # 建立排行榜


        # 电影推荐区域*************************

        # 设置区域
        self.rankingTabel = QTableWidget(5, 2)  # 从0开始计数，所以是六行三列（第一行是标题，第一列是序号）
                                                # 所以只算使用部分的话确实是5行2列
        self.rankingTabel.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置编辑权限：禁止编辑
        self.rankingTabel.setColumnWidth(0, 150)  # 第一列的宽度
        self.rankingTabel.setColumnWidth(1, 138)  # 第二列的宽度 45
        # 使用QGridLayout进行布局
        rankingLayout = QGridLayout()  # 格栅布局
        rankingLayout.addWidget(searchLabel, 0, 0)
        rankingLayout.addWidget(self.searchEdit, 0, 1)
        rankingLayout.addWidget(searchButton, 0, 2)
        rankingLayout.addWidget(recommendButton, 0, 3)
        rankingLayout.addWidget(self.rankingTabel, 1, 0, 1, 4)

        # 设置显示内容
        self.rankingTabel.setHorizontalHeaderLabels(['电影', '评分'])  # 水平标题
        # 通过遍历将排行榜数据显示在该区域
        for i in range(0, 5):
            for j in range(0, 2):
                tempItem = QTableWidgetItem(rateList[i][j])
                tempItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.rankingTabel.setItem(i, j, tempItem)



        # 主布局：使用QGridLayout网格布局进行主布局
        mainLayout = QGridLayout()
        mainLayout.addLayout(rankingLayout, 0,0,1,1)
        mainLayout.addLayout(self.serchResultLayout, 0,2,1,1)
        mainLayout.setSizeConstraint(QLayout.SetFixedSize) #固定对话框

        self.setLayout(mainLayout)






# 启动界面
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)


        self.setFixedSize(600, 600)
        self.label = QLabel(self)
        self.label.setFixedWidth(400)
        self.label.setFixedHeight(400)
        self.label.setAlignment(Qt.AlignCenter)


        # 设置启动界面显示的软件名称
        widget = QWidget()

        label = QLabel()
        # pyqt可以使用html格式来设置字体
        label.setText("<font size=%s><B>%s</B></font>" % ("15", "Movie Recommand System"))

        # 设置启动按钮，点击就会直接启动使用界面
        start = QPushButton("Start", self)
        start.setToolTip('Press to recommand movie') #按钮提示
        start.clicked.connect(self.startClicked)

        # 设置退出按钮，按键退出
        quit = QPushButton("Quit", self)
        quit.clicked.connect(QCoreApplication.quit)

        # 改变按钮风格
        self.style = """
                                QPushButton{background-color:grey;color:white;}
                            """
        self.setStyleSheet(self.style)


        #显示背景
        pixMap = QPixmap("film.png").scaled(self.label.width(), self.label.height())
        self.label.setPixmap(pixMap)
        self.label.setFont(QFont("Roman times", 10, QFont.Bold))
        self.label.move(100, 100)



        # 整体布局
        vbox1 = QVBoxLayout()  # 垂直布局
        vbox2 = QVBoxLayout()
        vbox3 = QVBoxLayout()
        vbox4 = QVBoxLayout()


        # 两边空隙填充
        label1 = QLabel()
        label1.resize(60, 60)
        label2 = QLabel()
        label2.resize(50, 50)
        vbox2.addWidget(label)
        vbox1.addWidget(label1)
        vbox3.addWidget(label2)
        vbox4.addWidget(start)
        vbox4.addWidget(quit)
        # 按钮两边空隙填充
        label3 = QLabel()
        label3.resize(50, 50)
        label4 = QLabel()
        label4.resize(50, 50)
        hbox1 = QHBoxLayout()
        hbox1.addWidget(label3)
        hbox1.addLayout(vbox4)
        hbox1.addWidget(label4)
        # 标题与两个按钮上下协调
        label5 = QLabel()
        label5.resize(1, 1)
        label6 = QLabel()
        label6.resize(1, 1)
        label7 = QLabel()
        label7.resize(1, 1)
        vbox2.addWidget(label5)
        vbox2.addWidget(label)
        vbox2.addLayout(hbox1)


        hbox = QHBoxLayout()
        hbox.addLayout(vbox1)
        hbox.addLayout(vbox2)
        hbox.addLayout(vbox3)
        widget.setLayout(hbox)

        self.setCentralWidget(widget)

    # 启动使用界面的方法
    def startClicked(self):
        self.hide()
        self.ui = MyGui()  # 必须将另一个界面改为成员变量，负责MainPage会与函数调用周期一样一闪而过
        self.ui.show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    splash = QSplashScreen(QPixmap("hello.ico"))
    splash.show()
    mainwindow = MainWindow()
    mainwindow.show()
    splash.finish(mainwindow)
    sys.exit(app.exec_())
