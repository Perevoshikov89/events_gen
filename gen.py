import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from faker import Faker
from uuid import uuid4

# --- Инициализация ---
fake = Faker("ru_RU")

# --- Валидаторы ИНН и СНИЛС ---
def validate_inn(inn: str) -> bool:
    if len(inn) != 12 or not inn.isdigit():
        return False

    def calc(digits, coeffs):
        return str(sum(int(d) * c for d, c in zip(digits, coeffs)) % 11 % 10)

    n1 = calc(inn[:10], [7, 2, 4, 10, 3, 5, 9, 4, 6, 8])
    n2 = calc(inn[:11], [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8])
    return inn[10] == n1 and inn[11] == n2

def validate_snils(snils: str) -> bool:
    if len(snils) != 11 or not snils.isdigit():
        return False

    num = snils[:9]
    control = int(snils[9:])
    s = sum(int(num[i]) * (9 - i) for i in range(9))
    if s < 100:
        check = s
    elif s in (100, 101):
        check = 0
    else:
        check = s % 101
        if check in (100, 101):
            check = 0

    return check == control

# --- Генерация валидных значений ---
def generate_valid_inn():
    while True:
        inn = str(fake.random_int(100000000000, 999999999999))
        if validate_inn(inn):
            return inn

def generate_valid_snils():
    while True:
        snils = str(fake.random_int(10000000000, 99999999999)).zfill(11)
        if validate_snils(snils):
            return snils

# --- Генерация случайного субъекта ---
def generate_random_person():
    name_parts = fake.name().split()
    while len(name_parts) < 3:
        name_parts.append("")
    return {
        "lastName": name_parts[0].upper(),
        "firstName": name_parts[1].upper(),
        "middleName": name_parts[2].upper(),
        "birthDate": fake.date_of_birth(minimum_age=18, maximum_age=99).strftime('%Y-%m-%d'),
        "birthPlace": fake.city().upper(),
        "citizenship": "643",
        "docCode": "21",
        "docSeries": str(fake.random_int(1000, 9999)),
        "docNum": str(fake.random_int(100000, 999999)),
        "issueDate": fake.date_between(start_date='-15y', end_date='-1y').strftime('%Y-%m-%d'),
        "docIssuer": fake.company().upper(),
        "deptCode": f"{fake.random_int(100,999)}-{fake.random_int(100,999)}",
        "foreignerCode": "1",
        "taxNum": generate_valid_inn(),
        "snils": generate_valid_snils()
    }

def generate_prev_name():
    name_parts = fake.name().split()
    while len(name_parts) < 3:
        name_parts.append("")
    return {
        "lastName": name_parts[0].upper(),
        "firstName": name_parts[1].upper(),
        "middleName": name_parts[2].upper(),
        "date": fake.date_between(start_date='-20y', end_date='-10y').strftime('%Y-%m-%d')
    }

def generate_prev_doc():
    return {
        "countryCode": str(fake.random_int(100, 899)),
        "docCode": "21",
        "docSeries": str(fake.random_int(1000, 9999)),
        "docNum": str(fake.random_int(100000, 999999)),
        "issueDate": fake.date_between(start_date='-15y', end_date='-5y').strftime('%Y-%m-%d'),
        "docIssuer": fake.company().upper(),
        "deptCode": f"{fake.random_int(100,999)}-{fake.random_int(100,999)}",
        "endDate": fake.date_between(start_date='today', end_date='+10y').strftime('%Y-%m-%d')
    } 

  
