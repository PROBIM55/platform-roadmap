"""Загружает чертёж DWG или DXF новой версией файла сводного плана.

Файл ищется по названию в нужном разделе; если его нет - создаётся. Дальше: сессия загрузки,
куски по 8 МиБ с Content-Range, завершение, ожидание импорта, регистрация версии.

Пример:
  python upload_drawing.py --project <id> --discipline "Водоснабжение" \\
      --section "План сетей В1" --file plan_v2.dwg --unit mm --note "Добавлены сети на участке 2"

Нужен ключ в режиме «Полный — по роли» и право записи в раздел.
"""

import argparse
import hashlib
import os
import time

from common import ApiError, Client, find_discipline, find_section, run

CHUNK_BYTES = 8 * 1024 * 1024   # предел куска на сервере (maxChunkBytes)
POLL_SECONDS = 3                # пауза между опросами импорта
MAX_RESUMES = 5                 # сколько раз продолжать загрузку после сбоя


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def upload_chunks(client, base, session_id, path, total):
    """Отправляет куски с позиции receivedBytes. После сбоя перечитывает сессию и продолжает."""
    session_path = "%s/uploads/%s" % (base, session_id)
    resumes = 0
    with open(path, "rb") as source:
        while True:
            received = client.get(session_path)["session"]["receivedBytes"]
            if received >= total:
                return
            source.seek(received)
            block = source.read(min(CHUNK_BYTES, total - received))
            end = received + len(block) - 1
            headers = {
                "Content-Type": "application/octet-stream",
                "Content-Range": "bytes %d-%d/%d" % (received, end, total),
            }
            try:
                # Повтор того же куска безопасен: сервер сверяет уже принятые байты.
                client.request("PUT", "%s/content" % session_path, data=block, headers=headers, idempotent=True)
            except ApiError as error:
                if error.code in ("CAD_UPLOAD_OFFSET_CONFLICT", "CAD_UPLOAD_SESSION_BUSY") and resumes < MAX_RESUMES:
                    resumes += 1
                    time.sleep(1)
                    continue
                raise
            except OSError:
                if resumes >= MAX_RESUMES:
                    raise
                resumes += 1
                time.sleep(2)
                continue
            print("  принято %d из %d байт" % (end + 1, total))


def wait_import(client, project_id, import_id, timeout):
    path = client.cad_import_path(project_id, import_id)
    deadline = time.time() + timeout
    while True:
        item = client.get(path)["item"]
        if item["status"] == "succeeded":
            return item
        if item["status"] in ("failed", "cancelled"):
            raise SystemExit("Импорт не удался: статус %s, причина %s." % (item["status"], item.get("error")))
        if time.time() > deadline:
            raise SystemExit("Импорт не завершился за %d с; идентификатор импорта: %s." % (timeout, import_id))
        time.sleep(POLL_SECONDS)


def wait_ready(client, base, section_id, version_id, timeout):
    deadline = time.time() + timeout
    while True:
        answer = client.get(base + "/processing", query={"sectionId": section_id})
        row = next((i for i in answer.get("items", []) if i["versionId"] == version_id), None)
        state = row["state"] if row else None
        if state in ("ready", "failed"):
            return state
        if time.time() > deadline:
            return state
        time.sleep(max(1, int(answer.get("retryAfterMs", 2000)) / 1000))


