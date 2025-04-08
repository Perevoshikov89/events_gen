import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
# from faker import Faker

# Инициализация Faker для русскоязычных данных
# fake = Faker("ru_RU")


person_data = {
    "lastName": "ПЕРЕВОЩИКОВ",
    "firstName": "ЮРИЙ",
    "middleName": "ЛЬВОВИЧ",
    "birthDate": "1989-01-01",
    "birthPlace": "ГЛАЗОВ",
    "citizenship": "234",
    "docCode": "21",
    "docSeries": "2121",
    "docNum": "123356",
    "issueDate": "2008-01-01",
    "docIssuer": "МВД РОССИИ",
    "deptCode": "111-212",
    "foreignerCode": "3",
    "taxNum": "309963085325",
    "snils": "12277154143"
}

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

def build_data(person):
    data = ET.Element("Data")
    subject_fl = build_subject_fl(person)
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

def build_event(person, date_str):
    event = ET.Element("Event")
    source = build_source(date_str)
    data = build_data(person)
    event.append(source)
    event.append(data)
    return event

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

    event = build_event(person, date_str)
    document.append(event)

    return document

def prettify(elem):
    rough_string = ET.tostring(elem, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    xml_string = reparsed.toprettyxml(indent="    ", encoding="utf-8").decode("utf-8")

    # Переводим атрибуты <Document ...> в столбик
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

# === Основной код ===
now = datetime.now()
date_for_doc = now.strftime('%Y-%m-%d')
timestamp = now.strftime('%Y%m%d_%H%M%S')

base_id = "YP01MM000001"
reg_number = f"{base_id}_{timestamp}"

document_xml = build_document(person_data, reg_number, date_for_doc)

file_name = f"{reg_number}.xml"
with open(file_name, "w", encoding="utf-8") as f:
    f.write(prettify(document_xml))

print(f"Документ сохранен в файл: {file_name}")
