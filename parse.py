from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from database import DB
from datetime import datetime
import asyncio
from aiogram import Bot
import traceback
from config import Config


async def send_message(id, text):
    bot = Bot(token=Config.Bot.TOKEN)
    await bot.send_message(chat_id = id, text = text, disable_web_page_preview = True)
    await bot.session.close()

def login(browser, timeout=10):
    WebDriverWait(browser, timeout).until(EC.element_to_be_clickable((By.ID,  'onetrust-accept-btn-handler'))).click()
    WebDriverWait(browser, timeout).until(EC.element_to_be_clickable((By.ID,  'login-username-sign'))).send_keys(Config.Oddsportal.LOGIN)
    WebDriverWait(browser, timeout).until(EC.element_to_be_clickable((By.ID,  'login-password-sign'))).send_keys(Config.Oddsportal.PASSW)
    WebDriverWait(browser, timeout).until(EC.element_to_be_clickable((By.CLASS_NAME,  'user-button'))).click()

def parse_page(browser, player, timeout = 3):
    full_result = []
    WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[1]/div/main/div[3]/div[4]')))
    try:
        table = browser.find_element(By.CLASS_NAME, 'tab-content').find_element(By.TAG_NAME, 'div')
    except NoSuchElementException:
        return full_result
    rows = table.find_elements(By.XPATH, './*')
    for row in rows:
        row_sectors = row.find_elements(By.XPATH, './*')
        link_match = row_sectors[-1].find_element(By.TAG_NAME, 'a').get_attribute('href')
        type = row_sectors[-1].find_element(By.TAG_NAME, 'a').get_attribute('href').split('#')[1].split(';')[0]
        row_header = row_sectors[1].text.split('\n')
        json_res = {
            'user': player,
            'type': type,
            'sport': row_header[0],
            'country': row_header[2],
            'league': row_header[4],
            'avalable_results': [],
            'link_match': link_match,
            'link_user': f'https://www.oddsportal.com/profile/{player}/my-predictions/next/'
        }
        text_els = row_sectors[-1].find_elements(By.TAG_NAME, 'p')
        if type == 'league-winner':
            json_res.update({
                'player1': text_els[0].text,
            })
        elif type != 'league-winner':
            json_res.update({
                'type': text_els[2].text,
                'date': text_els[0].text,
                'time': text_els[1].text,
                'player1': text_els[3].text,
                'player2': text_els[4].text,
            })
        results = []
        pre_results = row_sectors[-1].find_element(By.TAG_NAME, 'div').find_elements(By.XPATH, './*[position() > 1]')
        for pre_result in pre_results:
            if pre_result.text != '':
                results.append(pre_result)
        kounter = 0
        for avalable_result in row_sectors[2].find_element(By.TAG_NAME, 'div').find_elements(By.TAG_NAME, 'div'):
            if 'PICK' in results[kounter].text:
                is_picked = True
            else:
                is_picked = False
            json_res['avalable_results'].append({
                'result': avalable_result.text,
                'coef': results[kounter].find_elements(By.TAG_NAME, 'p')[0].text,
                'is_picked': is_picked
                })
            kounter += 1
        full_result.append(json_res)
    return full_result
    

def parse_player(browser, player, timeout=5):
    result = []
    browser.get(f'https://www.oddsportal.com/profile/{player}/my-predictions/next/')
    try:
        last_page = browser.find_elements(By.CLASS_NAME, 'pagination-link')[-2].text
    except:
        last_page = 1
    for page in range(1, int(last_page)+1):
        if page != 1:
            browser.get(f'https://www.oddsportal.com/profile/{player}/my-predictions/next/page/{page}')
        result = result + parse_page(browser, player)
    return result
    
filter_names = {
    'Страна': 'country',
    'Спорт': 'sport',
    'Лига': 'league'
}

async def handle_result(array):
    for json in array:
        message = f"•{json['user']} - {json['type']} - {json['sport']} - {json['country']} - {json['league']}\n"
        if json['type'] == 'league-winner':
            message += f"•{json['player1']}\n"
        else:
            message += f"•{json['player1']} - {json['player2']} - {json['date']} {json['time']}\n"
        system_message = message
        for result in json['avalable_results']:
            if result['is_picked'] == True:
                message += f"✅ - {result['result']} - {result['coef']}x\n"
                system_message += f"✅ - {result['result']}\n"
            else:
                message += f"❌ - {result['result']} - {result['coef']}x\n"
                system_message += f"❌ - {result['result']}\n"
        if DB.Messages.select({'text': system_message}) != []:
            continue
        message += f'\n{json["link_match"]}\n{json["link_user"]}'
        player = DB.Players.select({'name': json['user']})[0]
        to_send_positive, to_send_negative = True, True
        for key_json in filter_names:
            k_positive, to_send_positive_small = 0, False
            for filter in DB.Filters.select({'player_id': player.id, 'type': key_json}):
                if filter.is_positive == 1:
                    k_positive += 1
                    if filter.keyword == json[filter_names[key_json]]:
                        to_send_positive_small = True
                if filter.is_positive == 0:
                    if filter.keyword == json[filter_names[key_json]]:
                        to_send_negative = False
            if k_positive != 0 and to_send_positive_small == False:
                to_send_positive = False
        if to_send_positive == True and to_send_negative == True:
            DB.Messages.insert({'text': system_message})
            for user in DB.Users.select({'to_notice': True}):
                await send_message(user.user_id, message)


async def main(browser):
    result = []
    for player in DB.Players.select():
        try:
            result = result + parse_player(browser, player.name)
        except Exception as e:
            print(f'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}. Ошибка при парсинге {player.name}')
            traceback.print_exc()
    await handle_result(result)


async def start_browser():
    options = Options()
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches",["enable-automation"])
    options.add_experimental_option("detach", True)
    # options.add_argument("--no-sandbox")
    # options.add_argument("--headless")
    # options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_argument('log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome(options=options)
    browser.maximize_window()
    browser.get('https://www.oddsportal.com/login')
    login(browser)
    return browser

async def finish_browser(browser):
    await browser.quit()


async def starter():
    browser = await start_browser()
    while True:
        try:
            await main(browser)
        except:
            print(f'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}. Главная ошибка:')
            traceback.print_exc()
            await finish_browser(browser)
            browser = await start_browser()
        else:
            print(f'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}. Парсинг произведён')
            print("Number of opened pages (tabs):", len(browser.window_handles))


if __name__ == '__main__':
    asyncio.run(starter())
