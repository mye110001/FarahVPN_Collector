# telegram_parser.py
import os
import re
import asyncio
from pyrogram import Client, errors

# --- КОНСТАНТЫ ИЗ СЕКРЕТОВ GITHUB ACTIONS ---
try:
    API_ID = int(os.environ['TG_API_ID'])
    API_HASH = os.environ['TG_API_HASH']
    BOT_TOKEN = os.environ['BOT_TOKEN']
except KeyError as e:
    print(f"Ошибка: Отсутствует необходимая переменная окружения {e}. Проверьте Secrets.")
    exit(1)

# Имя вашего канала (username без @)
CHANNEL_USERNAME = "Farah_VPN" 

OUTPUT_FILENAME = "farah_vpn_configs.txt"
CONFIG_COUNT = 500 # Сканировать последние 500 сообщений

# Шаблон для поиска VLESS, VMESS, TROJAN, SS, SSR
# Ищет протокол:// и все символы до первого пробела или новой строки
CONFIG_REGEX = re.compile(r'(vless|vmess|trojan|ss|ssr|hysteria|hy2)://[^\s]+', re.IGNORECASE)

async def main():
    configs = set()
    
    # Инициализация клиента
    app = Client(
        "Farah_VPN_Collector",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN # Используем бота для авторизации, это стабильнее в Actions
    )

    try:
        await app.start()
        print(f"Парсинг канала: @{CHANNEL_USERNAME}")

        # Сканируем сообщения
        async for message in app.get_chat_history(CHANNEL_USERNAME, limit=CONFIG_COUNT):
            if message.text:
                config_matches = CONFIG_REGEX.findall(message.text)
                
                for match in config_matches:
                    # Нормализация: приводим схему (vless://, vmess://) к нижнему регистру
                    config_uri = match.lower()
                    configs.add(config_uri)
        
        await app.stop()

        print(f"Найдено {len(configs)} уникальных конфигов.")
        
        # Сохраняем в файл
        if configs:
            with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
                f.write('\n'.join(sorted(configs)))
            print(f"Конфиги сохранены в {OUTPUT_FILENAME}")
        else:
            print("Конфиги не найдены. Файл не создан/обновлен.")

    except errors.AuthKeyUnregistered:
        print("Ошибка авторизации: Ключи API недействительны или токен бота неверен.")
    except Exception as e:
        print(f"Произошла ошибка при парсинге: {e}")
        if 'CHANNEL_INVALID' in str(e):
             print(f"Проверьте, что @{CHANNEL_USERNAME} является публичным каналом.")
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())