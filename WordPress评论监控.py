import json
import logging
import os
import platform
import sys
import time
import zipfile
from datetime import datetime
from typing import List, Dict

import aiohttp
import discord
import requests
from discord.ext import tasks
from markdownify import markdownify

LogFileName = ""
LogPath = ""
WorkDirectory = ""


class DiscordConfig(object):
    def __init__(self):
        self.Ignore_List: List = []
        self.__Bot_Token: str = ""
        self.URL: str = ""
        self.Admin_User_ID: int = 0
        self.Channel_ID: int = 0
        self.Channel_Message: bool = True

    def From_Dict(self, OriginDict: dict):
        self.Ignore_List = OriginDict["Ignore_List"]
        self.__Bot_Token = OriginDict["_DiscordConfig__Bot_Token"]
        self.URL = OriginDict["URL"]
        self.Admin_User_ID = OriginDict["Admin_User_ID"]
        self.Channel_ID = OriginDict["Channel_ID"]
        self.Channel_Message = OriginDict["Channel_Message"]
        return self

    def Get_Token(self):
        return self.__Bot_Token

    def Set_Token(self, Token: str):
        self.__Bot_Token = Token


class DiscordClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Config = None
        # an attribute we can access from our task

    async def on_ready(self):
        logging.info(f'以{BotClient.user}登录')

    @tasks.loop(minutes=1)
    async def TimerTrigger(self) -> None:
        logging.info(f'现在是{datetime.now().replace().strftime("%Y-%m-%d %H:%M:%S")}，开始检测评论状态。')
        Compress_LogFile()
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.Config.URL}/wp-json/wp/v2/comments') as response:
                response = await response.json()
        with open('最新评论发布时间.txt', 'r+', encoding="utf-8") as f:
            FileCommentDate = f.readline().replace('\n', '')
            FileCommentDate = int(time.mktime(time.strptime(FileCommentDate, '%Y年%m月%d日 %H时%M分%S秒')))
            comment: Dict = response[0]
            '''
              {
                "id": 1,
                "post": 1,
                "parent": 0,
                "author": 0,
                "author_name": "一位WordPress评论者",
                "author_url": "https://wordpress.org/",
                "date": "2020-12-26T21:26:51",
                "date_gmt": "2020-12-26T13:26:51",
                "content": {
                  "rendered": "<p>嗨，这是一条评论。<br />\n要开始审核、编辑及删除评论，请访问仪表盘的“评论”页面。<br />\n评论者头像来自<a href=\"https://gravatar.com\">Gravatar</a>。</p>\n"
                },
                "link": "https://www.thewhitedog9487.xyz/2020/12/26/hello-world/#comment-1",
                "status": "approved",
                "type": "comment",
                "author_avatar_urls": {
                  "24": "https://secure.gravatar.com/avatar/d7a973c7dab26985da5f961be7b74480?s=24&d=identicon&r=g",
                  "48": "https://secure.gravatar.com/avatar/d7a973c7dab26985da5f961be7b74480?s=48&d=identicon&r=g",
                  "96": "https://secure.gravatar.com/avatar/d7a973c7dab26985da5f961be7b74480?s=96&d=identicon&r=g"
                },
                "meta": [],
                "_links": {
                  "self": [
                    {
                      "href": "https://www.thewhitedog9487.xyz/wp-json/wp/v2/comments/1",
                      "targetHints": {
                        "allow": [
                          "GET"
                        ]
                      }
                    }
                  ],
                  "collection": [
                    {
                      "href": "https://www.thewhitedog9487.xyz/wp-json/wp/v2/comments"
                    }
                  ],
                  "up": [
                    {
                      "embeddable": true,
                      "post_type": "post",
                      "href": "https://www.thewhitedog9487.xyz/wp-json/wp/v2/posts/1"
                    }
                  ]
                }
              }
            '''
            RemoteCommentDate = int(time.mktime(time.strptime(comment["date"], '%Y-%m-%dT%H:%M:%S')))
            if int(FileCommentDate) < RemoteCommentDate:
                logging.info('有新评论')
                f.seek(0)
                f.truncate()
                f.write(time.strftime('%Y年%m月%d日 %H时%M分%S秒', time.localtime(RemoteCommentDate)))

                Message = f'''评论者：{comment["author_name"]}
评论内容：{comment["content"]["rendered"]}
评论链接：{comment["link"]}
评论时间：{time.strftime("%Y年%m月%d日 %H时%M分%S秒", time.localtime(RemoteCommentDate))}'''

                MarkdownMessage = markdownify(Message)
                logging.info(Message)
                for comment_sender in self.Config.Ignore_List:
                    comment_sender: str
                    # ↑ https://stackoverflow.com/questions/41641449/how-do-i-annotate-types-in-a-for-loop
                    if comment["author_name"] == comment_sender:
                        logging.info("由于发送评论的用户位于忽略列表当中，因此本次新评论不会发送提醒。")
                        logging.info('\n' + MarkdownMessage)
                        return
                if self.Config.Channel_Message:
                    channel = self.get_channel(self.Config.Channel_ID)
                    # await channel.send(f"<@{self.Config.Admin_User_ID}>\n{self.Message}")
                    await channel.send(MarkdownMessage)
                else:
                    discord_user = await self.fetch_user(self.Config.Admin_User_ID)
                    await discord_user.send(MarkdownMessage)
                logging.info('已发送新通知\n')
            elif int(FileCommentDate) > RemoteCommentDate:
                f.seek(0)
                f.truncate()
                f.write(time.strftime('%Y年%m月%d日 %H时%M分%S秒', time.localtime(RemoteCommentDate)))
                logging.info('有评论被删除\n')
            elif int(FileCommentDate) == RemoteCommentDate:
                logging.info('没有新评论\n')

    async def setup_hook(self) -> None:
        self.TimerTrigger.start()

    @TimerTrigger.before_loop
    async def Before_Loop(self):
        await self.wait_until_ready()  # wait until the bot logs in


