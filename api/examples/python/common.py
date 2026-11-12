"""Общий клиент для примеров API сводного плана сетей.

Только стандартная библиотека Python 3.9+. Ключ берётся из переменной окружения
PLATFORM_API_KEY, адрес сервера - из PLATFORM_BASE_URL (по умолчанию https://bimplatforma.ru).
Ключ нигде не печатается.
"""

import http.client
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_BASE_URL = "https://bimplatforma.ru"
MAX_RATE_LIMIT_WAITS = 5      # сколько раз подряд ждать Retry-After на один запрос
MAX_RETRY_AFTER_SECONDS = 120  # дольше этого не ждём: лучше сообщить человеку
NETWORK_RETRIES = 3            # повторы при обрыве сети (только для безопасных запросов)
TIMEOUT_SECONDS = 120


class ApiError(Exception):
    """Ответ сервера с ошибкой. status - код HTTP, code - поле error из тела (если есть)."""

    def __init__(self, status, code, message, body=None):
        super().__init__("HTTP %s %s: %s" % (status, code or "-", message or ""))
        self.status = status
        self.code = code
        self.message = message
        self.body = body

    @property
    def is_denial(self):
        """Отказ доступа: после него по проекту нужно остановиться (иначе сработает защита)."""
        return self.status in (401, 403, 404)


class Client:
    """Тонкий клиент: заголовок Authorization, разбор ошибок, ожидание Retry-After."""

    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or os.environ.get("PLATFORM_API_KEY", "")
        self.base_url = (base_url or os.environ.get("PLATFORM_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        if not self.api_key:
            raise SystemExit("Не задан ключ: установите переменную окружения PLATFORM_API_KEY.")

    # --- адреса -----------------------------------------------------------------

    def plan_path(self, project_id):
        return "/api/platform/projects/%s/network-federation" % urllib.parse.quote(project_id, safe="")

    def cad_import_path(self, project_id, import_id):
        return "/api/platform/projects/%s/cad-imports/%s" % (
            urllib.parse.quote(project_id, safe=""), urllib.parse.quote(import_id, safe=""))

    def url(self, path, query=None):
        text = self.base_url + path
        if query:
            pairs = [(k, v) for k, v in query.items() if v is not None]
            if pairs:
                text += "?" + urllib.parse.urlencode(pairs)
        return text

    # --- запросы ----------------------------------------------------------------

    def _open(self, method, path, query, data, headers, idempotent):
        merged = {"Accept": "application/json"}
        merged.update(headers or {})
        request = urllib.request.Request(self.url(path, query), data=data, method=method, headers=merged)
        request.add_unredirected_header("Authorization", "Bearer " + self.api_key)
        waits = 0
        network_failures = 0
        while True:
            try:
                return urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
            except urllib.error.HTTPError as error:
                body = error.read()
                if error.code == 429 and waits < MAX_RATE_LIMIT_WAITS:
                    delay = _retry_after(error.headers, body)
                    if delay > MAX_RETRY_AFTER_SECONDS:
                        raise _api_error(error.code, body)
                    waits += 1
                    time.sleep(delay)
                    continue
                raise _api_error(error.code, body)
            except (urllib.error.URLError, ConnectionError, TimeoutError, socket.timeout):
                network_failures += 1
                if not idempotent or network_failures >= NETWORK_RETRIES:
                    raise
                time.sleep(2 * network_failures)

    def request(self, method, path, query=None, body=None, data=None, headers=None, idempotent=None):
        """Запрос с JSON-ответом. body - объект для JSON, data - готовые байты (тогда задайте Content-Type)."""
        headers = dict(headers or {})
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers.setdefault("Content-Type", "application/json")
        if idempotent is None:
            idempotent = method in ("GET", "HEAD")
        with self._open(method, path, query, data, headers, idempotent) as response:
            response_status = response.status
            raw = response.read()
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except ValueError:
            raise ApiError(response_status, "NON_JSON_RESPONSE", "Ответ сервера не является JSON.", None)

    def get(self, path, query=None):
        return self.request("GET", path, query=query)

    def post(self, path, body=None, query=None, idempotent=False):
        return self.request("POST", path, query=query, body=body, idempotent=idempotent)

    def download(self, path, destination, query=None, chunk_bytes=1024 * 1024):
        """Скачивает ответ в файл по частям. Возвращает число записанных байт."""
        written = 0
        temp = destination + ".part"
        try:
            with self._open("GET", path, query, None, {"Accept": "*/*"}, True) as response:
                expected = response.headers.get("Content-Length")
                with open(temp, "wb") as out:
                    while True:
                        block = response.read(chunk_bytes)
                        if not block:
                            break
                        out.write(block)
                        written += len(block)
            if expected is not None and int(expected) != written:
                raise IOError("Ответ оборван: получено %d из %s байт." % (written, expected))
            os.replace(temp, destination)
        except BaseException:
            if os.path.exists(temp):
                os.remove(temp)
            raise
        return written


def _retry_after(headers, body):
    value = headers.get("Retry-After") if headers else None
    if value is None:
        try:
            parsed = json.loads(body.decode("utf-8"))
            details = parsed.get("details") if isinstance(parsed.get("details"), dict) else {}
            # Время ожидания лежит в details (ошибки платформы) или в корне тела (например, при создании ссылок).
            value = details.get("retry_after_seconds", parsed.get("retry_after_seconds"))
        except (ValueError, AttributeError):
            value = None
    try:
        return max(1, int(float(value)))
    except (TypeError, ValueError):
        return 5


def _api_error(status, body):
    code = message = None
    parsed = None
    if body:
        try:
            parsed = json.loads(body.decode("utf-8"))
        except ValueError:
            parsed = None
    if isinstance(parsed, dict):
        code = parsed.get("error") or parsed.get("code")
        message = parsed.get("message")
    return ApiError(status, code, message, parsed)


# --- помощники для плана ---------------------------------------------------------


def find_discipline(plan, name):
    """Раздел по названию (без учёта регистра) или None."""
    wanted = name.strip().casefold()
    for item in plan["document"]["disciplines"]:
        if item["name"].strip().casefold() == wanted:
            return item
    return None


def find_section(plan, discipline_id, name):
    """Файл раздела по названию (без учёта регистра) или None."""
    wanted = name.strip().casefold()
    for item in plan["document"]["sections"]:
        if item["disciplineId"] == discipline_id and item["name"].strip().casefold() == wanted:
            return item
    return None


def run(main):
    """Запуск с понятным сообщением об ошибке и кодом выхода. Ключ в сообщения не попадает."""
    try:
        main()
    except ApiError as error:
        print("Ошибка сервера: %s" % error, file=sys.stderr)
        if error.is_denial:
            print("Это отказ доступа: дальнейшие запросы по проекту не выполняются.", file=sys.stderr)
        sys.exit(2)
    except (urllib.error.URLError, http.client.HTTPException, OSError) as error:
        print("Ошибка связи: %s" % error, file=sys.stderr)
        sys.exit(3)
    except KeyboardInterrupt:
        sys.exit(130)
