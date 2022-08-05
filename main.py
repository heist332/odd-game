import requests
import discord
from bs4 import BeautifulSoup
import sqlite3
import asyncio
import random
import ast
import time
import uuid
import datetime
from datetime import timedelta
import os
from discord_components import DiscordComponents, Button, ButtonStyle
client = discord.Client()

DiscordComponents(client)

global result
global msg
result = '대기중'
msg = '대기중'

admin = ['관리자 아이디', ]


token = '봇토큰'  # 테스트봇

pickes = ['홀', '짝']


def embed(content: str):
    embed = discord.Embed(title='도박봇', description=content, color=0x7fde25)
    return embed


def check_true(number):
    if number == 1:
        return '적중'
    elif number == 0:
        return '대기중'
    else:
        return '미적중'


@client.event
async def on_ready():
    print('IM READY')

    global custom
    custom = []
    while True:
        global times

        times = '대기중'
        f = open('list.txt', 'r')
        data = f.read()
        f.close()
        number = [1, 2]  # number = [1, 2]
        if len(custom) == 0:
            result = random.choice(number)

            if result == 1:
                pick = '홀'
                if data == '':
                    round = 1
                    f = open('list.txt', 'w')
                    f.write(f'1회차 {pick}\n')
                    f.close()
                else:
                    parsing = data.split('\n')[-2]
                    round = int(parsing.split('회차')[0]) + 1
                    f = open('list.txt', 'a')
                    f.write(f'{round}회차 {pick}\n')
                    f.close()

            else:
                pick = '짝'
                if data == '':
                    round = 1
                    f = open('list.txt', 'w')
                    f.write(f'1회차 {pick}\n')
                    f.close()

                else:
                    parsing = data.split('\n')[-2]
                    round = int(parsing.split('회차')[0]) + 1
                    f = open('list.txt', 'a')
                    f.write(f'{round}회차 {pick}\n')
                    f.close()
        else:
            pick = custom[0]
            if data == '':
                round = 1
                f = open('list.txt', 'w')
                f.write(f'1회차 {pick}\n')
                f.close()

            else:
                parsing = data.split('\n')[-2]
                round = int(parsing.split('회차')[0]) + 1
                f = open('list.txt', 'a')
                f.write(f'{round}회차 {pick}\n')
                f.close()
            custom = []

        print(pick, round)

        con = sqlite3.connect('main.db')
        cur = con.cursor()
        cur.execute('SELECT * FROM users;')
        user = cur.fetchall()
        con.close()
        for i in user:
            par = ast.literal_eval(i[2])
            if not par == []:
                if par[-1][0] == round:
                    if par[-1][1] == pick:
                        if par[-1][3] == 0:
                            print('적중')
                            par.append([par[-1][0], par[-1][1], par[-1][2], 1])
                            par.remove(par[-2])

                            con = sqlite3.connect('main.db')
                            cur = con.cursor()
                            cur.execute(
                                'UPDATE users SET money = money + ?, bat = ? WHERE id == ?;', (int(int(par[-1][2]) * 1.95), str(par), str(i[0])))
                            con.commit()
                            con.close()
                    else:
                        if par[-1][3] == 0:
                            par.append([par[-1][0], par[-1][1], par[-1][2], 2])
                            par.remove(par[-2])

                            con = sqlite3.connect('main.db')
                            cur = con.cursor()
                            cur.execute(
                                'UPDATE users SET bat = ? WHERE id == ?;', (str(par), str(i[0])))
                            con.commit()
                            con.close()

        times = (datetime.datetime.now() + timedelta(seconds=60))

        await asyncio.sleep(60)


