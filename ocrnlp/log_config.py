import logging

def setup_logging():
    logging.basicConfig(
        filename="logs/app.log",                  # куда писать
        level=logging.DEBUG,                     # уровень
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )