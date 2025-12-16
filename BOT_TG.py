from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import datetime
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Общий токен бота
TOKEN = "8222858325:AAGHHnc3dYWYjUrkOnS7HABaSyVKKLgFM6o"

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Список активных групп
active_group_ids = set()

# Словарь для хранения активных ключей
active_keys = {}

# Набор проверенных пользователей
verified_users = set()

# Единственное доступное действие для неподтвержденных пользователей
allowed_commands = {"/key"}

# 🗂️ Словарь для хранения никнеймов (без базы данных!)
nicknames = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    await update.message.reply_text("Привет! Чтобы начать работу, введите ключ с помощью команды /key.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help."""
    help_message = (
        "<b>📌 Инструкция по работе с ботом:</b>\n\n"
        "<i>Основные команды:</i>\n\n"
        "🔑 <code>/key ваш_ключ</code> — подтверждение доступа с использованием уникального ключа.\n"
        "🚨 <code>/bot</code> — проверка работоспособности бота.\n"
        "📝 <code>/info</code> — информация о семье.\n"
        "\n<b>Работа с никнеймами:</b>\n"
        "💬 <code>/snick @username new_nickname</code> — присвоить никнейм пользователю.\n"
        "🛠️ <code>/nlist</code> — вывести список всех установленных никнеймов.\n"
        "🗑️ <code>/dnick @username</code> — удалить никнейм пользователя.\n"
        "\n<b>Специальные мероприятия:</b>\n"
        "🕰️ <code>/reid</code> — информация о рейдах.\n"
        "💥 <code>/fv</code> — информация о семейных ограблениях.\n"
        "\n<i>Дополнительные возможности становятся доступны после подтверждения доступа.</i>"
    )
    await update.message.reply_html(text=help_message)

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /info."""
    if not await check_access(update, context): return
    family_info = (
        "Вас приветствует семья HUCKSTERS (06)\n"
        "Фамка специализируется на общении, коммуникации и командной игре на проекте \"Amazing PR\"\n"
        "Активная фама, участвующая на мероприятиях и других семейных активностях\n\n"
        "Феймовая фама, имеющая большую популярность не только на 06 сервере, но и на других серверах, обладает хорошей доминацией над другими семьями на сервере\n\n"
        "В составе HUCKSTERS одни из лучших стрелков сервера 06, обладающие большим опытом игры, что значительно повышает конкурентоспособность\n\n"
        "Семья существует уже длительное время, ранее она называлась (Gladiator's), и это название остается известным на сервере GREEN, именно оттуда всё началось. Именно там был взят первый рейд без какой-либо поддержки извне\n\n"
        "В заключение семья HUCKSTERS передает привет своим конкурентам и пока что может предложить лишь одно — отсосать и не чавкать при этом!"
    )
    await update.message.reply_text(family_info)

async def add_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда для добавления нового ключа администратором.
    Пример использования: /addkey ваш_ключ
    """
    if len(context.args) != 1:
        await update.message.reply_text("Используйте команду следующим образом: /addkey ваш_ключ")
        return
    
    key = context.args[0]
    active_keys[key] = True
    await update.message.reply_text(f"Ключ {key} успешно добавлен!")

async def del_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда для удаления существующего ключа администратором.
    Пример использования: /delkey ваш_ключ
    """
    if len(context.args) != 1:
        await update.message.reply_text("Используйте команду следующим образом: /delkey ваш_ключ")
        return
    
    key = context.args[0]
    if key in active_keys:
        del active_keys[key]
        await update.message.reply_text(f"Ключ {key} удалён.")
    else:
        await update.message.reply_text("Указанный ключ не найден.")

async def enter_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда для ввода ключа пользователем.
    Пример использования: /key ваш_ключ
    """
    if len(context.args) != 1:
        await update.message.reply_text("Используйте команду следующим образом: /key ваш_ключ")
        return
    
    user_id = update.effective_user.id
    key = context.args[0]
    
    if key in active_keys and active_keys[key]:
        verified_users.add(user_id)
        await update.message.reply_text("Вы успешно подтвердили свою личность. Теперь можете пользоваться ботом.")
    else:
        await update.message.reply_text("Некорректный ключ. Попробуйте снова.")

async def check_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Проверяет, прошел ли пользователь проверку.
    """
    user_id = update.effective_user.id
    command = update.message.text.strip()

    if command.startswith("/") and command not in allowed_commands and user_id not in verified_users:
        await update.message.reply_text("Сначала подтвердите доступ с помощью команды /key.")
        return False
    return True

# ⭐ НОВАЯ КОМАНДА 🤖
async def bot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отвечает на команду /bot."""
    if not await check_access(update, context): return
    first_name = update.effective_user.first_name
    reply = f"Привет, {first_name}, я тут."
    await update.message.reply_text(reply)

# 🎯 Новые команды для работы с никнеймами 🏆
async def snick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда для установки никнейма пользователю.
    Формат: /snick @username your_new_nickname
    """
    if not await check_access(update, context): return
    
    args = context.args
    if len(args) != 2 or '@' not in args[0]:
        await update.message.reply_text("Использование: /snick @username new_nickname")
        return
    
    username = args[0].strip('@')
    new_nickname = args[1]
    
    nicknames[username] = new_nickname
    await update.message.reply_text(f"Ники обновлены!\nИспользуйте /nlist для просмотра текущего списка.")

async def nlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда для вывода списка всех существующих никнеймов с активными ссылками.
    """
    if not await check_access(update, context): return
    
    if not nicknames:
        await update.message.reply_text("Нет установленных никнеймов.")
        return
    
    # Формируем список никнеймов с активной ссылкой на каждого пользователя
    nicknames_list = []
    for username, nickname in nicknames.items():
        link = f'<a href="tg://resolve?domain={username}">{username}</a>'
        nicknames_list.append(f"{link} → {nickname}")
    
    formatted_list = "\n".join(nicknames_list)
    await update.message.reply_html(f"<b>Установленные никнеймы:</b>\n{formatted_list}")

async def dnick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда для удаления никнейма пользователя.
    Формат: /dnick @username
    """
    if not await check_access(update, context): return
    
    args = context.args
    if len(args) != 1 or '@' not in args[0]:
        await update.message.reply_text("Использование: /dnick @username")
        return
    
    username = args[0].strip('@')
    
    if username in nicknames:
        del nicknames[username]
        await update.message.reply_text(f"Никнейм для {username} успешно удалён.")
    else:
        await update.message.reply_text(f"Указанного никнейма не найдено.")

# 🕰️ Реализация команды /reid
async def reid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Реализует команду /reid"""
    if not await check_access(update, context): return
    response = (
        "__Рейд__ — мероприятие, предназначенное исключительно для криминальных организаций и семей, "
        "у которых активировано улучшение **«Рейды»**. Это улучшение открывает доступ к особым рейдовым событиям, "
        "предлагающим разнообразные задачи и возможности для участников.\n\n"
        
        "*Местоположение и время проведения*\n"
        "Рейды начинаются автоматически каждые **3 часа**: в **9:05**, **12:05**, **15:05**, **18:05**, **21:05**, **00:05** и **03:05** по московскому времени. "
        "Продолжительность каждого рейда — **40 минут** с момента начала.\n\n"
        
        "_Всего существует четыре локации нефтяных вышек:_"
        "- Территория возле авианосца\n"
        "- Территория возле новогоднего острова\n"
        "- Территория возле вокзала г. Южный\n"
        "- Территория возле фермы\n\n"
        
        "*Проведение рейда*\n"
        "Рейд состоит из **восьми волн**, каждая из которых имеет свои особенности:\n"
        "- Волна 1: уничтожение NPC-персонажей и захват нефтяной вышки.\n"
        "- Волна 2: поиск ключей, расположенных на различных платформах. Чёрные ключи трудно заметить, но достаточно нажать \"E\", чтобы поднять их.\n"
        "- Волны 3–8: появление 6 бочек с топливом для запуска цеха и более ожесточённое противостояние с NPC. С каждой волной сложность возрастает, NPC становятся сильнее.\n\n"
        
        "После прохождения всех восьми волн и успешного завершения рейда участники получают награду.\n\n"
        
        "*Особенности проведения*\n"
        "Между волнами предусмотрены короткие перерывы — от **1,5 до 3 минут** — для подготовки к следующему этапу. В начале каждой волны игроков ожидает воздушная атака с взрывами на платформах.\n\n"
        
        "Если участники выдерживают все 8 волн, появляется груз, который могут подобрать **2–4 игрока**. Если целостность груза упадет до **0%**, он считается испорченным, и содержимое утеряно.\n\n"
        
        "*Получение и распределение груза*\n"
        "После получения груза игроку с меньшим ID среди участников предлагается выбрать, кому его отдать — семье или организации"
    )
    await update.message.reply_markdown(response)

# 💥 Реализация команды /fv
async def fv_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Реализует команду /fv"""
    if not await check_access(update, context): return
    response = (
        "Семейное ограбление — особое мероприятие для семей в игре, позволяющее получить дополнительное денежное вознаграждение. Участвовать могут только члены семей, число участников — неограничено. Начинается в 18:00 по московскому времени, у семьи есть 3 часа на выполнение целей.\n\n"
        
        "__Основная суть__\n"
        "Цель — угнать автомобиль, заработать деньги и отмыть их в здании Маяка. Месторасположение автомобилей может меняться, но начните с обращения к коммерсанту Жоре за информацией о месте нахождения авто.\n\n"
        
        "Когда задание появится, немедленно направляйтесь к Жоре. Он продаёт сведения о местонахождении машины. Координатор поможет грамотно распределить силы, иначе конкуренты могут атаковать первыми.\n\n"
        
        "__Этапы ограбления__\n"
        "1. Поиск и зачистка локации — найдите и захватите автомобиль, соберите:\n"
        "— Охранника с запиской и секретными кодами для отмывания денег\n"
        "— Портфель с инструментами для ремонта автомобиля\n\n"
        
        "2. Перегонка и охрана — переведите машину на Южный Химический Завод, где надо найти мешки с деньгами. Там много наёмников, защищающих деньги лучше, чем автомобиль.\n\n"
        
        "3. Отмывание денег — доставьте грузовик с деньгами в Маяк, найдите Виталия и с помощью компьютера и кодов осуществите отмывку. За успешное завершение вас ждет приятный бонус.\n\n"
        
        "__Помощник Жора__\n"
        "Жора — торговец информацией и услугами. Продаст вам информацию о местоположении автомобиля, найме охраны и даже откроет шлагбаум для быстрого проникновения на объект. Его помощь весьма полезна!"
    )
    await update.message.reply_markdown(response)

# Обработчик массовых рассылок
async def send_message_to_all_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем наличие аргументов команды (/g)
    if len(context.args) > 0:
        message_text = ' '.join(context.args)
        
        for group_id in active_group_ids:
            try:
                await context.bot.send_message(group_id, text=message_text)
            except Exception as e:
                logger.error(f"Ошибка отправки в группу {group_id}: {e}")
    
        await update.message.reply_text("Сообщение успешно отправлено во все группы!")
    else:
        await update.message.reply_text("Используйте команду в таком формате: /g ваш_текст")

# Функция обработки новых сообщений в группе
async def handle_new_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик новых сообщений в группах."""
    global active_group_ids
    group_id = update.effective_chat.id
    active_group_ids.add(group_id)
    logger.info(f'Группа {group_id} была добавлена.')

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Обработка старта бота
    application.add_handler(CommandHandler("start", start))
    
    # Массовые рассылки по командам
    application.add_handler(CommandHandler("g", send_message_to_all_groups))
    
    # Другие команды
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("addkey", add_key))   
    application.add_handler(CommandHandler("delkey", del_key))   
    application.add_handler(CommandHandler("key", enter_key))    
    application.add_handler(CommandHandler("bot", bot_command))  
    application.add_handler(CommandHandler("snick", snick_command))  
    application.add_handler(CommandHandler("nlist", nlist_command))  
    application.add_handler(CommandHandler("dnick", dnick_command))  
    application.add_handler(CommandHandler("reid", reid_command))  
    application.add_handler(CommandHandler("fv", fv_command))       

    # Добавляем обработчик входящих сообщений для отслеживания групп
    application.add_handler(MessageHandler(filters.ChatType.GROUPS | filters.ChatType.SUPERGROUP, handle_new_group))
    
    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
