from src.bot.bot import Bot


def main():
    bot = Bot(rate_limit=20)
    bot.run_bot()


if __name__ == '__main__':
    main()