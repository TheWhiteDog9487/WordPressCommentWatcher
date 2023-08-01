# 介绍
关于这个东西可以看[这篇文章](https://www.thewhitedog9487.xyz/2023/07/31/%e8%bf%91%e4%ba%8b%e5%b0%8f%e8%ae%b0-%e5%8d%9a%e5%ae%a2%e5%8f%91%e7%9a%84%e8%af%84%e8%ae%ba%e5%8f%af%e4%bb%a5%e5%8f%8a%e6%97%b6%e9%80%9a%e7%9f%a5%e5%88%b0%e6%88%91%e4%ba%86)

# 部署
从仓库下载"WordPress评论监控.py"，打开。  
看一下里边的注释，有两个地方需要换成你自己的信息。  

# 依赖项
需要pip里的discord.py包。
```shell
# Windows用户看这边~
pip install discord.py
# Linux用户看这边~
# 我自己用的是Ubuntu，所以是apt
apt install python3-discord
```

# 定时器
本程序不负责定时调用，所以需要你来处理。  
Linux用户可以用cron，Windows我没具体试过所以自己查一下咋整。  
## 注意事项
如果你要用cron做定时器，注意会有一些问题。  
如果你直接在cron里写  
```cron
* * * * * python3 WordPress评论监控.py
```
你会发现日志里有点奇怪，而且完全没有实际功能。  
解决方案是，建一个Shell脚本，比如叫做WordPress评论监控.sh，里面的内容可以这么写：
```bash
#！/usr/bin/bash
cd /home/App/
/usr/bin/python3 WordPress评论监控.py
```
crontab里换成这样：  
```cron
* * * * * python3 WordPress评论监控.sh
```
小提示：5个\*表示每分钟调用一次。  
