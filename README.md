# StockAnalysisSystem
This program is designed for Chinese market and Chinese accounting policies (currently). So this document will only provide Chinese version.

# 股票分析系统

更确切的说，应该叫上市公司财报分析系统。当初写这个程序的目的就是能够快速高效地分析和排除上市公司。这一想法来源于《手把手教你读财报》里的一句话：财报是用来排除公司的。
现在量化非常流行，但比较流行的做法还是将技术分析程序化。常见的开源库也专注于获取交易数据。然而本人还是倾向于稳，所以从去年开始学习财务知识和财务分析方法，希望通过寻找优秀的股票，以稳定的增长达到财富自由。
  
好了梦想说完了，下面是程序的说明。

本程序希望达到以下目的：
1. 能以较为自然的词语获取对应的数据（如库存现金和现金应该取到一样的数据）
2. 能自动从网上下载你所需要的数据
3. 能进行离线分析
4. 数据抓取模块应该可以方便地扩充和替换，甚至通过适配器接入其它的库
5. 分析模块（策略模块）应该可以动态扩充和组合

暂停更新，感觉设计有问题，寻求更好的设计（如bigquant），并期望融合回测框架（如zipline）。

Pause update. Meet design problem. Seeking for a better design.
