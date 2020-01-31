# StockAnalysisSystem
This program is designed for Chinese market and Chinese accounting policies (currently). So this document will only provide Chinese version.
  
# 股票分析系统
  
更确切的说，应该叫上市公司财报分析系统。当初写这个程序的目的就是能够快速高效地分析和排除上市公司。这一想法来源于《手把手教你读财报》里的一句话：财报是用来排除公司的。
现在量化非常流行，但比较流行的做法还是将技术分析程序化。常见的开源库也专注于获取交易数据。然而本人还是倾向于稳，所以从去年开始学习财务知识和财务分析方法，希望通过寻找优秀的股票，以稳定的增长达到财富自由。
  
好了梦想说完了，下面是程序的说明。
  
----------------------------------------------------------------------------------------------------------------------
  
# 本程序的目的：
1. 自动选择合适的数据抓取模块和数据源下载所需要的数据  
2. 数据抓取模块能够进行有效性检测，并且能够方便地扩充和替换，可以通过适配器接入其它的库  
3. 增加一个数据源以及将其本地化所需的代码应尽可能少  
4. 能进行离线分析  
5. 分析模块（策略模块）应该可以动态扩充和组合  
6. 最终能生成矩阵式excel报告：以证券为行，以分析方法为列，相交点为此分析方法对此证券的评分；最后一列为该证券的总分  
  
----------------------------------------------------------------------------------------------------------------------
  
# 使用方法及软件依赖与配置
## 环境及软件依赖
1. 使用python3，推荐python3.7. IDE推荐pycharm（如果需要调试）：https://www.jetbrains.com/pycharm/download/#section=windows  
2. 依赖pandas，推荐使用anaconda的环境：https://www.anaconda.com/distribution/  
3. 需要安装sqlite：https://www.sqlite.org/index.html  
4. 需要安装mongodb（免费的社区版即可）：https://www.mongodb.com/what-is-mongodb  
5. 当前数据采集依赖于tushare的pro接口（未来会加入其它采集方式）  
> 1.1 在当前运行的python环境中安装tushare：pip install tushare  
> 1.2 注册一个tushare的账号：https://tushare.pro/register?reg=271027  
> 1.3 想办法获取500以上的积分（如果没有，无法更新数据，但可以使用离线数据）：https://tushare.pro/document/1?doc_id=13  
> 1.4 获取你的token并填入config.py：https://tushare.pro/document/1?doc_id=39  
  
# 软件配置
1. 将tushare的token填入config.py 
2. 将mongodb的配置信息填入config.py 
3. 将Data/mongodb.zip解压，并导入mongodb
> 如果不做1，则无法更新数据，但已下载的数据可以正常使用
> 如果不做2和3，则需要自己下载数据，建议将Data/sAsUtility.db一并删除
  
----------------------------------------------------------------------------------------------------------------------
  
# 开发计划：
1. 生成EXCEL格式的报告 -> 20200129: Done  
2. 编写数据更新的管理界面  -> 20200130: Done
> 已加入显示更新进度功能  
> 硬编码过多，待重构数据结构解决  
3. 编写策略选择界面  -> 20200131: Done
4. 策略运行进度显示
5. 界面集成
6. 策略参数可配置可保存  
