def main():
    parser = argparse.ArgumentParser(description="Загрузка новой версии чертежа в сводный план")
    parser.add_argument("--project", required=True, help="идентификатор проекта")
    parser.add_argument("--discipline", required=True, help="название раздела")
    parser.add_argument("--file", required=True, help="путь к файлу .dwg или .dxf")
    parser.add_argument("--section", help="название файла в плане (по умолчанию - имя файла без расширения)")
    parser.add_argument("--unit", choices=["m", "mm"], help="единицы чертежа; без параметра берутся определённые сервером")
    parser.add_argument("--note", help="что изменилось (до 1000 знаков)")
    parser.add_argument("--label", help="метка версии")
    parser.add_argument("--import-id", help="продолжить с регистрации версии для уже загруженного импорта, без повторной загрузки файла")
    parser.add_argument("--wait-ready", action="store_true", help="дождаться подготовки показа и вывести итоговый статус")
    parser.add_argument("--timeout", type=int, default=600, help="сколько секунд ждать импорт (по умолчанию 600)")
    args = parser.parse_args()

    path = args.file
    if not os.path.isfile(path):
        raise SystemExit("Файл не найден: %s" % path)
    file_name = os.path.basename(path)
    if os.path.splitext(file_name)[1].lower() not in (".dwg", ".dxf"):
        raise SystemExit("Нужен файл .dwg или .dxf.")
    total = os.path.getsize(path)
    section_name = args.section or os.path.splitext(file_name)[0]

    client = Client()
    base = client.plan_path(args.project)

    plan = client.get(base)
    discipline = find_discipline(plan, args.discipline)
    if discipline is None:
        raise SystemExit("Раздел «%s» не найден в плане." % args.discipline)

    section = find_section(plan, discipline["id"], section_name)
    if section is None:
        print("Файл «%s» в разделе «%s» не найден, создаю." % (section_name, discipline["name"]))
        section = client.post(base + "/sections", {"disciplineId": discipline["id"], "name": section_name})["section"]
    else:
        print("Файл «%s» найден (%s)." % (section["name"], section["id"]))

    limits = client.get(base + "/uploads/limits")
    if total > limits["maxSourceBytes"]:
        raise SystemExit("Файл больше лимита сервера: %d байт при лимите %d." % (total, limits["maxSourceBytes"]))

    if args.import_id:
        import_id = args.import_id
        print("Продолжаю с импорта %s без повторной загрузки." % import_id)
    else:
        digest = file_sha256(path)
        session = client.post(base + "/uploads", {
            "disciplineId": discipline["id"], "fileName": file_name, "declaredBytes": total, "sha256": digest,
        })["session"]
        print("Сессия загрузки: %s" % session["sessionId"])

        upload_chunks(client, base, session["sessionId"], path, total)

        # complete безопасно повторять: для завершённой сессии вернётся тот же импорт.
        done = client.request("POST", "%s/uploads/%s/complete" % (base, session["sessionId"]), idempotent=True)
        import_id = done["item"]["importId"]
        print("Загрузка завершена, импорт %s; жду разбор файла." % import_id)

    item = wait_import(client, args.project, import_id, args.timeout)

    unit = args.unit
    if unit is None:
        if item.get("sourceUnitDetection") == "detected" and item.get("detectedSourceUnit") in ("m", "mm"):
            unit = item["detectedSourceUnit"]
            print("Единицы определены сервером: %s." % unit)
        else:
            raise SystemExit("Сервер не определил единицы чертежа. Импорт %s готов; продолжите без повторной загрузки: "
                             "добавьте --import-id %s --unit m (или --unit mm)." % (import_id, import_id))

    body = {"importId": import_id, "sourceUnit": unit}
    if args.note:
        body["note"] = args.note
    if args.label:
        body["label"] = args.label
    # Регистрация безопасна к повтору: тот же файл с теми же единицами вернёт существующую версию.
    known_ids = {v["id"] for v in section.get("cadVersions", [])}
    version = client.request("POST", "%s/sections/%s/cad-versions" % (base, section["id"]),
                             body=body, idempotent=True)["cadVersion"]
    print("Версия %s: id %s, статус %s." % (version["number"], version["id"], version["status"]))
    # Сервер возвращает уже имеющуюся версию с той же SHA-256 и теми же единицами, в любом статусе.
    if version["id"] in known_ids or version["status"] not in ("submitted", "accepted"):
        print("ВНИМАНИЕ: новая версия не создана — в файле уже есть версия с тем же содержимым и единицами "
              "(статус %s). На проверку ничего не отправлено; если версию возвращали, исправьте чертёж." % version["status"])

    if args.wait_ready:
        state = wait_ready(client, base, section["id"], version["id"], args.timeout)
        print("Подготовка показа: %s." % state)
        plan = client.get(base)
        current = find_section(plan, discipline["id"], section["name"])
        final = next((v for v in current["cadVersions"] if v["id"] == version["id"]), None)
        if final:
            print("Итоговый статус версии: %s." % final["status"])


if __name__ == "__main__":
    run(main)
