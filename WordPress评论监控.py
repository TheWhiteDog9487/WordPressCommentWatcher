import discord
import datetime
import logging
import requests
import os

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
    LogPath = "/var/log/thewhitedog9487/"
    if os.path.exists(LogPath) == False:
        os.makedirs(LogPath)
    logging.basicConfig(filename=f'{LogPath}WordPress评论监控.log', level=logging.INFO)
    logging.info(f'程序在{datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()}运行')
    for comment in requests.get('https://www.thewhitedog9487.xyz/wp-json/wp/v2/comments').json():
        with open('UpdateTime.txt', 'r') as r:
            Line = r.readline()
            if(Line != comment["date"]):
                global NewComment
                logging.info('有新评论')
                with open('UpdateTime.txt', 'w') as w:
                    w.write(comment["date"])
                if Line != "":
                    NewComment = f'评论者：{comment["author_name"]}\n评论内容：{comment["content"]["rendered"]}\n评论链接：{comment["link"]}\n评论时间：{comment["date"]}'
                    BotClient.run("你的机器人令牌")
                    # 记得填！
                    # 你自己的令牌！
                    logging.info('已发送新通知\n')
            else:
                logging.info('没有新评论\n')
        break

TimerTrigger()