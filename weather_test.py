import requests

API_KEY = '99df747ca7846b04e0dfa8a6bdff30aa'
city_name = '서울'
limit = '1'

coord_response = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit={limit}&appid={API_KEY}')

lat = coord_response.json()[0]['lat']
lon = coord_response.json()[0]['lon']
lang = 'kr'

weather_response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&lang={lang}')

print(weather_response.json())
print(weather_response.json()['weather'][0]['description']) # 날씨 설명
print(weather_response.json()['weather'][0]['icon'])    # 아이콘 https://openweathermap.org/img/wn/{여기에 들어갈 내용}@2x.png
print(round(weather_response.json()['main']['temp'] - 273.15, 2))   # 섭씨 온도
print(round((weather_response.json()['main']['temp'] - 273.15) * 9/5 + 32, 2))  # 화씨 온도
print(round(weather_response.json()['main']['feels_like'] - 273.15, 2))   # 섭씨 체감 온도
print(round((weather_response.json()['main']['feels_like'] - 273.15) * 9/5 + 32, 2))  # 화씨 체감 온도
print(weather_response.json()['main']['humidity'])   # 습도 %
print(weather_response.json()['visibility'] / 1000)   # 가시 거리
print(weather_response.json()['wind']['speed'])    # 풍속
print(weather_response.json()['sys']['country'])    # 국가 코드
print(weather_response.json()['name'])  # 도시