# --- Генерация события FL_Event_1_1 ---
def build_event_fl_1_1(date_str):
    fl_event = ET.Element("FL_Event_1_1", {
        "operationCode": "A",
        "orderNum": "1",
        "eventDate": date_str
    })

    application = ET.SubElement(fl_event, "FL_55_Application")
    ET.SubElement(application, "role").text = "1"
    ET.SubElement(application, "sum").text = f"{fake.random_int(100000, 1000000):.2f}"
    ET.SubElement(application, "currency").text = "RUB"
    ET.SubElement(application, "uid").text = str(uuid4()) + "-e"

    application_date = fake.date_between(start_date='-30d', end_date='today').strftime('%Y-%m-%d')
    ET.SubElement(application, "applicationDate").text = application_date
    ET.SubElement(application, "sourceCode").text = "1"
    ET.SubElement(application, "wayCode").text = "6"
    ET.SubElement(application, "stageEndDate").text = application_date
    ET.SubElement(application, "purposeCode").text = "2"
    ET.SubElement(application, "stageCode").text = "1"
    ET.SubElement(application, "stageDate").text = application_date
    ET.SubElement(application, "applicationCode").text = "6"
    ET.SubElement(application, "num").text = application_date.replace("-", "") + f"-{fake.random_int(10000,99999)}"
    ET.SubElement(application, "loanSum").text = application.find("sum").text

    return fl_event

# --- Построение XML для события ---
def build_events(date_str):
    events = ET.Element("Events")
    events.append(build_event_fl_1_1(date_str))
    return events

# --- Построение других частей документа ---

def build_title(person):
    title = ET.Element("Title")
    fl_group = ET.SubElement(title, "FL_1_4_Group")

    fl_name = ET.SubElement(fl_group, "FL_1_Name")
    ET.SubElement(fl_name, "lastName").text = person["lastName"]
    ET.SubElement(fl_name, "firstName").text = person["firstName"]
    ET.SubElement(fl_name, "middleName").text = person["middleName"]

    fl_doc = ET.SubElement(fl_group, "FL_4_Doc")
    ET.SubElement(fl_doc, "countryCode").text = person["citizenship"]
    ET.SubElement(fl_doc, "docCode").text = person["docCode"]
    ET.SubElement(fl_doc, "docSeries").text = person["docSeries"]
    ET.SubElement(fl_doc, "docNum").text = person["docNum"]
    ET.SubElement(fl_doc, "issueDate").text = person["issueDate"]
    ET.SubElement(fl_doc, "docIssuer").text = person["docIssuer"]
    ET.SubElement(fl_doc, "deptCode").text = person["deptCode"]
    ET.SubElement(fl_doc, "foreignerCode").text = person["foreignerCode"]

    fl_2_5_group = ET.SubElement(title, "FL_2_5_Group")

    # --- Случайное предыдущее имя ---
    prev_name = generate_prev_name()
    fl_2_prev_name = ET.SubElement(fl_2_5_group, "FL_2_PrevName")
    ET.SubElement(fl_2_prev_name, "prevNameFlag_1")
    ET.SubElement(fl_2_prev_name, "lastName").text = prev_name["lastName"]
    ET.SubElement(fl_2_prev_name, "firstName").text = prev_name["firstName"]
    ET.SubElement(fl_2_prev_name, "middleName").text = prev_name["middleName"]
    ET.SubElement(fl_2_prev_name, "date").text = prev_name["date"]

    # --- Случайный предыдущий документ ---
    prev_doc = generate_prev_doc()
    fl_5_prev_doc = ET.SubElement(fl_2_5_group, "FL_5_PrevDoc")
    ET.SubElement(fl_5_prev_doc, "prevDocFact_1")
    ET.SubElement(fl_5_prev_doc, "countryCode").text = prev_doc["countryCode"]
    ET.SubElement(fl_5_prev_doc, "docCode").text = prev_doc["docCode"]
    ET.SubElement(fl_5_prev_doc, "docSeries").text = prev_doc["docSeries"]
    ET.SubElement(fl_5_prev_doc, "docNum").text = prev_doc["docNum"]
    ET.SubElement(fl_5_prev_doc, "issueDate").text = prev_doc["issueDate"]
    ET.SubElement(fl_5_prev_doc, "docIssuer").text = prev_doc["docIssuer"]
    ET.SubElement(fl_5_prev_doc, "deptCode").text = prev_doc["deptCode"]
    ET.SubElement(fl_5_prev_doc, "endDate").text = prev_doc["endDate"]

    fl_birth = ET.SubElement(title, "FL_3_Birth")
    ET.SubElement(fl_birth, "birthDate").text = person["birthDate"]
    ET.SubElement(fl_birth, "countryCode").text = "999"
    ET.SubElement(fl_birth, "birthPlace").text = person["birthPlace"]

    fl_tax = ET.SubElement(title, "FL_6_Tax")
    tax_group = ET.SubElement(fl_tax, "TaxNum_group_FL_6_Tax")
    ET.SubElement(tax_group, "taxCode").text = "1"
    ET.SubElement(tax_group, "taxNum").text = person["taxNum"]
    ET.SubElement(tax_group, "innChecked_0")
    ET.SubElement(fl_tax, "regNum").text = "_"
    ET.SubElement(fl_tax, "specialMode_0")

    fl_social = ET.SubElement(title, "FL_7_Social")
    ET.SubElement(fl_social, "socialNum").text = person["snils"]

    return title


