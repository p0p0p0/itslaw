# itslaw
年\裁判类型\文书类型
shodan上下载的21142461
3298208 第一次抓取
23823561 共
23823987 工具导出的结果
423 脏数据, 空内容
23823560 个

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
最后超过400的用法官法院过滤即可, 一个地方法院的法官数量不会太多, 一个法官一年的案子也不太可能超过400, 完美解决.
还是需要细致过滤, 从401开始一个一个地确定完成条件组合过滤.
先变换排序确定获取到count量的id, 如果无法获取到全部, 则开始抓取能抓取到的所有id的case, 然后配合法官, 法院过滤.


# conditions
一个结果的: 762136 个case 
两个结果以上且一页以内: 4939779 个case
两页以上但不超过400: 16377601 个case
超过20页的: 11474003 个case
共 33553519 个
网站显示 58853591 个
-25300072

11229164
6775706


# requests
762136
914908
1134197
521720
共 3332961 请求
600 req/min
5555 mins = 93 hours = 4 days