@ client.event
async def on_message(msg):
    if msg.author.bot:
        return

    if msg.content.startswith('!조작 '):
        if msg.author.id == '관리자 아이디':
            if len(custom) == 0:
                try:
                    pick = msg.content.split(' ')[1]
                    print(pick)
                    if not pick in pickes:
                        raise TypeError
                except Exception as e:
                    print(e)
                    return await msg.channel.send(embed=embed('!조작 (홀 or 짝)으로 입력해주세요.'))

                custom.append(str(pick))
                await msg.channel.send(embed=embed(f'조작이 완료되었습니다.\n이번 회차의 결과는 {pick}입니다.'))
            else:
                await msg.channel.send(embed=embed('이미 회차의 결과가 조작되었습니다.'))

    if msg.content.startswith('!충전 '):
        try:
            pin = msg.content.split(' ')[1]
        except:
            return await msg.channel.send(embed=embed('핀번호를 제대로 입력해주세요.'))

        jsondata = {
            'api_key': 'HXTN', 'cid': '컬쳐아디', 'cpw': '컬쳐비번', 'pin': pin
        }
        res = requests.post('Supporter#4799', json=jsondata)

        if res.status_code != 200:
            return await msg.channel.send(embed=embed('충전실패'))

        res = res.json()

        if res['success']:
            con = sqlite3.connect('main.db')
            cur = con.cursor()
            cur.execute('UPDATE users SET money = money + ? WHERE id == ?;',
                        (int(res['amount']), str(msg.author.id),))
            con.commit()
            con.close()
            a = res['amount']
            await msg.channel.send(embed=embed(f'{a}원 충전 완료'))
        else:

            await msg.channel.send(embed=embed('충전실패'))

    if msg.content == '!시작':
        if msg.author.id == '관리자 아이디':
            await msg.delete()

            l = (times - datetime.datetime.now())
            minute = str(l).split(':')[1]
            second = str(l).split(':')[2]
            fs = open('list.txt', 'r')
            data = fs.read()
            fs.close()

            parsing = data.split('\n')[-2]

            round = int(parsing.split('회차')[0]) + 1
            msg = await msg.channel.send(embed=embed(f'현재 회차는 {round}회차 입니다.\n남은시간: {minute[1:]}분 {second[:2]}초\n{parsing}'))

            while True:
                l = (times - datetime.datetime.now())
                minute = str(l).split(':')[1]
                second = str(l).split(':')[2]

                fs = open('list.txt', 'r')
                data = fs.read()
                fs.close()
                parsing = data.split('\n')[-2]

                json = {
                    'embed': {"title": '도박봇', "description": f'현재 회차는 {round}회차 입니다.\n남은시간: {minute[1:]}분 {second[:2]}초\n{parsing}', 'color': 0x7fde25}
                }

                round = int(data.split('\n')[-2].split('회차')[0]) + 1
                res = requests.patch(f'https://discord.com/api/v9/channels/{msg.channel.id}/messages/{msg.id}', json=json, headers={
                                     'Authorization': 'Bot ' + token}).json()
                # print(res)
                # await msg.edit(f'현재 회차는 {round}회차 입니다.\n남은시간: {minute[1:]}분 {second[:2]}초')
                await asyncio.sleep(0.75)

    if msg.content == '!가입':
        con = sqlite3.connect('main.db')
        cur = con.cursor()
        cur.execute('SELECT * FROM users WHERE id == ?;',
                    (str(msg.author.id),))
        user = cur.fetchone()
        con.close()

        if user is not None:
            return await msg.channel.send(embed=embed('이미 가입된 유저입니다.'))
        else:
            con = sqlite3.connect('main.db')
            cur = con.cursor()
            cur.execute('INSERT INTO users VALUES(?, ?, ?);',
                        (str(msg.author.id), 0, str([]),))
            con.commit()
            con.close()
            await msg.channel.send(embed=embed('가입에 성공했습니다.'))

    if msg.content.startswith('!배팅 '):

        con = sqlite3.connect('main.db')
        cur = con.cursor()
        cur.execute('SELECT * FROM users WHERE id == ?;',
                    (str(msg.author.id),))
        user = cur.fetchone()
        con.close()

        if user is None:
            return await msg.channel.send(embed=embed('가입이 안된 유저입니다.'))

        try:
            pick = msg.content.split(' ')[1]
            amount = msg.content.split(' ')[2]
        except Exception as e:
            print(str(e))
            return await msg.channel.send(embed=embed('올바른 픽, 금액을 입력해주세요 예시: !배팅 짝 1000'))

        if not amount.isdigit():
            return await msg.channel.send(embed=embed('배팅하실 금액은 숫자로만 입력해주세요.'))
        elif not pick in pickes:
            return await msg.channel.send(embed=embed('배팅하실 수 있는 픽은 홀 또는 짝밖에 없습니다.'))
        else:
            if int(user[1]) < int(amount):
                return await msg.channel.send(embed=embed('배팅하실 금액이 보유하신 금액보다 많습니다.'))
            else:
                f = open('list.txt', 'r')
                data = f.read()
                f.close()

                parsing = data.split('\n')[-2]

                round = int(parsing.split('회차')[0]) + 1

                print(round, pick, amount)

                par = ast.literal_eval(user[2])
                if not par == []:
                    if par[-1][0] == round:
                        return await msg.channel.send(embed=embed('중복배팅은 허용되지 않습니다.'))

                par.append([int(round), str(pick), int(amount), 0])
                con = sqlite3.connect('main.db')
                cur = con.cursor()
                cur.execute(
                    'UPDATE users SET money = money - ?, bat = ? WHERE id == ?;', (int(amount), str(par), str(msg.author.id)))
                con.commit()
                con.close()
                await msg.channel.send(embed=embed(f'{round}회차에 {pick}으로 {amount}원을 배팅하셨습니다.'))

    if msg.content == '!전적':
        win = 0
        wait = 0
        all = []

        con = sqlite3.connect('main.db')
        cur = con.cursor()
        cur.execute('SELECT * FROM users WHERE id == ?;',
                    (str(msg.author.id),))
        user = cur.fetchone()
        con.close()

        if user is None:
            return await msg.channel.send(embed=embed('가입이 안된 유저입니다.'))

        par = ast.literal_eval(user[2])

        for i in par:

            all.append(
                f'`{i[0]}`회차 : `{check_true(i[3])}` - 픽 : `{i[1]}` - 배팅 금액 : `{i[2]}`')

            if check_true(i[3]) == '적중':
                win += 1
            elif check_true(i[3]) == '대기중':
                wait += 1
        result = '\n'.join(all[-10:])
        try:
            await msg.reply(embed=embed(f'{msg.author}님의 배팅 전적입니다.\n승률: {int(win / (len(all) - wait) * 100)}%\n{result}'))
        except Exception as e:
            print(str(e))
            await msg.reply(embed=embed(f'{msg.author}님의 배팅 전적입니다.\n승률:0%\n배팅 전적 없음'))

    if msg.content == '!회차':
        con = sqlite3.connect('main.db')
        cur = con.cursor()
        cur.execute('SELECT * FROM users WHERE id == ?;',
                    (str(msg.author.id),))
        user = cur.fetchone()
        con.close()

        if user is None:
            return await msg.channel.send(embed=embed('가입이 안된 유저입니다.'))

        fs = open('list.txt', 'r')
        data = fs.read()
        fs.close()

        parsing = data.split('\n')[-2]
        datas = '\n'.join(data.split('\n')[-15:])

        round = int(parsing.split('회차')[0]) + 1
        if times is not '대기중':
            l = (times - datetime.datetime.now())
            minute = str(l).split(':')[1]
            second = str(l).split(':')[2]
            await msg.channel.send(embed=embed(f'{msg.author}\n현재 회차는 {round}회차 입니다.\n남은시간: {minute[1:]}분 {second[:2]}초\n{datas}'))
            f = open(f'{msg.author.id}.txt', 'a', encoding='utf8')
            f.write('회차정보\n' + '\n'.join(data.split('\n')[:-1]))
            f.close()

            await msg.channel.send(file=discord.File(f'{msg.author.id}.txt'))
            os.remove(f'{msg.author.id}.txt')
        else:
            await msg.channel.send(embed=embed(f'{msg.author}\n현재 회차는 {round}회차 입니다.\n남은시간: 대기중\n\n{datas}'))
            f = open(f'{msg.author.id}.txt', 'a', encoding='utf8')
            f.write('회차정보\n' + '\n'.join(data.split('\n')[:-1]))
            f.close()
            await msg.channel.send(file=discord.File(f'{msg.author.id}.txt'))
            os.remove(f'{msg.author.id}.txt')

    if msg.content == '!회차초기화':
        if str(msg.author.id) in admin:
            os.remove(f'list.txt')
            f = open(f'list.txt', 'a', encoding='utf8')
            f.write('')
            f.close()
            await msg.reply(embed=embed('초기화 완료'))

    if msg.content.startswith('!환전 '):
        try:
            amount = msg.content.split(' ')[1]
            print(amount)
            if not amount.isdigit():
                raise TypeError

        except Exception as e:
            print(e)
            return await msg.reply(embed=embed('환전금액은 숫자로만 입력해주세요. - 예시:  !환전 1'))

        con = sqlite3.connect('main.db')
        cur = con.cursor()
        cur.execute('SELECT * FROM users WHERE id == ?;',
                    (str(msg.author.id),))
        user = cur.fetchone()
        con.close()

        if int(user[1]) < int(amount):
            return await msg.reply(embed=embed('환전금액이 보유금액보다 많습니다.'))

        i = 0
        for channel in msg.guild.channels:
            print(channel.name)
            if str(channel.name) == str(msg.author.id):
                print(channel.name)
                i = 1
                break

        if i == 0:
            overwrites = {
                msg.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                msg.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            }
            channel = await msg.guild.create_text_channel(str(msg.author.id), overwrites=overwrites)
            await msg.reply(embed=discord.Embed(description=f"<#{str(channel.id)}>로 이동해주세요."))
            await channel.send(embed=discord.Embed(description=f'<@{str(msg.author.id)}>님 관리자를 호출했습니다.\n환전을 기다려주세요.\n관리자가 부재라면 5분 후 자동 환불과 함께 채널이 삭제됩니다.'))

            con = sqlite3.connect('main.db')
            cur = con.cursor()
            cur.execute('UPDATE users SET money = money - ? WHERE id == ?;',
                        (int(amount), str(msg.author.id),))
            con.commit()
            con.close()

            try:
                user = await client.fetch_user('관리자 아이디')
                await user.send(f'환전 신청이 접수되었습니다.\n금액: {amount}\n일시: {datetime.datetime.now()}\n승인 방법: !승인\n바로가기" <#{channel.id}>')
                user = await client.fetch_user(534700925298802689)
                await user.send(f'환전 신청이 접수되었습니다.\n금액: {amount}\n일시: {datetime.datetime.now()}\n승인 방법: !승인\n바로가기" <#{channel.id}>')
                t = await client.wait_for("message", timeout=300, check=lambda m: (m.author.id == 534700925298802689 or m.author.id == '관리자 아이디') and m.channel.id == channel.id and m.content == '!승인')
                print(t)
                await channel.send("10초 후 채널이 삭제됩니다.")
                await asyncio.sleep(10)
                await channel.delete()
            except asyncio.TimeoutError:
                await channel.send("제한시간이 다 되었습니다 10초 후 채널이 삭제됩니다.")
                con = sqlite3.connect('main.db')
                cur = con.cursor()
                cur.execute('UPDATE users SET money = money + ? WHERE id == ?;',
                            (int(amount), str(msg.author.id),))
                con.commit()
                con.close()
                await asyncio.sleep(10)
                await channel.delete()

        else:
            await msg.reply(embed=discord.Embed(title=f"이미 충전채널이 있습니다.\n관리자에게 디엠해주세요."))

    if msg.content == '!정보':
        con = sqlite3.connect('main.db')
        cur = con.cursor()
        cur.execute('SELECT * FROM users WHERE id == ?;',
                    (str(msg.author.id),))
        user = cur.fetchone()
        con.close()

        if user is None:
            return await msg.channel.send(embed=embed('가입이 안된 유저입니다.'))
        else:
            if user[1] > 10000:
                await msg.channel.send(embed=embed(f'<@{msg.author.id}>\n잔액 {user[1]}원'))
            else:
                await msg.channel.send(embed=embed(f'<@{msg.author.id}>\n잔액 {user[1]}원'))

    if msg.content.startswith('!생성 '):
        if str(msg.author.id) in admin:
            try:
                amount = msg.content.split(' ')[1]
                quantity = msg.content.split(' ')[2]
                if not quantity.isdigit():
                    raise Exception('Not isdigit')
            except Exception as e:
                print(str(e))
                return await msg.channel.send(embed=embed('생성은 !생성 금액 수량 으로 입력해주세요.'))

            codes = []

            for i in range(int(quantity)):
                code = str(uuid.uuid4()).upper()
                con = sqlite3.connect('keys.db')
                cur = con.cursor()
                cur.execute('INSERT INTO license VALUES(?, ?);',
                            (str(code), int(amount),))
                con.commit()
                con.close()
                codes.append(code)

            result = '\n'.join(codes)
            await msg.channel.send(embed=embed(f'코드 생성이 완료되었습니다.\n{result}'))

    if msg.content.startswith('!충전 '):
        con = sqlite3.connect('main.db')
        cur = con.cursor()
        cur.execute('SELECT * FROM users WHERE id == ?;',
                    (str(msg.author.id),))
        user = cur.fetchone()
        con.close()

        if user is None:
            return await msg.channel.send(embed=embed('가입이 안된 유저입니다.'))

        try:
            code = msg.content.split(' ')[1]
        except Exception as e:
            print(str(e))
            return await msg.channel.send(embed=embed('!충전 코드 로 입력해주세요.'))

        con = sqlite3.connect('keys.db')
        cur = con.cursor()
        cur.execute('SELECT * FROM license WHERE key == ?;',
                    (str(code),))
        k = cur.fetchone()
        con.close()

        if k is None:
            return await msg.channel.send(embed=embed('존재하지 않는 라이센스 입니다.'))
        else:
            con = sqlite3.connect('keys.db')
            cur = con.cursor()
            cur.execute('DELETE FROM license WHERE key == ?;',
                        (str(code),))
            con.commit()
            con.close()

            con = sqlite3.connect('main.db')
            cur = con.cursor()
            cur.execute('UPDATE users SET money = money + ? WHERE id == ?;',
                        (int(k[1]), str(msg.author.id),))
            con.commit()
            con.close()
            await msg.channel.send(embed=embed(f'{k[1]}원이 충전되었습니다.'))


@client.event
async def on_button_click(interaction):
    print(interaction)
    pass


client.run(token)
