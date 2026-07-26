# Obsidian CLI

## Оглавление

- [Предусловия](#предусловия)
- [Безопасный порядок](#безопасный-порядок)
- [Read-only команды](#read-only-команды)
- [Write-команды](#write-команды)

## Предусловия

Использовать CLI только если:

- установлена поддерживаемая версия Obsidian;
- Command line interface включён в Settings;
- приложение Obsidian доступно;
- выбран точный vault;
- фактический синтаксис проверен через `obsidian help`.

Не считать CLI обязательным: прямой read-only анализ файлов остаётся допустимым.

## Безопасный порядок

1. Выполнить `obsidian help`.
2. Выбрать vault через точный `vault=<name-or-id>`.
3. Для неоднозначных имён использовать `path=<vault-relative-path>`, а не `file=<basename>`.
4. Начать с read-only команды.
5. Перед write снять baseline и проверить target.
6. Не использовать `overwrite` без прямого разрешения и backup.
7. После write прочитать файл и сравнить diff.

## Read-only команды

Примеры, которые нужно сверять с `help` текущей версии:

```bash
obsidian help
obsidian vault="Matreshka OS" search query="source_ids"
obsidian vault="Matreshka OS" read path="30_Wiki/Wiki-Index.md"
obsidian vault="Matreshka OS" tags counts
```

Для проверки существования точного пути предпочесть файловую систему или `read path=...`.

## Write-команды

Write разрешён только в рамках уже одобренной операции:

```bash
obsidian vault="Matreshka OS" create \
  name="New note" \
  content="# New note\n"
```

Не:

- создавать заметку в default location, если маршрут требует точный путь;
- append-ить в неизвестный активный файл;
- запускать команды, меняющие текущую заметку, без явного target;
- использовать CLI для bulk rename/delete;
- полагаться на UI auto-update links как на единственную проверку миграции.

Официальная документация:

- https://obsidian.md/help/cli
