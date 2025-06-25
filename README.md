# 介绍
关于这个东西可以看[这篇文章](https://www.thewhitedog9487.xyz/2023/07/31/%e8%bf%91%e4%ba%8b%e5%b0%8f%e8%ae%b0-%e5%8d%9a%e5%ae%a2%e5%8f%91%e7%9a%84%e8%af%84%e8%ae%ba%e5%8f%af%e4%bb%a5%e5%8f%8a%e6%97%b6%e9%80%9a%e7%9f%a5%e5%88%b0%e6%88%91%e4%ba%86)

# 适用平台
WordPress  
没别的原因，只是因为我自己在用而已。

# 部署
克隆本仓库  
```shell
git clone https://github.com/TheWhiteDog9487/WordPressCommentWatcher.git
```
本项目使用uv管理Python环境，请确保你的设备上已经安装，具体请参考[uv的官方文档](https://docs.astral.sh/uv/getting-started/installation/)  
然后，在仓库文件夹下打开终端.
```shell
# 安装项目依赖项
uv sync

# 运行项目
uv run WordPress评论监控.py
```
如果不愿意安装uv，也没关系的喏  
你可以直接使用pip，但我仍然建议你创建一个虚拟环境，而不是在全局安装包  
隔离掉环境污染，好管理一些，也会好看点，对吧？  
```shell
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境  
# Windows用户看这边~
.venv/Scripts/activate.ps1
# ↑ 如果使用命令提示符，就用activate.bat

# Linux用户看这边~
source .venv/bin/activate
# ↑ 如果使用fish，就用activate.fish

# 安装依赖
pip install -r requirements.txt

# 然后运行项目
python3 WordPress评论监控.py
```
首次运行会直接退出，目录下多出来一个json配置文件，打开。  
- URL：要监测博客的地址，可以是IP或域名  
- _DiscordConfig__Bot_Token：机器人的令牌
  - **请务必开启机器人privileged intents中的Message Content项，哪怕你不需要在Discord内回复评论**
- _DiscordConfig__WordPress_Application_Password：WordPress站点上创建的应用密码，如果需要在Discord内回复评论的话需要填写，不需要的话不管就是了

注：不用在意这个属性的名称为什么看起来很奇怪，受保护的类型序列化之后是这样的。  

- Channel_Message：如果你希望机器人在一个服务器的频道内提醒你，这里就填true；如果你希望机器人私信你，那就填false。
- Admin_User_ID：选择私信提醒的朋友，这里填上你的Discord用户ID，选择频道提醒的不用理会。
  - 另外，只有这个用户有权在Discord内回复评论。
  - 如果你不想让机器人私信提醒但是需要在Discord内回复评论，请填写这个属性并将Channel_Message设置为true。
- Channel_ID：选择频道提醒的朋友，这里填上你想让机器人发送消息的频道ID，选择私信提醒的不用理会。
- Ignore_List：如果你希望某一位或某些用户发送评论时你不会收到通知，就把他（们）的用户名填入这个列表内，如果有多个就用逗号分隔。
- WordPress_User_Name：WordPress用户名，如果需要在Discord内回复评论的话需要填写，内容为创建应用密码时的使用的用户的用户名。

注意：Admin_User_ID和Channel_ID直接写数字就行，不用像上面的Token那样加引号。Channel_Message直接填true或false，也不要加引号。  
    
填写完成之后应该大致长这样：
```json
{
	"URL":"https://www.thewhitedog9487.xyz",
	"_DiscordConfig__Bot_Token":"MTA4ODA2OTI5Nzg2MTA1MDQ0OA.GZkIBA.-11qdvzOz5o3zFiC-pW1YjbpFOaa93Q1vycOYg",
	"Admin_User_ID":531317938863603722,
	"Channel_ID":1141585619819188244,
	"Channel_Message":true,
	"Ignore_List": ["TheWhiteDog9487"],
    "_DiscordConfig__WordPress_Application_Password": "a3DB 7J4q 8d3b 9f2c 6e5a 1c2b",
    "WordPress_User_Name": "TheWhiteDog9487"
}
```
( 献祭一下以前的令牌，来这当下例子  
**警告：本项目不保证配置文件向后兼容**

这个时候就已经可以跑起来了。  
但是，如果每次重启设备后都是人工去开启程序，非常麻烦且不必要，非常的不人性化。  
所以，我的建议是，把这个东西注册成一个服务。  
Windows用户考虑下计划任务（我没实际用过，仅提供可能的建议）  
Linux系统上实现了Systemd服务的自动安装与卸载：
- 安装  
    给脚本添加install参数，将systemd服务自动安装到系统内。  
    ```shell
    uv run WordPress评论监控.py install
    # 如果你使用虚拟环境+pip，记得首先激活你的虚拟环境，然后像这样喏（￣︶￣）↗　
    python3 WordPress评论监控.py install
    ```
    这会同时设置服务为开机自启并启动服务。  
    安装完成之后可以使用下面的命令查看服务状态：  
    ```shell
    systemctl status WordPressCommentWatcher
    ```
- 卸载
    使用uninstall参数。  
    ```shell
    uv run WordPress评论监控.py uninstall
    # 虚拟环境版本的命令，和上面install那边一样喏
    python3 WordPress评论监控.py uninstall
    ```
    
