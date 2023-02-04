from tg_bot import run_tg_bot
from loguru import logger

logger.add(
    'logs/{time}.log',
    format='{time} {level} {message}',
    level='DEBUG',
    rotation='100 MB',
    retention='14 days',
    compression='zip',
)

if __name__ == '__main__':
    run_tg_bot()