def Compress_LogFile():
    if os.path.exists(LogFileName):
        if os.path.getsize(LogFileName) > 1024 * 1024 * 1:  # 1MB
            os.chdir(LogPath)
            with zipfile.ZipFile(datetime.now().replace().strftime("%Y-%m-%d %H:%M:%S") + ".zip", 'w',
                                 zipfile.ZIP_DEFLATED) as zf:
                zf.write("WordPress评论监控.log")
            os.remove(LogFileName)
            os.chdir(WorkDirectory)


def Initialization():
    logging.info(f'程序从{datetime.now().replace().strftime("%Y-%m-%d %H:%M:%S")}开始运行')
    if (not os.path.exists("配置文件.json")) or (
            os.path.exists("配置文件.json") and (os.path.getsize("配置文件.json") == 0)):
        with open("配置文件.json", "w", encoding="utf-8") as w:
            json.dump(DiscordConfig().__dict__, w, indent=4)
            logging.info('首次运行')
            logging.error('配置文件模板已生成，请填写配置文件')
        exit()
    with open("配置文件.json", "r", encoding="utf-8") as r:
        Config = DiscordConfig().From_Dict(json.load(r))
    if Config.Get_Token() == "":
        logging.error('请填写机器人令牌')
        logging.error('这是必填项，如果为空程序将不能运行')
        exit()
    if Config.URL == "":
        logging.error('请填写要监测博客的地址')
        logging.error('这是必填项，如果为空程序将不能运行')
        exit()
    if Config.Channel_Message:
        logging.debug('程序在频道中运行')
        if Config.Channel_ID == "":
            logging.error('请填写频道ID')
            logging.error('这是必填项，如果为空程序将不能运行')
            exit()
    else:
        logging.debug('程序在私信中运行')
        if Config.Admin_User_ID == "":
            logging.error('请填写Discord管理员用户ID')
            logging.error('这是必填项，如果为空程序将不能运行')
            exit()
    if not os.path.exists('最新评论发布时间.txt') or os.path.getsize('最新评论发布时间.txt') == 0:
        if not str(Config.URL).startswith(("http://", "https://")):
            try:
                res = requests.get('https://' + Config.URL)
                if res.status_code != 200:
                    raise Exception
                Config.URL = 'https://' + Config.URL
            except:
                Config.URL = 'http://' + Config.URL
        if Config.URL.endswith('/'):
            Config.URL = Config.URL[:-1]
        with open('最新评论发布时间.txt', 'w', encoding="utf-8") as w:
            w.write(datetime.strptime(
                requests.get(Config.URL + '/wp-json/wp/v2/comments').json()[0]["date"],
                '%Y-%m-%dT%H:%M:%S').strftime('%Y年%m月%d日 %H时%M分%S秒'))
    return Config


