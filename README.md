# itslaw
年\裁判类型\文书类型

1994-2019
#conditions

caseTypeResults
courtLevelResults
judgementTypeResults
topCourtResults
topReasonResults
topCourtResults
trialRoundResults


keywordResults

# related
根据现有id抓取相关案件的id

start: 已经抓取到有详细数据的但是没有抓取相关的id
id: 已经抓取了相关id的id
crawled: 抓取到但是没有详细数据的id

手动更新start-crawled, 防止异常丢失数据

# speed
10000: 2分钟
100000: 20分钟
300000: 1小时
3000000: 10小时, 3百万, 2100万70个小时
3000万: 100小时

# 按条件过滤
搜索词不是必要的
年份1000-2020 -> 案由1013 -> 文书性质5 -> 审理程序4 -> 地域3462
