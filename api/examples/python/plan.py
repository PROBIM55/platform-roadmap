"""Печатает краткую сводку сводного плана проекта: разделы, файлы и их версии.

Пример:  python plan.py --project <идентификатор проекта>
Параметр --json печатает ответ сервера как есть.
"""

import argparse
import json

from common import Client, run


def main():
    parser = argparse.ArgumentParser(description="Сводка сводного плана сетей проекта")
    parser.add_argument("--project", required=True, help="идентификатор проекта")
    parser.add_argument("--json", action="store_true", help="напечатать ответ сервера целиком")
    args = parser.parse_args()

    client = Client()
    plan = client.get(client.plan_path(args.project))
    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return

    document = plan["document"]
    permissions = plan.get("permissions", {})
    print("Версия документа: %s" % document["version"])
    print("Ваши права: администрирование=%s, запись=%s, координация=%s"
          % (permissions.get("canAdminister"), permissions.get("canWrite"), permissions.get("canCoordinate")))

    for discipline in document["disciplines"]:
        sections = [s for s in document["sections"] if s["disciplineId"] == discipline["id"]]
        print("\nРаздел «%s» (%s), файлов: %d" % (discipline["name"], discipline["id"], len(sections)))
        for section in sections:
            versions = section.get("cadVersions", [])
            pending = [v for v in versions if v.get("status") == "submitted" and not v.get("superseded")]
            accepted = next((v for v in versions if v["id"] == section.get("acceptedCadVersionId")), None)
            actual = ("версия %s, %s" % (accepted["number"], accepted["fileName"])) if accepted else "нет актуальной"
            print("  - %s (%s): %s; на проверке: %d; всего версий: %d"
                  % (section["name"], section["id"], actual, len(pending), len(versions)))
            for model in section.get("modelSources", []):
                print("      модель IFC «%s»: версий %d" % (model["name"], len(model.get("versions", []))))


if __name__ == "__main__":
    run(main)
