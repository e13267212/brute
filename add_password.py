import telebot
import time
import re
import config

bot = telebot.TeleBot(config.token_dict)

@bot.message_handler(content_types=['text'])
def add_pass(message):
    if len(message.text) < 9:
        password = re.sub(r"[/#%!@*]", "", message.text)

        with open('passwords.txt', 'a+') as pass_file:
            pass_file.write(password + '\n')
            pass_file.close()

        with open('passwords.txt') as pass_file:
            pass_list = [i for i in pass_file]
            pass_list = list(set(pass_list))
            pass_list.sort()
            pass_file.close()

        with open('passwords.txt', 'w') as pass_file:
            for pwd in pass_list:
                pass_file.write(pwd)

            pass_file.close()
            bot.reply_to(message, 'done!')
    else:
        bot.reply_to(message, 'wrong!')

while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        print(e)
        time.sleep(15)