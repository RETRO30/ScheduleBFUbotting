import requests
import datetime
import bs4
import time

ERROR = 'ERROR'

def datetime_from_str(day):
    return datetime.datetime.strptime(day, '%d.%m.%Y')

def str_from_datetime(string):
    return datetime.datetime.strftime(string, '%Y-%m-%d')

class Parser:
    def __init__(self) -> None:
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    def get_day_lessons(self, group, day):
        payload = {
            'group_last': '',
            'group': group,
            'setdate': day
            }
        res = requests.post('https://schedule.kantiana.ru/setday', headers=self.headers, data=payload)
        if res.status_code != 200:
            print(res.status_code)
            return ERROR
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        lessons = []
        for i in soup.find_all('div', class_='col-12'):
            lesson = {}
            lesson['number'] = i.find('h5').text.strip()
            lesson['time'] = i.find('h6').text.strip()
            lesson['name'] = i.find_all('p', class_='card-text text-center')[0].text
            lesson['teacher'] = i.find_all('p', class_='card-text text-center')[1].text
            lesson['class'] = i.find_all('p', class_='card-text text-center')[2].text.split('\n')[0]
            lesson['group'] = i.find_all('p', class_='card-text text-center')[3].text
            lessons.append(lesson)
        return lessons
    
    def get_week_lessons(self, group, first_day):
        day = datetime_from_str(first_day)
        string_day = str_from_datetime(day)
        week = []
        for _ in range(7):
            lessons = self.get_day_lessons(group, string_day)
            week.append({string_day: lessons})
            time.sleep(0.1)
            day += datetime.timedelta(days=1)
            string_day = str_from_datetime(day)
        return week


if __name__ == '__main__':
    app = Parser()
    print(app.get_day_lessons('03_МОАИС_23_о_РБД_1', '2023-09-02'))
    print(app.get_week_lessons('03_МОАИС_23_о_РБД_1', '1.9.2023'))