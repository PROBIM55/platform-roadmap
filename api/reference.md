# Справочник маршрутов API сводного плана сетей

Версия каталога: 1.2 от 2026-11-14. Базовый адрес: `https://bimplatforma.ru`. Заголовок: `Authorization: Bearer <ключ>`.
Маршрутов, доступных ключу: 129.

## Как читать справочник

- **Раздел** в интерфейсе (например, «Водоснабжение») — `discipline`. **Файл** внутри раздела — в адресах `sections`. **Версия** — версия чертежа файла (`cad-versions`) или модели IFC.
- **Роли:** «Администратор» (`admin`), «Координатор» (`coordinator`), «Загрузка» (`uploader`), «Просмотр» (`viewer`). Ключ действует правами своего владельца в проекте и не даёт ничего сверх них. Глобальная роль администратора платформы по ключу не применяется: считается только настоящее участие в проекте или администрирование компании проекта.
- **Режимы ключа:** `read` — Доступен ключу в режиме «Чтение» и «Полный — по роли» (методы GET и HEAD, а также три чтения показа методом POST: диапазоны тайлов отрисовки и разбор шрифтов). `full` — Только ключу в режиме «Полный — по роли» (запись: методы, кроме GET и HEAD, кроме трёх чтений показа методом POST). `closed` — Ключу недоступен (403 AGENT_GRANT_DENIED или 401).
- **Служебные** маршруты показа (подготовленные виды, тайлы, шрифты показа, ACIS, протокол сравнений) открыты, но их формат может меняться; для интеграций опирайтесь на остальные.
- В оглавлении `…` заменяет `/api/platform/projects/{projectId}/network-federation`; в описаниях маршрутов пути указаны полностью. Фрагмент `{index:int}` в пути означает целое число.
- Запись документа плана идёт с `expectedVersion`; у обсуждений и видов — со своим `rowVersion` (см. соглашения).

## Ошибки, возможные у любого маршрута

| Статус | Код | Смысл |
|---|---|---|
| 401 | `AGENT_TOKEN_INVALID` | Bearer-ключ недействителен, отозван или просрочен (тело JSON). На маршруте проверки ключа — также при отсутствии ключа. |
| 403 | `AGENT_GRANT_DENIED` | Запись ключом «Чтение» или маршрут закрыт для ключа. |
| 400 | `API_KEY_WITH_SESSION` | В одном запросе пришли и ключ, и cookie сессии. |
| 403 | `API_KEY_EMPLOYEES_ONLY` | Ключи доступны только сотрудникам компании. |
| 404 | `PROJECT_NOT_FOUND` | Проект не найден либо вне списка ключа (различий нет). |
| 403 | `PROJECT_ACCESS_DENIED` | Владелец ключа не участник проекта. |
| 403 | `PROJECT_MODULE_ACCESS_DENIED` | В составе проекта нет сводного плана сетей. |
| 403 | `MODULE_ACCESS_DENIED` | У учётной записи нет права на модуль. |
| 429 | `RATE_LIMIT_AGENT_READ` | Больше 600 чтений в минуту; заголовок Retry-After. |
| 429 | `RATE_LIMIT_AGENT_WRITE` | Больше 120 записей в минуту; заголовок Retry-After. |
| 400 | `NETWORK_REQUEST_INVALID` | Тело запроса не разобрано как JSON. |
| 409 | `NETWORK_FEDERATION_DOCUMENT_CONFLICT` | Документ изменили параллельно: перечитать и повторить. |
| 409 | `API_KEY_LIMIT` | При выпуске ключа: у человека уже 10 действующих ключей. |
| 400 | `API_KEY_PROJECTS_ONE_COMPANY` | При выпуске ключа: проекты одного ключа — из одной компании. |

Формат ошибки: ошибки модуля приходят как `{"ok": false, "error": "КОД"}`; ошибки уровня платформы могут добавлять `message` и `details`. Запрос с ключом, не прошедший проверку, получает 401 и JSON `{"ok": false, "error": "AGENT_TOKEN_INVALID", "message": "..."}`. Программа должна ветвиться по `error`, а не по `message`. При скачивании у 404 тела может не быть.

## Оглавление

### Ключ (1)

