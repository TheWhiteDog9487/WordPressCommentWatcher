import discord
from datetime import datetime
import logging
import requests
import os
import time
import platform
import zipfile
import json

intents = discord.Intents.default()
intents.messages = True
BotClient = discord.Client(intents=intents)
Config = {}
Message = ""

@BotClient.event
async def on_ready():
    logging.info(f'以{BotClient.user}登录')
    if Config["Channel_Message"]:
        channel = BotClient.get_channel(Config["Channel_ID"])
        await channel.send(f"<@{Config['Admin_User_ID']}>\n{Message}")
    else:
        user = await BotClient.fetch_user(Config["Admin_User_ID"])
        await user.send(Message)
    logging.info('已发送新通知\n')
    await BotClient.close()


def init():
    LogPath = ""
    if platform.system() == 'Windows':
        LogPath = os.curdir + "\\日志\\"
    elif platform.system() == 'Linux':
        LogPath = "/var/log/thewhitedog9487/"
    LogFileName = LogPath + "WordPress评论监控.log"
    if not os.path.exists(LogPath):
        os.makedirs(LogPath)
    if not os.path.exists('最新评论发布时间.txt'):
        with open('最新评论发布时间.txt', 'w', encoding="utf-8") as w:
            w.write(datetime.strptime(
                requests.get('https://www.thewhitedog9487.xyz/wp-json/wp/v2/comments').json()[0]["date"],
                '%Y-%m-%dT%H:%M:%S').strftime('%Y年%m月%d日 %H时%M分%S秒'))
    if os.path.exists(LogFileName):
        if os.path.getsize(LogFileName) > 1024 * 1024 * 10:
            with zipfile.ZipFile(LogFileName, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(datetime.now().strftime('%Y%m%d') + '.zip')
            os.remove(LogFileName)
    logging.basicConfig(filename=LogFileName, level=logging.INFO, encoding="utf-8")
    logging.info(f'程序在{datetime.now().replace().strftime("%Y-%m-%d %H:%M:%S")}运行')
    if not os.path.exists("配置文件.json"):
        with open("配置文件.json", "w", encoding="utf-8") as w:
            w.write("{\n\t\"Bot_Token\":\"\",\n\t\"Admin_User_ID\":1234,\n\t\"Channel_ID\":5678,\n\t\"Channel_Message\":true\n}")
            logging.info('首次运行')
            logging.error('配置文件模板已生成，请填写配置文件')
        exit()
    with open("配置文件.json", "r", encoding="utf-8") as r:
        global Config
        Config = json.load(r)
    if Config["Bot_Token"] == "":
        logging.error('请填写机器人令牌')
        logging.error('这是必填项，如果为空程序将不能运行')
        exit()
    if Config["Channel_Message"]:
        logging.debug('程序在频道中运行')
        if Config["Channel_ID"] == "":
            logging.error('请填写频道ID')
            logging.error('这是必填项，如果为空程序将不能运行')
            exit()
    else:
        logging.debug('程序在私信中运行')
        if Config["Admin_User_ID"] == "":
            logging.error('请填写Discord管理员用户ID')
            logging.error('这是必填项，如果为空程序将不能运行')
            exit()

def TimerTrigger() -> None:
    for comment in requests.get('https://www.thewhitedog9487.xyz/wp-json/wp/v2/comments').json():
        RemoteCommentDate = int(time.mktime(time.strptime(comment["date"], '%Y-%m-%dT%H:%M:%S')))
        with open('最新评论发布时间.txt', 'r', encoding="utf-8") as r:
            FileCommentDate = r.readline()
            FileCommentDate = int(time.mktime(time.strptime(FileCommentDate, '%Y年%m月%d日 %H时%M分%S秒')))
            if int(FileCommentDate) < RemoteCommentDate:
                logging.info('有新评论')
                with open('最新评论发布时间.txt', 'w', encoding="utf-8") as w:
                    w.write(time.strftime('%Y年%m月%d日 %H时%M分%S秒', time.localtime(RemoteCommentDate)))
                    global Message
                    Message = f'评论者：{comment["author_name"]}\n评论内容：{comment["content"]["rendered"]}评论链接：{comment["link"]}\n评论时间：{comment["date"]}'
                    BotClient.run(Config["Bot_Token"])
            elif int(FileCommentDate) > RemoteCommentDate:
                logging.info('有评论被删除\n')
            elif int(FileCommentDate) == RemoteCommentDate:
                logging.info('没有新评论\n')
        break


if __name__ == '__main__':
    init()
    TimerTrigger()
