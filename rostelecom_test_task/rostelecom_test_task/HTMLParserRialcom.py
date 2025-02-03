import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

from DataParser import DataParser


class HTMLParserRialcom(DataParser):
    def __init__(self):
        super().__init__()
        self.names = []
        self.channels = []
        self.speeds = []
        self.payments = []
        self.count_tariff_channel = {}

    def load_data(self, url: str = 'https://www.rialcom.ru/internet_tariffs/'):

        # Заголовки, чтобы замаскироваться под браузер
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }

        response = requests.get(url=url, headers=headers)

        if response.status_code == 200:
            # Парсим HTML при помощи Beautiful Soup
            self.data = BeautifulSoup(response.text, 'html.parser')
            return 200
        else:
            return response.status_code

    def process_data(self):
        processRialcom = HTMLProcessRialcom(self.data)
        return processRialcom.process_data()

    def save_data(self, name: str = "example"):
        _dict = {}
        headers = ['Название тарифа', 'Количество каналов', 'Скорость доступа', 'Абонентская плата']
        data = self.process_data()
        for i in range(len(headers)):
            _dict[headers[i]] = data[i]
        df = pd.DataFrame(_dict)
        df.to_excel(f"{name}.xlsx", index=False)


class HTMLProcessRialcom(HTMLParserRialcom):
    def __init__(self, data):
        super().__init__()
        self.data = data

    def process_data(self):

        # CSS-селектор для основных таблиц
        tables = self.data.find_all('table')

        # Обходим строки в цикле, проверяя заголовки на триггеры
        for table in tables:
            rows = table.find_all('tr')
            heads = rows[0].find_all('th')
            united_heads = ' '.join(map(lambda x: x.get_text(), heads))

            # Сценарий для таблиц формата 1
            if re.search("тариф", united_heads) is not None:
                self.__process_tariff(rows)

            # Сценарий для таблиц формата 2
            elif re.search("Интернет", united_heads) is not None:
                self.__process_tariff_TV(rows, heads)

            # Сценарий для остальных таблиц
            else:
                continue

        return [self.names, self.channels, self.speeds, self.payments]

    def __process_tariff(self, rows):
        for row in rows[1:]:
            columns = row.find_all('td')
            self.names.append(columns[0].text.strip())
            self.channels.append('null')
            self.speeds.append(int(int(re.search(r'\d+', columns[3].text.strip()).group()) / 1000))
            self.payments.append(int(columns[1].text.strip().split()[0]))

    def __process_tariff_TV(self, rows, heads):
        for row in rows[1:]:
            columns = row.find_all('td')
            tariff = columns[0].text.strip()
            is_tariff = False

            if tariff in self.count_tariff_channel.keys():
                channel = self.count_tariff_channel[tariff]
                is_tariff = True

            else:
                pattern = r"(?P<name>[\s\S]*?)\s*\((?P<num>\d+)[\s\S]*\)"
                groups = re.search(pattern, tariff)
                name, num = groups.groupdict()['name'], int(groups.groupdict()['num'])
                self.count_tariff_channel[name] = num
                channel = num

            self.__wrtite_tariff_TV(heads, columns, channel, is_tariff, tariff)

    def __wrtite_tariff_TV(self, heads, columns, channel: int, is_tariff: bool, tariff: str):
        for i in range(1, len(heads)):
            head = heads[i].text.strip()
            speed = int(re.search(r'\d+', head).group())
            if is_tariff:
                self.names.append(f"{tariff} + РиалКом Интернет {speed} + TB_ч")
            else:
                self.names.append(f"{tariff} + РиалКом Интернет {speed} + TB")
            self.channels.append(channel)
            self.speeds.append(speed)
            self.payments.append(int(columns[i].text.strip()))