- [GET `/api/platform/network-federation/me`](#key-me) — Узнать, чей это ключ: владелец, режим, срок и проекты ключа с ролью владельца в каждом.

### Документ и разделы (11)

- [GET `…`](#plan-read) — Открыть сводный план проекта: разделы, файлы, версии чертежей, модели IFC, права, участники.
- [GET `/api/platform/network-federation/projects/{projectId}/context`](#plan-context) — Получить сведения о проекте для модуля: проект, участники, варианты проекта, состав модуля.
- [GET `/api/platform/network-federation/variants/{variantId}/revisions`](#variant-revisions-list) — Прочитать список ревизий варианта проекта для модуля.
- [GET `/api/platform/network-federation/variants/{variantId}/revisions/{revisionId}`](#variant-revision-read) — Прочитать одну ревизию варианта проекта.
- [POST `…/disciplines`](#discipline-create) — Добавить раздел в сводный план.
- [PUT `…/disciplines/{disciplineId}`](#discipline-rename) — Переименовать раздел.
- [DELETE `…/disciplines/{disciplineId}`](#discipline-delete) — Убрать раздел в архив (данные сохраняются).
- [POST `…/disciplines/{disciplineId}/archive`](#discipline-archive) — Убрать раздел в архив (данные сохраняются).
- [PUT `…/disciplines/{disciplineId}/plan-settings`](#discipline-plan-settings) — Изменить настройки раздела на весь проект: подоснова, цвет раздела, показ в сводном плане по умолчанию.
- [PUT `…/disciplines/order`](#discipline-order) — Задать порядок прорисовки разделов на весь проект (сверху вниз).
- [PUT `…/disciplines/{disciplineId}/drawing-order`](#discipline-drawing-order) — Задать порядок прорисовки чертежей внутри раздела на весь проект (сверху вниз).

### Файлы и версии (5)

- [POST `…/sections`](#section-create) — Завести новый файл в разделе (карточку под будущие версии чертежа).
- [POST `…/sections/{sectionId}/cad-versions`](#cad-version-register) — Зарегистрировать загруженный и разобранный чертёж как новую версию файла.
- [POST `…/sections/{sectionId}/cad-versions/{versionId}/unit-revision`](#cad-version-unit-revision) — Исправить единицы измерения версии на проверке: создать уточнённую версию с определёнными единицами.
- [GET `…/sections/{sectionId}/cad-versions/{versionId}/original`](#cad-version-download-original) — Скачать оригинал версии чертежа (DWG или DXF, как загружен).
- [GET `…/sections/{sectionId}/cad-versions/{versionId}/dxf`](#cad-version-download-dxf) — Скачать нормализованный DXF версии чертежа.

### Загрузка (12)

- [GET `…/uploads/limits`](#upload-limits) — Узнать лимиты загрузки чертежей: максимальный размер файла и куска.
- [POST `…/uploads`](#upload-create) — Открыть сессию загрузки чертежа (DWG или DXF) в раздел.
- [GET `…/uploads/{sessionId}`](#upload-read) — Узнать состояние сессии загрузки (сколько байт принято).
- [PUT `…/uploads/{sessionId}/content`](#upload-chunk) — Отправить очередной кусок файла (до 8 МиБ) в сессию загрузки.
- [POST `…/uploads/{sessionId}/complete`](#upload-complete) — Завершить загрузку: сервер сверит размер и SHA-256 и поставит файл в очередь импорта.
- [POST `…/uploads/{sessionId}/retry`](#upload-retry) — Повторить обработку уже загруженного файла, если импорт завершился ошибкой.
- [DELETE `…/uploads/{sessionId}`](#upload-cancel) — Отменить сессию загрузки и удалить принятые куски.
- [GET `…/processing`](#processing-read) — Посмотреть, как идёт подготовка версий к показу (очередь, этапы, ошибки).
- [POST `…/sections/{sectionId}/cad-versions/{versionId}/processing/retry`](#processing-retry) — Повторить подготовку версии к показу, если фоновая подготовка остановилась.
- [POST `…/sections/{sectionId}/cad-versions/{versionId}/processed/prepare`](#processed-prepare) — Подготовить обработанный DWG версии к скачиванию.
- [GET `…/sections/{sectionId}/cad-versions/{versionId}/processed/report`](#processed-report) — Прочитать отчёт об обработке версии (JSON).
- [GET `…/sections/{sectionId}/cad-versions/{versionId}/processed`](#processed-download) — Скачать обработанный DWG версии.

### Импорт CAD (1)

- [GET `/api/platform/projects/{projectId}/cad-imports/{importId}`](#cad-import-read) — Узнать состояние импорта загруженного файла (в очереди, идёт, готов, ошибка).

### Модели IFC (3)

- [POST `…/sections/{sectionId}/models`](#model-create) — Завести модель IFC в файле (под будущие версии модели).
- [POST `…/sections/{sectionId}/models/{modelId}/versions`](#model-version-upload) — Загрузить новую версию модели IFC одним запросом (файл — телом запроса).
- [GET `…/sections/{sectionId}/models/{modelId}/versions/{versionId}/original`](#model-version-download-original) — Скачать оригинал версии модели IFC.

### Проверка версий (6)

- [POST `…/sections/{sectionId}/cad-versions/{versionId}/submit`](#cad-version-submit) — Отправить версию чертежа на проверку (совместимость: новые версии уже «на проверке» после регистрации).
- [POST `…/sections/{sectionId}/cad-versions/{versionId}/accept`](#cad-version-accept) — Принять версию на проверке или сделать прежнюю принятую версию актуальной.
- [POST `…/sections/{sectionId}/cad-versions/{versionId}/return`](#cad-version-return) — Вернуть версию чертежа автору с причиной.
- [POST `…/sections/{sectionId}/models/{modelId}/versions/{versionId}/submit`](#model-version-submit) — Отправить версию модели IFC на проверку (совместимость).
- [POST `…/sections/{sectionId}/models/{modelId}/versions/{versionId}/accept`](#model-version-accept) — Принять версию модели IFC (или сделать прежнюю принятую актуальной).
- [POST `…/sections/{sectionId}/models/{modelId}/versions/{versionId}/return`](#model-version-return) — Вернуть версию модели IFC автору с причиной.

### Состав и размещения (4)

- [PUT `…/sections/{sectionId}/federation-settings`](#section-federation-settings) — Включить файл в сводную картину или исключить; задать порядок отрисовки.
- [GET `…/sections/{sectionId}/cad-versions/{versionId}/placements`](#placements-list) — Прочитать размещения версии чертежа (положение в общей системе координат).
- [POST `…/sections/{sectionId}/cad-versions/{versionId}/placements`](#placement-create) — Добавить новое размещение версии чертежа.
- [GET `…/model-adapters`](#model-adapters-list) — Узнать, какие форматы моделей поддерживает сводный план.

### Снимки (4)

- [GET `…/snapshots`](#snapshots-list) — Получить список снимков сводной картины.
- [POST `…/snapshots`](#snapshot-create) — Зафиксировать снимок: набор версий и размещений на этот момент.
- [GET `…/snapshots/{snapshotId}`](#snapshot-read) — Прочитать снимок.
- [GET `…/snapshots/{beforeId}/compare/{afterId}`](#snapshot-compare) — Сравнить два снимка: что добавилось, убралось, сменило версию или размещение.

### Подготовка и показ — служебные (11)

- [GET `…/sections/{sectionId}/cad-versions/{versionId}/presentation`](#cad-version-presentation) — Получить представление чертежа для показа в просмотрщике (JSON).
- [GET `…/sections/{sectionId}/cad-versions/{versionId}/preview`](#cad-version-preview) — Получить встроенную картинку-предпросмотр версии (PNG).
- [GET `…/prepared-views`](#prepared-views-list) — Получить перечень подготовленных видов всех видимых версий.
- [GET `…/sections/{sectionId}/cad-versions/{versionId}/prepared-view`](#prepared-view-read) — Получить подготовленный вид одной версии.
- [GET `…/sections/{sectionId}/cad-versions/{versionId}/prepared-scene`](#prepared-scene-read) — Узнать состояние подготовленной сцены версии.
- [POST `…/sections/{sectionId}/cad-versions/{versionId}/prepared-scene`](#prepared-scene-start) — Запустить подготовку сцены версии (если ещё не готова).
- [GET `…/sections/{sectionId}/cad-versions/{versionId}/prepared-scene/{attemptId}/assets/{assetId}`](#prepared-scene-asset) — Получить ресурс подготовленной сцены (двоичный блок).
- [GET `…/sections/{sectionId}/cad-versions/{versionId}/prepared-scene/{attemptId}/render-tile/{packSha256}`](#prepared-scene-render-tile) — Получить пакет тайлов отрисовки готовой попытки.
- [GET `…/sections/{sectionId}/cad-versions/{versionId}/prepared-scene/{attemptId}/asset-pack`](#prepared-scene-asset-pack) — Получить набор ресурсов подготовленной сцены одним ответом.
- [POST `…/render-tile-ranges`](#render-tile-ranges) — Получить несколько диапазонов тайлов отрисовки одним запросом (чтение, но методом POST).
- [GET `…/sections/{sectionId}/cad-versions/{versionId}/native-acis`](#native-acis) — Получить встроенные данные ACIS версии (твёрдотельная геометрия).

### Шрифты (8)

- [POST `…/sections/{sectionId}/cad-versions/{versionId}/render-font-resources/resolve`](#render-font-resolve) — Подобрать шрифтовые ресурсы для показа версии (чтение, но методом POST).
- [GET `…/sections/{sectionId}/cad-versions/{versionId}/render-font-resources/{bindingId}/font-pack`](#render-font-pack-read) — Прочитать опись пакета шрифтов привязки.
- [GET `…/sections/{sectionId}/cad-versions/{versionId}/render-font-resources/{bindingId}/font-pack/fonts/{fontSha256}`](#render-font-pack-font) — Скачать шрифт из пакета привязки.
- [POST `…/render-font-resources/resolve-batch`](#render-font-resolve-batch) — Подобрать шрифтовые ресурсы сразу для многих версий (чтение, но методом POST).
- [POST `…/sections/{sectionId}/cad-versions/{versionId}/font-packs`](#font-pack-upload) — Загрузить пакет шрифтов для версии чертежа (недостающие шрифты чертежа).
- [GET `…/sections/{sectionId}/cad-versions/{versionId}/font-packs/{packSha256}`](#font-pack-read) — Прочитать опись загруженного пакета шрифтов.
- [GET `…/sections/{sectionId}/cad-versions/{versionId}/font-packs/{packSha256}/fonts/{fontSha256}`](#font-pack-font) — Скачать шрифт из загруженного пакета.
- [POST `…/sections/{sectionId}/cad-versions/{versionId}/font-revisions`](#font-revision-create) — Создать новую версию чертежа, привязанную к загруженному пакету шрифтов.

### Сравнения (8)

- [GET `…/sections/{sectionId}/comparisons/{beforeId}/{afterId}`](#comparison-read) — Прочитать сравнение двух версий файла (если уже посчитано).
- [POST `…/sections/{sectionId}/comparisons/{beforeId}/{afterId}/claim`](#comparison-claim) — Взять расчёт сравнения на себя (получить аренду).
- [GET `…/comparisons/{pairId}`](#comparison-read-by-id) — Прочитать сравнение по идентификатору.
- [POST `…/comparisons/{pairId}/lease`](#comparison-lease) — Продлить аренду расчёта сравнения.
- [GET `…/comparisons/{pairId}/pages/{kind}/{index:int}`](#comparison-page-read) — Прочитать страницу результата сравнения.
- [POST `…/comparisons/{pairId}/pages/{kind}/{index:int}`](#comparison-page-publish) — Опубликовать страницу результата сравнения.
- [POST `…/comparisons/{pairId}/complete`](#comparison-complete) — Завершить расчёт сравнения.
- [POST `…/comparisons/{pairId}/summary`](#comparison-summary-request) — Запросить краткую сводку по готовому сравнению.

### Сводки изменений (2)

- [GET `…/sections/{sectionId}/cad-versions/{versionId}/change-summary`](#change-summary-read) — Прочитать сводку изменений версии чертежа относительно предыдущей.
- [POST `…/sections/{sectionId}/cad-versions/{versionId}/change-summary`](#change-summary-request) — Запросить построение сводки изменений версии.

### Обсуждения (17)

- [GET `…/discussions`](#discussions-list) — Получить список обсуждений (замечаний) проекта с фильтрами.
- [GET `…/discussions/summary`](#discussions-summary) — Получить счётчики обсуждений для вкладок «Открытые · Мои · Просрочено · Решённые».
- [GET `…/discussions/changes`](#discussions-changes) — Получить ленту изменений обсуждений после курсора (для автообновления).
- [POST `…/discussions`](#discussion-create) — Завести обсуждение (замечание) с первым сообщением.
- [GET `…/discussions/{discussionId}`](#discussion-read) — Открыть обсуждение: заголовок, сообщения, историю.
- [PATCH `…/discussions/{discussionId}`](#discussion-update) — Изменить обсуждение: статус, заголовок, приоритет, исполнителя, срок, метки.
- [DELETE `…/discussions/{discussionId}`](#discussion-delete) — Удалить обсуждение.
- [POST `…/discussions/{discussionId}/messages`](#discussion-message-post) — Ответить в обсуждении.
- [PATCH `…/discussions/{discussionId}/messages/{messageId}`](#discussion-message-edit) — Исправить своё сообщение.
- [DELETE `…/discussions/{discussionId}/messages/{messageId}`](#discussion-message-delete) — Удалить сообщение.
- [GET `…/discussions/{discussionId}/attachments/{attachmentId}`](#discussion-attachment-download) — Скачать вложение обсуждения.
- [POST `…/discussion-attachments`](#discussion-attachment-upload) — Загрузить вложение до отправки сообщения (затем его идентификатор указывают в attachmentIds).
- [DELETE `…/discussion-attachments/{attachmentId}`](#discussion-attachment-delete) — Удалить загруженное, но ещё не отправленное вложение.
- [GET `…/discussion-labels`](#discussion-labels-list) — Получить справочник меток обсуждений.
- [POST `…/discussion-labels`](#discussion-label-create) — Создать метку обсуждений.
- [PATCH `…/discussion-labels/{labelId}`](#discussion-label-update) — Изменить метку обсуждений.
- [DELETE `…/discussion-labels/{labelId}`](#discussion-label-delete) — Удалить метку обсуждений.

### Виды (18)

- [GET `…/display-configurations`](#display-configs-list) — Получить список конфигураций показа (личных и общих).
- [GET `…/display-configurations/{configurationId}`](#display-config-read) — Прочитать конфигурацию показа.
- [POST `…/display-configurations`](#display-config-create) — Сохранить конфигурацию показа.
- [PUT `…/display-configurations/{configurationId}`](#display-config-update) — Заменить конфигурацию показа целиком.
- [DELETE `…/display-configurations/{configurationId}`](#display-config-delete) — Удалить конфигурацию показа.
- [GET `…/viewpoints`](#viewpoints-list) — Получить список видов (сохранённых точек обзора).
- [GET `…/viewpoints/home`](#viewpoint-home-read) — Узнать начальный вид сводной картины.
- [DELETE `…/viewpoints/home`](#viewpoint-home-clear) — Снять начальный вид сводной картины.
- [GET `…/viewpoints/{viewpointId}`](#viewpoint-read) — Прочитать вид.
- [POST `…/viewpoints`](#viewpoint-create) — Сохранить вид: камеру и, при желании, показ.
- [PUT `…/viewpoints/{viewpointId}`](#viewpoint-update) — Заменить вид целиком.
- [PATCH `…/viewpoints/{viewpointId}`](#viewpoint-share) — Сделать вид общим или личным (только автор).
- [DELETE `…/viewpoints/{viewpointId}`](#viewpoint-delete) — Удалить вид.
- [GET `…/viewpoints/{viewpointId}/preview`](#viewpoint-preview) — Получить картинку предпросмотра вида.
- [PUT `…/viewpoints/{viewpointId}/home`](#viewpoint-home-set) — Назначить вид начальным для сводной картины.
- [POST `…/viewpoint-folders/rename`](#viewpoint-folder-rename) — Переименовать папку видов.
- [POST `…/viewpoint-folders/delete`](#viewpoint-folder-delete) — Удалить папку видов (виды остаются без папки или удаляются).
- [POST `…/viewpoint-folders/visibility`](#viewpoint-folder-visibility) — Сделать виды папки общими или личными.

### Участники и права (8)

- [POST `…/contractors`](#contractor-create) — Завести подрядчика в справочнике сводного плана.
- [GET `/api/platform/projects/{projectId}/modules/federated-networks/grants`](#grants-list) — Получить список участников сводного плана с ролями и разделами.
- [GET `/api/platform/projects/{projectId}/modules/federated-networks/grants/candidates`](#grants-candidates) — Найти, кого можно пригласить: сотрудники компании и известные гости, ещё не участники.
- [POST `/api/platform/projects/{projectId}/modules/federated-networks/grants`](#grant-add) — Подключить существующую учётную запись к проекту с ролью и разделами.
- [PUT `/api/platform/projects/{projectId}/modules/federated-networks/grants/{userId}`](#grant-update) — Сменить роль и разделы участника.
- [DELETE `/api/platform/projects/{projectId}/modules/federated-networks/grants/{userId}`](#grant-remove) — Убрать участника из проекта.
- [POST `…/members`](#member-connect) — Подключить существующего человека к проекту (старый способ; новые программы используют маршруты прав).
- [PUT `…/assignments/{userId}`](#assignment-put) — Назначить участнику разделы, подрядчика и признак координатора (старое окно назначений).

### Приглашения (3)

- [GET `…/invitations`](#invitations-list) — Получить список приглашений в проект.
- [POST `…/invitations`](#invitation-create) — Пригласить человека в проект: сервер вернёт одноразовую ссылку-приглашение.
- [DELETE `…/invitations/{invitationId}`](#invitation-revoke) — Отозвать приглашение, которое ещё не принято.

### Ссылки просмотра (3)

- [GET `…/share-links`](#share-links-list) — Получить список ссылок «только просмотр» на сводный план.
- [POST `…/share-links`](#share-link-create) — Создать ссылку «только просмотр» на сводный план.
- [DELETE `…/share-links/{shareId}`](#share-link-revoke) — Отозвать ссылку «только просмотр».

### Архив (1)

- [GET `…/archive`](#archive-download) — Скачать ZIP-архив оригиналов актуальных версий — всего плана или одного раздела.

### Трассы (3)

- [GET `…/sections/{sectionId}/cad-versions/{versionId}/routes`](#routes-read) — Прочитать последний сохранённый черновик трасс выбранной версии чертежа.
- [POST `…/sections/{sectionId}/cad-versions/{versionId}/routes`](#routes-extract) — Выделить и сохранить черновик трасс из исходного чертежа по точным именам слоёв.
- [PUT `…/route-drafts/{draftId}/candidates/{candidateId}`](#route-candidate-decide) — Сохранить решение инженера по кандидату трассы.

## Ключ

<a id="key-me"></a>
### GET `/api/platform/network-federation/me`

Узнать, чей это ключ: владелец, режим, срок и проекты ключа с ролью владельца в каждом.

- Идентификатор в каталоге: `key-me`
- Кто может: Любой владелец действующего ключа (по cookie сессии маршрут не предназначен) (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Ответ: ok, keyId, name, mode (read|full), expiresAtUtc, tokenHint (последние знаки ключа), user{id, name}, projects[{projectId, name, role}] — роль владельца в проекте (admin, coordinator, uploader, viewer).

Примечания: Первый запрос программы: проверить ключ и получить список проектов. Если доступ по ключу выключен на сервере, маршрут отвечает 404.

## Документ и разделы

<a id="plan-read"></a>
### GET `/api/platform/projects/{projectId}/network-federation`

Открыть сводный план проекта: разделы, файлы, версии чертежей, модели IFC, права, участники.

- Идентификатор в каталоге: `plan-read`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Ответ: ok, capabilities, document{schemaVersion, version, disciplines[{id, name, isBasemap, tint, shownByDefault, drawingOrder}], disciplineOrder, sections[{id, disciplineId, name, includedInFederation, drawOrder, acceptedCadVersionId, cadVersions[], modelSources[]}]; для администратора ещё contractors[] и assignments[]}, permissions{canAdminister, canWrite, canCoordinate, disciplineIds}, members[], reviewers[]. document.version — значение для expectedVersion. Настройки раздела на весь проект: isBasemap — подоснова (null — раздел ещё не настраивали, интерфейс решает по названию), tint — цвет #rrggbb или null, shownByDefault — показ по умолчанию, drawingOrder — файлы раздела сверху вниз или null; disciplineOrder — разделы сверху вниз или null.

Примечания: Версию видят: администратор и координатор — любую; остальные — только принятую; «Загрузка» — ещё и любые версии файлов своих разделов. Главная точка чтения: файл ищут по имени в document.sections[].name внутри нужного раздела.

<a id="plan-context"></a>
### GET `/api/platform/network-federation/projects/{projectId}/context`

Получить сведения о проекте для модуля: проект, участники, варианты проекта, состав модуля.

- Идентификатор в каталоге: `plan-context`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Ответ: ok, project, access_role, members[], variants[], module_composition[].

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `PROJECT_MODULE_ACCESS_DENIED` | В составе проекта нет сводного плана сетей. |
| 403 | `MODULE_ACCESS_DENIED` | У учётной записи нет права на модуль. |

Примечания: Вспомогательное чтение для экрана; для программы обычно хватает GET сводного плана.

<a id="variant-revisions-list"></a>
### GET `/api/platform/network-federation/variants/{variantId}/revisions`

Прочитать список ревизий варианта проекта для модуля.

- Идентификатор в каталоге: `variant-revisions-list`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `variantId` | путь | да | Идентификатор варианта проекта. |
| `limit` | запрос | нет | Сколько ревизий вернуть, 1–500 (по умолчанию 100). |
| `summaryOnly` | запрос | нет | true — только краткие сводки без содержимого. |

Ответ: ok, total, items[] — ревизии (или их сводки при summaryOnly=true).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `VARIANT_NOT_FOUND` | Вариант проекта не найден. |

Примечания: Доступ — по проекту варианта.

<a id="variant-revision-read"></a>
### GET `/api/platform/network-federation/variants/{variantId}/revisions/{revisionId}`

Прочитать одну ревизию варианта проекта.

- Идентификатор в каталоге: `variant-revision-read`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `variantId` | путь | да | Идентификатор варианта проекта. |
| `revisionId` | путь | да | Идентификатор ревизии варианта. |

Ответ: ok, item — ревизия.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `VARIANT_NOT_FOUND` | Вариант проекта не найден. |
| 404 | `REVISION_NOT_FOUND` | Ревизия не найдена. |

Примечания: Чтение записывается в журнал аудита.

<a id="discipline-create"></a>
### POST `/api/platform/projects/{projectId}/network-federation/disciplines`

Добавить раздел в сводный план.

- Идентификатор в каталоге: `discipline-create`
- Кто может: Администратор проекта: владелец проекта или администратор компании проекта. По ключу глобальная роль администратора платформы не действует — только настоящее участие в проекте или администрирование компании проекта (роли: Администратор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `name` | string | да | Название раздела (до 240 знаков), уникально среди неархивных. |

Ответ: ok, discipline{id, name}.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_ADMIN_REQUIRED` | Нужна роль администратора (где сказано — также координатора). |
| 400 | `NETWORK_DISCIPLINE_NAME_REQUIRED` | Не указано название раздела. |
| 409 | `NETWORK_DISCIPLINE_NAME_DUPLICATE` | Раздел с таким названием уже есть. |
| 400 | `NETWORK_VALUE_TOO_LONG` | Значение длиннее 240 знаков. |

<a id="discipline-rename"></a>
### PUT `/api/platform/projects/{projectId}/network-federation/disciplines/{disciplineId}`

Переименовать раздел.

- Идентификатор в каталоге: `discipline-rename`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `disciplineId` | путь | да | Идентификатор раздела (в интерфейсе — раздел, например «Водоснабжение»). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `name` | string | да | Новое название (до 240 знаков). |

Ответ: ok, discipline{id, name}.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_COORDINATOR_REQUIRED` | Нужна роль координатора или администратора. |
| 404 | `NETWORK_DISCIPLINE_NOT_FOUND` | Раздел не найден. |
| 409 | `NETWORK_DISCIPLINE_ARCHIVED` | Раздел в архиве. |
| 400 | `NETWORK_DISCIPLINE_NAME_REQUIRED` | Не указано название раздела. |
| 409 | `NETWORK_DISCIPLINE_NAME_DUPLICATE` | Раздел с таким названием уже есть. |
| 400 | `NETWORK_VALUE_TOO_LONG` | Значение длиннее 240 знаков. |

<a id="discipline-delete"></a>
### DELETE `/api/platform/projects/{projectId}/network-federation/disciplines/{disciplineId}`

Убрать раздел в архив (данные сохраняются).

- Идентификатор в каталоге: `discipline-delete`
- Кто может: Администратор проекта: владелец проекта или администратор компании проекта. По ключу глобальная роль администратора платформы не действует — только настоящее участие в проекте или администрирование компании проекта (роли: Администратор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `disciplineId` | путь | да | Идентификатор раздела (в интерфейсе — раздел, например «Водоснабжение»). |

Ответ: ok, discipline (с отметкой архивации). Повтор над уже архивным разделом ничего не меняет.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_ADMIN_REQUIRED` | Нужна роль администратора (где сказано — также координатора). |
| 404 | `NETWORK_DISCIPLINE_NOT_FOUND` | Раздел не найден. |

Примечания: Делает то же, что POST …/archive. Раздел уходит из порядка разделов проекта (document.disciplineOrder).

<a id="discipline-archive"></a>
### POST `/api/platform/projects/{projectId}/network-federation/disciplines/{disciplineId}/archive`

Убрать раздел в архив (данные сохраняются).

- Идентификатор в каталоге: `discipline-archive`
- Кто может: Администратор проекта: владелец проекта или администратор компании проекта. По ключу глобальная роль администратора платформы не действует — только настоящее участие в проекте или администрирование компании проекта (роли: Администратор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `disciplineId` | путь | да | Идентификатор раздела (в интерфейсе — раздел, например «Водоснабжение»). |

Ответ: ok, discipline (с отметкой архивации).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_ADMIN_REQUIRED` | Нужна роль администратора (где сказано — также координатора). |
| 404 | `NETWORK_DISCIPLINE_NOT_FOUND` | Раздел не найден. |

Примечания: Раздел уходит из порядка разделов проекта (document.disciplineOrder).

<a id="discipline-plan-settings"></a>
### PUT `/api/platform/projects/{projectId}/network-federation/disciplines/{disciplineId}/plan-settings`

Изменить настройки раздела на весь проект: подоснова, цвет раздела, показ в сводном плане по умолчанию.

- Идентификатор в каталоге: `discipline-plan-settings`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `disciplineId` | путь | да | Идентификатор раздела (в интерфейсе — раздел, например «Водоснабжение»). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `isBasemap` | boolean | нет | Подоснова: раздел всегда рисуется под остальными, без своего цвета — серым. Нет поля — не меняется. |
| `tint` | string\|null | нет | Цвет раздела #rrggbb; null — исходные цвета чертежей. Нет поля — не меняется. |
| `shownByDefault` | boolean | нет | Показывать раздел в сводном плане по умолчанию. Нет поля — не меняется. |
| `expectedVersion` | integer | да | document.version из GET сводного плана. |

Ответ: ok, discipline{id, name, isBasemap, tint, shownByDefault, drawingOrder}, version — версия документа после записи (для следующего expectedVersion).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_DOCUMENT_VERSION_REQUIRED` | Не передан expectedVersion — версия документа из GET сводного плана (document.version). |
| 403 | `NETWORK_COORDINATOR_REQUIRED` | Нужна роль координатора или администратора. |
| 404 | `NETWORK_DISCIPLINE_NOT_FOUND` | Раздел не найден. |
| 409 | `NETWORK_DISCIPLINE_ARCHIVED` | Раздел в архиве. |
| 400 | `NETWORK_DISCIPLINE_TINT_INVALID` | tint не в виде #rrggbb и не null. |

Примечания: Запись документа: expectedVersion — document.version из GET сводного плана. Без него 428, при расхождении 409 — перечитать план и повторить. Меняет картину у всех участников: сохранённые виды берут цвет и показ раздела из проекта, если не задали их сами. Запрос без изменений документ не меняет, version в ответе прежняя.

<a id="discipline-order"></a>
### PUT `/api/platform/projects/{projectId}/network-federation/disciplines/order`

Задать порядок прорисовки разделов на весь проект (сверху вниз).

- Идентификатор в каталоге: `discipline-order`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `disciplineIds` | string[] | да | Разделы сверху вниз: только действующие, без повторов. Не перечисленные остаются ниже, в прежнем порядке. Пустой список снимает сохранённый порядок (disciplineOrder становится null) — разделы идут в исходном порядке. |
| `expectedVersion` | integer | да | document.version из GET сводного плана. |

Ответ: ok, disciplineOrder — порядок разделов проекта после записи (как в document.disciplineOrder; null — порядок снят), version — версия документа после записи.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_DOCUMENT_VERSION_REQUIRED` | Не передан expectedVersion — версия документа из GET сводного плана (document.version). |
| 403 | `NETWORK_COORDINATOR_REQUIRED` | Нужна роль координатора или администратора. |
| 400 | `NETWORK_DISCIPLINE_ORDER_INVALID` | Нет disciplineIds, раздел не найден или в архиве, раздел указан дважды. |

Примечания: Запись документа: expectedVersion — document.version из GET сводного плана. Без него 428, при расхождении 409 — перечитать план и повторить. Подоснова на плане всегда снизу, где бы она ни стояла в списке. Раздел, убранный в архив, из порядка уходит.

<a id="discipline-drawing-order"></a>
### PUT `/api/platform/projects/{projectId}/network-federation/disciplines/{disciplineId}/drawing-order`

Задать порядок прорисовки чертежей внутри раздела на весь проект (сверху вниз).

- Идентификатор в каталоге: `discipline-drawing-order`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `disciplineId` | путь | да | Идентификатор раздела (в интерфейсе — раздел, например «Водоснабжение»). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `sectionIds` | string[] | да | Файлы (чертежи) раздела сверху вниз: только файлы этого раздела, без повторов. Не перечисленные остаются ниже, в прежнем порядке. Пустой список снимает сохранённый порядок раздела (drawingOrder становится null) — файлы идут в исходном порядке. |
| `expectedVersion` | integer | да | document.version из GET сводного плана. |

Ответ: ok, drawingOrder — порядок чертежей раздела после записи (как в disciplines[].drawingOrder; null — порядок снят), version — версия документа после записи.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_DOCUMENT_VERSION_REQUIRED` | Не передан expectedVersion — версия документа из GET сводного плана (document.version). |
| 403 | `NETWORK_COORDINATOR_REQUIRED` | Нужна роль координатора или администратора. |
| 404 | `NETWORK_DISCIPLINE_NOT_FOUND` | Раздел не найден. |
| 409 | `NETWORK_DISCIPLINE_ARCHIVED` | Раздел в архиве. |
| 400 | `NETWORK_DRAWING_ORDER_INVALID` | Нет sectionIds, файл не найден или из другого раздела, файл указан дважды. |

Примечания: Запись документа: expectedVersion — document.version из GET сводного плана. Без него 428, при расхождении 409 — перечитать план и повторить. Файлы, которых в порядке нет, на плане ниже перечисленных, по прежнему приоритету drawOrder (больше — выше) и имени.

## Файлы и версии

<a id="section-create"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections`

Завести новый файл в разделе (карточку под будущие версии чертежа).

- Идентификатор в каталоге: `section-create`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `disciplineId` | string | да | Раздел, в котором заводится файл. |
| `name` | string | да | Название файла (до 240 знаков), уникально в разделе без учёта регистра. |

Ответ: ok, section{id, disciplineId, name, includedInFederation, drawOrder, cadVersions[], modelSources[]}.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_DISCIPLINE_NOT_FOUND` | Раздел не найден. |
| 409 | `NETWORK_DISCIPLINE_ARCHIVED` | Раздел в архиве. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |
| 400 | `NETWORK_SECTION_NAME_REQUIRED` | Не указано название файла. |
| 409 | `NETWORK_SECTION_NAME_DUPLICATE` | Файл с таким названием в этом разделе уже есть. |
| 400 | `NETWORK_VALUE_TOO_LONG` | Значение длиннее 240 знаков. |

Примечания: Так программа создаёт файл, если не нашла его по имени в плане; затем загружает в него версию.

<a id="cad-version-register"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions`

Зарегистрировать загруженный и разобранный чертёж как новую версию файла.

- Идентификатор в каталоге: `cad-version-register`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `importId` | string | да | Идентификатор импорта из ответа complete; импорт должен быть завершён (status = succeeded) и загружен этим же человеком. |
| `sourceUnit` | string | да | Единицы чертежа: «m» (метры) или «mm» (миллиметры). |
| `label` | string | нет | Метка версии (до 240 знаков). |
| `note` | string | нет | Что изменилось (до 1000 знаков). |

Ответ: ok, cadVersion — хранимая запись версии: id, number, label, importId, fileName, sourceUnit, scaleToMm, sha256, createdAtUtc, createdByUserId, status, submittedByUserId, submittedAtUtc, acceptedByUserId, acceptedAtUtc, acceptedPlacementId, returnedByUserId, returnedAtUtc, returnReason, autoAcceptByUserId, note, dependencies, unitRevision, changeSummary. Полей плана placement, workingPlacement, superseded, nativeAcis здесь нет — их даёт GET сводного плана.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_SECTION_NOT_FOUND` | Файл не найден. |
| 409 | `NETWORK_DISCIPLINE_ARCHIVED` | Раздел в архиве. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |
| 400 | `NETWORK_CAD_IMPORT_REQUIRED` | Не указан importId. |
| 404 | `NETWORK_CAD_IMPORT_NOT_FOUND` | Импорт не найден. |
| 409 | `NETWORK_CAD_IMPORT_NOT_SUCCEEDED` | Импорт ещё не завершён успешно (дождитесь status = succeeded). |
| 409 | `NETWORK_CAD_IMPORT_DIGEST_MISSING` | У импорта нет контрольной суммы. |
| 403 | `NETWORK_CAD_IMPORT_OWNER_REQUIRED` | Импорт загружен другим человеком. |
| 403 | `NETWORK_CAD_IMPORT_DISCIPLINE_MISMATCH` | Файл загружен в сессии другого раздела. |
| 400 | `NETWORK_SOURCE_UNIT_REQUIRED` | sourceUnit должен быть «m» или «mm». |
| 409 | `NETWORK_CAD_IMPORT_ALREADY_REGISTERED` | Этот импорт уже зарегистрирован как версия. |
| 400 | `NETWORK_NOTE_TOO_LONG` | Примечание длиннее 1000 знаков. |
| 400 | `NETWORK_VALUE_TOO_LONG` | Значение длиннее 240 знаков. |

Примечания: Статус после регистрации: у «Загрузки» — «на проверке» (submitted); у координатора и администратора — «актуальная» (accepted), если показ готов, иначе «на проверке» с автопринятием, когда показ подготовится. Если в этом файле уже есть версия с той же SHA-256 и теми же единицами, сервер возвращает ту версию — в любом её статусе, в том числе «возвращена» (returned) или «на проверке»; новая версия не создаётся и на проверку ничего не уходит. Поэтому после возврата загрузка неизменённого файла ничего не даёт: исправьте чертёж. Для повтора после обрыва ответа это безопасно. Нового expectedVersion маршрут не требует. При загрузке по ключу у версии сохраняется название программы («через …»).

<a id="cad-version-unit-revision"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/unit-revision`

Исправить единицы измерения версии на проверке: создать уточнённую версию с определёнными единицами.

- Идентификатор в каталоге: `cad-version-unit-revision`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `expectedVersion` | integer | да | document.version из GET сводного плана. |

Ответ: ok, cadVersion: id, number, label, importId, fileName, sourceUnit (m|mm), scaleToMm, sha256, createdAtUtc, status (submitted|accepted|returned), submittedByUserId, acceptedByUserId, returnedByUserId, returnReason, note, placement и др. (те же поля, что в document.sections[].cadVersions[] плана).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_DOCUMENT_VERSION_REQUIRED` | Не передан expectedVersion — версия документа из GET сводного плана (document.version). |
| 403 | `NETWORK_COORDINATOR_REQUIRED` | Нужна роль координатора или администратора. |
| 404 | `NETWORK_SECTION_NOT_FOUND` | Файл не найден. |
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 409 | `NETWORK_UNIT_REVISION_REQUIRES_UNPLACED_SUBMITTED_VERSION` | Уточнение единиц — только для версии на проверке без размещения. |
| 409 | `NETWORK_UNIT_REVISION_DETECTED_UNIT_REQUIRED` | У импорта нет определённых единиц измерения. |
| 409 | `NETWORK_UNIT_REVISION_ACCEPTED_BASIS_REQUIRED` | Нет принятого файла с той же контрольной суммой как основания. |
| 409 | `NETWORK_UNIT_REVISION_BASIS_CONFLICT` | Единицы основания не совпадают с определёнными. |
| 409 | `NETWORK_UNIT_REVISION_UNIT_PLACEMENT_BASIS_REQUIRED` | У основания нет подходящего размещения. |

Примечания: Запись документа: expectedVersion — document.version из GET сводного плана. Без него 428, при расхождении 409 — перечитать план и повторить. Оригинал и контрольная сумма сохраняются; уточнённая версия идёт на проверку.

<a id="cad-version-download-original"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/original`

Скачать оригинал версии чертежа (DWG или DXF, как загружен).

- Идентификатор в каталоге: `cad-version-download-original`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Ответ: Тело файла (application/octet-stream), имя — в Content-Disposition. Поддерживаются частичные запросы (Range).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |

Примечания: Версию видят: администратор и координатор — любую; остальные — только принятую; «Загрузка» — ещё и любые версии файлов своих разделов. Если версии или оригинала нет — 404 без тела.

<a id="cad-version-download-dxf"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/dxf`

Скачать нормализованный DXF версии чертежа.

- Идентификатор в каталоге: `cad-version-download-dxf`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Ответ: Тело DXF (text/plain; charset=utf-8), поддерживается Range.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |

Примечания: Версию видят: администратор и координатор — любую; остальные — только принятую; «Загрузка» — ещё и любые версии файлов своих разделов. Если версии или данных нет — 404 без тела. Формат нормализации определяется сервером.

## Загрузка

<a id="upload-limits"></a>
### GET `/api/platform/projects/{projectId}/network-federation/uploads/limits`

Узнать лимиты загрузки чертежей: максимальный размер файла и куска.

- Идентификатор в каталоге: `upload-limits`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Ответ: ok, actorId, maxSourceBytes (размер файла; по умолчанию 64 МиБ), maxChunkBytes (8388608).

Примечания: Размер файла настраивается на сервере: читайте maxSourceBytes, а не фиксируйте число.

<a id="upload-create"></a>
### POST `/api/platform/projects/{projectId}/network-federation/uploads`

Открыть сессию загрузки чертежа (DWG или DXF) в раздел.

- Идентификатор в каталоге: `upload-create`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `disciplineId` | string | да | Раздел, куда грузится файл (на него нужно право записи). |
| `fileName` | string | да | Имя файла с расширением .dwg или .dxf (до 255 знаков). |
| `declaredBytes` | integer | да | Точный размер файла в байтах. |
| `sha256` | string | да | SHA-256 всего файла, 64 шестнадцатеричных знака. |

Ответ: ok, session{sessionId, projectId, actorId, disciplineId, fileName, declaredBytes, sha256, receivedBytes, status (uploading|completed|failed|cancelled|expired), importId, error, createdAtUtc, updatedAtUtc}.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 409 | `NETWORK_DISCIPLINE_ARCHIVED` | Раздел в архиве. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |
| 400 | `CAD_FILE_MUST_BE_DWG_OR_DXF` | Файл должен быть .dwg или .dxf, имя до 255 знаков. |
| 413 | `CAD_UPLOAD_LENGTH_INVALID` | Размер файла 0 или больше лимита (GET uploads/limits). |
| 400 | `CAD_UPLOAD_SHA256_REQUIRED` | Нужна sha256 файла — 64 шестнадцатеричных знака. |
| 400 | `CAD_UPLOAD_BINDING_INVALID` | Недопустимый идентификатор в запросе загрузки. |
| 429 | `CAD_IMPORT_STORAGE_QUOTA_EXCEEDED` | Исчерпана квота хранилища загрузок. |

Примечания: Неизвестный или пустой disciplineId даёт 409 NETWORK_DISCIPLINE_ARCHIVED. Сессия принадлежит человеку, который её открыл: другой человек её не видит (404). Неиспользованные сессии удаляются по времени простоя.

<a id="upload-read"></a>
### GET `/api/platform/projects/{projectId}/network-federation/uploads/{sessionId}`

Узнать состояние сессии загрузки (сколько байт принято).

- Идентификатор в каталоге: `upload-read`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sessionId` | путь | да | Идентификатор сессии загрузки (upload_…). |

Ответ: ok, session (см. создание сессии). С receivedBytes продолжают загрузку после обрыва.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `CAD_UPLOAD_SESSION_NOT_FOUND` | Сессия загрузки не найдена (или чужая). |
| 409 | `CAD_UPLOAD_SESSION_BUSY` | Сессия занята другим запросом: повторить через секунду. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |

<a id="upload-chunk"></a>
### PUT `/api/platform/projects/{projectId}/network-federation/uploads/{sessionId}/content`

Отправить очередной кусок файла (до 8 МиБ) в сессию загрузки.

- Идентификатор в каталоге: `upload-chunk`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sessionId` | путь | да | Идентификатор сессии загрузки (upload_…). |
| `Content-Type` | заголовок | да | application/octet-stream. |
| `Content-Range` | заголовок | да | bytes <начало>-<конец>/<весь размер>, например bytes 0-8388607/20000000; «весь размер» равен declaredBytes. |

Тело запроса: двоичные данные файла (`application/octet-stream`).

Ответ: ok, session (receivedBytes — сколько принято подряд).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 415 | `CAD_IMPORT_CONTENT_TYPE_REQUIRED` | Нужен Content-Type: application/octet-stream. |
| 416 | `CAD_UPLOAD_RANGE_INVALID` | Content-Range не по форме «bytes начало-конец/всего», либо «всего» не равно размеру файла. |
| 413 | `CAD_UPLOAD_CHUNK_TOO_LARGE` | Кусок больше 8 МиБ. |
| 409 | `CAD_UPLOAD_OFFSET_CONFLICT` | Кусок идёт не с того места: начните с receivedBytes из ответа. |
| 400 | `CAD_UPLOAD_CHUNK_LENGTH_MISMATCH` | Длина тела не совпала с Content-Range. |
| 409 | `CAD_UPLOAD_CHUNK_CONFLICT` | Повторно присланный кусок отличается от принятого. |
| 409 | `CAD_UPLOAD_CONTENT_MISSING` | Принятые байты потеряны на сервере: создайте сессию заново. |
| 404 | `CAD_UPLOAD_SESSION_NOT_FOUND` | Сессия загрузки не найдена (или чужая). |
| 409 | `CAD_UPLOAD_SESSION_BUSY` | Сессия занята другим запросом: повторить через секунду. |
| 409 | `CAD_UPLOAD_SESSION_EXPIRED` | Сессия загрузки истекла по времени простоя: откройте новую. |
| 409 | `CAD_UPLOAD_SESSION_CANCELLED` | Сессия загрузки отменена. |
| 409 | `CAD_UPLOAD_SESSION_FAILED` | Сессия загрузки завершилась ошибкой (например, не совпала сумма): откройте новую. |
| 409 | `CAD_UPLOAD_SESSION_COMPLETED` | Сессия уже завершена: куски больше не принимаются. |
| 429 | `CAD_IMPORT_STORAGE_QUOTA_EXCEEDED` | Исчерпана квота хранилища загрузок. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |

Примечания: Куски идут строго по порядку с позиции receivedBytes. Повтор уже принятого куска безопасен: байты сверяются, лишнего не записывается. Каждый кусок считается записью для лимита запросов.

<a id="upload-complete"></a>
### POST `/api/platform/projects/{projectId}/network-federation/uploads/{sessionId}/complete`

Завершить загрузку: сервер сверит размер и SHA-256 и поставит файл в очередь импорта.

- Идентификатор в каталоге: `upload-complete`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sessionId` | путь | да | Идентификатор сессии загрузки (upload_…). |

Ответ (202): ok, item{importId, projectId, fileName, sourceFormat (dwg|dxf), status, phase, sha256, detectedSourceUnit, sourceUnitDetection, detectedSourceUnitLabel}. Состояние импорта дальше читают по importId.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 409 | `CAD_UPLOAD_INCOMPLETE` | Принято меньше байт, чем заявлено. |
| 409 | `CAD_UPLOAD_CONTENT_MISSING` | Принятые байты потеряны на сервере: создайте сессию заново. |
| 409 | `CAD_UPLOAD_CONTENT_LENGTH_MISMATCH` | Размер принятых данных не совпал с заявленным. |
| 422 | `CAD_UPLOAD_SHA256_MISMATCH` | Контрольная сумма принятого файла не совпала с заявленной (сессия потеряна, загрузите заново). |
| 404 | `CAD_UPLOAD_SESSION_NOT_FOUND` | Сессия загрузки не найдена (или чужая). |
| 409 | `CAD_UPLOAD_SESSION_BUSY` | Сессия занята другим запросом: повторить через секунду. |
| 409 | `CAD_UPLOAD_SESSION_EXPIRED` | Сессия загрузки истекла по времени простоя: откройте новую. |
| 409 | `CAD_UPLOAD_SESSION_CANCELLED` | Сессия загрузки отменена. |
| 409 | `CAD_UPLOAD_SESSION_FAILED` | Сессия загрузки завершилась ошибкой (например, не совпала сумма): откройте новую. |
| 429 | `CAD_IMPORT_QUEUE_FULL` | Очередь импорта заполнена: повторить позже. |
| 429 | `CAD_IMPORT_STORAGE_QUOTA_EXCEEDED` | Исчерпана квота хранилища загрузок. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |

Примечания: Повтор complete для уже завершённой сессии возвращает тот же импорт (безопасно). Ответ содержит заголовок Location с адресом чтения импорта. После 422 эта же сессия отвечает 409 CAD_UPLOAD_SESSION_FAILED. detectedSourceUnit подсказывает значение sourceUnit при регистрации версии, когда sourceUnitDetection = detected.

<a id="upload-retry"></a>
### POST `/api/platform/projects/{projectId}/network-federation/uploads/{sessionId}/retry`

Повторить обработку уже загруженного файла, если импорт завершился ошибкой.

- Идентификатор в каталоге: `upload-retry`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sessionId` | путь | да | Идентификатор сессии загрузки (upload_…). |

Ответ: ok, item (состояние импорта, как у complete).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 409 | `CAD_UPLOAD_NOT_COMPLETED` | Сессия ещё не завершена вызовом complete. |
| 409 | `CAD_IMPORT_RETRY_BUSY` | Повторная обработка уже идёт. |
| 404 | `CAD_UPLOAD_SESSION_NOT_FOUND` | Сессия загрузки не найдена (или чужая). |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |

<a id="upload-cancel"></a>
### DELETE `/api/platform/projects/{projectId}/network-federation/uploads/{sessionId}`

Отменить сессию загрузки и удалить принятые куски.

- Идентификатор в каталоге: `upload-cancel`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sessionId` | путь | да | Идентификатор сессии загрузки (upload_…). |

Ответ: ok, session (status = cancelled; для завершённой сессии — как есть).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `CAD_UPLOAD_SESSION_NOT_FOUND` | Сессия загрузки не найдена (или чужая). |
| 409 | `CAD_UPLOAD_SESSION_BUSY` | Сессия занята другим запросом: повторить через секунду. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |

<a id="processing-read"></a>
### GET `/api/platform/projects/{projectId}/network-federation/processing`

Посмотреть, как идёт подготовка версий к показу (очередь, этапы, ошибки).

- Идентификатор в каталоге: `processing-read`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `disciplineId` | запрос | нет | Только версии этого раздела. |
| `sectionId` | запрос | нет | Только версии этого файла. |

Ответ: ok, active, retryAfterMs (через сколько опрашивать снова), items[{sectionId, sourceId, versionId, kind (drawing|model), state (queued|processing|ready|failed), stages, error, queue{ahead}, retry, retryable, downloads{original, processedDwg}}].

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_DISCIPLINE_NOT_FOUND` | Раздел не найден. |
| 404 | `NETWORK_SECTION_NOT_FOUND` | Файл не найден. |

Примечания: Только версии, видимые роли. Ответ не кэшируется. После регистрации версии опрашивают, пока state не станет ready (нужно для автопринятия версий координатора). Значения state: queued, processing, ready, failed. Пауза опроса: retryAfterMs равен 2500 или 10000 миллисекундам.

<a id="processing-retry"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/processing/retry`

Повторить подготовку версии к показу, если фоновая подготовка остановилась.

- Идентификатор в каталоге: `processing-retry`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Ответ: ok.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |
| 409 | `NETWORK_PROCESSING_NOT_RETRYABLE` | Повтор подготовки сейчас не нужен или невозможен. |

<a id="processed-prepare"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/processed/prepare`

Подготовить обработанный DWG версии к скачиванию.

- Идентификатор в каталоге: `processed-prepare`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Ответ: ok, processedDwg{state (ready|preparing|unavailable), format («dwg»), fileName, bytes, reason, cleanup}. Сервер ждёт готовности до 20 секунд; при state = preparing повторите запрос позже.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |
| 404 | `NETWORK_CAD_IMPORT_NOT_FOUND` | Импорт не найден. |

Примечания: Метод POST: ключом «Чтение» недоступен.

<a id="processed-report"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/processed/report`

Прочитать отчёт об обработке версии (JSON).

- Идентификатор в каталоге: `processed-report`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Ответ: JSON отчёта об обработке как есть (application/json). Ответ не кэшируется. Пока готового отчёта нет — 404 NETWORK_PROCESSED_DWG_REPORT_NOT_FOUND.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |
| 404 | `NETWORK_PROCESSED_DWG_REPORT_NOT_FOUND` | Отчёта об обработке нет. |

<a id="processed-download"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/processed`

Скачать обработанный DWG версии.

- Идентификатор в каталоге: `processed-download`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Ответ: Тело файла (application/octet-stream), поддерживается Range.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |
| 409 | `NETWORK_PROCESSED_DWG_NOT_READY` | Обработанный DWG ещё не готов. |

## Импорт CAD

<a id="cad-import-read"></a>
### GET `/api/platform/projects/{projectId}/cad-imports/{importId}`

Узнать состояние импорта загруженного файла (в очереди, идёт, готов, ошибка).

- Идентификатор в каталоге: `cad-import-read`
- Кто может: Пока импорт не зарегистрирован как версия: тот, кто его загрузил, и администратор; координатор чужой незарегистрированный импорт не читает. После регистрации доступ как к версии (в том числе «Просмотр» для принятой); иначе 403 NETWORK_SOURCE_ACCESS_DENIED (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `importId` | путь | да | Идентификатор импорта CAD. |

Ответ: ok, item{importId, projectId, fileName, sourceFormat, status (queued|running|succeeded|failed|cancelled), phase, diagnostics[{code, message, severity, count}], error, sha256, originalBytes, detectedSourceUnit (m|mm|null), sourceUnitDetection (detected|unknown|unsupported), detectedSourceUnitLabel, losslessNormalization}.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |

Примечания: Единственное, что ключу открыто в «импорте CAD»: чтение состояния. Опрашивайте не чаще раза в 2–3 секунды, пока status не станет succeeded или failed. Остальные маршруты импорта закрыты (см. раздел «Закрытые маршруты»). Если импорта нет — 404 без тела.

## Модели IFC

<a id="model-create"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/models`

Завести модель IFC в файле (под будущие версии модели).

- Идентификатор в каталоге: `model-create`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `name` | string | да | Название модели (до 240 знаков). |
| `format` | string | да | Только «ifc». |

Ответ: ok, modelSource{id, name, format, status}.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_SECTION_NOT_FOUND` | Файл не найден. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |
| 400 | `NETWORK_MODEL_FORMAT_UNSUPPORTED` | Поддерживается только format = «ifc». |
| 400 | `NETWORK_MODEL_NAME_REQUIRED` | Не указано название модели. |
| 400 | `NETWORK_VALUE_TOO_LONG` | Значение длиннее 240 знаков. |

<a id="model-version-upload"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/models/{modelId}/versions`

Загрузить новую версию модели IFC одним запросом (файл — телом запроса).

- Идентификатор в каталоге: `model-version-upload`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `modelId` | путь | да | Идентификатор модели IFC внутри файла. |
| `fileName` | запрос | да | Имя файла .ifc без пути (до 240 знаков). |
| `sourceUnit` | запрос | да | Единицы: «m» или «mm». |
| `note` | запрос | нет | Что изменилось (до 1000 знаков). |
| `Content-Type` | заголовок | да | application/octet-stream. |

Тело запроса: двоичные данные файла (`application/octet-stream`).

Ответ: ok, modelVersion{id, number, fileName, sha256, originalBytes, sourceUnit, status (submitted|accepted|returned), createdAtUtc, createdByUserId, …}.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 415 | `NETWORK_IFC_CONTENT_TYPE_REQUIRED` | Нужен Content-Type: application/octet-stream. |
| 413 | `NETWORK_IFC_TOO_LARGE` | Файл IFC больше 512 МиБ. |
| 400 | `NETWORK_IFC_FILE_NAME_REQUIRED` | fileName: имя файла .ifc без пути, до 240 знаков. |
| 400 | `NETWORK_SOURCE_UNIT_REQUIRED` | sourceUnit должен быть «m» или «mm». |
| 400 | `NETWORK_NOTE_TOO_LONG` | Примечание длиннее 1000 знаков. |
| 400 | `NETWORK_IFC_STEP_HEADER_INVALID` | Файл не похож на IFC (заголовок STEP). |
| 400 | `NETWORK_IFC_STEP_INCOMPLETE` | Файл IFC оборван (нет конца STEP). |
| 404 | `NETWORK_SECTION_NOT_FOUND` | Файл не найден. |
| 404 | `NETWORK_MODEL_SOURCE_NOT_FOUND` | Модель IFC не найдена. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |

Примечания: Куски и сессии для IFC не используются: до 512 МиБ одним запросом. Статус: у «Загрузки» — «на проверке»; у координатора и администратора — сразу принята. Повтор того же файла с теми же единицами возвращает существующую версию (безопасно).

<a id="model-version-download-original"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/models/{modelId}/versions/{versionId}/original`

Скачать оригинал версии модели IFC.

- Идентификатор в каталоге: `model-version-download-original`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `modelId` | путь | да | Идентификатор модели IFC внутри файла. |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Ответ: Тело файла (application/octet-stream), имя — в Content-Disposition, поддерживается Range.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_SECTION_NOT_FOUND` | Файл не найден. |
| 404 | `NETWORK_MODEL_SOURCE_NOT_FOUND` | Модель IFC не найдена. |
| 404 | `NETWORK_MODEL_VERSION_NOT_FOUND` | Версия модели не найдена. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |
| 404 | `NETWORK_IFC_ORIGINAL_MISSING` | Оригинал IFC на сервере отсутствует. |

Примечания: Версию видят: администратор и координатор — любую; остальные — только принятую; «Загрузка» — ещё и любые версии файлов своих разделов.

## Проверка версий

<a id="cad-version-submit"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/submit`

Отправить версию чертежа на проверку (совместимость: новые версии уже «на проверке» после регистрации).

- Идентификатор в каталоге: `cad-version-submit`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Ответ: ok, cadVersion. Повтор над версией на проверке ничего не меняет.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_SECTION_NOT_FOUND` | Файл не найден. |
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 409 | `NETWORK_DISCIPLINE_ARCHIVED` | Раздел в архиве. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |
| 409 | `NETWORK_CAD_VERSION_ALREADY_ACCEPTED` | Версия уже принята. |
| 409 | `NETWORK_CAD_VERSION_RETURNED` | Версия возвращена: загрузите исправленную. |

<a id="cad-version-accept"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/accept`

Принять версию на проверке или сделать прежнюю принятую версию актуальной.

- Идентификатор в каталоге: `cad-version-accept`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `expectedVersion` | integer | да | document.version из GET сводного плана. |

Ответ: ok, cadVersion: id, number, label, importId, fileName, sourceUnit (m|mm), scaleToMm, sha256, createdAtUtc, status (submitted|accepted|returned), submittedByUserId, acceptedByUserId, returnedByUserId, returnReason, note, placement и др. (те же поля, что в document.sections[].cadVersions[] плана).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_DOCUMENT_VERSION_REQUIRED` | Не передан expectedVersion — версия документа из GET сводного плана (document.version). |
| 403 | `NETWORK_COORDINATOR_REQUIRED` | Нужна роль координатора или администратора. |
| 404 | `NETWORK_SECTION_NOT_FOUND` | Файл не найден. |
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 409 | `NETWORK_DISCIPLINE_ARCHIVED` | Раздел в архиве. |
| 409 | `NETWORK_CAD_VERSION_NOT_SUBMITTED` | Версия не «на проверке». |
| 409 | `NETWORK_CAD_VERSION_SUPERSEDED` | Есть версия новее — эта заменена до проверки. |
| 409 | `NETWORK_CAD_VERSION_NOT_READY` | Показ версии ещё не подготовлен. |

Примечания: Запись документа: expectedVersion — document.version из GET сводного плана. Без него 428, при расхождении 409 — перечитать план и повторить. Принимается только последняя версия на проверке и только при готовом показе (processing-read: state = ready); 409 NETWORK_CAD_VERSION_NOT_READY — подождать и повторить. Прежняя принятая версия возвращается в актуальные тем же маршрутом.

<a id="cad-version-return"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/return`

Вернуть версию чертежа автору с причиной.

- Идентификатор в каталоге: `cad-version-return`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `reason` | string | да | Причина возврата, 1–1000 знаков. |
| `expectedVersion` | integer | да | document.version из GET сводного плана. |

Ответ: ok, cadVersion: id, number, label, importId, fileName, sourceUnit (m|mm), scaleToMm, sha256, createdAtUtc, status (submitted|accepted|returned), submittedByUserId, acceptedByUserId, returnedByUserId, returnReason, note, placement и др. (те же поля, что в document.sections[].cadVersions[] плана).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_DOCUMENT_VERSION_REQUIRED` | Не передан expectedVersion — версия документа из GET сводного плана (document.version). |
| 403 | `NETWORK_COORDINATOR_REQUIRED` | Нужна роль координатора или администратора. |
| 404 | `NETWORK_SECTION_NOT_FOUND` | Файл не найден. |
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 409 | `NETWORK_DISCIPLINE_ARCHIVED` | Раздел в архиве. |
| 409 | `NETWORK_CAD_VERSION_NOT_SUBMITTED` | Версия не «на проверке». |
| 409 | `NETWORK_CAD_VERSION_SUPERSEDED` | Есть версия новее — эта заменена до проверки. |
| 400 | `NETWORK_RETURN_REASON_REQUIRED` | Не указана причина возврата (1–1000 знаков). |

Примечания: Запись документа: expectedVersion — document.version из GET сводного плана. Без него 428, при расхождении 409 — перечитать план и повторить. Возвращается только последняя версия на проверке. Автор видит причину и загружает исправленную версию.

<a id="model-version-submit"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/models/{modelId}/versions/{versionId}/submit`

Отправить версию модели IFC на проверку (совместимость).

- Идентификатор в каталоге: `model-version-submit`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `modelId` | путь | да | Идентификатор модели IFC внутри файла. |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Ответ: ok, modelVersion.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_SECTION_NOT_FOUND` | Файл не найден. |
| 404 | `NETWORK_MODEL_SOURCE_NOT_FOUND` | Модель IFC не найдена. |
| 404 | `NETWORK_MODEL_VERSION_NOT_FOUND` | Версия модели не найдена. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |
| 409 | `NETWORK_MODEL_VERSION_ALREADY_ACCEPTED` | Версия модели уже принята. |
| 409 | `NETWORK_MODEL_VERSION_RETURNED` | Версия модели возвращена. |

<a id="model-version-accept"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/models/{modelId}/versions/{versionId}/accept`

Принять версию модели IFC (или сделать прежнюю принятую актуальной).

- Идентификатор в каталоге: `model-version-accept`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `modelId` | путь | да | Идентификатор модели IFC внутри файла. |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `expectedVersion` | integer | да | document.version из GET сводного плана. |

Ответ: ok, modelVersion.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_DOCUMENT_VERSION_REQUIRED` | Не передан expectedVersion — версия документа из GET сводного плана (document.version). |
| 403 | `NETWORK_COORDINATOR_REQUIRED` | Нужна роль координатора или администратора. |
| 404 | `NETWORK_SECTION_NOT_FOUND` | Файл не найден. |
| 404 | `NETWORK_MODEL_SOURCE_NOT_FOUND` | Модель IFC не найдена. |
| 404 | `NETWORK_MODEL_VERSION_NOT_FOUND` | Версия модели не найдена. |
| 409 | `NETWORK_MODEL_VERSION_NOT_SUBMITTED` | Версия модели не «на проверке». |
| 409 | `NETWORK_MODEL_VERSION_SUPERSEDED` | Есть версия модели новее. |

Примечания: Запись документа: expectedVersion — document.version из GET сводного плана. Без него 428, при расхождении 409 — перечитать план и повторить.

<a id="model-version-return"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/models/{modelId}/versions/{versionId}/return`

Вернуть версию модели IFC автору с причиной.

- Идентификатор в каталоге: `model-version-return`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `modelId` | путь | да | Идентификатор модели IFC внутри файла. |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `reason` | string | да | Причина возврата, 1–1000 знаков. |
| `expectedVersion` | integer | да | document.version из GET сводного плана. |

Ответ: ok, modelVersion.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_DOCUMENT_VERSION_REQUIRED` | Не передан expectedVersion — версия документа из GET сводного плана (document.version). |
| 403 | `NETWORK_COORDINATOR_REQUIRED` | Нужна роль координатора или администратора. |
| 404 | `NETWORK_SECTION_NOT_FOUND` | Файл не найден. |
| 404 | `NETWORK_MODEL_SOURCE_NOT_FOUND` | Модель IFC не найдена. |
| 404 | `NETWORK_MODEL_VERSION_NOT_FOUND` | Версия модели не найдена. |
| 409 | `NETWORK_MODEL_VERSION_NOT_SUBMITTED` | Версия модели не «на проверке». |
| 409 | `NETWORK_MODEL_VERSION_SUPERSEDED` | Есть версия модели новее. |
| 400 | `NETWORK_RETURN_REASON_REQUIRED` | Не указана причина возврата (1–1000 знаков). |

Примечания: Запись документа: expectedVersion — document.version из GET сводного плана. Без него 428, при расхождении 409 — перечитать план и повторить.

## Состав и размещения

<a id="section-federation-settings"></a>
### PUT `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/federation-settings`

Включить файл в сводную картину или исключить; задать порядок отрисовки.

- Идентификатор в каталоге: `section-federation-settings`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `includedInFederation` | boolean | нет | Включён ли файл в сводную картину (по умолчанию true). |
| `drawOrder` | integer | нет | Порядок отрисовки, от -1000000 до 1000000. |
| `expectedVersion` | integer | да | document.version из GET сводного плана. |

Ответ: ok, section.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_DOCUMENT_VERSION_REQUIRED` | Не передан expectedVersion — версия документа из GET сводного плана (document.version). |
| 403 | `NETWORK_COORDINATOR_REQUIRED` | Нужна роль координатора или администратора. |
| 404 | `NETWORK_SECTION_NOT_FOUND` | Файл не найден. |
| 409 | `NETWORK_DISCIPLINE_ARCHIVED` | Раздел в архиве. |
| 400 | `NETWORK_DRAW_ORDER_INVALID` | drawOrder вне диапазона от -1000000 до 1000000. |

Примечания: Запись документа: expectedVersion — document.version из GET сводного плана. Без него 428, при расхождении 409 — перечитать план и повторить. Меняет картину у всех участников.

<a id="placements-list"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/placements`

Прочитать размещения версии чертежа (положение в общей системе координат).

- Идентификатор в каталоге: `placements-list`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Ответ: ok, items[] — размещение по единицам и явные размещения (id, number, sourceToWorldMm — 16 чисел, origin, createdAtUtc, createdByUserId, comment).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_SECTION_NOT_FOUND` | Файл не найден. |
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |

Примечания: Версию видят: администратор и координатор — любую; остальные — только принятую; «Загрузка» — ещё и любые версии файлов своих разделов.

<a id="placement-create"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/placements`

Добавить новое размещение версии чертежа.

- Идентификатор в каталоге: `placement-create`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `sourceToWorldMm` | number[16] | да | Матрица 4×4 по строкам: поворот вокруг оси Z, масштаб и сдвиг на плоскости проекта; последняя строка 0,0,0,1. |
| `comment` | string | нет | Комментарий (до 240 знаков). |
| `expectedVersion` | integer | да | document.version из GET сводного плана. |

Ответ: ok, placement{id, sourceId, versionId, number, sourceToWorldMm, origin, createdAtUtc, createdByUserId, comment}.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_DOCUMENT_VERSION_REQUIRED` | Не передан expectedVersion — версия документа из GET сводного плана (document.version). |
| 404 | `NETWORK_SECTION_NOT_FOUND` | Файл не найден. |
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 409 | `NETWORK_DISCIPLINE_ARCHIVED` | Раздел в архиве. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |
| 400 | `NETWORK_PLACEMENT_MATRIX_INVALID` | sourceToWorldMm: 16 конечных чисел по правилам размещения на плоскости XY. |

Примечания: Запись документа: expectedVersion — document.version из GET сводного плана. Без него 428, при расхождении 409 — перечитать план и повторить. Закрепляет размещение принятием версии координатором (accept).

<a id="model-adapters-list"></a>
### GET `/api/platform/projects/{projectId}/network-federation/model-adapters`

Узнать, какие форматы моделей поддерживает сводный план.

- Идентификатор в каталоге: `model-adapters-list`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Ответ: ok, items[] — возможности адаптеров (сейчас: ifc, показ в клиентском просмотрщике).

## Снимки

<a id="snapshots-list"></a>
### GET `/api/platform/projects/{projectId}/network-federation/snapshots`

Получить список снимков сводной картины.

- Идентификатор в каталоге: `snapshots-list`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `offset` | запрос | нет | Сколько снимков пропустить (по умолчанию 0). |
| `limit` | запрос | нет | Сколько вернуть (по умолчанию 50). |

Ответ: ok, total, items[{id, name, comment, createdAtUtc, compositionKind, digest, sourceCount, documentVersion}] — новые первыми; limit 1–100.

<a id="snapshot-create"></a>
### POST `/api/platform/projects/{projectId}/network-federation/snapshots`

Зафиксировать снимок: набор версий и размещений на этот момент.

- Идентификатор в каталоге: `snapshot-create`
- Кто может: Рабочий снимок — участники с правом записи; принятый (accepted) — координатор и администратор (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `name` | string | да | Название снимка. |
| `comment` | string | нет | Комментарий. |
| `compositionKind` | string | нет | «working» (по умолчанию) или «accepted». |
| `sources` | object[] | да | Закрепы 1–1024: {sourceId (файл), versionId, placementId?, visible?} без повторов файла. |
| `expectedVersion` | integer | да | document.version из GET сводного плана. |
| `idempotencyKey` | string | нет | Ключ повтора: тот же ключ с тем же содержимым возвращает уже созданный снимок. |

Ответ: ok, snapshot{id, name, comment, createdAtUtc, createdByUserId, documentVersion, compositionKind, digest, sources[], idempotencyKey, disciplineOrder, disciplines[{id, isBasemap, tint, shownByDefault, drawingOrder}]}. disciplineOrder и disciplines — настройки разделов снимка на момент создания (порядок — только разделы и файлы снимка); у снимков, созданных до этих настроек, полей нет.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_DOCUMENT_VERSION_REQUIRED` | Не передан expectedVersion — версия документа из GET сводного плана (document.version). |
| 400 | `NETWORK_SNAPSHOT_NAME_REQUIRED` | Не указано название снимка. |
| 400 | `NETWORK_COMPOSITION_KIND_INVALID` | compositionKind: «working» или «accepted». |
| 400 | `NETWORK_SNAPSHOT_SOURCES_INVALID` | sources: от 1 до 1024 закрепов без повторов файлов. |
| 403 | `NETWORK_SNAPSHOT_WRITE_DENIED` | Рабочий снимок создают участники с правом записи; принятый — координатор. |
| 403 | `NETWORK_COORDINATOR_REQUIRED` | Нужна роль координатора или администратора. |
| 409 | `NETWORK_SNAPSHOT_VERSION_NOT_ACCEPTED` | В принятый снимок можно закрепить только принятые версии. |
| 409 | `NETWORK_SNAPSHOT_PLACEMENT_NOT_ACCEPTED` | В принятый снимок можно закрепить только принятое размещение. |
| 409 | `NETWORK_IDEMPOTENCY_CONFLICT` | idempotencyKey уже использован с другим содержимым. |
| 403 | `NETWORK_SNAPSHOT_ACCESS_DENIED` | Снимок вам недоступен. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |
| 404 | `NETWORK_SECTION_NOT_FOUND` | Файл не найден. |
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |

Примечания: Запись документа: expectedVersion — document.version из GET сводного плана. Без него 428, при расхождении 409 — перечитать план и повторить. Безопасно повторять с одним idempotencyKey.

<a id="snapshot-read"></a>
### GET `/api/platform/projects/{projectId}/network-federation/snapshots/{snapshotId}`

Прочитать снимок.

- Идентификатор в каталоге: `snapshot-read`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `snapshotId` | путь | да | Идентификатор снимка. |

Ответ: ok, snapshot.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_SNAPSHOT_NOT_FOUND` | Снимок не найден. |
| 403 | `NETWORK_SNAPSHOT_ACCESS_DENIED` | Снимок вам недоступен. |

<a id="snapshot-compare"></a>
### GET `/api/platform/projects/{projectId}/network-federation/snapshots/{beforeId}/compare/{afterId}`

Сравнить два снимка: что добавилось, убралось, сменило версию или размещение.

- Идентификатор в каталоге: `snapshot-compare`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `beforeId` | путь | да | Идентификатор «до» (версия или снимок). |
| `afterId` | путь | да | Идентификатор «после» (версия или снимок). |

Ответ: ok, comparison{beforeId, afterId, cacheKey, algorithm («source-manifest-v1»), changes[{sourceId, kind (added|removed|changed|unchanged), before, after, contentChanged, placementChanged, dependenciesChanged}]}.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_SNAPSHOT_NOT_FOUND` | Снимок не найден. |
| 403 | `NETWORK_SNAPSHOT_ACCESS_DENIED` | Снимок вам недоступен. |

## Подготовка и показ — служебные

<a id="cad-version-presentation"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/presentation`

Получить представление чертежа для показа в просмотрщике (JSON).

- Идентификатор в каталоге: `cad-version-presentation`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Ответ: JSON представления чертежа; формат может меняться.

Примечания: Служебный маршрут показа. Возможны ошибки CAD_PRESENTATION_* (подготовка представления); отдельные коды уточняются. Коды ошибок подготовки представления (CAD_PRESENTATION_*) формирует сервер, список может дополняться.

<a id="cad-version-preview"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/preview`

Получить встроенную картинку-предпросмотр версии (PNG).

- Идентификатор в каталоге: `cad-version-preview`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Ответ: Изображение image/png; поддерживаются ETag и If-None-Match (304).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |

Примечания: Служебный маршрут показа. Если предпросмотра нет — 404.

<a id="prepared-views-list"></a>
### GET `/api/platform/projects/{projectId}/network-federation/prepared-views`

Получить перечень подготовленных видов всех видимых версий.

- Идентификатор в каталоге: `prepared-views-list`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Ответ: ok, retryAfterMs (2000), items[{sectionId, versionId, status, error, generation, retryAfterMs, renderTile}] (renderTile может отсутствовать). Ответ не кэшируется.

Примечания: Служебный маршрут показа: формат может меняться без объявления несовместимости. Версию видят: администратор и координатор — любую; остальные — только принятую; «Загрузка» — ещё и любые версии файлов своих разделов.

<a id="prepared-view-read"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/prepared-view`

Получить подготовленный вид одной версии.

- Идентификатор в каталоге: `prepared-view-read`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Ответ: ok, item — та же строка, что в списке подготовленных видов, для одной версии. Ответ не кэшируется.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |

Примечания: Служебный маршрут показа: формат может меняться без объявления несовместимости. Версию видят: администратор и координатор — любую; остальные — только принятую; «Загрузка» — ещё и любые версии файлов своих разделов.

<a id="prepared-scene-read"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/prepared-scene`

Узнать состояние подготовленной сцены версии.

- Идентификатор в каталоге: `prepared-scene-read`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |
| `renderFontBindingId` | запрос | нет | Привязка шрифтовых ресурсов (необязательно, не более одной). |

Ответ: ok, item — описание подготовленной сцены версии (status, attemptId, assets[] и др.). Формат служебный.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |
| 400 | `NETWORK_RENDER_FONT_BINDING_INVALID` | Недопустимый renderFontBindingId. |

Примечания: Служебный маршрут показа: формат может меняться без объявления несовместимости. Версию видят: администратор и координатор — любую; остальные — только принятую; «Загрузка» — ещё и любые версии файлов своих разделов.

<a id="prepared-scene-start"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/prepared-scene`

Запустить подготовку сцены версии (если ещё не готова).

- Идентификатор в каталоге: `prepared-scene-start`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |
| `renderFontBindingId` | запрос | нет | Привязка шрифтовых ресурсов (необязательно, не более одной). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `profile` | string | нет | Профиль подготовки (по умолчанию «default»). |

Ответ: 200 или 202: ok, item — состояние сцены (200, когда status = ready).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 400 | `CAD_PREPARED_PROFILE_INVALID` | Недопустимый profile подготовки. |
| 429 | `CAD_IMPORT_QUEUE_FULL` | Очередь импорта заполнена: повторить позже. |
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |

Примечания: Служебный маршрут показа: формат может меняться без объявления несовместимости. Версию видят: администратор и координатор — любую; остальные — только принятую; «Загрузка» — ещё и любые версии файлов своих разделов. Метод POST: ключом «Чтение» недоступен. Прочие ошибки CAD_* (409) уточняются. Ответ 200, если сцена готова, иначе 202.

<a id="prepared-scene-asset"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/prepared-scene/{attemptId}/assets/{assetId}`

Получить ресурс подготовленной сцены (двоичный блок).

- Идентификатор в каталоге: `prepared-scene-asset`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |
| `attemptId` | путь | да | Идентификатор попытки подготовки. |
| `assetId` | путь | да | Идентификатор ресурса подготовленной сцены. |
| `renderFontBindingId` | запрос | нет | Привязка шрифтовых ресурсов (необязательно, не более одной). |

Ответ: Двоичные данные ресурса; ETag по SHA-256, поддерживаются If-None-Match (304) и Range.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_PREPARED_ASSET_NOT_FOUND` | Ресурс подготовленной сцены не найден. |
| 404 | `NETWORK_PREPARED_ATTEMPT_NOT_FOUND` | Попытка подготовки не найдена. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |

Примечания: Служебный маршрут показа: формат может меняться без объявления несовместимости. Версию видят: администратор и координатор — любую; остальные — только принятую; «Загрузка» — ещё и любые версии файлов своих разделов.

<a id="prepared-scene-render-tile"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/prepared-scene/{attemptId}/render-tile/{packSha256}`

Получить пакет тайлов отрисовки готовой попытки.

- Идентификатор в каталоге: `prepared-scene-render-tile`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |
| `attemptId` | путь | да | Идентификатор попытки подготовки. |
| `packSha256` | путь | да | SHA-256 пакета, строчными шестнадцатеричными. |
| `renderFontBindingId` | запрос | нет | Привязка шрифтовых ресурсов (необязательно, не более одной). |

Ответ: Двоичный пакет; неизменяем по SHA-256, кэшируется; поддерживаются Range, If-Range, If-None-Match.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_RENDER_TILE_NOT_FOUND` | Пакет тайлов не найден. |
| 404 | `NETWORK_PREPARED_ATTEMPT_NOT_FOUND` | Попытка подготовки не найдена. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |

Примечания: Служебный маршрут показа: формат может меняться без объявления несовместимости. Версию видят: администратор и координатор — любую; остальные — только принятую; «Загрузка» — ещё и любые версии файлов своих разделов.

<a id="prepared-scene-asset-pack"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/prepared-scene/{attemptId}/asset-pack`

Получить набор ресурсов подготовленной сцены одним ответом.

- Идентификатор в каталоге: `prepared-scene-asset-pack`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |
| `attemptId` | путь | да | Идентификатор попытки подготовки. |
| `assetId` | запрос | да | Идентификатор ресурса; параметр повторяется для каждого нужного ресурса. |
| `renderFontBindingId` | запрос | нет | Привязка шрифтовых ресурсов (необязательно, не более одной). |

Ответ: Склеенные двоичные данные ресурсов; ETag, If-None-Match (304).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 400 | `NETWORK_PREPARED_ASSET_PACK_COUNT_INVALID` | Недопустимое число ресурсов в наборе. |
| 400 | `NETWORK_PREPARED_ASSET_PACK_IDS_INVALID` | Недопустимые идентификаторы ресурсов в наборе. |
| 413 | `NETWORK_PREPARED_ASSET_PACK_TOO_LARGE` | Набор ресурсов слишком большой. |
| 404 | `NETWORK_PREPARED_ASSET_NOT_FOUND` | Ресурс подготовленной сцены не найден. |
| 404 | `NETWORK_PREPARED_ATTEMPT_NOT_FOUND` | Попытка подготовки не найдена. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |

Примечания: Служебный маршрут показа: формат может меняться без объявления несовместимости. Версию видят: администратор и координатор — любую; остальные — только принятую; «Загрузка» — ещё и любые версии файлов своих разделов.

<a id="render-tile-ranges"></a>
### POST `/api/platform/projects/{projectId}/network-federation/render-tile-ranges`

Получить несколько диапазонов тайлов отрисовки одним запросом (чтение, но методом POST).

- Идентификатор в каталоге: `render-tile-ranges`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `version` | integer | да | Версия формата запроса (1). |
| `items` | object[] | да | Диапазоны: {key, packSha256, start, length, …}; до 16 КиБ тела. |

Ответ: Двоичный конверт application/vnd.platform.cad-render-tile-ranges.v1: заголовок RTRB, опись JSON, затем данные.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 400 | `NETWORK_JSON_REQUIRED` | Нужен Content-Type: application/json. |
| 400 | `NETWORK_RENDER_TILE_RANGES_INVALID` | Недопустимый запрос диапазонов тайлов. |
| 413 | `NETWORK_RENDER_TILE_RANGES_TOO_LARGE` | Запрос диапазонов тайлов слишком большой. |

Примечания: Служебный маршрут показа: формат может меняться без объявления несовместимости. Версию видят: администратор и координатор — любую; остальные — только принятую; «Загрузка» — ещё и любые версии файлов своих разделов. Метод POST, но это чтение: доступен ключу «Чтение» и считается в лимите чтений.

<a id="native-acis"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/native-acis`

Получить встроенные данные ACIS версии (твёрдотельная геометрия).

- Идентификатор в каталоге: `native-acis`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Ответ: Двоичные данные application/vnd.platform.cad-acis; ETag, If-None-Match (304), Range.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |
| 409 | `NETWORK_NATIVE_ACIS_INVALID` | Данные native-acis повреждены. |

Примечания: Служебный маршрут показа: формат может меняться без объявления несовместимости. Версию видят: администратор и координатор — любую; остальные — только принятую; «Загрузка» — ещё и любые версии файлов своих разделов. Если данных нет — 404; 503 или 507 — сервер занят или переполнено хранилище.

## Шрифты

<a id="render-font-resolve"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/render-font-resources/resolve`

Подобрать шрифтовые ресурсы для показа версии (чтение, но методом POST).

- Идентификатор в каталоге: `render-font-resolve`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Ответ: ok, binding, fontResources. Ответ не кэшируется.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |
| 404 | `CAD_FONT_PACK_NOT_FOUND` | Пакет шрифтов не найден. |

Примечания: Служебный маршрут показа: формат может меняться без объявления несовместимости. Версию видят: администратор и координатор — любую; остальные — только принятую; «Загрузка» — ещё и любые версии файлов своих разделов. Метод POST, но это чтение: доступен ключу «Чтение» и считается в лимите чтений.

<a id="render-font-pack-read"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/render-font-resources/{bindingId}/font-pack`

Прочитать опись пакета шрифтов привязки.

- Идентификатор в каталоге: `render-font-pack-read`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |
| `bindingId` | путь | да | Идентификатор привязки шрифтовых ресурсов. |

Ответ: ok, pack — опись пакета шрифтов привязки; ETag и If-None-Match (304).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |

Примечания: Служебный маршрут показа: формат может меняться без объявления несовместимости. Версию видят: администратор и координатор — любую; остальные — только принятую; «Загрузка» — ещё и любые версии файлов своих разделов.

<a id="render-font-pack-font"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/render-font-resources/{bindingId}/font-pack/fonts/{fontSha256}`

Скачать шрифт из пакета привязки.

- Идентификатор в каталоге: `render-font-pack-font`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |
| `bindingId` | путь | да | Идентификатор привязки шрифтовых ресурсов. |
| `fontSha256` | путь | да | SHA-256 шрифта, строчными шестнадцатеричными. |

Ответ: Файл шрифта; ETag по SHA-256, If-None-Match (304).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `CAD_FONT_NOT_IN_PACK` | Шрифта нет в пакете. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |

Примечания: Служебный маршрут показа: формат может меняться без объявления несовместимости. Версию видят: администратор и координатор — любую; остальные — только принятую; «Загрузка» — ещё и любые версии файлов своих разделов.

<a id="render-font-resolve-batch"></a>
### POST `/api/platform/projects/{projectId}/network-federation/render-font-resources/resolve-batch`

Подобрать шрифтовые ресурсы сразу для многих версий (чтение, но методом POST).

- Идентификатор в каталоге: `render-font-resolve-batch`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `expectedDocumentVersion` | integer | да | document.version из GET сводного плана. |
| `rows` | object[] | да | Строки: {key, sectionId, versionId, …}; до 16 КиБ тела. |

Ответ: ok, documentVersion, rows[{key, ok, binding, fontResources, status, error}].

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_DOCUMENT_VERSION_REQUIRED` | Не передан expectedVersion — версия документа из GET сводного плана (document.version). |
| 400 | `NETWORK_RENDER_FONT_BATCH_TOO_LARGE` | Пакетный запрос шрифтов слишком большой. |
| 400 | `NETWORK_RENDER_FONT_BATCH_INVALID` | Недопустимый пакетный запрос шрифтов. |

Примечания: Служебный маршрут показа: формат может меняться без объявления несовместимости. Версию видят: администратор и координатор — любую; остальные — только принятую; «Загрузка» — ещё и любые версии файлов своих разделов. Метод POST, но это чтение: доступен ключу «Чтение» и считается в лимите чтений.

<a id="font-pack-upload"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/font-packs`

Загрузить пакет шрифтов для версии чертежа (недостающие шрифты чертежа).

- Идентификатор в каталоге: `font-pack-upload`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |
| `Content-Type` | заголовок | да | multipart/form-data с boundary. |

Тело запроса: `multipart/form-data`.

Части формы:

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `manifest` | json (часть формы) | да | Опись: fonts[{fileName, sha256, codePage}]. |
| `fonts` | file (часть формы, повторяется) | да | Файлы шрифтов; имя файла без пути. |

Ответ (201): ok, pack — опись созданного пакета (packSha256, fonts[]).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 400 | `CAD_FONT_MULTIPART_REQUIRED` | Нужен Content-Type: multipart/form-data. |
| 400 | `CAD_FONT_MANIFEST_REQUIRED` | В запросе нет части manifest. |
| 400 | `CAD_FONT_REQUEST_TOO_LARGE` | Запрос шрифтов больше допустимого. |
| 429 | `CAD_FONT_UPLOAD_BUSY` | Идёт другая загрузка шрифтов: повторить позже. |
| 507 | `CAD_FONT_STORAGE_QUOTA_EXCEEDED` | Исчерпана квота хранилища шрифтов. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |

Примечания: Пределы размера и числа шрифтов задаёт сервер; остальные коды CAD_FONT_* (формат, суммы, имена) уточняются. Одновременно принимается одна загрузка шрифтов — иначе 429.

<a id="font-pack-read"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/font-packs/{packSha256}`

Прочитать опись загруженного пакета шрифтов.

- Идентификатор в каталоге: `font-pack-read`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |
| `packSha256` | путь | да | SHA-256 пакета, строчными шестнадцатеричными. |

Ответ: ok, pack — опись; ETag, If-None-Match (304).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `CAD_FONT_PACK_NOT_FOUND` | Пакет шрифтов не найден. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |

<a id="font-pack-font"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/font-packs/{packSha256}/fonts/{fontSha256}`

Скачать шрифт из загруженного пакета.

- Идентификатор в каталоге: `font-pack-font`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |
| `packSha256` | путь | да | SHA-256 пакета, строчными шестнадцатеричными. |
| `fontSha256` | путь | да | SHA-256 шрифта, строчными шестнадцатеричными. |

Ответ: Файл шрифта; ETag по SHA-256.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 400 | `CAD_FONT_SHA_INVALID` | Недопустимая SHA-256 шрифта. |
| 404 | `CAD_FONT_NOT_IN_PACK` | Шрифта нет в пакете. |
| 404 | `CAD_FONT_PACK_NOT_FOUND` | Пакет шрифтов не найден. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |

<a id="font-revision-create"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/font-revisions`

Создать новую версию чертежа, привязанную к загруженному пакету шрифтов.

- Идентификатор в каталоге: `font-revision-create`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `packSha256` | string | да | SHA-256 пакета шрифтов этой версии. |
| `label` | string | нет | Метка версии. |

Ответ (201): ok, cadVersion — новая версия.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |
| 409 | `NETWORK_FONT_PACK_BINDING_MISMATCH` | Пакет шрифтов не подходит этой версии. |
| 409 | `NETWORK_FONT_PACK_DEPENDENCY_INVALID` | Недопустимая зависимость версии от пакета шрифтов. |
| 409 | `NETWORK_FONT_PACK_IDENTITY_CHANGED` | Содержимое пакета изменилось. |
| 400 | `NETWORK_JSON_REQUIRED` | Нужен Content-Type: application/json. |
| 400 | `NETWORK_REQUEST_TOO_LARGE` | Тело запроса больше допустимого. |

Примечания: Тело — JSON не более 8 КиБ, Content-Type: application/json. Новая версия проходит те же ворота проверки, что и загрузка.

## Сравнения

<a id="comparison-read"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/comparisons/{beforeId}/{afterId}`

Прочитать сравнение двух версий файла (если уже посчитано).

- Идентификатор в каталоге: `comparison-read`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `beforeId` | путь | да | Идентификатор «до» (версия или снимок). |
| `afterId` | путь | да | Идентификатор «после» (версия или снимок). |
| `runtime` | запрос | нет | Среда расчёта сравнения. |

Ответ: ok, enabled, state (absent|computing|ready), pairId, claimToken, leaseUntilUtc, pages (или null), manifestSha256 (или null), summary (или null), provenance («participant-browser»).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |
| 400 | `COMPARISON_DISTINCT_VERSIONS_REQUIRED` | Для сравнения нужны разные версии. |
| 409 | `AI_SOURCE_UNITS_DIFFER` | Единицы измерения версий различаются. |
| 409 | `COMPARISON_INPUT_CHANGED` | Исходные версии изменились. |
| 409 | `NETWORK_DISCIPLINE_ARCHIVED` | Раздел в архиве. |

Примечания: Чтение готового результата доступно программе; расчёт — служебный протокол в браузере участника.

<a id="comparison-claim"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/comparisons/{beforeId}/{afterId}/claim`

Взять расчёт сравнения на себя (получить аренду).

- Идентификатор в каталоге: `comparison-claim`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `beforeId` | путь | да | Идентификатор «до» (версия или снимок). |
| `afterId` | путь | да | Идентификатор «после» (версия или снимок). |
| `runtime` | запрос | да | Среда расчёта. |

Ответ: ok, enabled, state (absent|computing|ready), pairId, claimToken, leaseUntilUtc, pages (или null), manifestSha256 (или null), summary (или null), provenance («participant-browser»). Токен аренды — claimToken.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 400 | `COMPARISON_RUNTIME_REQUIRED` | Не указан runtime сравнения. |
| 400 | `COMPARISON_DISTINCT_VERSIONS_REQUIRED` | Для сравнения нужны разные версии. |
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |
| 409 | `AI_SOURCE_UNITS_DIFFER` | Единицы измерения версий различаются. |
| 409 | `COMPARISON_INPUT_CHANGED` | Исходные версии изменились. |
| 409 | `NETWORK_DISCIPLINE_ARCHIVED` | Раздел в архиве. |

Примечания: Служебный протокол расчёта сравнения в браузере участника; формат может меняться. Параметр runtime — 64 шестнадцатеричных знака.

<a id="comparison-read-by-id"></a>
### GET `/api/platform/projects/{projectId}/network-federation/comparisons/{pairId}`

Прочитать сравнение по идентификатору.

- Идентификатор в каталоге: `comparison-read-by-id`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `pairId` | путь | да | Идентификатор сравнения. |

Ответ: ok, enabled, state (absent|computing|ready), pairId, claimToken, leaseUntilUtc, pages (или null), manifestSha256 (или null), summary (или null), provenance («participant-browser»).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `COMPARISON_NOT_FOUND` | Сравнение не найдено. |
| 409 | `AI_SOURCE_UNITS_DIFFER` | Единицы измерения версий различаются. |
| 409 | `COMPARISON_INPUT_CHANGED` | Исходные версии изменились. |
| 409 | `NETWORK_DISCIPLINE_ARCHIVED` | Раздел в архиве. |

<a id="comparison-lease"></a>
### POST `/api/platform/projects/{projectId}/network-federation/comparisons/{pairId}/lease`

Продлить аренду расчёта сравнения.

- Идентификатор в каталоге: `comparison-lease`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `pairId` | путь | да | Идентификатор сравнения. |
| `X-Cad-Comparison-Claim` | заголовок | да | Токен аренды — 32 шестнадцатеричных знака. |

Ответ: ok: true.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 400 | `COMPARISON_CLAIM_REQUIRED` | Нужен заголовок X-Cad-Comparison-Claim (32 шестнадцатеричных знака). |
| 409 | `COMPARISON_LEASE_EXPIRED` | Аренда сравнения истекла. |
| 404 | `COMPARISON_NOT_FOUND` | Сравнение не найдено. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |

Примечания: Служебный протокол расчёта сравнения в браузере участника; формат может меняться. Заголовок X-Cad-Comparison-Claim — 32 шестнадцатеричных знака.

<a id="comparison-page-read"></a>
### GET `/api/platform/projects/{projectId}/network-federation/comparisons/{pairId}/pages/{kind}/{index:int}`

Прочитать страницу результата сравнения.

- Идентификатор в каталоге: `comparison-page-read`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `pairId` | путь | да | Идентификатор сравнения. |
| `kind` | путь | да | Вид страницы сравнения. |
| `index` | путь | да | Номер страницы сравнения (целое). |

Ответ: JSON страницы как есть (application/json).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `COMPARISON_PAGE_NOT_FOUND` | Страницы сравнения нет. |
| 400 | `COMPARISON_PAGE_INVALID` | Недопустимая страница сравнения. |
| 404 | `COMPARISON_NOT_FOUND` | Сравнение не найдено. |
| 409 | `COMPARISON_NOT_READY` | Сравнение ещё не готово. |

Примечания: Служебный протокол расчёта сравнения; формат может меняться.

<a id="comparison-page-publish"></a>
### POST `/api/platform/projects/{projectId}/network-federation/comparisons/{pairId}/pages/{kind}/{index:int}`

Опубликовать страницу результата сравнения.

- Идентификатор в каталоге: `comparison-page-publish`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `pairId` | путь | да | Идентификатор сравнения. |
| `kind` | путь | да | Вид страницы сравнения. |
| `index` | путь | да | Номер страницы сравнения (целое). |
| `X-Cad-Comparison-Claim` | заголовок | да | Токен аренды. |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `(тело)` | json | да | Страница результата; до 512 КиБ. |

Ответ: ok, page.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 400 | `COMPARISON_CLAIM_REQUIRED` | Нужен заголовок X-Cad-Comparison-Claim (32 шестнадцатеричных знака). |
| 413 | `COMPARISON_PAGE_TOO_LARGE` | Страница сравнения слишком большая. |
| 400 | `COMPARISON_PAGE_INVALID` | Недопустимая страница сравнения. |
| 409 | `COMPARISON_LEASE_EXPIRED` | Аренда сравнения истекла. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |

Примечания: Служебный протокол расчёта сравнения в браузере участника; формат может меняться. Тело до 512 КиБ, индекс страницы 0–8191.

<a id="comparison-complete"></a>
### POST `/api/platform/projects/{projectId}/network-federation/comparisons/{pairId}/complete`

Завершить расчёт сравнения.

- Идентификатор в каталоге: `comparison-complete`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»
- **Служебный маршрут показа:** формат может меняться без объявления несовместимости.

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `pairId` | путь | да | Идентификатор сравнения. |
| `X-Cad-Comparison-Claim` | заголовок | да | Токен аренды. |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `(тело)` | json | да | Массив описаний страниц; до 2 МиБ. |

Ответ: ok, enabled, state (absent|computing|ready), pairId, claimToken, leaseUntilUtc, pages (или null), manifestSha256 (или null), summary (или null), provenance («participant-browser»).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 400 | `COMPARISON_CLAIM_REQUIRED` | Нужен заголовок X-Cad-Comparison-Claim (32 шестнадцатеричных знака). |
| 413 | `COMPARISON_PAGE_TOO_LARGE` | Страница сравнения слишком большая. |
| 409 | `COMPARISON_MANIFEST_INCOMPLETE` | Опись страниц сравнения неполная. |
| 409 | `COMPARISON_INPUT_CHANGED` | Исходные версии изменились. |
| 409 | `COMPARISON_LEASE_EXPIRED` | Аренда сравнения истекла. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |
| 409 | `AI_SOURCE_UNITS_DIFFER` | Единицы измерения версий различаются. |
| 409 | `NETWORK_DISCIPLINE_ARCHIVED` | Раздел в архиве. |

Примечания: Служебный протокол расчёта сравнения в браузере участника; формат может меняться. Тело до 2 МиБ — список описаний страниц.

<a id="comparison-summary-request"></a>
### POST `/api/platform/projects/{projectId}/network-federation/comparisons/{pairId}/summary`

Запросить краткую сводку по готовому сравнению.

- Идентификатор в каталоге: `comparison-summary-request`
- Кто может: Администратор и координатор — в любой раздел; «Загрузка» — только в назначенные ей разделы (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `pairId` | путь | да | Идентификатор сравнения. |

Ответ: ok, enabled, state (absent|computing|ready), pairId, claimToken, leaseUntilUtc, pages (или null), manifestSha256 (или null), summary (или null), provenance («participant-browser»).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `COMPARISON_NOT_FOUND` | Сравнение не найдено. |
| 409 | `COMPARISON_NOT_READY` | Сравнение ещё не готово. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в этот раздел. |
| 409 | `AI_NOT_CONFIGURED` | Построение сводок на сервере не настроено. |
| 409 | `AI_SOURCE_UNITS_DIFFER` | Единицы измерения версий различаются. |
| 409 | `COMPARISON_INPUT_CHANGED` | Исходные версии изменились. |
| 409 | `NETWORK_DISCIPLINE_ARCHIVED` | Раздел в архиве. |

## Сводки изменений

<a id="change-summary-read"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/change-summary`

Прочитать сводку изменений версии чертежа относительно предыдущей.

- Идентификатор в каталоге: `change-summary-read`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Ответ: ok, enabled (включена ли функция на сервере), summary — сводка (или null, пока не построена).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |

Примечания: Версию видят: администратор и координатор — любую; остальные — только принятую; «Загрузка» — ещё и любые версии файлов своих разделов.

<a id="change-summary-request"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/change-summary`

Запросить построение сводки изменений версии.

- Идентификатор в каталоге: `change-summary-request`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sectionId` | путь | да | Идентификатор файла внутри раздела (в адресе и в коде — sections). |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Ответ: ok, enabled, summary — текущее состояние сводки.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |
| 409 | `AI_BROWSER_COMPARISON_REQUIRED` | Готовой сводки нет: сначала нужно сравнение версий, посчитанное в браузере участника. |
| 409 | `AI_VERSION_PAIR_CHANGED` | Пара версий для сводки изменилась. |

Примечания: Метод POST: ключом «Чтение» недоступен. Если готовой сводки нет, сервер всегда отвечает 409 AI_BROWSER_COMPARISON_REQUIRED: новую сводку запускают только через сравнение версий (группа «сравнения»).

## Обсуждения

<a id="discussions-list"></a>
### GET `/api/platform/projects/{projectId}/network-federation/discussions`

Получить список обсуждений (замечаний) проекта с фильтрами.

- Идентификатор в каталоге: `discussions-list`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `status` | запрос | нет | Через запятую: open, in_progress, review, resolved. |
| `sourceId` | запрос | нет | Только обсуждения файла. |
| `versionId` | запрос | нет | Только обсуждения версии. |
| `priority` | запрос | нет | Через запятую: high, normal, low, none. |
| `assignee` | запрос | нет | «me», «none» или идентификатор исполнителя. |
| `label` | запрос | нет | Идентификатор метки. |
| `overdue` | запрос | нет | true — только просроченные (нужен today). |
| `q` | запрос | нет | Поиск по тексту, до 200 знаков. |
| `sourceIds` | запрос | нет | Через запятую — файлы сцены (до 1000). |
| `anchorSourceIds` | запрос | нет | Через запятую — файлы привязки (до 1000). |
| `sort` | запрос | нет | activity, created, due или priority. |
| `today` | запрос | нет | Сегодняшняя дата клиента, ГГГГ-ММ-ДД (для overdue). |
| `offset` | запрос | нет | Сколько пропустить (по умолчанию 0). |
| `limit` | запрос | нет | Сколько вернуть, до 100 (по умолчанию 50). |

Ответ: ok, total, offset, limit, items[] — обсуждения с последним сообщением.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 400 | `NETWORK_DISCUSSION_STATUS_INVALID` | status: open, in_progress, review или resolved. |
| 400 | `NETWORK_DISCUSSION_FILTER_INVALID` | Недопустимое значение фильтра списка. |
| 503 | `NETWORK_DISCUSSIONS_STORAGE_UNAVAILABLE` | Хранилище обсуждений на сервере не готово. |

Примечания: Обсуждения видят только те, чей файл-источник вам виден по роли.

<a id="discussions-summary"></a>
### GET `/api/platform/projects/{projectId}/network-federation/discussions/summary`

Получить счётчики обсуждений для вкладок «Открытые · Мои · Просрочено · Решённые».

- Идентификатор в каталоге: `discussions-summary`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `sourceId` | запрос | нет | Файл. |
| `versionId` | запрос | нет | Версия. |
| `priority` | запрос | нет | Приоритеты. |
| `assignee` | запрос | нет | Исполнитель. |
| `label` | запрос | нет | Метка. |
| `q` | запрос | нет | Поиск. |
| `sourceIds` | запрос | нет | Файлы сцены. |
| `anchorSourceIds` | запрос | нет | Файлы привязки. |
| `today` | запрос | нет | Дата клиента, ГГГГ-ММ-ДД. |

Ответ: ok, total, unresolved, open, inProgress, review, resolved, mine, overdue.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 400 | `NETWORK_DISCUSSION_FILTER_INVALID` | Недопустимое значение фильтра списка. |
| 503 | `NETWORK_DISCUSSIONS_STORAGE_UNAVAILABLE` | Хранилище обсуждений на сервере не готово. |

Примечания: Обсуждения видят только те, чей файл-источник вам виден по роли.

<a id="discussions-changes"></a>
### GET `/api/platform/projects/{projectId}/network-federation/discussions/changes`

Получить ленту изменений обсуждений после курсора (для автообновления).

- Идентификатор в каталоге: `discussions-changes`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `after` | запрос | нет | Курсор из прошлого ответа; без него вернётся текущий курсор без элементов. |
| `limit` | запрос | нет | Сколько элементов, 1–500 (по умолчанию 100). |

Ответ: ok, cursor, items[{id, changeSeq, deleted}], hasMore.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 400 | `NETWORK_DISCUSSION_CURSOR_INVALID` | Недопустимый курсор after. |
| 503 | `NETWORK_DISCUSSIONS_STORAGE_UNAVAILABLE` | Хранилище обсуждений на сервере не готово. |

<a id="discussion-create"></a>
### POST `/api/platform/projects/{projectId}/network-federation/discussions`

Завести обсуждение (замечание) с первым сообщением.

- Идентификатор в каталоге: `discussion-create`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `title` | string | нет | Заголовок, до 200 знаков. Нужен заголовок или текст (хотя бы одно). |
| `text` | string | нет | Описание (первое сообщение), до 4000 знаков; может быть пустым при наличии заголовка. |
| `anchor` | object | да | Привязка. kind: «element» (sourceId, versionId, handle, instancePath?, boundsMm? — [minX, minY, maxX, maxY]), «model-element» (sourceId, versionId, globalId, instancePath?), «area» (minMm и maxMm — по два числа [x, y]) или «point» (pointMm — [x, y]); необязательно camera {centerMm, widthMm, heightMm} и viewpointId. |
| `priority` | string | нет | high, normal или low. |
| `assigneeUserId` | string | нет | Исполнитель — участник проекта. |
| `dueDate` | string | нет | Срок, ГГГГ-ММ-ДД. |
| `labelIds` | string[] | нет | Метки (до 20). |
| `clientRequestId` | string | нет | Ключ повтора до 128 знаков: повтор с ним вернёт уже созданное обсуждение. |
| `context` | object | нет | Снимок вида при создании (до 512 КиБ). |
| `attachmentIds` | string[] | нет | Вложения, загруженные заранее (до 5). |
| `mentionUserIds` | string[] | нет | Упомянутые участники (до 20). |

Ответ: ok, discussion, message.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 400 | `NETWORK_DISCUSSION_TITLE_TOO_LONG` | Заголовок длиннее 200 знаков. |
| 400 | `NETWORK_DISCUSSION_TEXT_TOO_LONG` | Текст длиннее 4000 знаков. |
| 400 | `NETWORK_DISCUSSION_ANCHOR_INVALID` | Недопустимая привязка (anchor). |
| 400 | `NETWORK_DISCUSSION_PRIORITY_INVALID` | priority: high, normal или low. |
| 400 | `NETWORK_DISCUSSION_ASSIGNEE_INVALID` | Исполнитель должен быть участником проекта. |
| 400 | `NETWORK_DISCUSSION_DUE_DATE_INVALID` | dueDate: дата в формате ГГГГ-ММ-ДД. |
| 400 | `NETWORK_DISCUSSION_LABEL_INVALID` | Недопустимая метка. |
| 400 | `NETWORK_DISCUSSION_MENTION_INVALID` | Упоминание — только участник проекта (до 20 в сообщении). |
| 400 | `NETWORK_DISCUSSION_ATTACHMENT_INVALID` | Недопустимое или чужое вложение. |
| 400 | `NETWORK_DISCUSSION_CONTEXT_INVALID` | context — объект допустимой формы. |
| 400 | `NETWORK_DISCUSSION_CLIENT_REQUEST_ID_INVALID` | clientRequestId до 128 знаков. |
| 413 | `NETWORK_DISCUSSION_REQUEST_TOO_LARGE` | Тело запроса больше допустимого (создание и ответ — до 576 КиБ, остальное — до 64 КиБ). |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия вам не видна по роли (черновики и версии на проверке видят координатор, администратор и «Загрузка» своего раздела). |
| 409 | `NETWORK_DISCUSSION_LIMIT` | Достигнут предел обсуждений проекта. |
| 409 | `NETWORK_DISCUSSION_AUTHOR_OPEN_LIMIT` | У автора слишком много открытых обсуждений (до 200). |
| 503 | `NETWORK_DISCUSSIONS_STORAGE_UNAVAILABLE` | Хранилище обсуждений на сервере не готово. |
| 400 | `NETWORK_DISCUSSION_TEXT_REQUIRED` | Не указан текст. |
| 429 | `NETWORK_DISCUSSION_AUTHOR_DAILY_LIMIT` | Автор исчерпал суточный предел сообщений (2000). |
| 409 | `NETWORK_DISCUSSION_PROJECT_MESSAGE_LIMIT` | В проекте предельное число сообщений. |

Примечания: Безопасно повторять с одним clientRequestId. Обсуждения видят только те, чей файл-источник вам виден по роли.

<a id="discussion-read"></a>
### GET `/api/platform/projects/{projectId}/network-federation/discussions/{discussionId}`

Открыть обсуждение: заголовок, сообщения, историю.

- Идентификатор в каталоге: `discussion-read`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `discussionId` | путь | да | Идентификатор обсуждения. |
| `offset` | запрос | нет | Сколько сообщений пропустить. |
| `limit` | запрос | нет | Сколько вернуть, до 200 (по умолчанию 100). |

Ответ: ok, discussion, messages{total, offset, limit, items[]}, events[], eventsTruncated.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_DISCUSSION_NOT_FOUND` | Обсуждение не найдено или не видно вам. |
| 503 | `NETWORK_DISCUSSIONS_STORAGE_UNAVAILABLE` | Хранилище обсуждений на сервере не готово. |

<a id="discussion-update"></a>
### PATCH `/api/platform/projects/{projectId}/network-federation/discussions/{discussionId}`

Изменить обсуждение: статус, заголовок, приоритет, исполнителя, срок, метки.

- Идентификатор в каталоге: `discussion-update`
- Кто может: Автор обсуждения, координатор, администратор; «Загрузка» — по обсуждениям файлов своих разделов (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `discussionId` | путь | да | Идентификатор обсуждения. |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `rowVersion` | integer | да | Версия обсуждения из последнего ответа. |
| `status` | string | нет | open, in_progress, review, resolved. |
| `title` | string | нет | Новый заголовок. |
| `priority` | string\|null | нет | high, normal, low; null — снять. |
| `assigneeUserId` | string\|null | нет | Исполнитель; null — снять. |
| `dueDate` | string\|null | нет | ГГГГ-ММ-ДД; null — снять. |
| `labelIds` | string[]\|null | нет | Метки целиком; null — снять все. |

Ответ: ok, discussion.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_DISCUSSION_ROW_VERSION_REQUIRED` | Не передан rowVersion (≥ 1) — версия обсуждения или сообщения из последнего ответа. |
| 409 | `NETWORK_DISCUSSION_ROW_VERSION_CONFLICT` | Обсуждение или сообщение изменили: перечитать и повторить. |
| 400 | `NETWORK_DISCUSSION_PATCH_EMPTY` | В PATCH нет ни одного изменения. |
| 403 | `NETWORK_DISCUSSION_MANAGE_DENIED` | Менять обсуждение может автор, координатор, администратор и «Загрузка» раздела файла. |
| 404 | `NETWORK_DISCUSSION_NOT_FOUND` | Обсуждение не найдено или не видно вам. |
| 400 | `NETWORK_DISCUSSION_STATUS_INVALID` | status: open, in_progress, review или resolved. |
| 400 | `NETWORK_DISCUSSION_PRIORITY_INVALID` | priority: high, normal или low. |
| 400 | `NETWORK_DISCUSSION_ASSIGNEE_INVALID` | Исполнитель должен быть участником проекта. |
| 400 | `NETWORK_DISCUSSION_DUE_DATE_INVALID` | dueDate: дата в формате ГГГГ-ММ-ДД. |
| 400 | `NETWORK_DISCUSSION_LABEL_INVALID` | Недопустимая метка. |
| 400 | `NETWORK_DISCUSSION_TITLE_INVALID` | Недопустимый заголовок. |
| 400 | `NETWORK_DISCUSSION_TITLE_TOO_LONG` | Заголовок длиннее 200 знаков. |
| 400 | `NETWORK_DISCUSSION_TITLE_REQUIRED` | Не указан заголовок. |

Примечания: Версия записи — rowVersion из последнего ответа (не версия документа плана): без него 428, при расхождении 409 — перечитать и повторить.

<a id="discussion-delete"></a>
### DELETE `/api/platform/projects/{projectId}/network-federation/discussions/{discussionId}`

Удалить обсуждение.

- Идентификатор в каталоге: `discussion-delete`
- Кто может: Автор (если в обсуждении нет чужих сообщений), координатор и администратор — любое видимое (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `discussionId` | путь | да | Идентификатор обсуждения. |
| `rowVersion` | запрос | да | Версия обсуждения из последнего ответа. |

Ответ: ok, id.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_DISCUSSION_ROW_VERSION_REQUIRED` | Не передан rowVersion (≥ 1) — версия обсуждения или сообщения из последнего ответа. |
| 409 | `NETWORK_DISCUSSION_ROW_VERSION_CONFLICT` | Обсуждение или сообщение изменили: перечитать и повторить. |
| 403 | `NETWORK_DISCUSSION_DELETE_DENIED` | Удалить обсуждение может автор, координатор или администратор. |
| 409 | `NETWORK_DISCUSSION_HAS_FOREIGN_REPLIES` | В обсуждении есть сообщения других людей: автор его удалить не может. |
| 404 | `NETWORK_DISCUSSION_NOT_FOUND` | Обсуждение не найдено или не видно вам. |

Примечания: Версия записи — rowVersion из последнего ответа (не версия документа плана): без него 428, при расхождении 409 — перечитать и повторить.

<a id="discussion-message-post"></a>
### POST `/api/platform/projects/{projectId}/network-federation/discussions/{discussionId}/messages`

Ответить в обсуждении.

- Идентификатор в каталоге: `discussion-message-post`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `discussionId` | путь | да | Идентификатор обсуждения. |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `text` | string | да | Текст ответа, до 4000 знаков. |
| `attachmentIds` | string[] | нет | Вложения (до 5). |
| `mentionUserIds` | string[] | нет | Упомянутые участники (до 20). |
| `context` | object | нет | Текущий вид (до 512 КиБ). |

Ответ: ok, discussion, message.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_DISCUSSION_NOT_FOUND` | Обсуждение не найдено или не видно вам. |
| 400 | `NETWORK_DISCUSSION_TEXT_REQUIRED` | Не указан текст. |
| 400 | `NETWORK_DISCUSSION_TEXT_INVALID` | Недопустимый текст. |
| 400 | `NETWORK_DISCUSSION_TEXT_TOO_LONG` | Текст длиннее 4000 знаков. |
| 400 | `NETWORK_DISCUSSION_ATTACHMENT_INVALID` | Недопустимое или чужое вложение. |
| 400 | `NETWORK_DISCUSSION_ATTACHMENTS_TOO_MANY` | Больше 5 вложений в сообщении. |
| 400 | `NETWORK_DISCUSSION_MENTION_INVALID` | Упоминание — только участник проекта (до 20 в сообщении). |
| 400 | `NETWORK_DISCUSSION_CONTEXT_INVALID` | context — объект допустимой формы. |
| 409 | `NETWORK_DISCUSSION_MESSAGE_LIMIT` | В обсуждении предельное число сообщений (1000). |
| 409 | `NETWORK_DISCUSSION_PROJECT_MESSAGE_LIMIT` | В проекте предельное число сообщений. |
| 429 | `NETWORK_DISCUSSION_AUTHOR_DAILY_LIMIT` | Автор исчерпал суточный предел сообщений (2000). |
| 413 | `NETWORK_DISCUSSION_REQUEST_TOO_LARGE` | Тело запроса больше допустимого (создание и ответ — до 576 КиБ, остальное — до 64 КиБ). |

Примечания: Повтор запроса создаст второй ответ: не повторяйте вслепую.

<a id="discussion-message-edit"></a>
### PATCH `/api/platform/projects/{projectId}/network-federation/discussions/{discussionId}/messages/{messageId}`

Исправить своё сообщение.

- Идентификатор в каталоге: `discussion-message-edit`
- Кто может: Только автор сообщения (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `discussionId` | путь | да | Идентификатор обсуждения. |
| `messageId` | путь | да | Идентификатор сообщения обсуждения. |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `text` | string | да | Новый текст. |
| `rowVersion` | integer | да | Версия сообщения из последнего ответа. |

Ответ: ok, discussion, message.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_DISCUSSION_ROW_VERSION_REQUIRED` | Не передан rowVersion (≥ 1) — версия обсуждения или сообщения из последнего ответа. |
| 409 | `NETWORK_DISCUSSION_ROW_VERSION_CONFLICT` | Обсуждение или сообщение изменили: перечитать и повторить. |
| 403 | `NETWORK_DISCUSSION_MESSAGE_EDIT_DENIED` | Править сообщение может только его автор. |
| 404 | `NETWORK_DISCUSSION_MESSAGE_NOT_FOUND` | Сообщение не найдено. |
| 409 | `NETWORK_DISCUSSION_MESSAGE_DELETED` | Сообщение уже удалено. |
| 400 | `NETWORK_DISCUSSION_TEXT_REQUIRED` | Не указан текст. |
| 400 | `NETWORK_DISCUSSION_TEXT_TOO_LONG` | Текст длиннее 4000 знаков. |

Примечания: Версия записи — rowVersion из последнего ответа (не версия документа плана): без него 428, при расхождении 409 — перечитать и повторить.

<a id="discussion-message-delete"></a>
### DELETE `/api/platform/projects/{projectId}/network-federation/discussions/{discussionId}/messages/{messageId}`

Удалить сообщение.

- Идентификатор в каталоге: `discussion-message-delete`
- Кто может: Автор сообщения и администратор (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `discussionId` | путь | да | Идентификатор обсуждения. |
| `messageId` | путь | да | Идентификатор сообщения обсуждения. |
| `rowVersion` | запрос | да | Версия сообщения из последнего ответа. |

Ответ: ok, discussion, message.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_DISCUSSION_ROW_VERSION_REQUIRED` | Не передан rowVersion (≥ 1) — версия обсуждения или сообщения из последнего ответа. |
| 409 | `NETWORK_DISCUSSION_ROW_VERSION_CONFLICT` | Обсуждение или сообщение изменили: перечитать и повторить. |
| 403 | `NETWORK_DISCUSSION_MESSAGE_DELETE_DENIED` | Удалить сообщение может автор или администратор. |
| 404 | `NETWORK_DISCUSSION_MESSAGE_NOT_FOUND` | Сообщение не найдено. |
| 409 | `NETWORK_DISCUSSION_MESSAGE_DELETED` | Сообщение уже удалено. |

Примечания: Версия записи — rowVersion из последнего ответа (не версия документа плана): без него 428, при расхождении 409 — перечитать и повторить.

<a id="discussion-attachment-download"></a>
### GET `/api/platform/projects/{projectId}/network-federation/discussions/{discussionId}/attachments/{attachmentId}`

Скачать вложение обсуждения.

- Идентификатор в каталоге: `discussion-attachment-download`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `discussionId` | путь | да | Идентификатор обсуждения. |
| `attachmentId` | путь | да | Идентификатор вложения. |

Ответ: Файл вложения. Типы png, jpeg, gif, webp, pdf отдаются как есть, остальные — как application/octet-stream.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_DISCUSSION_NOT_FOUND` | Обсуждение не найдено или не видно вам. |
| 400 | `NETWORK_DISCUSSION_ATTACHMENT_INVALID` | Недопустимое или чужое вложение. |

<a id="discussion-attachment-upload"></a>
### POST `/api/platform/projects/{projectId}/network-federation/discussion-attachments`

Загрузить вложение до отправки сообщения (затем его идентификатор указывают в attachmentIds).

- Идентификатор в каталоге: `discussion-attachment-upload`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `X-File-Name` | заголовок | да | Имя файла, закодированное как URL-кодировка UTF-8. |
| `Content-Type` | заголовок | да | Тип файла (по умолчанию application/octet-stream). |

Тело запроса: двоичные данные файла (`application/octet-stream`).

Ответ: ok, attachment{id, fileName, contentType, bytes, …}.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 413 | `NETWORK_DISCUSSION_ATTACHMENT_TOO_LARGE` | Вложение больше 25 МиБ. |
| 400 | `NETWORK_DISCUSSION_ATTACHMENT_INVALID` | Недопустимое или чужое вложение. |
| 503 | `NETWORK_DISCUSSIONS_STORAGE_UNAVAILABLE` | Хранилище обсуждений на сервере не готово. |

Примечания: До 25 МиБ на файл; у человека не более 20 неприкреплённых вложений.

<a id="discussion-attachment-delete"></a>
### DELETE `/api/platform/projects/{projectId}/network-federation/discussion-attachments/{attachmentId}`

Удалить загруженное, но ещё не отправленное вложение.

- Идентификатор в каталоге: `discussion-attachment-delete`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `attachmentId` | путь | да | Идентификатор вложения. |

Ответ: ok, id.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_DISCUSSION_ATTACHMENT_NOT_FOUND` | Вложение не найдено (в том числе чужое). |
| 409 | `NETWORK_DISCUSSION_ATTACHMENT_BOUND` | Вложение уже прикреплено к сообщению. |

Примечания: Удаляется только своё вложение, ещё не прикреплённое к сообщению; на чужое отвечает 404.

<a id="discussion-labels-list"></a>
### GET `/api/platform/projects/{projectId}/network-federation/discussion-labels`

Получить справочник меток обсуждений.

- Идентификатор в каталоге: `discussion-labels-list`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Ответ: ok, items[], canManage.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 503 | `NETWORK_DISCUSSIONS_STORAGE_UNAVAILABLE` | Хранилище обсуждений на сервере не готово. |

<a id="discussion-label-create"></a>
### POST `/api/platform/projects/{projectId}/network-federation/discussion-labels`

Создать метку обсуждений.

- Идентификатор в каталоге: `discussion-label-create`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `name` | string | да | Название, до 60 знаков. |
| `color` | string | нет | Цвет; допустимые значения уточняются. |

Ответ: ok, label.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_DISCUSSION_LABEL_MANAGE_DENIED` | Метками управляют координатор и администратор. |
| 400 | `NETWORK_DISCUSSION_LABEL_INVALID` | Недопустимая метка. |

Примечания: В проекте не более 100 меток.

<a id="discussion-label-update"></a>
### PATCH `/api/platform/projects/{projectId}/network-federation/discussion-labels/{labelId}`

Изменить метку обсуждений.

- Идентификатор в каталоге: `discussion-label-update`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `labelId` | путь | да | Идентификатор метки обсуждений. |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `name` | string | нет | Новое название. |
| `color` | string | нет | Новый цвет. |

Ответ: ok, label.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_DISCUSSION_LABEL_MANAGE_DENIED` | Метками управляют координатор и администратор. |
| 400 | `NETWORK_DISCUSSION_LABEL_INVALID` | Недопустимая метка. |

<a id="discussion-label-delete"></a>
### DELETE `/api/platform/projects/{projectId}/network-federation/discussion-labels/{labelId}`

Удалить метку обсуждений.

- Идентификатор в каталоге: `discussion-label-delete`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `labelId` | путь | да | Идентификатор метки обсуждений. |

Ответ: ok, id.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_DISCUSSION_LABEL_MANAGE_DENIED` | Метками управляют координатор и администратор. |
| 400 | `NETWORK_DISCUSSION_LABEL_INVALID` | Недопустимая метка. |

## Виды

<a id="display-configs-list"></a>
### GET `/api/platform/projects/{projectId}/network-federation/display-configurations`

Получить список конфигураций показа (личных и общих).

- Идентификатор в каталоге: `display-configs-list`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `offset` | запрос | нет | Сколько пропустить. |
| `limit` | запрос | нет | Сколько вернуть. |

Ответ: ok, total, offset, limit (по умолчанию 50), canShare, items[] — краткие описания конфигураций.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 503 | `NETWORK_VIEWS_STORAGE_UNAVAILABLE` | Хранилище видов на сервере не готово. |

<a id="display-config-read"></a>
### GET `/api/platform/projects/{projectId}/network-federation/display-configurations/{configurationId}`

Прочитать конфигурацию показа.

- Идентификатор в каталоге: `display-config-read`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `configurationId` | путь | да | Идентификатор конфигурации показа. |

Ответ: ok, displayConfiguration.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_DISPLAY_CONFIGURATION_NOT_FOUND` | Конфигурация показа не найдена. |
| 503 | `NETWORK_VIEWS_STORAGE_UNAVAILABLE` | Хранилище видов на сервере не готово. |

<a id="display-config-create"></a>
### POST `/api/platform/projects/{projectId}/network-federation/display-configurations`

Сохранить конфигурацию показа.

- Идентификатор в каталоге: `display-config-create`
- Кто может: Личную — любой участник; общую (shared=true) — участник с правом записи и координатор (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `name` | string | да | Название. |
| `shared` | boolean | нет | Общая (по умолчанию false — личная). |
| `items` | object[] | нет | Показ: {targetKind, targetId, visible?, tint?} — по элементу на раздел, файл, модель или слой. tint: #rrggbb — свой цвет в этом виде; original — в этом виде явно исходные цвета (кроме слоя); null или нет поля — как в проекте (цвет раздела по умолчанию). |
| `isolation` | object | нет | Изоляция: {targetKind, targetId}. |
| `enabledModels` | string[] | нет | Включённые модели. |
| `drawings` | object | нет | Отличия вида от проекта по чертежам: {styles[], disciplineOrder[], drawingOrder{}}. disciplineOrder — разделы сверху вниз, если в виде поменяли порядок разделов; drawingOrder — по id раздела его файлы сверху вниз, если поменяли порядок внутри раздела; нет поля — порядок проекта. Id без повторов, не больше 512 в каждом поле. Прежний плоский order принимается, но интерфейс его не читает. |
| `colors` | string | нет | «original» — исходные цвета; иначе цвета разделов. |

Ответ: ok, displayConfiguration (с rowVersion).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 400 | `NETWORK_VIEW_NAME_REQUIRED` | Не указано название. |
| 400 | `NETWORK_VIEW_NAME_INVALID` | Недопустимое название. |
| 400 | `NETWORK_VIEW_NAME_TOO_LONG` | Название слишком длинное. |
| 403 | `NETWORK_VIEW_SHARE_DENIED` | Общие элементы создают участники с правом записи и координатор; переносит между личными и общими только автор. |
| 409 | `NETWORK_DISPLAY_CONFIGURATION_LIMIT` | Достигнут предел общих конфигураций. |
| 409 | `NETWORK_DISPLAY_CONFIGURATION_PERSONAL_LIMIT` | Достигнут предел личных конфигураций. |
| 400 | `NETWORK_DISPLAY_ITEMS_INVALID` | Недопустимые items показа. |
| 400 | `NETWORK_DISPLAY_STATE_TOO_LARGE` | Состояние показа слишком большое. |
| 503 | `NETWORK_VIEWS_STORAGE_UNAVAILABLE` | Хранилище видов на сервере не готово. |

Примечания: Вложенные объекты показа проще всего копировать из ответа чтения.

<a id="display-config-update"></a>
### PUT `/api/platform/projects/{projectId}/network-federation/display-configurations/{configurationId}`

Заменить конфигурацию показа целиком.

- Идентификатор в каталоге: `display-config-update`
- Кто может: Личную правит автор; общую — автор с правом записи, координатор, администратор (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `configurationId` | путь | да | Идентификатор конфигурации показа. |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `name` | string | да | Название. |
| `shared` | boolean | да | Общая или личная (обязателен: PUT заменяет целиком). |
| `rowVersion` | integer | да | Версия из последнего ответа. |
| `items` | object[] | нет | Показ: {targetKind, targetId, visible?, tint?} — по элементу на раздел, файл, модель или слой. tint: #rrggbb — свой цвет в этом виде; original — в этом виде явно исходные цвета (кроме слоя); null или нет поля — как в проекте (цвет раздела по умолчанию). |
| `isolation` | object | нет | Изоляция: {targetKind, targetId}. |
| `enabledModels` | string[] | нет | Включённые модели. |
| `drawings` | object | нет | Отличия вида от проекта по чертежам: {styles[], disciplineOrder[], drawingOrder{}}, как при создании. |
| `colors` | string | нет | Режим цветов. |

Ответ: ok, displayConfiguration.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_VIEW_ROW_VERSION_REQUIRED` | Не передан rowVersion (≥ 1) — версия из последнего ответа. |
| 409 | `NETWORK_VIEW_ROW_VERSION_CONFLICT` | Элемент изменили: перечитать и повторить. |
| 400 | `NETWORK_VIEW_SHARED_REQUIRED` | Нужен признак shared (true/false). |
| 403 | `NETWORK_VIEW_EDIT_DENIED` | Личное меняет автор; общее — автор с правом записи, координатор или администратор. |
| 403 | `NETWORK_VIEW_SHARE_DENIED` | Общие элементы создают участники с правом записи и координатор; переносит между личными и общими только автор. |
| 404 | `NETWORK_DISPLAY_CONFIGURATION_NOT_FOUND` | Конфигурация показа не найдена. |
| 409 | `NETWORK_VIEW_CONCURRENT_CHANGE` | Параллельная запись в хранилище, ничего не записано: повторить тот же запрос. |

Примечания: Версия записи — rowVersion из последнего ответа (не версия документа плана): без него 428, при расхождении 409 — перечитать и повторить.

<a id="display-config-delete"></a>
### DELETE `/api/platform/projects/{projectId}/network-federation/display-configurations/{configurationId}`

Удалить конфигурацию показа.

- Идентификатор в каталоге: `display-config-delete`
- Кто может: Как для правки: личную — автор; общую — автор с правом записи, координатор, администратор (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `configurationId` | путь | да | Идентификатор конфигурации показа. |
| `rowVersion` | запрос | да | Версия из последнего ответа. |

Ответ: ok, id.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_VIEW_ROW_VERSION_REQUIRED` | Не передан rowVersion (≥ 1) — версия из последнего ответа. |
| 409 | `NETWORK_VIEW_ROW_VERSION_CONFLICT` | Элемент изменили: перечитать и повторить. |
| 403 | `NETWORK_VIEW_EDIT_DENIED` | Личное меняет автор; общее — автор с правом записи, координатор или администратор. |
| 404 | `NETWORK_DISPLAY_CONFIGURATION_NOT_FOUND` | Конфигурация показа не найдена. |

Примечания: Версия записи — rowVersion из последнего ответа (не версия документа плана): без него 428, при расхождении 409 — перечитать и повторить.

<a id="viewpoints-list"></a>
### GET `/api/platform/projects/{projectId}/network-federation/viewpoints`

Получить список видов (сохранённых точек обзора).

- Идентификатор в каталоге: `viewpoints-list`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `offset` | запрос | нет | Сколько пропустить. |
| `limit` | запрос | нет | Сколько вернуть. |

Ответ: Страница: ok, total, offset, limit, items[] (с hasPreview), canShare, canSetHome.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 503 | `NETWORK_VIEWS_STORAGE_UNAVAILABLE` | Хранилище видов на сервере не готово. |

<a id="viewpoint-home-read"></a>
### GET `/api/platform/projects/{projectId}/network-federation/viewpoints/home`

Узнать начальный вид сводной картины.

- Идентификатор в каталоге: `viewpoint-home-read`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `compositionKind` | запрос | нет | «working» (по умолчанию) или «accepted». |

Ответ: ok, viewpoint — вид или null, если начального нет.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 400 | `NETWORK_COMPOSITION_KIND_INVALID` | compositionKind: «working» или «accepted». |

<a id="viewpoint-home-clear"></a>
### DELETE `/api/platform/projects/{projectId}/network-federation/viewpoints/home`

Снять начальный вид сводной картины.

- Идентификатор в каталоге: `viewpoint-home-clear`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `compositionKind` | запрос | нет | «working» (по умолчанию) или «accepted». |

Ответ: ok, compositionKind, viewpointId (снятый).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_VIEW_HOME_DENIED` | Начальный вид задаёт координатор. |
| 400 | `NETWORK_COMPOSITION_KIND_INVALID` | compositionKind: «working» или «accepted». |
| 409 | `NETWORK_VIEW_HOME_CONCURRENT_CHANGE` | Начальный вид изменили параллельно: повторить. |

<a id="viewpoint-read"></a>
### GET `/api/platform/projects/{projectId}/network-federation/viewpoints/{viewpointId}`

Прочитать вид.

- Идентификатор в каталоге: `viewpoint-read`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `viewpointId` | путь | да | Идентификатор вида (viewpoint_…). |

Ответ: ok, viewpoint (камера, показ, rowVersion…).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_VIEWPOINT_NOT_FOUND` | Вид не найден. |
| 503 | `NETWORK_VIEWS_STORAGE_UNAVAILABLE` | Хранилище видов на сервере не готово. |

<a id="viewpoint-create"></a>
### POST `/api/platform/projects/{projectId}/network-federation/viewpoints`

Сохранить вид: камеру и, при желании, показ.

- Идентификатор в каталоге: `viewpoint-create`
- Кто может: Личный — любой участник; общий (shared=true) — участник с правом записи и координатор (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `name` | string | да | Название. |
| `shared` | boolean | нет | Общий (по умолчанию false). |
| `camera` | object | да | Камера: {centerMm: [x, y], widthMm, heightMm} — видимый прямоугольник плоскости проекта в миллиметрах. |
| `compositionKind` | string | нет | «working» или «accepted». |
| `snapshotId` | string | нет | Связанный снимок. |
| `displayConfigurationId` | string | нет | Связанная конфигурация показа. |
| `display` | object | нет | Показ (items, isolation, enabledModels, drawings, colors); drawings — как у конфигурации показа. |
| `folder` | string | нет | Папка. |
| `preview` | string | нет | Картинка предпросмотра. |
| `rememberDisplay` | boolean | нет | false — «только камера». |

Ответ: ok, viewpoint.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 400 | `NETWORK_VIEW_NAME_REQUIRED` | Не указано название. |
| 400 | `NETWORK_VIEW_NAME_INVALID` | Недопустимое название. |
| 400 | `NETWORK_VIEW_NAME_TOO_LONG` | Название слишком длинное. |
| 400 | `NETWORK_VIEWPOINT_CAMERA_INVALID` | Недопустимая камера вида. |
| 403 | `NETWORK_VIEW_SHARE_DENIED` | Общие элементы создают участники с правом записи и координатор; переносит между личными и общими только автор. |
| 409 | `NETWORK_VIEWPOINT_LIMIT` | Достигнут предел общих видов. |
| 409 | `NETWORK_VIEWPOINT_PERSONAL_LIMIT` | Достигнут предел личных видов. |
| 400 | `NETWORK_VIEW_LINK_INVALID` | Недопустимая связь вида (снимок или конфигурация). |
| 400 | `NETWORK_VIEW_FOLDER_INVALID` | Недопустимое название папки. |
| 400 | `NETWORK_VIEW_PREVIEW_INVALID` | Недопустимая картинка предпросмотра. |
| 503 | `NETWORK_VIEWS_STORAGE_UNAVAILABLE` | Хранилище видов на сервере не готово. |

Примечания: Показ (display) проще всего копировать из ответа чтения; камера — {centerMm, widthMm, heightMm}.

<a id="viewpoint-update"></a>
### PUT `/api/platform/projects/{projectId}/network-federation/viewpoints/{viewpointId}`

Заменить вид целиком.

- Идентификатор в каталоге: `viewpoint-update`
- Кто может: Личный правит автор; общий — автор с правом записи, координатор, администратор (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `viewpointId` | путь | да | Идентификатор вида (viewpoint_…). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `name` | string | да | Название. |
| `shared` | boolean | да | Общий или личный (обязателен). |
| `rowVersion` | integer | да | Версия из последнего ответа. |
| `camera` | object | да | Камера: {centerMm: [x, y], widthMm, heightMm} — видимый прямоугольник плоскости проекта в миллиметрах. |
| `compositionKind` | string | нет | working\|accepted. |
| `snapshotId` | string | нет | Снимок. |
| `displayConfigurationId` | string | нет | Конфигурация показа. |
| `display` | object | нет | Показ. |
| `folder` | string | нет | Папка: не передан — сохраняется, пустая строка — убрать. |
| `preview` | string | нет | Картинка: не передана — сохраняется, пустая строка — убрать. |
| `rememberDisplay` | boolean | нет | Не передан — сохраняется прежнее. |

Ответ: ok, viewpoint.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_VIEW_ROW_VERSION_REQUIRED` | Не передан rowVersion (≥ 1) — версия из последнего ответа. |
| 409 | `NETWORK_VIEW_ROW_VERSION_CONFLICT` | Элемент изменили: перечитать и повторить. |
| 400 | `NETWORK_VIEW_SHARED_REQUIRED` | Нужен признак shared (true/false). |
| 403 | `NETWORK_VIEW_EDIT_DENIED` | Личное меняет автор; общее — автор с правом записи, координатор или администратор. |
| 403 | `NETWORK_VIEW_SHARE_DENIED` | Общие элементы создают участники с правом записи и координатор; переносит между личными и общими только автор. |
| 404 | `NETWORK_VIEWPOINT_NOT_FOUND` | Вид не найден. |
| 400 | `NETWORK_VIEWPOINT_CAMERA_INVALID` | Недопустимая камера вида. |
| 409 | `NETWORK_VIEW_CONCURRENT_CHANGE` | Параллельная запись в хранилище, ничего не записано: повторить тот же запрос. |

Примечания: Версия записи — rowVersion из последнего ответа (не версия документа плана): без него 428, при расхождении 409 — перечитать и повторить.

<a id="viewpoint-share"></a>
### PATCH `/api/platform/projects/{projectId}/network-federation/viewpoints/{viewpointId}`

Сделать вид общим или личным (только автор).

- Идентификатор в каталоге: `viewpoint-share`
- Кто может: Автор вида; сделать общим — при праве записи (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `viewpointId` | путь | да | Идентификатор вида (viewpoint_…). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `shared` | boolean | да | Общий или личный. |
| `rowVersion` | integer | да | Версия из последнего ответа. |

Ответ: ok, viewpoint.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_VIEW_ROW_VERSION_REQUIRED` | Не передан rowVersion (≥ 1) — версия из последнего ответа. |
| 409 | `NETWORK_VIEW_ROW_VERSION_CONFLICT` | Элемент изменили: перечитать и повторить. |
| 400 | `NETWORK_VIEW_SHARED_REQUIRED` | Нужен признак shared (true/false). |
| 403 | `NETWORK_VIEW_SHARE_DENIED` | Общие элементы создают участники с правом записи и координатор; переносит между личными и общими только автор. |
| 403 | `NETWORK_VIEW_EDIT_DENIED` | Личное меняет автор; общее — автор с правом записи, координатор или администратор. |
| 404 | `NETWORK_VIEWPOINT_NOT_FOUND` | Вид не найден. |

Примечания: Версия записи — rowVersion из последнего ответа (не версия документа плана): без него 428, при расхождении 409 — перечитать и повторить.

<a id="viewpoint-delete"></a>
### DELETE `/api/platform/projects/{projectId}/network-federation/viewpoints/{viewpointId}`

Удалить вид.

- Идентификатор в каталоге: `viewpoint-delete`
- Кто может: Как для правки (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `viewpointId` | путь | да | Идентификатор вида (viewpoint_…). |
| `rowVersion` | запрос | да | Версия из последнего ответа. |

Ответ: ok, id.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_VIEW_ROW_VERSION_REQUIRED` | Не передан rowVersion (≥ 1) — версия из последнего ответа. |
| 409 | `NETWORK_VIEW_ROW_VERSION_CONFLICT` | Элемент изменили: перечитать и повторить. |
| 403 | `NETWORK_VIEW_EDIT_DENIED` | Личное меняет автор; общее — автор с правом записи, координатор или администратор. |
| 404 | `NETWORK_VIEWPOINT_NOT_FOUND` | Вид не найден. |

Примечания: Версия записи — rowVersion из последнего ответа (не версия документа плана): без него 428, при расхождении 409 — перечитать и повторить.

<a id="viewpoint-preview"></a>
### GET `/api/platform/projects/{projectId}/network-federation/viewpoints/{viewpointId}/preview`

Получить картинку предпросмотра вида.

- Идентификатор в каталоге: `viewpoint-preview`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `viewpointId` | путь | да | Идентификатор вида (viewpoint_…). |

Ответ: Изображение; ETag, If-None-Match (304).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_VIEWPOINT_NOT_FOUND` | Вид не найден. |
| 404 | `NETWORK_VIEWPOINT_PREVIEW_NOT_FOUND` | У вида нет картинки. |

<a id="viewpoint-home-set"></a>
### PUT `/api/platform/projects/{projectId}/network-federation/viewpoints/{viewpointId}/home`

Назначить вид начальным для сводной картины.

- Идентификатор в каталоге: `viewpoint-home-set`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `viewpointId` | путь | да | Идентификатор вида (viewpoint_…). |
| `rowVersion` | запрос | нет | Версия вида: необязателен, если передан — закрепляет версию. |

Ответ: ok, viewpoint.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_VIEW_HOME_DENIED` | Начальный вид задаёт координатор. |
| 409 | `NETWORK_VIEW_HOME_SHARED_REQUIRED` | Начальным может быть только общий вид. |
| 409 | `NETWORK_VIEW_HOME_SNAPSHOT_NOT_ALLOWED` | Вид со снимком не может быть начальным. |
| 409 | `NETWORK_VIEW_ROW_VERSION_CONFLICT` | Элемент изменили: перечитать и повторить. |
| 404 | `NETWORK_VIEWPOINT_NOT_FOUND` | Вид не найден. |
| 409 | `NETWORK_VIEW_HOME_CONCURRENT_CHANGE` | Начальный вид изменили параллельно: повторить. |

Примечания: rowVersion необязателен: если передан, закрепляет версию вида. Начальным может быть только общий вид без снимка. Ответ: ok, viewpoint; rowVersion вида не меняется.

<a id="viewpoint-folder-rename"></a>
### POST `/api/platform/projects/{projectId}/network-federation/viewpoint-folders/rename`

Переименовать папку видов.

- Идентификатор в каталоге: `viewpoint-folder-rename`
- Кто может: Меняются те виды секции (личной или общей), которые вы вправе менять (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `from` | string | да | Текущее название папки. |
| `to` | string | да | Новое название. |
| `shared` | boolean | да | Общие виды (true) или личные (false). |

Ответ: ok, changed, skipped, overLimit.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 400 | `NETWORK_VIEW_SHARED_REQUIRED` | Нужен признак shared (true/false). |
| 400 | `NETWORK_VIEW_FOLDER_REQUIRED` | Не указана папка. |
| 400 | `NETWORK_VIEW_FOLDER_INVALID` | Недопустимое название папки. |
| 400 | `NETWORK_VIEW_FOLDER_TOO_LONG` | Название папки слишком длинное. |
| 403 | `NETWORK_VIEW_SHARE_DENIED` | Общие элементы создают участники с правом записи и координатор; переносит между личными и общими только автор. |

<a id="viewpoint-folder-delete"></a>
### POST `/api/platform/projects/{projectId}/network-federation/viewpoint-folders/delete`

Удалить папку видов (виды остаются без папки или удаляются).

- Идентификатор в каталоге: `viewpoint-folder-delete`
- Кто может: Затрагиваются виды, которые вы вправе менять (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `name` | string | да | Название папки. |
| `shared` | boolean | да | Общие виды или личные. |
| `deleteViews` | boolean | нет | true — удалить и сами виды (по умолчанию false). |

Ответ: ok, changed, skipped, overLimit.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 400 | `NETWORK_VIEW_SHARED_REQUIRED` | Нужен признак shared (true/false). |
| 400 | `NETWORK_VIEW_FOLDER_REQUIRED` | Не указана папка. |
| 400 | `NETWORK_VIEW_FOLDER_INVALID` | Недопустимое название папки. |
| 403 | `NETWORK_VIEW_SHARE_DENIED` | Общие элементы создают участники с правом записи и координатор; переносит между личными и общими только автор. |

<a id="viewpoint-folder-visibility"></a>
### POST `/api/platform/projects/{projectId}/network-federation/viewpoint-folders/visibility`

Сделать виды папки общими или личными.

- Идентификатор в каталоге: `viewpoint-folder-visibility`
- Кто может: Только виды, автором которых вы являетесь; общими — при праве записи (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `name` | string | да | Название папки. |
| `shared` | boolean | да | Целевой доступ: общие (true) или личные (false). |

Ответ: ok, changed, skipped, overLimit.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 400 | `NETWORK_VIEW_SHARED_REQUIRED` | Нужен признак shared (true/false). |
| 400 | `NETWORK_VIEW_FOLDER_REQUIRED` | Не указана папка. |
| 400 | `NETWORK_VIEW_FOLDER_INVALID` | Недопустимое название папки. |
| 403 | `NETWORK_VIEW_SHARE_DENIED` | Общие элементы создают участники с правом записи и координатор; переносит между личными и общими только автор. |

Примечания: Переводит все свои виды папки в общие или личные. skipped — виды, которые вам менять нельзя; overLimit — виды сверх квоты.

## Участники и права

<a id="contractor-create"></a>
### POST `/api/platform/projects/{projectId}/network-federation/contractors`

Завести подрядчика в справочнике сводного плана.

- Идентификатор в каталоге: `contractor-create`
- Кто может: Администратор проекта: владелец проекта или администратор компании проекта. По ключу глобальная роль администратора платформы не действует — только настоящее участие в проекте или администрирование компании проекта (роли: Администратор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `name` | string | да | Название подрядчика (до 240 знаков). |

Ответ: ok, contractor{id, name}.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_ADMIN_REQUIRED` | Нужна роль администратора (где сказано — также координатора). |
| 400 | `NETWORK_CONTRACTOR_NAME_REQUIRED` | Не указано название подрядчика. |
| 409 | `NETWORK_CONTRACTOR_NAME_DUPLICATE` | Подрядчик с таким названием уже есть. |
| 400 | `NETWORK_VALUE_TOO_LONG` | Значение длиннее 240 знаков. |

<a id="grants-list"></a>
### GET `/api/platform/projects/{projectId}/modules/federated-networks/grants`

Получить список участников сводного плана с ролями и разделами.

- Идентификатор в каталоге: `grants-list`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Ответ: ok, actor{role, assignableRoles[]}, items[{userId, username, displayName, organization, external, role (viewer|uploader|coordinator|admin), disciplineIds, notes, editable, removable, accessExpiresAtUtc}].

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_GRANTS_FORBIDDEN` | Права ведут администратор и координатор. |

Примечания: Координатор видит и выдаёт только «Просмотр» и «Загрузку»; администратор — все четыре роли.

<a id="grants-candidates"></a>
### GET `/api/platform/projects/{projectId}/modules/federated-networks/grants/candidates`

Найти, кого можно пригласить: сотрудники компании и известные гости, ещё не участники.

- Идентификатор в каталоге: `grants-candidates`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `q` | запрос | нет | Поиск по имени и логину без учёта регистра. |

Ответ: ok, items[{userId, username, displayName, organization, external}] — до 50.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_GRANTS_FORBIDDEN` | Права ведут администратор и координатор. |

<a id="grant-add"></a>
### POST `/api/platform/projects/{projectId}/modules/federated-networks/grants`

Подключить существующую учётную запись к проекту с ролью и разделами.

- Идентификатор в каталоге: `grant-add`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `username` | string | да | Логин существующей активной учётной записи (до 240 знаков). |
| `role` | string | да | viewer, uploader, coordinator или admin (координатор выдаёт только viewer и uploader). |
| `disciplineIds` | string[] | нет | Разделы — обязательны для роли uploader. |

Ответ: ok, item — строка участника.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_GRANTS_FORBIDDEN` | Права ведут администратор и координатор. |
| 400 | `NETWORK_GRANT_ROLE_INVALID` | role: viewer, uploader, coordinator или admin. |
| 403 | `NETWORK_GRANT_ROLE_FORBIDDEN` | Эту роль или этого участника вам менять нельзя (координатор выдаёт только «Просмотр» и «Загрузка»). |
| 400 | `USERNAME_REQUIRED` | Не указан логин (до 240 знаков). |
| 404 | `WEB_USER_NOT_FOUND` | Активной учётной записи с таким логином нет. |
| 400 | `NETWORK_GRANT_ROLE_EMPLOYEES_ONLY` | Роль «Координатор» и «Администратор» — только сотруднику компании проекта. |
| 409 | `NETWORK_GRANT_COMPANY_ADMIN` | У администратора компании роль идёт от компании: строку не меняют. |
| 409 | `NETWORK_GRANT_ALREADY_MEMBER` | Человек уже участник проекта (в том числе с истёкшим сроком): его строку меняют, а не добавляют. |
| 400 | `NETWORK_GRANT_DISCIPLINES_REQUIRED` | Для роли «Загрузка» нужен хотя бы один раздел. |
| 400 | `NETWORK_ASSIGNMENT_DISCIPLINE_NOT_FOUND` | Раздел из списка не найден или в архиве. |
| 409 | `NETWORK_GRANT_CONFLICT` | Права изменили параллельно: перечитать и повторить. |

Примечания: Учётные записи этим маршрутом не создаются — гостей приглашают маршрутом приглашений.

<a id="grant-update"></a>
### PUT `/api/platform/projects/{projectId}/modules/federated-networks/grants/{userId}`

Сменить роль и разделы участника.

- Идентификатор в каталоге: `grant-update`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `userId` | путь | да | Идентификатор учётной записи участника. |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `role` | string | да | viewer, uploader, coordinator или admin. |
| `disciplineIds` | string[] | нет | Разделы (для uploader — обязательны). |

Ответ: ok, item — строка участника.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_GRANTS_FORBIDDEN` | Права ведут администратор и координатор. |
| 400 | `NETWORK_GRANT_ROLE_INVALID` | role: viewer, uploader, coordinator или admin. |
| 403 | `NETWORK_GRANT_ROLE_FORBIDDEN` | Эту роль или этого участника вам менять нельзя (координатор выдаёт только «Просмотр» и «Загрузка»). |
| 404 | `NETWORK_GRANT_MEMBER_NOT_FOUND` | Участника нет в проекте. |
| 409 | `NETWORK_GRANT_COMPANY_ADMIN` | У администратора компании роль идёт от компании: строку не меняют. |
| 400 | `NETWORK_GRANT_ROLE_EMPLOYEES_ONLY` | Роль «Координатор» и «Администратор» — только сотруднику компании проекта. |
| 400 | `PROJECT_LAST_OWNER_PROTECTED` | Нельзя понизить или убрать последнего владельца проекта. |
| 400 | `NETWORK_GRANT_DISCIPLINES_REQUIRED` | Для роли «Загрузка» нужен хотя бы один раздел. |
| 400 | `NETWORK_ASSIGNMENT_DISCIPLINE_NOT_FOUND` | Раздел из списка не найден или в архиве. |
| 409 | `NETWORK_GRANT_CONFLICT` | Права изменили параллельно: перечитать и повторить. |

Примечания: Безопасно повторять: повтор того же значения ничего не меняет. Понижение роли действует сразу, в том числе на ключи этого человека.

<a id="grant-remove"></a>
### DELETE `/api/platform/projects/{projectId}/modules/federated-networks/grants/{userId}`

Убрать участника из проекта.

- Идентификатор в каталоге: `grant-remove`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `userId` | путь | да | Идентификатор учётной записи участника. |

Ответ: ok, removed.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_GRANTS_FORBIDDEN` | Права ведут администратор и координатор. |
| 403 | `NETWORK_GRANT_ROLE_FORBIDDEN` | Эту роль или этого участника вам менять нельзя (координатор выдаёт только «Просмотр» и «Загрузка»). |
| 404 | `NETWORK_GRANT_MEMBER_NOT_FOUND` | Участника нет в проекте. |
| 409 | `NETWORK_GRANT_COMPANY_ADMIN` | У администратора компании роль идёт от компании: строку не меняют. |
| 400 | `PROJECT_LAST_OWNER_PROTECTED` | Нельзя понизить или убрать последнего владельца проекта. |
| 409 | `NETWORK_GRANT_CONFLICT` | Права изменили параллельно: перечитать и повторить. |

Примечания: Личные виды участника удаляются, общие остаются. Права ключей этого человека на проект удаляются вместе с участием: после повторного приглашения нужен новый ключ.

<a id="member-connect"></a>
### POST `/api/platform/projects/{projectId}/network-federation/members`

Подключить существующего человека к проекту (старый способ; новые программы используют маршруты прав).

- Идентификатор в каталоге: `member-connect`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `username` | string | да | Логин существующей активной учётной записи. |
| `role` | string | да | Роль проекта: viewer или editor. |

Ответ: ok, member{userId, username, displayName, role}, added.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_ADMIN_REQUIRED` | Нужна роль администратора (где сказано — также координатора). |
| 400 | `USERNAME_REQUIRED` | Не указан логин (до 240 знаков). |
| 400 | `PROJECT_MEMBER_ROLE_INVALID` | role: viewer или editor. |
| 404 | `WEB_USER_NOT_FOUND` | Активной учётной записи с таким логином нет. |
| 409 | `PROJECT_MEMBER_ALREADY_EXISTS` | Участник уже есть с другой ролью проекта. |
| 409 | `NETWORK_GRANT_COMPANY_ADMIN` | У администратора компании роль идёт от компании: строку не меняют. |
| 400 | `PROJECT_ID_REQUIRED` | Не указан проект. |

Примечания: Для выдачи ролей сводного плана используйте GET/POST/PUT/DELETE …/modules/federated-networks/grants.

<a id="assignment-put"></a>
### PUT `/api/platform/projects/{projectId}/network-federation/assignments/{userId}`

Назначить участнику разделы, подрядчика и признак координатора (старое окно назначений).

- Идентификатор в каталоге: `assignment-put`
- Кто может: Администратор проекта: владелец проекта или администратор компании проекта. По ключу глобальная роль администратора платформы не действует — только настоящее участие в проекте или администрирование компании проекта (роли: Администратор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `userId` | путь | да | Идентификатор учётной записи участника. |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `disciplineIds` | string[] | нет | Разделы участника. |
| `contractorId` | string | нет | Подрядчик из справочника. |
| `contractorLabel` | string | нет | Подпись подрядчика (если нет в справочнике). |
| `canCoordinate` | boolean | нет | Признак координатора (только сотруднику компании). |

Ответ: ok, assignment{userId, disciplineIds, contractorId, contractorLabel, canCoordinate}.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_ADMIN_REQUIRED` | Нужна роль администратора (где сказано — также координатора). |
| 404 | `NETWORK_ASSIGNMENT_MEMBER_NOT_FOUND` | Участника нет в проекте. |
| 400 | `NETWORK_ASSIGNMENT_USER_REQUIRED` | Не указан участник. |
| 400 | `NETWORK_ASSIGNMENT_DISCIPLINE_NOT_FOUND` | Раздел из списка не найден или в архиве. |
| 400 | `NETWORK_ASSIGNMENT_CONTRACTOR_NOT_FOUND` | Подрядчик не найден. |
| 400 | `NETWORK_GRANT_ROLE_EMPLOYEES_ONLY` | Роль «Координатор» и «Администратор» — только сотруднику компании проекта. |

Примечания: Совместимость со старым окном назначений; роли удобнее выдавать маршрутами прав.

## Приглашения

<a id="invitations-list"></a>
### GET `/api/platform/projects/{projectId}/network-federation/invitations`

Получить список приглашений в проект.

- Идентификатор в каталоге: `invitations-list`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Ответ: ok, items[{id, inviteeLabel, organization, role, disciplineIds, accessDays, status, createdAtUtc, createdBy, expiresAtUtc, acceptedAtUtc, acceptedBy}].

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_ADMIN_REQUIRED` | Нужна роль администратора (где сказано — также координатора). |
| 503 | `INVITATIONS_SCHEMA_NOT_FOUND` | Хранилище приглашений не готово на сервере. |

<a id="invitation-create"></a>
### POST `/api/platform/projects/{projectId}/network-federation/invitations`

Пригласить человека в проект: сервер вернёт одноразовую ссылку-приглашение.

- Идентификатор в каталоге: `invitation-create`
- Кто может: Администратор и координатор. Приглашение даёт только роли viewer и editor с разделами; координаторство не выдаёт (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `inviteeLabel` | string | да | Кого приглашают (подпись, до 240 знаков). |
| `role` | string | да | viewer или editor. |
| `disciplineIds` | string[] | нет | Разделы (активные). |
| `accessDays` | integer | нет | Срок доступа после принятия, 1–3650 дней; без значения — бессрочно. |
| `organization` | string | нет | Организация приглашённого, до 240 знаков. |

Ответ: ok, invitation{id, status, expiresAtUtc, …}, link — относительная ссылка вида /invite/{id}#{секрет}. Секрет возвращается один раз.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_ADMIN_REQUIRED` | Нужна роль администратора (где сказано — также координатора). |
| 400 | `INVITEE_LABEL_REQUIRED` | Не указано, кого приглашают (inviteeLabel, до 240 знаков). |
| 400 | `PROJECT_MEMBER_ROLE_INVALID` | role: viewer или editor. |
| 400 | `INVITATION_ACCESS_DAYS_INVALID` | accessDays: от 1 до 3650. |
| 400 | `INVITATION_ORGANIZATION_TOO_LONG` | Название организации длиннее 240 знаков. |
| 400 | `NETWORK_ASSIGNMENT_DISCIPLINE_NOT_FOUND` | Раздел из списка не найден или в архиве. |
| 503 | `INVITATIONS_SCHEMA_NOT_FOUND` | Хранилище приглашений не готово на сервере. |

Примечания: Приглашение действует 7 дней. Ссылку передают человеку сами: хранить её как секрет. Повтор создаст второе приглашение. Роль приглашения: viewer («Просмотр») или editor («Загрузка», с разделами). Ссылка в ответе относительная: допишите базовый адрес.

<a id="invitation-revoke"></a>
### DELETE `/api/platform/projects/{projectId}/network-federation/invitations/{invitationId}`

Отозвать приглашение, которое ещё не принято.

- Идентификатор в каталоге: `invitation-revoke`
- Кто может: Администратор — любое; координатор — только свои (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `invitationId` | путь | да | Идентификатор приглашения. |

Ответ: ok, invitation (с отметкой отзыва).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_ADMIN_REQUIRED` | Нужна роль администратора (где сказано — также координатора). |
| 404 | `INVITATION_NOT_FOUND` | Приглашение не найдено. |
| 409 | `INVITATION_NOT_PENDING` | Приглашение уже принято или отозвано. |
| 503 | `INVITATIONS_SCHEMA_NOT_FOUND` | Хранилище приглашений не готово на сервере. |

## Ссылки просмотра

<a id="share-links-list"></a>
### GET `/api/platform/projects/{projectId}/network-federation/share-links`

Получить список ссылок «только просмотр» на сводный план.

- Идентификатор в каталоге: `share-links-list`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Ответ: ok, items[{shareId, title, createdAtUtc, createdBy, expiresAtUtc, lastAccessedAtUtc}].

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_ADMIN_REQUIRED` | Нужна роль администратора (где сказано — также координатора). |

<a id="share-link-create"></a>
### POST `/api/platform/projects/{projectId}/network-federation/share-links`

Создать ссылку «только просмотр» на сводный план.

- Идентификатор в каталоге: `share-link-create`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `title` | string | нет | Название ссылки, до 200 знаков (по умолчанию «<проект> · сводный план сетей»). |
| `expiresInDays` | integer\|null | нет | 7, 30, 90 или 365; не передан — 30; null — бессрочно. |

Ответ: ok, link{shareId, title, …}, url — полный адрес ссылки с секретом (возвращается один раз).

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_ADMIN_REQUIRED` | Нужна роль администратора (где сказано — также координатора). |
| 400 | `SHARE_EXPIRY_INVALID` | expiresInDays: 7, 30, 90, 365 или null (бессрочно). |
| 400 | `SHARE_TITLE_TOO_LONG` | Название ссылки длиннее 200 знаков. |
| 429 | `RATE_LIMIT_SHARE_CREATE` | Слишком частое создание ссылок; в теле — retry_after_seconds. |
| 404 | `PROJECT_NOT_FOUND` | Проект не найден (или вне списка ключа). |

Примечания: Секрет ссылки хранить как пароль. При 429 в теле retry_after_seconds.

<a id="share-link-revoke"></a>
### DELETE `/api/platform/projects/{projectId}/network-federation/share-links/{shareId}`

Отозвать ссылку «только просмотр».

- Идентификатор в каталоге: `share-link-revoke`
- Кто может: Администратор и координатор (роли: Администратор, Координатор).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `shareId` | путь | да | Идентификатор ссылки просмотра. |

Ответ: ok.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_ADMIN_REQUIRED` | Нужна роль администратора (где сказано — также координатора). |
| 404 | `SHARE_LINK_NOT_FOUND` | Ссылка не найдена. |

## Архив

<a id="archive-download"></a>
### GET `/api/platform/projects/{projectId}/network-federation/archive`

Скачать ZIP-архив оригиналов актуальных версий — всего плана или одного раздела.

- Идентификатор в каталоге: `archive-download`
- Кто может: Любой участник проекта со сводным планом; состав данных зависит от роли (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта (ключ действует только в проектах из его списка). |
| `disciplineId` | запрос | нет | Только этот раздел; без параметра — все разделы. |

Ответ: ZIP (application/zip), имя — в Content-Disposition. Внутри папки по разделам и оригиналы актуальных версий чертежей и моделей IFC.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 404 | `NETWORK_DISCIPLINE_NOT_FOUND` | Раздел не найден. |

Примечания: Версии, которых роль не видит, в архив не попадают. Ошибка определяется до первого байта (обычный JSON), дальше архив идёт потоком; обрыв потока означает неполный архив — проверяйте ZIP. Ответ не кэшируется.

## Трассы

<a id="routes-read"></a>
### GET `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/routes`

Прочитать последний сохранённый черновик трасс выбранной версии чертежа.

- Идентификатор в каталоге: `routes-read`
- Кто может: Участник с доступом к этой версии чертежа (роли: Администратор, Координатор, Загрузка, Просмотр).
- Ключ: доступен ключам «Чтение» и «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта из списка ключа. |
| `sectionId` | путь | да | Идентификатор файла сводного плана. |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Ответ: draft (черновик или null), placementCurrent (boolean). Обёртки ok нет. Черновик содержит исходный report и отдельные worldSegments, revision и decisions.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия недоступна владельцу ключа. |
| 404 | `NETWORK_SECTION_NOT_FOUND` | Файл не найден. |
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |

Примечания: Чтение не запускает выделение геометрии. placementCurrent проверяет соответствие исходника, единиц, нормализации и текущего размещения. Геометрия report хранится в drawing-wcs-mm, worldSegments — в миллиметрах проекта.

<a id="routes-extract"></a>
### POST `/api/platform/projects/{projectId}/network-federation/sections/{sectionId}/cad-versions/{versionId}/routes`

Выделить и сохранить черновик трасс из исходного чертежа по точным именам слоёв.

- Идентификатор в каталоге: `routes-extract`
- Кто может: Администратор, координатор или исполнитель с правом записи в раздел и доступом к версии (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта из списка ключа. |
| `sectionId` | путь | да | Идентификатор файла сводного плана. |
| `versionId` | путь | да | Идентификатор версии чертежа. |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `placementId` | string | да | Идентификатор текущего размещения версии из маршрута placements. |
| `layers` | string[] | да | От 1 до 64 уникальных точных имён слоёв, каждое непустое и не длиннее 512 знаков. Порядок учитывается при повторе. |
| `expectedDocumentVersion` | integer | да | document.version из последнего GET сводного плана. |

Ответ: Черновик напрямую, без обёртки ok или draft: id, projectId, sectionId, versionId, sourceSha256, sourceUnit, scaleToMm, placement, normalizationProfile, artifactGeneration, algorithmFingerprint, revision, report, worldSegments[], decisions[], createdByUserId, createdAtUtc.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Версия недоступна владельцу ключа. |
| 404 | `NETWORK_SECTION_NOT_FOUND` | Файл не найден. |
| 404 | `NETWORK_CAD_VERSION_NOT_FOUND` | Версия чертежа не найдена. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в раздел. |
| 428 | `NETWORK_DOCUMENT_VERSION_REQUIRED` | Не передан expectedDocumentVersion. |
| 409 | `NETWORK_FEDERATION_DOCUMENT_CONFLICT` | Версия документа изменилась до выделения или во время него. Перечитайте сводный план. |
| 400 | `NETWORK_ROUTE_LAYERS_INVALID` | Список слоёв не соответствует ограничениям. |
| 404 | `NETWORK_PLACEMENT_NOT_FOUND` | placementId отсутствует или указывает на размещение другой версии. |
| 409 | `NETWORK_ROUTE_PLACEMENT_CHANGED` | Размещение перестало быть текущим. |
| 409 | `NETWORK_ROUTE_READER_CHANGED` | Алгоритм изменился во время обработки. |
| 409 | `NETWORK_ROUTE_SOURCE_MISMATCH` | Отчёт не соответствует исходной версии чертежа. |
| 409 | `CAD_ROUTE_IMPORT_NOT_SUCCEEDED` | Импорт исходного чертежа не завершён успешно. |
| 422 | `NETWORK_ROUTE_GEOMETRY_INVALID` | Отчёт содержит некорректные координаты или дуги. |
| 422 | `NETWORK_ROUTE_ID_INVALID` | Идентификатор кандидата отсутствует или повторяется. |
| 422 | `NETWORK_ROUTE_ARC_PLACEMENT_UNSUPPORTED` | Преобразование размещения не поддерживает исходные дуги. |
| 422 | `CAD_ROUTE_READER_FAILED` | Чтение геометрии завершилось ошибкой. |
| 422 | `CAD_ROUTE_REPORT_TOO_LARGE` | Отчёт превышает 32 МиБ. |
| 503 | `CAD_ROUTE_READER_NOT_CONFIGURED` | На сервере не настроен reader исходной геометрии. |
| 503 | `CAD_ROUTE_READER_BUSY` | Reader занят другим выделением трасс. |
| 503 | `CAD_ROUTE_READER_START_FAILED` | Не удалось запустить reader. |
| 504 | `CAD_ROUTE_READER_TIMEOUT` | Reader превысил время выполнения. |

Примечания: Геометрию вычисляет сервер. При актуальной версии документа, совпадающих слоях, размещении и отпечатке алгоритма возвращается существующий черновик с решениями инженера. Повтор после сохранения требует перечитать document.version. Новое выделение сохраняет прежние черновики в истории. Результат является черновиком для проверки инженером.

<a id="route-candidate-decide"></a>
### PUT `/api/platform/projects/{projectId}/network-federation/route-drafts/{draftId}/candidates/{candidateId}`

Сохранить решение инженера по кандидату трассы.

- Идентификатор в каталоге: `route-candidate-decide`
- Кто может: Администратор, координатор или исполнитель с правом записи в раздел и доступом к версии (роли: Администратор, Координатор, Загрузка).
- Ключ: только «Полный — по роли»

Параметры:

| Имя | Где | Обязателен | Описание |
|---|---|---|---|
| `projectId` | путь | да | Идентификатор проекта из списка ключа. |
| `draftId` | путь | да | Идентификатор сохранённого черновика. |
| `candidateId` | путь | да | Идентификатор кандидата из report.candidates[].id. |

Тело запроса (JSON):

| Поле | Тип | Обязательно | Описание |
|---|---|---|---|
| `status` | string | да | candidate — вернуть в кандидаты, confirmed — подтвердить, excluded — исключить. |
| `expectedRevision` | integer | да | revision из последнего ответа черновика. |

Ответ: Черновик напрямую, без обёртки ok или draft: id, projectId, sectionId, versionId, sourceSha256, sourceUnit, scaleToMm, placement, normalizationProfile, artifactGeneration, algorithmFingerprint, revision, report, worldSegments[], decisions[], createdByUserId, createdAtUtc.

Ошибки маршрута:

| Статус | Код | Когда |
|---|---|---|
| 428 | `NETWORK_DOCUMENT_VERSION_REQUIRED` | Не передан expectedRevision. |
| 403 | `NETWORK_SOURCE_ACCESS_DENIED` | Нет доступа к версии. |
| 403 | `NETWORK_DISCIPLINE_WRITE_DENIED` | Нет права записи в раздел. |
| 404 | `NETWORK_ROUTE_DRAFT_NOT_FOUND` | Черновик не найден. |
| 404 | `NETWORK_ROUTE_CANDIDATE_NOT_FOUND` | Кандидат отсутствует в черновике. |
| 400 | `NETWORK_ROUTE_DECISION_INVALID` | Недопустимое значение status. |
| 409 | `NETWORK_ROUTE_REVISION_CONFLICT` | Черновик уже изменён. Перечитайте его. |
| 409 | `NETWORK_ROUTE_PLACEMENT_CHANGED` | Размещение или исходная версия изменились. |
| 409 | `NETWORK_ROUTE_DRAFT_SUPERSEDED` | У этой версии чертежа уже есть более новый черновик. |

Примечания: Успешная запись увеличивает revision черновика и версию документа. Повтор с прежней expectedRevision возвращает 409. Запись разрешена для последнего черновика актуального размещения. Исходные сегменты сохраняются.
