import os
import discord
import json
import requests
from discord.ext import commands
from googletrans import Translator
from dotenv import load_dotenv

load_dotenv()

with open('./message_content.json', 'r', encoding='UTF8') as file:
    content = json.load(file)

MEMU_URL = os.environ.get('MEMU_URL')
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
embedColor = 0xFEB309

game = discord.Game(">도움말 & >halp & >ヘルプ")
bot = commands.Bot(command_prefix='>', intents=discord.Intents.all(), status=discord.Status.online, activity=game)


@bot.command(aliases=['도움말', 'halp', 'ヘルプ'])
async def help_(ctx):
    message = (content['help'])[ctx.message.content]

    dm_channel = await ctx.message.author.create_dm()
    await dm_channel.send(embed=discord.Embed(title=message['title'], description=message['content'], color=embedColor))


@bot.command(aliases=['메뉴추천', 'MenuRec', 'おすすめ'])
async def menuRec_(ctx, select='st'):
    headers = {
        'Content-type': 'application/x-www-form-urlencoded',
        'Origin': 'http://dogumaster.com'
    }

    memu_content = content['menuRec']
    country = 'all'

    for key in memu_content.keys():
        if select == key:
            country = memu_content[select]
            break

    response = requests.post(MEMU_URL, verify=False, headers=headers, data='type_01=all&country=' + country + '&type_03=all')

    message = 'error'
    explanation = '음식 이름이 구글 번역기를 통해 번역이 되기 때문에 잘못된 번역이 있을 수 있습니다.'
    translator = Translator()

    if response.status_code == 200:
        message_content = ctx.message.content
        dest = 'ko'
        if '>menurec' in message_content.lower():
            dest = 'en'
            explanation = 'There may be a wrong translation because the food name is translated through Google Translator.'
        elif '>おすすめ' in message_content:
            dest = 'ja'
            explanation = '食べ物の名前がグーグル翻訳機を通じて翻訳されるため、間違った翻訳がある可能性があります。'

        if '>메뉴추천' in message_content:
            message = response.json()['name']
        else:
            message = translator.translate(response.json()['name'], src='ko', dest=dest).text

    image_response = requests.get('https://s.search.naver.com/p/c/image/search.naver?where=image&mode=&rev=44&section=image&query=' + response.json()['name'] + '&ac=0&aq=0&spq=0&nx_search_query=' + response.json()['name'] + '&nx_and_query=&nx_sub_query=&nx_search_hlquery=&nx_search_fasquery=&res_fr=0&res_to=0&color=&datetype=0&startdate=0&enddate=0&nso=so%3Ar%2Ca%3Aall%2Cp%3Aall&json_type=6&nlu_query=%7B%22r_category%22%3A%2229%22%7D&nqx_theme=%7B%22theme%22%3A%7B%22main%22%3A%7B%22name%22%3A%22restaurant_list%22%7D%2C%22sub%22%3A%5B%7B%22name%22%3A%22food_recipe%22%7D%5D%7D%7D&gif=0&optStr=&ccl=0&x_image=&display=100&abt=&pq=&start={=start}')

    image_url = 'https://search.pstatic.net/common/?src=' + ((json.loads(image_response.text[3:-4])['items'])[1])['viewerThumb']

    await ctx.send(embed=discord.Embed(title=':fork_and_knife: ' + message, color=embedColor).set_image(url=image_url).set_footer(text='※ ' + explanation))

@bot.command(aliases=['날씨', 'weather', '天気'])
async def weather_(ctx, city_name='None'):
    lang = ''

    message_content = ctx.message.content
    if '>날씨' in message_content:
        lang = 'kr'
    elif '>weather' in message_content.lower():
        lang = 'en'
    elif '>天気' in message_content:
        lang = 'ja'

    if city_name in 'None':
        await ctx.send(embed=discord.Embed(
            title=':octagonal_sign: Error',
            description=content['weather'][lang]['error']['city_none'],
            color=embedColor
        ))
        return

    limit = '1'

    coord_response = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit={limit}&appid={WEATHER_API_KEY}')

    if coord_response.text == '[]':
        await ctx.send(embed=discord.Embed(
            title=':octagonal_sign: Error',
            description=content['weather'][lang]['error']['coord_none'],
            color=embedColor
        ))
        return

    lat = coord_response.json()[0]['lat']
    lon = coord_response.json()[0]['lon']


    weather_response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&lang={lang}')

    title = ':white_sun_small_cloud: ' + city_name + '/' + weather_response.json()['sys']['country'] + content['weather'][lang]['title']
    description = weather_response.json()['weather'][0]['description'] + '.\n' + \
                  content['weather'][lang]['description']['temp'] + \
                  '`' + str(round(weather_response.json()['main']['temp'] - 273.15, 2)) + '°C` / ' + \
                  '`' + str(round((weather_response.json()['main']['temp'] - 273.15) * 9/5 + 32, 2)) + '°F`. \n' + \
                  content['weather'][lang]['description']['feels_like'] + \
                  '`' + str(round(weather_response.json()['main']['feels_like'] - 273.15, 2)) + '°C` / ' + \
                  '`' + str(round((weather_response.json()['main']['feels_like'] - 273.15) * 9/5 + 32, 2)) + '°F`.'

    url = weather_response.json()['weather'][0]['icon']

    embed = discord.Embed(title=title, description=description, color=embedColor)\
        .set_thumbnail(url=f'https://openweathermap.org/img/wn/{url}@2x.png')\
        .add_field(name=content['weather'][lang]['field_value']['value1'],
                   value='`' + str(round(weather_response.json()['main']['temp_min'] - 273.15, 2)) + '°C` / ' + \
                   '`' + str(round((weather_response.json()['main']['temp_min'] - 273.15) * 9/5 + 32, 2)) + '°F`.', inline=True)\
        .add_field(name=content['weather'][lang]['field_value']['value2'],
               value='`' + str(round(weather_response.json()['main']['temp_max'] - 273.15, 2)) + '°C` / ' + \
                     '`' + str(round((weather_response.json()['main']['temp_max'] - 273.15) * 9/5 + 32, 2)) + '°F`.', inline=True)\
        .add_field(name=content['weather'][lang]['field_value']['value3'], value='`' + str(round(weather_response.json()['visibility'] / 1000, 1)) + 'km`', inline=True)\
        .add_field(name=content['weather'][lang]['field_value']['value4'], value='`' + str(weather_response.json()['main']['humidity']) + '%`', inline=True)\
        .add_field(name=content['weather'][lang]['field_value']['value5'], value='`' + str(weather_response.json()['wind']['speed']) + 'm/s`', inline=True)

    await ctx.send(embed=embed)

@bot.command(aliases=['개발자','developer','開発者'])
async def developer_(ctx):
    message = (content['developer'])[ctx.message.content]
    await ctx.send(embed=discord.Embed(title=message['title'], description=message['content'], color=embedColor).set_thumbnail(url='https://cdn.discordapp.com/attachments/862053936876879875/1122802213463527585/developer_profile.jpg'))

bot.run(DISCORD_TOKEN)
