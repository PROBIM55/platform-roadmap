"""Скачивает ZIP-архив оригиналов актуальных версий: всего плана или одного раздела.

Примеры:
  python download_archive.py --project <id> --out plan.zip
  python download_archive.py --project <id> --discipline "Водоснабжение" --out vk.zip
"""

import argparse
import os
import zipfile

from common import Client, find_discipline, run


def main():
    parser = argparse.ArgumentParser(description="Архив актуальных версий сводного плана")
    parser.add_argument("--project", required=True, help="идентификатор проекта")
    parser.add_argument("--discipline", help="название раздела; без параметра - все разделы")
    parser.add_argument("--out", required=True, help="куда сохранить ZIP")
    args = parser.parse_args()

    if os.path.exists(args.out):
        raise SystemExit("Файл уже есть: %s. Укажите другое имя или удалите его." % args.out)

    client = Client()
    base = client.plan_path(args.project)

    discipline_id = None
    if args.discipline:
        plan = client.get(base)
        discipline = find_discipline(plan, args.discipline)
        if discipline is None:
            raise SystemExit("Раздел «%s» не найден в плане." % args.discipline)
        discipline_id = discipline["id"]

    size = client.download(base + "/archive", args.out, query={"disciplineId": discipline_id})
    if not zipfile.is_zipfile(args.out):
        os.remove(args.out)
        raise SystemExit("Получен не ZIP-файл: ответ неполный или повреждён.")
    with zipfile.ZipFile(args.out) as archive:
        names = archive.namelist()
    print("Сохранено: %s (%d байт, записей в архиве: %d)" % (args.out, size, len(names)))


if __name__ == "__main__":
    run(main)
