import xml.etree.ElementTree as ET
from faker import Faker
from uuid import uuid4
from datetime import datetime
import random
import re

fake = Faker("ru_RU")


# --- Валидация ---
def validate_uid(uid: str) -> bool:
    pattern = re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}-[a-f0-9]$')
    return bool(pattern.match(uid))

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


# --- Генераторы ---
def generate_uid_with_suffix():
    return f"{str(uuid4()).lower()}-{random.choice('abcdef0123456789')}"

def generate_valid_inn():
    while True:
        inn = str(fake.random_int(10**11, 10**12 - 1))
        if validate_inn(inn):
            return inn

def generate_valid_snils():
    while True:
        snils = str(fake.random_int(10**10, 10**11 - 1)).zfill(11)
        if validate_snils(snils):
            return snils

def generate_person():
    name_parts = fake.name().split()
    while len(name_parts) < 3:
        name_parts.append("")
    return {
        "lastName": name_parts[0].upper(),
        "firstName": name_parts[1].upper(),
        "middleName": name_parts[2].upper(),
        "birthDate": fake.date_of_birth(minimum_age=18, maximum_age=99).strftime('%Y-%m-%d'),
        "birthPlace": fake.city().upper(),
        "countryCode": "643",
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
    parts = fake.name().split()
    while len(parts) < 3:
        parts.append("")
    return {
        "lastName": parts[0].upper(),
        "firstName": parts[1].upper(),
        "middleName": parts[2].upper(),
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


# --- Page Object классы ---
class EventPage:
    def __init__(self, date_str):
        self.date_str = date_str

    def build(self):
        root = ET.Element("FL_Event_1_1", {
            "operationCode": "A", "orderNum": "1", "eventDate": self.date_str
        })

        app = ET.SubElement(root, "FL_55_Application")
        ET.SubElement(app, "role").text = "1"
        ET.SubElement(app, "sum").text = f"{fake.random_int(100000, 1000000):.2f}"
        ET.SubElement(app, "currency").text = "RUB"

        uid = generate_uid_with_suffix()
        if not validate_uid(uid):
            raise ValueError(f"Invalid UID: {uid}")
        ET.SubElement(app, "uid").text = uid

        app_date = fake.date_between(start_date='-30d', end_date='today').strftime('%Y-%m-%d')
        for tag, value in {
            "applicationDate": app_date, "sourceCode": "1", "wayCode": "6",
            "stageEndDate": app_date, "purposeCode": "2", "stageCode": "1",
            "stageDate": app_date, "applicationCode": "6",
            "num": app_date.replace("-", "") + f"-{fake.random_int(10000,99999)}",
            "loanSum": app.find("sum").text
        }.items():
            ET.SubElement(app, tag).text = value

        return root


class TitlePage:
    def __init__(self, person):
        self.person = person

    def build(self):
        title = ET.Element("Title")
        fl_group = ET.SubElement(title, "FL_1_4_Group")
        fl_name = ET.SubElement(fl_group, "FL_1_Name")
        for field in ("lastName", "firstName", "middleName"):
            ET.SubElement(fl_name, field).text = self.person[field]

        fl_doc = ET.SubElement(fl_group, "FL_4_Doc")
        for tag in ["countryCode", "docCode", "docSeries", "docNum", "issueDate", "docIssuer", "deptCode", "foreignerCode"]:
            ET.SubElement(fl_doc, tag).text = self.person[tag if tag != "countryCode" else "countryCode"]

        fl_2_5_group = ET.SubElement(title, "FL_2_5_Group")
        prev_name = generate_prev_name()
        fl_prev = ET.SubElement(fl_2_5_group, "FL_2_PrevName")
        ET.SubElement(fl_prev, "prevNameFlag_1")
        for tag in ("lastName", "firstName", "middleName", "date"):
            ET.SubElement(fl_prev, tag).text = prev_name[tag]

        prev_doc = generate_prev_doc()
        fl_doc = ET.SubElement(fl_2_5_group, "FL_5_PrevDoc")
        ET.SubElement(fl_doc, "prevDocFact_1")
        for tag in ("countryCode", "docCode", "docSeries", "docNum", "issueDate", "docIssuer", "deptCode", "endDate"):
            ET.SubElement(fl_doc, tag).text = prev_doc[tag]

        fl_birth = ET.SubElement(title, "FL_3_Birth")
        ET.SubElement(fl_birth, "birthDate").text = self.person["birthDate"]
        ET.SubElement(fl_birth, "countryCode").text = "999"
        ET.SubElement(fl_birth, "birthPlace").text = self.person["birthPlace"]

        fl_tax = ET.SubElement(title, "FL_6_Tax")
        group = ET.SubElement(fl_tax, "TaxNum_group_FL_6_Tax")
        ET.SubElement(group, "taxCode").text = "1"
        ET.SubElement(group, "taxNum").text = self.person["taxNum"]
        ET.SubElement(group, "innChecked_0")
        ET.SubElement(fl_tax, "regNum").text = "_"
        ET.SubElement(fl_tax, "specialMode_0")

        fl_social = ET.SubElement(title, "FL_7_Social")
        ET.SubElement(fl_social, "socialNum").text = self.person["snils"]

        return title


class DocumentBuilder:
    def __init__(self, person, reg_number, date_str):
        self.person = person
        self.reg_number = reg_number
        self.date_str = date_str

    def build(self):
        doc = ET.Element("Document", {
            "xmlns:xs": "http://www.w3.org/2001/XMLSchema",
            "schemaVersion": "3.0",
            "ogrn": "1234567890123",
            "sourceID": "YP01MM000001",
            "regNumberDoc": self.reg_number,
            "dateDoc": self.date_str,
            "inn": "123456789012",
            "subjectsCount": "1",
            "groupBlocksCount": "1",
            "regNumberDocInaccept": self.reg_number
        })

        source = ET.SubElement(doc, "Source")
        org = ET.SubElement(source, "FL_46_UL_36_OrgSource")
        ET.SubElement(org, "sourceCode").text = "1"
        ET.SubElement(org, "sourceRegistrationFact_0")
        for tag in ["fullName", "shortName", "otherName"]:
            ET.SubElement(org, tag).text = "ООО Тестовая передача"
        ET.SubElement(org, "sourceDateStart").text = "2020-01-01"
        ET.SubElement(org, "regNum").text = "1"
        tax = ET.SubElement(org, "TaxNum_group_FL_46_UL_36_OrgSource")
        ET.SubElement(tax, "taxCode").text = "1"
        ET.SubElement(tax, "taxNum").text = "1"
        ET.SubElement(org, "sourceCreditInfoDate").text = self.date_str

        data = ET.SubElement(doc, "Data")
        subject = ET.SubElement(data, "Subject_FL")
        subject.append(TitlePage(self.person).build())
        events = ET.SubElement(subject, "Events")
        events.append(EventPage(self.date_str).build())

        return doc
