import os
import discord
import asyncio
import time
# from threading import (Event, Thread)
import threading

# 環境変数にDISCORD_BOT_TOKEN=xxxと追加しておくと楽になる
TOKEN = os.environ['DISCORD_BOT_TOKEN']
client = discord.Client()
# スレッド内でメッセージ送信するために必要らしい
loop = asyncio.get_event_loop()
endtk = threading.Event()

base_interval = 0
shorter_time = 0
dead_time = 0


@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')


# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    print('メッセージ受信：', message.content)
    if message.author.bot:
        return
    elif message.content == '!isrunning':
        await message.channel.send('I\'m ready!')
    elif message.content.startswith('!settk'):
        # メッセージを空白ごとに要素分けし、base_interval、shorter_time、dead_timeのそれぞれに代入
        msg = message.content
        a = msg.split()
        global base_interval, shorter_time, dead_time
        base_interval = int(a[1])
        shorter_time = int(a[2])
        dead_time = int(a[3])
        # 内容確認用表示
        await message.channel.send(f'base_interval = {base_interval} shorter_time = {shorter_time} dead_time = {dead_time}')
    elif message.content == '!starttk':
        # スレッド作成&開始
        th = threading.Thread(target=up_timer, args=(endtk, message))
        th.start()
        print('スレッド開始')
    # グローバル変数で処理しないとendtkがないのでエラーになると思う
    elif message.content == '!endtk':
        endtk.set()
        print('スレッド終了')
    elif message.content == '!cleartk':
        base_interval = 0
        shorter_time = 0
        dead_time = 0


# カウントアップタイマー処理
def up_timer(endtk, message):
    i = 0
    while True:
        if i == dead_time:
            _send_msg(message, f'**{i}**')
        elif i >= shorter_time:
            _send_msg(message, f'{i}')
        elif i % base_interval == 0:
            _send_msg(message, f'{i}')
        print(i)
        i += 1
        # 多分endtk.waitで処理が止まってるけどそこは未解決
        if endtk.wait(timeout=1):
            _send_msg(message, 'タイマー停止')
            print('タイマー停止')
            break
        elif i > dead_time * 3:
            endtk.set()
            print('スレッド終了')
            break


# 実際のメッセージ送信する処理
def _send_msg(message, text):
    asyncio.ensure_future(message.channel.send(text), loop=loop)


client.run(TOKEN)