def build_subject_fl(person):
    subject = ET.Element("Subject_FL")
    title = build_title(person)
    subject.append(title)
    return subject

def build_data(person, date_str):
    data = ET.Element("Data")
    subject_fl = build_subject_fl(person)
    
    # Вставляем <Events> с <FL_Event_1_1>
    events = build_events(date_str)
    subject_fl.append(events)

    data.append(subject_fl)
    return data

def build_source(date_str):
    source = ET.Element("Source")
    fl_46_org_source = ET.SubElement(source, "FL_46_UL_36_OrgSource")
    ET.SubElement(fl_46_org_source, "sourceCode").text = "1"
    ET.SubElement(fl_46_org_source, "sourceRegistrationFact_0")
    ET.SubElement(fl_46_org_source, "fullName").text = "ООО Тестовая передача"
    ET.SubElement(fl_46_org_source, "shortName").text = "ООО Тестовая передача"
    ET.SubElement(fl_46_org_source, "otherName").text = "ООО Тестовая передача"
    ET.SubElement(fl_46_org_source, "sourceDateStart").text = "2020-01-01"
    ET.SubElement(fl_46_org_source, "regNum").text = "1"

    tax_num_group = ET.SubElement(fl_46_org_source, "TaxNum_group_FL_46_UL_36_OrgSource")
    ET.SubElement(tax_num_group, "taxCode").text = "1"
    ET.SubElement(tax_num_group, "taxNum").text = "1"

    ET.SubElement(fl_46_org_source, "sourceCreditInfoDate").text = date_str

    return source

def build_document(person, reg_number, date_str):
    document = ET.Element("Document", {
        "xmlns:xs": "http://www.w3.org/2001/XMLSchema",
        "schemaVersion": "3.0",
        "ogrn": "1234567890123",
        "sourceID": "YP01MM000001",
        "regNumberDoc": reg_number,
        "dateDoc": date_str,
        "inn": "123456789012",
        "subjectsCount": "1",
        "groupBlocksCount": "1",
        "regNumberDocInaccept": reg_number
    })

    document.append(build_source(date_str))
    document.append(build_data(person, date_str))
    return document

def prettify(elem):
    rough_string = ET.tostring(elem, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    xml_string = reparsed.toprettyxml(indent="    ", encoding="utf-8").decode("utf-8")

    # Перенос атрибутов <Document ...> в столбик
    lines = xml_string.splitlines()
    new_lines = []
    for line in lines:
        if line.startswith("<Document "):
            parts = line.replace("<Document ", "").rstrip(">").split('" ')
            new_lines.append("<Document")
            for part in parts:
                if part:
                    if not part.endswith('"'):
                        part += '"'
                    new_lines.append("    " + part.strip())
            new_lines[-1] += ">"
        else:
            new_lines.append(line)
    return "\n".join(new_lines)

# --- Основной запуск ---
if __name__ == "__main__":
    now = datetime.now()
    date_for_doc = now.strftime('%Y-%m-%d')
    timestamp = now.strftime('%Y%m%d_%H%M%S')

    base_id = "YP01MM000001"
    reg_number = f"{base_id}_{timestamp}"

    person_data = generate_random_person()
    document_xml = build_document(person_data, reg_number, date_for_doc)

    file_name = f"{reg_number}.xml"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(prettify(document_xml))

    print(f"Документ сохранен в файл: {file_name}")
