import math
import requests
import sys


def get_picture_id(city):
    url = 'https://dialogs.yandex.ru/api/v1/skills/017775dc-bd4c-4d1d-9d1a-6926a90fd234/images'
    create_new_city_map(city)
    files = {'file': open('map.png', 'rb')}

    r = requests.post(url, files=files, headers={'Authorization':'AQAAAAAgWv7uAAT7o-H8lCO8I01urONK5e95Z6o'})

    return r.text


def make_toponym(geocoder_request):
    response1 = None
    try:
        response1 = requests.get(geocoder_request)
        if response1:
            # Преобразуем ответ в json-объект
            json_response = response1.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            return toponym
        else:
            print("Ошибка выполнения запроса:")
            print(geocoder_request)
            print("Http статус:", response1.status_code, "(", response1.reason, ")")
    except:
        print("Запрос не удалось выполнить. Проверьте подключение к сети Интернет.")


def get_response(name):
    try:
        api_server = "http://static-maps.yandex.ru/1.x/"
        geocoder_request = "http://geocode-maps.yandex.ru/1.x/?geocode={}&format=json".format(name)
        toponym = make_toponym(geocoder_request)
        x1, y1 = toponym['boundedBy']['Envelope']['upperCorner'].split()
        x2, y2 = toponym['boundedBy']['Envelope']['lowerCorner'].split()
        deltax = str(float(x1) / 4 - float(x2) / 4)
        deltay = str(float(y1) / 4 - float(y2) / 4)
        toponym_longitude, toponym_lattitude = toponym['Point']['pos'].split()
        params = {
            'll': ','.join([toponym_longitude, toponym_lattitude]),
            'spn': ','.join([deltax, deltay]),
            'l': 'map'
        }
        response = requests.get(api_server, params=params)

        if not response:

            print("Ошибка выполнения запроса:")

            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        return response


    except:
        print("Запрос не удалось выполнить. Проверьте наличие сети Интернет.")
        sys.exit(1)


def create_new_city_map(city):
    # Запишем полученное изображение в файл.
    map_file = "map.png"
    response = get_response(city)
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)


def get_distance(p1, p2):
    # p1 и p2 - это кортежи из двух элементов - координаты точек
    radius = 6373.0

    lon1 = math.radians(p1[0])
    lat1 = math.radians(p1[1])
    lon2 = math.radians(p2[0])
    lat2 = math.radians(p2[1])

    d_lon = lon2 - lon1
    d_lat = lat2 - lat1

    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * \
        math.cos(lat2) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(a ** 0.5, (1 - a) ** 0.5)

    distance = radius * c
    return distance


def get_country(city_name):
    try:
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            'geocode': city_name,
            'format': 'json'
        }
        data = requests.get(url, params).json()
        # все отличие тут, мы получаем имя страны
        return data['response']['GeoObjectCollection']['featureMember'][0][
            'GeoObject']['metaDataProperty']['GeocoderMetaData'][
            'Address']['formatted']
    except Exception as e:
        return e

def get_coordinates(city_name):
    try:
        # url, по которому доступно API Яндекс.Карт
        url = "https://geocode-maps.yandex.ru/1.x/"
        # параметры запроса
        params = {
            # город, координаты которого мы ищем
            'geocode': city_name,
            # формат ответа от сервера, в данном случае JSON
            'format': 'json'
        }
        # отправляем запрос
        response = requests.get(url, params)
        # получаем JSON ответа
        json = response.json()
        # получаем координаты города (там написаны долгота(longitude),
        # широта(latitude) через пробел).
        # Посмотреть подробное описание JSON-ответа можно
        # в документации по адресу
        # https://tech.yandex.ru/maps/geocoder/
        coordinates_str = json['response']['GeoObjectCollection'][
            'featureMember'][0]['GeoObject']['Point']['pos']
        # Превращаем string в список, так как точка -
        # это пара двух чисел - координат
        long, lat = map(float, coordinates_str.split())
        # Вернем ответ
        return long, lat
    except Exception as e:
        return e
