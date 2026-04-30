import logging

def setup_logging():
    logging.basicConfig(
        filename="/Users/kjj/Documents/GitHub/Document_scanning_project/logs/app.log",                         # куда писать
        level=logging.DEBUG,                         # уровень
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )