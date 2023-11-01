import requests
import datetime
import bs4
import time
from io import BytesIO

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
            lesson['type'] = i.find('p', class_='card-text rounded-3 text-center').text.strip()
            lesson['name'] = i.find_all('p', class_='card-text text-center')[0].text
            lesson['teacher'] = i.find_all('p', class_='card-text text-center')[1].text
            lesson['class'] = i.find_all('p', class_='card-text text-center')[2].text.split('\n')[0]
            lesson['group'] = i.find_all('p', class_='card-text text-center')[3].text
            lessons.append(lesson)
        return lessons
    
    def get_week_lessons(self, group, first_day):
        day = datetime_from_str(first_day)
        string_day = str_from_datetime(day)
        week = {}
        for _ in range(7):
            lessons = self.get_day_lessons(group, string_day)
            week.update({string_day: lessons})
            time.sleep(0.001)
            day += datetime.timedelta(days=1)
            string_day = str_from_datetime(day)
        return week
    
    def get_groups(self):
        res = requests.get('https://schedule.kantiana.ru/')

        if res.status_code != 200:
            return ERROR
        
        soup = bs4.BeautifulSoup(res.text, 'html.parser')

        groups = {'03':[], '04':[], '05': [], '06':[], '08':[]}

        for i in soup.find_all('option')[1:]:
            if i.text.startswith('0'):
                num = i.text.split('_')[0]
                if num in groups:
                    groups[num].append(i.text.strip())
        
        return groups
    
    def get_image_groups(self):
        res = requests.get('https://schedule.kantiana.ru/static/group.jpg')
        photo_data = BytesIO(res.content)
        return photo_data
