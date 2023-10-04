# 介绍
关于这个东西可以看[这篇文章](https://www.thewhitedog9487.xyz/2023/07/31/%e8%bf%91%e4%ba%8b%e5%b0%8f%e8%ae%b0-%e5%8d%9a%e5%ae%a2%e5%8f%91%e7%9a%84%e8%af%84%e8%ae%ba%e5%8f%af%e4%bb%a5%e5%8f%8a%e6%97%b6%e9%80%9a%e7%9f%a5%e5%88%b0%e6%88%91%e4%ba%86)

# 适用平台
WordPress  
没别的原因，只是因为我自己在用而已。  

# 依赖项
需要pip里的discord.py包。
```shell
# Windows用户看这边~
pip install discord.py
# Linux用户看这边~
# 我自己用的是Ubuntu，所以是apt
apt install python3-discord
```

# 部署
从仓库下载"WordPress评论监控.py"，打开。  
首次运行会直接退出，目录下多出来一个json配置文件，打开。  
URL：要监测博客的地址，可以是IP或域名，必须加http://或者https://，末尾不要加/  
_DiscordConfig__Bot_Token：机器人的令牌  
注：不用在意这个属性的名称为什么看起来很奇怪，受保护的类型序列化之后是这样的。  
Channel_Message：如果你希望机器人在一个服务器的频道内提醒你，这里就填true；如果你希望机器人私信你，那就填false。  
Admin_User_ID：选择私信提醒的朋友，这里填上你的Discord用户ID，选择频道提醒的不用理会。  
Channel_ID：选择频道提醒的朋友，这里填上你想让机器人发送消息的频道ID，选择私信提醒的不用理会。  
Ignore_List：如果你希望某一位或某些用户发送评论时你不会收到通知，就把他（们）用户名填入这个列表内，逗号分隔。  
注意：Admin_User_ID和Channel_ID直接写数字就行，不用像上面的Token那样加引号。Channel_Message直接填true或false，也不要加引号。  
    
填写完成之后应该大致长这样：
```json
{
  	"Ignore_List":["TheWhiteDog9487","twd"],
  	"URL":"https://www.thewhitedog9487.xyz",
	"_DiscordConfig__Bot_Token":"MTA4ODA2OTI5Nzg2MTA1MDQ0OA.GZkIBA.-11qdvzOz5o3zFiC-pW1YjbpFOaa93Q1vycOYg",
	"Admin_User_ID":785275297272909078,
	"Channel_ID":4987138441723578956,
	"Channel_Message":true
}
```
( 献祭一下以前的令牌，来这当下例子  

这个时候就已经可以跑起来了。  
但是，如果每次重启设备后都是人工去开启程序，非常麻烦且不必要，非常的不人性化。  
所以，我的建议是，把这个东西注册成一个服务。  
Windows用户考虑下计划任务（我没实际用过，仅提供可能的建议）  
Linux用户可以考虑用service文件，格式参考[这个](https://github.com/TheWhiteDog9487/WordPressCommentWatcher/blob/main/WordPressCommentWatcher.service)  
```ini
[Unit]
Description=WordPress评论监控
After=multi-user.target
[Service]
WorkingDirectory=/home/App
User=root
Type=idle
ExecStart=python3 /home/App/WordPress评论监控.py
Restart=always
[Install]
WantedBy=multi-user.target
```
注意一下里面的WorkingDirectory=和ExecStart=，后面的路径换成你自己程序的位置。  
把这个文件保存下来，假设你的文件路径在/home/App/WordPressCommentWatcher.service  
打开你的终端。  
```shell
ln -s /home/App/WordPressCommentWatcher.service /usr/lib/systemd/system/
# 链接还是复制，随意。
systemctl daemon-reload
systemctl enable WordPressCommentWatcher
systemctl start WordPressCommentWatcher 
# 然后你就可以用 systemctl status WordPressCommentWatcher 来查看服务状态。
```
不出意外的话，应该是没问题了。