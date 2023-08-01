import discord
from datetime import datetime
from datetime import timezone
import logging
import requests
import os
import time
import platform
import zipfile

intents = discord.Intents.default()
intents.messages = True
BotClient = discord.Client(intents=intents)
NewComment = ""


@BotClient.event
async def on_ready():
    print(f'以{BotClient.user}登录')
    user = await BotClient.fetch_user(你的用户ID)
    # 记得把你的ID换上去
    # 开启Discord的开发者模式，返回主界面，单击左下角你的头像，点击复制用户ID
    # 直接粘贴到上面，不用加引号，直接传数字就可以
    await user.send(NewComment)
    await BotClient.close()


def TimerTrigger() -> None:
    LogPath = ""
    if platform.system() == 'Windows':
        LogPath = os.curdir + "\\日志\\"
    elif platform.system() == 'Linux':
        LogPath = "/var/log/thewhitedog9487/"
    LogFileName = LogPath + "WordPress评论监控.log"
    if not os.path.exists(LogPath):
        os.makedirs(LogPath)
    if not os.path.exists('UpdateTime.txt'):
        with open('UpdateTime.txt', 'w', encoding="utf-8") as w:
            w.write("")



    if os.path.exists(LogFileName):
        if os.path.getsize(LogFileName) > 1024 * 1024 * 10:
            with zipfile.ZipFile(LogFileName, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(datetime.now().strftime('%Y%m%d') + '.zip')
            os.remove(LogFileName)
    


    logging.basicConfig(filename=LogFileName, level=logging.INFO, encoding="utf-8")
    logging.info(f'程序在{datetime.now().replace().strftime("%Y-%m-%d %H:%M:%S")}运行')
    for comment in requests.get('https://www.thewhitedog9487.xyz/wp-json/wp/v2/comments').json():
        RemoteCommentDate = int(time.mktime(time.strptime(comment["date"], '%Y-%m-%dT%H:%M:%S')))
        with open('UpdateTime.txt', 'r', encoding="utf-8") as r:
            FileCommentDate = r.readline()
            if FileCommentDate == "":
                with open('UpdateTime.txt', 'w', encoding="utf-8") as w:
                    w.write(datetime.strptime(comment["date"], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'))
                logging.info('首次运行')
                break
            FileCommentDate = int(time.mktime(time.strptime(FileCommentDate, '%Y-%m-%d %H:%M:%S')))
            if int(FileCommentDate) < RemoteCommentDate:
                global NewComment
                logging.info('有新评论')
                with open('UpdateTime.txt', 'w', encoding="utf-8") as w:
                    w.write(str(RemoteCommentDate))
                if FileCommentDate != "":
                    NewComment = f'评论者：{comment["author_name"]}\n评论内容：{comment["content"]["rendered"]}评论链接：{comment["link"]}\n评论时间：{comment["date"]}'
                    BotClient.run('你的机器人令牌')
                    # 记得填！
                    # 你自己的令牌！
                    logging.info('已发送新通知\n')
            elif int(FileCommentDate) > RemoteCommentDate:
                logging.info('有评论被删除\n')
            else:
                logging.info('没有新评论\n')
        break


if __name__ == '__main__':
    TimerTrigger()
