from time import sleep
import requests
from pprint import pprint
from tqdm import tqdm
import json

with open('token.txt', 'r', encoding='utf-8') as file_object:
    token = file_object.readline().strip()
    token_YD = file_object.readline().strip()

class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': '5.131'
        }

    def get_photo(self, vk_id: str):
        '''Данный метод класса VkUser необходим для получения информации о фотографиях по конкретному ID, после получения общих данных: переменная res,
        необходимо пройти цикл для создания нужного списка словарей, требуемый по заданию, в формате json-файла: [{"file_name": "34.jpg", "size": "z"}]'''
        url_photo = self.url + 'photos.get'
        params = {
            'owner_id': '82787437',
            'album_id': 'profile',
            'rev': 0,
            'extended': 1,
            'photo_sizes': 0,
            'count': 15
        }
        res = requests.get(url_photo, params={**self.params, **params}).json()
        res = res['response']['items']
        # return res
        # need_dict = {}
        # for i in res:
        #     if i['likes']['count'] not in need_dict:
        #         need_dict.setdefault(i['likes']['count'], '')
        #     else:
        #         need_dict.setdefault(i['date'], '')
        #     for k in sorted(i['sizes'], key=lambda type: type['type']):
        #         if k['type'] == 'w':
        #             need_dict[i['likes']['count']] = k['url']
        #         else:
        #             need_dict[i['likes']['count']] = sorted(i['sizes'], key=lambda type: type['type'])[-1]['url']
        need_list = [{'file_name': str(item['likes']['count']) + '.jpg', 'size': item['sizes'][-1]['type']} for item in
                     res]
        with open('res.json', 'w') as file:
            json.dump(need_list, file, indent=1)

        return res



class YaDisk:
    def __init__(self):
        self.token = token_YD



    def get_headers(self):
        '''Метод определяет заголовки в запросе'''

        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }


    def get_path(self, path: str):
        '''Метод получения пути, по которому следует загрузить файл, с помощью GET запроса'''

        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': path
                  }
        headers = self.get_headers()
        control = requests.get(url=url, params=params, headers=headers)
        return control.status_code


    def put_path(self, path: str):
        '''Прописываем путь с помощью метода PUT'''

        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': path
                  }
        headers = self.get_headers()
        pathway = requests.put(url=url, params=params, headers=headers)
        return pathway.status_code

    def status_operation(self, href):
        '''Статус операции'''
        while True:
            headers = self.get_headers()
            response = requests.get(url=href, headers=headers).json()
            if response['status'] == 'success':  # операция успешно завершена
                break
            elif response['status'] == 'failed':  # операцию завершить не удалось, попробйте повторить изгачальный запрос копирования
                break
            elif response['status'] == 'in-progress':  # операция начата, но еще не завершена
                sleep(0.5)
        return



    def upload_file(self, file_: str, file_path: str):
        '''Загружаем файлы на диск при помощи метода POST и проверяем статус загрузки status_operation'''
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": file_path,
                  "overwrite": "true",
                  'url': file_
                  }
        response = requests.post(url=url, headers=headers, params=params)
        request = response.json()
        if response.status_code == 202:
            self.status_operation(request["href"])
        else:
            print(response.status_code)
        return

    def vk_fotos_upload(self, files: list, album: str = 'FOTOS'):
        '''Запускаем загрузку в альбом(папку) на Яндексдиске, присваиваем требуемые по заданию имена для фотографий:
        количество лайков'''

        self.put_path(album)
        for file in tqdm(files, desc='Загрузка'):
            file_ = file['sizes'][-1]['url']
            file_path = f'{album}/{file["likes"]["count"]}.jpg'
            if self.get_path(file_path) == 200:
                file_path = f'{album}/{file["likes"]["count"]}_{file["date"]}.jpg'
            self.upload_file(file_, file_path)
        else:
            print(f'Загрузка выполнена. Загружено {len(files)} файлов')
        return


if __name__ == '__main__':
    user_vk = VkUser(token, '5.131')
    id_vk = "736368866"
    # pprint(user_vk.get_photo(id_vk))
    ya = YaDisk()
    vk = VkUser(token, '5.131')
    res = vk.get_photo("82787437")
    ya.vk_fotos_upload(res)
