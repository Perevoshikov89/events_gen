from pages.document_page import DocumentBuilder, generate_person
from datetime import datetime
from xml.dom import minidom
import xml.etree.ElementTree as ET

def prettify(elem):
    rough = ET.tostring(elem, encoding="utf-8")
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent="    ", encoding="utf-8").decode("utf-8")

if __name__ == "__main__":
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    base_id = "YP01MM000001"
    reg_number = f"{base_id}_{timestamp}"

    person = generate_person()
    doc = DocumentBuilder(person, reg_number, date_str).build()
    xml = prettify(doc)

    with open(f"{reg_number}.xml", "w", encoding="utf-8") as f:
        f.write(xml)

    print(f"✅ Документ создан: {reg_number}.xml")
