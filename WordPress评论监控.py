import asyncio

import discord
from datetime import datetime
import logging
import requests
import os
import time
import platform
import zipfile
import json
import aiohttp
from discord.ext import tasks


class DiscordClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # an attribute we can access from our task
        self.Config = {}
        self.Message = ""
        LogPath = ""
        if platform.system() == 'Windows':
            LogPath = os.curdir + "\\日志\\"
        elif platform.system() == 'Linux':
            LogPath = "/var/log/thewhitedog9487/"
        LogFileName = LogPath + "WordPress评论监控.log"
        if not os.path.exists(LogPath):
            os.makedirs(LogPath)
        if os.path.exists(LogFileName):
            if os.path.getsize(LogFileName) > 1024 * 1024 * 10:
                with zipfile.ZipFile(LogFileName, 'w', zipfile.ZIP_DEFLATED) as zf:
                    zf.write(datetime.now().strftime('%Y%m%d') + '.zip')
                os.remove(LogFileName)
        logging.basicConfig(filename=LogFileName, level=logging.INFO, encoding="utf-8")
        logging.info(f'程序从{datetime.now().replace().strftime("%Y-%m-%d %H:%M:%S")}开始运行')
        if not os.path.exists("配置文件.json"):
            with open("配置文件.json", "w", encoding="utf-8") as w:
                w.write(
                    "{\n\t\"URL\":\"\",\n\t\"Bot_Token\":\"\",\n\t\"Admin_User_ID\":1234,\n\t\"Channel_ID\":5678,\n\t\"Channel_Message\":true\n}")
                logging.info('首次运行')
                logging.error('配置文件模板已生成，请填写配置文件')
            exit()
        with open("配置文件.json", "r", encoding="utf-8") as r:
            self.Config = json.load(r)
        if self.Config["Bot_Token"] == "":
            logging.error('请填写机器人令牌')
            logging.error('这是必填项，如果为空程序将不能运行')
            exit()
        if self.Config["URL"] == "":
            logging.error('请填写要监测博客的地址')
            logging.error('这是必填项，如果为空程序将不能运行')
            exit()
        if self.Config["Channel_Message"]:
            logging.debug('程序在频道中运行')
            if self.Config["Channel_ID"] == "":
                logging.error('请填写频道ID')
                logging.error('这是必填项，如果为空程序将不能运行')
                exit()
        else:
            logging.debug('程序在私信中运行')
            if self.Config["Admin_User_ID"] == "":
                logging.error('请填写Discord管理员用户ID')
                logging.error('这是必填项，如果为空程序将不能运行')
                exit()
        if not os.path.exists('最新评论发布时间.txt') or os.path.getsize('最新评论发布时间.txt') == 0:
            if not str(self.Config["URL"]).startswith(("http://","https://")):
                logging.error("监测链接必须以http://或者https://打头！")
                exit()
            with open('最新评论发布时间.txt', 'w', encoding="utf-8") as w:
                w.write(datetime.strptime(
                    requests.get(self.Config["URL"]+'/wp-json/wp/v2/comments').json()[0]["date"],
                    '%Y-%m-%dT%H:%M:%S').strftime('%Y年%m月%d日 %H时%M分%S秒'))

    async def on_ready(self):
        logging.info(f'以{BotClient.user}登录')

    @tasks.loop(minutes=1)
    async def TimerTrigger(self) -> None:
        logging.info(f'现在是{datetime.now().replace().strftime("%Y-%m-%d %H:%M:%S")}，开始检测评论状态。')
        response = None
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.thewhitedog9487.xyz/wp-json/wp/v2/comments') as response:
                response = await response.json()
        for comment in response:
            RemoteCommentDate = int(time.mktime(time.strptime(comment["date"], '%Y-%m-%dT%H:%M:%S')))
            with open('最新评论发布时间.txt', 'r', encoding="utf-8") as r:
                FileCommentDate = r.readline()
                FileCommentDate = int(time.mktime(time.strptime(FileCommentDate, '%Y年%m月%d日 %H时%M分%S秒')))
                if int(FileCommentDate) < RemoteCommentDate:
                    logging.info('有新评论')
                    with open('最新评论发布时间.txt', 'w', encoding="utf-8") as w:
                        w.write(time.strftime('%Y年%m月%d日 %H时%M分%S秒', time.localtime(RemoteCommentDate)))
                        self.Message = f'评论者：{comment["author_name"]}\n评论内容：{comment["content"]["rendered"]}评论链接：{comment["link"]}\n评论时间：{comment["date"]}'
                        if self.Config["Channel_Message"]:
                            channel = self.get_channel(self.Config["Channel_ID"])
                            await channel.send(f"<@{self.Config['Admin_User_ID']}>\n{self.Message}")
                        else:
                            user = await self.fetch_user(self.Config["Admin_User_ID"])
                            await user.send(self.Message)
                        logging.info('已发送新通知\n')
                elif int(FileCommentDate) > RemoteCommentDate:
                    logging.info('有评论被删除\n')
                elif int(FileCommentDate) == RemoteCommentDate:
                    logging.info('没有新评论\n')
            break

    async def setup_hook(self) -> None:
        self.TimerTrigger.start()

    @TimerTrigger.before_loop
    async def Before_Loop(self):
        await self.wait_until_ready()  # wait until the bot logs in


if __name__ == '__main__':
    intent = discord.Intents.default()
    intent.messages = True
    BotClient = DiscordClient(intents=intent)
    BotClient.run(BotClient.Config["Bot_Token"])