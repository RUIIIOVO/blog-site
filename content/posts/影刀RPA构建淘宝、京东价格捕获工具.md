---
title: "影刀RPA构建淘宝、京东价格捕获工具"
date: 2026-04-08T10:42:51+08:00
draft: false
---

最近玩了下影刀RAP，查询了下影刀公开的RAP工作流，似乎没有很新的价格捕获工具，因此博主做了这次尝试，记录一下

整体的流程和爬虫中的selenium有点像，博主是初步搭建了在淘宝、京东查询商品并捕获店铺名称、商品名称、详情链接和价格后，将信息存储到excel的工作流，还没有做分页点击获取，大家有好的建议可以评论下

先看效果：

[video(video-33ENHSLi-1773302011262)(type-csdn)(url-https://live.csdn.net/v/embed/517002)(image-https://i-blog.csdnimg.cn/img_convert/e04ab7ae9cfd161fcebd74aa02835ff3.jpeg)(title-影刀RAP淘宝、京东价格捕获工具演示)]

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/caabd3a7e3a842549c7f67e98476f5f3.png)


整体的设计流程如下：
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/ff7d99a24cf847b798af82e30704d7dd.png)
注意，需要在chrome浏览器先登录好淘宝以及京东，否则无法执行

下面是详细配置信息：
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/ec6c43aa35914744bdd364caa274b820.png)

https://search.jd.com/Search?keyword=input_dialog.value
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/2bf3e14e57e44b6eb32a160a620fd45f.png)
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/b8be8976707c4e5fbea7dbc3f736859a.png)
数据列表在配置中选择“批量获取数据”，在京东或淘宝选择自己要获取的元素即可，若需要获取商品详情链接，点击表格旁边的提取链接即可

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/8bcee053458b4ccd896a9ff965554ee8.png)
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/639726a895834eddb4e46d31acd6abcc.png)
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/f1672a7fe55341229df6bd73207702f6.png)
https://s.taobao.com/search?q=input_dialog.value
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/3b6eb3b4545f4faa90df06233389c189.png)
淘宝和京东同理
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/d8598848b3ed45d7b5887c1ea0a497a3.png)
注意这里的新建路径需要自己调整下，博主设置的是桌面
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/b475ea8f01dc4d51974c5edcff251cd3.png)
插入表头：
["店铺名称","商品名称","商品链接","价格"]
注意这里需要点击一下python的图标，不然不会生效
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/c46b817f3c6042deabad44b5dc504508.png)
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/5ed66688da204fc3b6813184d192eb00.png)

若不需要筛选和排序功能可以删除，这里的排序可以叠加，点击python图标开启python模式，再以列表的形式写入即可（详细的可以看官方的使用说明）
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/fe79292eedaf4d8fa68102c0c1eeee1a.png)
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/175b7f5fc4e240209bffab7901e401c7.png)
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/ddc71c5fa75a43a1950b4a8d0a952f1c.png)
配置完毕之后点击运行即可，创作不易，帮忙点个赞吧~
