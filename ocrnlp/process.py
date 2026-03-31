from progress_ocr import *
f = process_image("/Users/kjj/Downloads/теория вероятности/tests/photo_2026-03-31_03-10-51.jpg")
print(f)
t = ocr_with_confidence("/Users/kjj/Downloads/теория вероятности/tests/пнг классик.png")[1]
#print(t)





print("""{'full_name': 'Петр Алексей Андреевич', 'own_date': '26.01.2024', 'reg_num': '92-4567', 'doc_num': '876543210987', 'date_from': '10 января 2024 г.', 'date_to': '25 января 2024 г.', 'city_name': 'Санкт-Петербург', 'new_spec': "Анализ данных", 'hours_num': '72', 'organization': 'ООО «Компания Пример Учебный центр «Профи»'}""")