def LoggingInit():
    global LogFileName
    global LogPath
    global WorkDirectory
    WorkDirectory = os.getcwd()
    if platform.system() == 'Windows':
        LogPath = os.curdir + "\\日志\\"
    elif platform.system() == 'Linux':
        LogPath = "/var/log/thewhitedog9487/WordPress评论监控/"
    else:
        print("不认识的操作系统，请联系开发者寻求适配。")
        exit()
    LogFileName = LogPath + "WordPress评论监控.log"
    if not os.path.exists(LogPath):
        os.makedirs(LogPath)
    Compress_LogFile()
    logging.basicConfig(filename=LogFileName, level=logging.INFO, encoding="utf-8")
    logging.info(f'程序从{datetime.now().replace().strftime("%Y-%m-%d %H:%M:%S")}开始运行')


def ParseArgument():
    Argument: str
    try:
        Argument = sys.argv[1]
    except IndexError:
        return
    WorkDirectory = os.getcwd()
    SystemdServiceFilePath = "/usr/lib/systemd/system/WordPressCommentWatcher.service"
    SystemdServiceFileContent = fr'''[Unit]
Description=WordPress评论监控
After=multi-user.target

[Service]
WorkingDirectory={WorkDirectory}
User=root
Type=idle
ExecStart=/bin/bash -c 'source {WorkDirectory}/.venv/bin/activate && python3 {sys.argv[0]}'
Restart=always

[Install]
WantedBy=multi-user.target'''

    if Argument == "install":
        if platform.system() == 'Linux':
            if os.path.exists(SystemdServiceFilePath):
                logging.error('已存在服务文件')
                print("已存在服务文件，无需再次安装。")
                exit()
            else:
                with open(SystemdServiceFilePath, "w", encoding="utf-8") as w:
                    w.write(SystemdServiceFileContent)
                logging.info("服务文件已生成")
                logging.info(f"服务文件路径：{SystemdServiceFilePath}")
                os.system("systemctl daemon-reload")
                logging.info("Systemd守护进程已重新加载")
                os.system("systemctl enable WordPressCommentWatcher")
                logging.info("服务已设置开机自启")
                os.system("systemctl start WordPressCommentWatcher")
                logging.info("服务已启动")
                print("成功安装服务！")
                exit()
        elif platform.system() == 'Windows':
            logging.error("Windows系统当前不支持自动安装")
            print("Windows系统当前不支持自动安装")
            exit()
    elif Argument == "uninstall":
        if platform.system() == 'Linux':
            if os.path.exists(SystemdServiceFilePath):
                logging.info("已找到服务文件")
                os.system("systemctl stop WordPressCommentWatcher")
                logging.info("服务已停止")
                os.system("systemctl disable WordPressCommentWatcher")
                logging.info("服务已取消开机自启")
                os.remove(SystemdServiceFilePath)
                logging.info("服务文件已删除")
                os.system("systemctl daemon-reload")
                logging.info("Systemd守护进程已重新加载")
                print("成功卸载服务！")
                exit()
            else:
                logging.error("服务文件不存在")
                print("服务文件不存在，无需卸载。")
                exit()
        elif platform.system() == 'Windows':
            logging.error("Windows系统当前不支持自动卸载")
            print("Windows系统当前不支持自动卸载")
            exit()
    elif Argument in ["-h", "--help", "help"]:
        HelpContent = f'''help 显示此帮助
    别名：
        --help
        -h
install 自动安装服务
    仅支持使用systemd的Linux系统
    配置文件会被写入到 {SystemdServiceFilePath} 
    自动启动并设置开机自启
uninstall 自动卸载服务
    仅支持使用systemd的Linux系统
    会移除位于 {SystemdServiceFilePath} 的服务文件'''
        print(HelpContent)
        exit()


if __name__ == '__main__':
    LoggingInit()
    ParseArgument()
    Compress_LogFile()
    intent = discord.Intents.default()
    intent.messages = True
    BotClient = DiscordClient(intents=intent)
    BotClient.Config = Initialization()
    # BotClient.Config.Ignore_List = []
    # ↑ 调试用
    # 为什么没有给变量用的装饰器啊
    # 我需要Mixin的@Redirect指令
    BotClient.run(BotClient.Config.Get_Token())
