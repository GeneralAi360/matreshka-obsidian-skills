---
name: matreshka-obsidian-skills
description: Safely analyze, create, edit, route, ingest, query, review, and validate Obsidian vaults, with full support for the Matreshka OS Inbox → Sources → Wiki lifecycle. Use for Obsidian Markdown, properties, wikilinks, Bases, Canvas, CLI, web sources, vault structure audits, migrations, or data-integrity checks in Codex, Claude Code, Cursor, and Google Antigravity. Always inspect the existing vault and protect existing data before making changes.
---

# Matreshka Obsidian Skills

Работать с Obsidian как с локальной файловой базой знаний. Для Матрешка ОС соблюдать жизненный цикл:

`00_Inbox → 20_Sources → 30_Wiki → 40_Projects / 50_Areas / 60_Operations`.

Считать `AGENTS.md`, Schema, Policies, Workflows и Templates конкретного vault каноническими. Не заменять ими пользовательское решение и не подменять их предположениями.

## 1. Сначала провести аудит

До любого изменения:

1. Разрешить точный корень vault. Если корень неоднозначен, остановиться и спросить.
2. Найти и полностью прочитать применимые `AGENTS.md`, `CLAUDE.md` или platform rules от корня до целевого файла.
3. Снять read-only инвентаризацию:
   - верхнеуровневые папки;
   - типы и количество файлов;
   - существующие Schema, Policies, Workflows, Templates, Maps и Indexes;
   - наличие Git или другой истории версий;
   - текущие незавершённые изменения;
   - возможные дубли и legacy-пути.
4. Не открывать `99_Private`, секреты и явно исключённые пути без прямой необходимости и разрешения.
5. Запустить read-only lint, если доступен Python:

```bash
python3 <skill-directory>/scripts/lint_vault.py <vault> --profile auto
```

6. Для изменения существующих файлов сохранить baseline вне vault:

```bash
python3 <skill-directory>/scripts/lint_vault.py <vault> \
  --profile auto --json --inventory > <temporary-baseline.json>
```

7. Разделить обнаруженное на:
   - фактическую структуру;
   - требования vault;
   - расхождения;
   - предлагаемые изменения;
   - блокирующие вопросы.

Запрос на анализ или проверку является только read-only задачей. Не «улучшать» структуру во время анализа.

## 2. Применить запрет по умолчанию

Не выполнять автоматически:

- удаление, очистку, purge или recursive remove;
- замену содержимого целого vault или каталога;
- перенос, переименование, merge или split существующих заметок;
- удаление неизвестных properties, вложений, aliases или ссылок;
- массовую нормализацию Markdown;
- миграцию legacy-структуры;
- перезапись файла через `overwrite`;
- изменение `id`, Raw или истории решений;
- чтение или индексацию `99_Private`;
- внешнюю публикацию, синхронизацию или отправку данных.

Для структурной миграции, удаления, merge, bulk rewrite или изменения Raw сначала прочитать `references/change-safety.md`. Требовать точный список путей, recoverable backup и явное подтверждение пользователя. Если восстановление не доказано, подготовить план и остановиться.

## 3. Определить профиль vault

- **Matreshka OS:** обнаружены её `AGENTS.md`, `01_System`, `20_Sources`, `30_Wiki` или явное указание пользователя. Применить `references/matreshka-vault-contract.md`.
- **Другой Obsidian vault:** сначала применить только общие правила Obsidian и локальный контракт. Не требовать папки Матрешка ОС и не считать отличие ошибкой.
- **Неизвестный vault:** выполнить generic-аудит, описать фактическую модель и спросить, нужно ли сопоставление с Матрешка ОС.

## 4. Выбрать только нужные материалы

| Задача | Прочитать |
|---|---|
| безопасность изменения, migration, move, merge, delete | `references/change-safety.md` |
| Codex, Claude, Cursor или Antigravity | `references/platform-compatibility.md` |
| структура и lifecycle Матрешка ОС | `references/matreshka-vault-contract.md` |
| `.md`, YAML, properties, links, embeds | `references/obsidian-markdown.md` |
| `.base` | `references/obsidian-bases.md` |
| `.canvas` | `references/json-canvas.md` |
| Obsidian CLI | `references/obsidian-cli.md` |
| web-источник | `references/web-ingest.md` |
| capture, triage, ingest, query, review, lint | `references/workflows.md` |
| deterministic audit и baseline comparison | `references/validation.md` |

Не загружать все references без необходимости.

## 5. Выполнить разрешённое изменение

1. Разрешить точные целевые пути без glob и предположений.
2. Проверить дубли по `id`, basename, aliases, Maps и Indexes.
3. Выбрать Template и допустимые properties из Schema.
4. Сохранить неизвестные поля и секции, если локальная Schema явно не требует иного.
5. Предпочесть минимальный patch. Не переписывать файл целиком ради локальной правки.
6. Для нового материала использовать additive write; не перемещать оригинал до подтверждённого triage.
7. Создать новый Wiki-вывод как draft. Не присваивать verified без review.
8. Не редактировать `20_Sources/00_Raw`.
9. Не менять один файл параллельно с человеком или другим агентом.
10. При обнаружении неожиданного изменения остановиться и показать конфликт.

## 6. Проверить сохранность

После изменения:

1. Повторить lint с тем же profile.
2. Сравнить новый inventory с baseline через `--baseline`.
3. Проверить, что ни один нецелевой файл не исчез и не изменился.
4. Проверить YAML/JSON, новые wikilinks, `id`, `source_ids`, статус и допустимый путь.
5. Проверить Raw, Private и project-scoped Sources отдельно.
6. Показать diff или точный перечень созданных и изменённых файлов.
7. Не скрывать warnings и не исправлять новые неоднозначности автоматически.

## 7. Вернуть отчёт

Указать:

1. какой vault и профиль проанализированы;
2. что существовало до изменения;
3. что создано или изменено;
4. что намеренно не изменялось;
5. результаты lint и baseline comparison;
6. какие решения, риски или блокеры остались.
