# pattern_library: имя паттерна -> regex
# document_schemas: тип документа -> поле -> список имен паттернов
patterns ={
   "pattern_lib" : {
                     #имеется ввиду после "что" V
        "full_name_classic": r"что\s([А-ЯЁ][а-яё]+)\s([А-ЯЁ][а-яё]+)\s([А-ЯЁ][а-яё]+)",
        "own_date_classic": r"выдачи\s+(\d{2}\.\d{2}\.\d{4})",
        "own_date_t2": r"выдачи\s+(\d{2}\s+[а-яё]+\s+\d{4}\s+г\.)",
        "reg_num_classic": r"Регистрационный\s+номер\s+(\d+-\d+)",
        "reg_num_t2": r"Регистрационный\s+номер\s+(\d{6})",
        "doc_num_classic":r"О\s+ПОВЫШЕНИИ\s+КВАЛИФИКАЦИИ\s+(\d+)",
        "doc_num_t2":r"\d{12}",
        "date_from_to_classic":r"с\s+(\d{2}\s+[а-яё]+\s+\d{4}\s+г\.)\sпо\s+(\d{2}\s+[а-яё]+\s+\d{4}\s+г\.)",
        "city_name_classic":r"Город\s([А-ЯЁ][а-яё]+(?:-[А-ЯЁ]?[а-яё]+)*)",
        "new_spec_classic": r"программе\s+«([^»]+)»",
        "hours_num_classic": r"объеме\s+(\d+)",
        "organization_classic": r"квалификации\s+в\s+(?:\(на\)\s+)?([\s\S]*?)\s+с\s+\d{2}\s+[а-яё]+\s+\d{4}\s+г\.",
        "organization_t2": r"обучение\s+в\s+(?:\(на\)\s+)?([\s\S]*?)\s+по\s+программе" 
    },
    "doc_schemas" : {
        "doc_type1": {
            "full_name": ["full_name_classic"],
            "own_date" : ["own_date_classic"],
            "reg_num" : ["reg_num_classic"],
            "doc_num" : ["doc_num_classic"],
            "date_from_to" : ["date_from_to_classic"],
            "city_name" : ["city_name_classic"],
            "new_spec" : ["new_spec_classic"],
            "hours_num" : ["hours_num_classic"],
            "organization" : [ "organization_classic"]
        },
        "doc_type2": {
            "full_name": ["full_name_classic"],
            "own_date" : ["own_date_t2"],
            "reg_num" : ["reg_num_t2"],
            "doc_num" : ["doc_num_t2"],
            "date_from_to" : ["date_from_to_classic"],
            "city_name" : ["city_name_classic"],
            "new_spec" : ["new_spec_classic"],
            "hours_num" : ["hours_num_classic"],
            "organization" : ["organization_t2"]
        }
    }
}
