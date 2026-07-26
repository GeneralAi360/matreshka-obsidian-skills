# Совместимость AI-сред

## Оглавление

- [Общий формат](#общий-формат)
- [Расположение](#расположение)
- [Канонический контракт vault](#канонический-контракт-vault)
- [Вызов](#вызов)
- [Переносимость скриптов](#переносимость-скриптов)

## Общий формат

Использовать один переносимый пакет Agent Skills:

```text
matreshka-obsidian-skills/
├── SKILL.md
├── references/
└── scripts/
```

В frontmatter `SKILL.md` оставлять только общие поля `name` и `description`. Платформенные метаданные хранить отдельно и не делать их обязательными для выполнения workflow.

## Расположение

| Среда | Workspace-путь |
|---|---|
| Codex | `.agents/skills/matreshka-obsidian-skills/` |
| Google Antigravity | `.agents/skills/matreshka-obsidian-skills/` |
| Claude Code | `.claude/skills/matreshka-obsidian-skills/` |
| Cursor | `.cursor/skills/matreshka-obsidian-skills/` |

Копировать или связывать весь каталог навыка. Один `SKILL.md` без `references/` и `scripts/` является неполной установкой.

## Канонический контракт vault

Хранить полные правила Матрешка ОС только в корневом `AGENTS.md`.

- Codex читает `AGENTS.md` напрямую.
- Claude Code использует короткий `CLAUDE.md`, который импортирует `@AGENTS.md` и содержит только реальные Claude-исключения.
- Antigravity использует тонкое Always-On правило в `.agents/rules/`, которое направляет агента к корневому `AGENTS.md`.
- Cursor использует корневой `AGENTS.md` как project instruction и сам навык из `.cursor/skills/`.

Не копировать весь `AGENTS.md` в четыре платформенных файла. Дубли расходятся и создают конфликтующие правила.

При конфликте применять:

1. прямое текущее указание пользователя;
2. ближайший применимый project contract;
3. `01_System/Schema`, Policies и Workflows;
4. этот навык;
5. общие правила платформы.

## Вызов

| Среда | Явный вызов |
|---|---|
| Codex | `$matreshka-obsidian-skills` или выбор через `/skills` |
| Claude Code | `/matreshka-obsidian-skills` |
| Cursor | `/matreshka-obsidian-skills` |
| Antigravity | выбрать навык или назвать `matreshka-obsidian-skills` в запросе |

Автоматическое срабатывание зависит от `description`. Не предполагать, что одинаковая slash-команда доступна во всех версиях продукта.

## Переносимость скриптов

Перед запуском определить каталог, содержащий загруженный `SKILL.md`, и строить путь к `scripts/lint_vault.py` относительно него.

Не предполагать:

- что текущая рабочая директория совпадает с каталогом навыка;
- что Obsidian CLI установлен;
- что Python называется одинаково на всех ОС;
- что vault использует Git;
- что агент имеет право записи за пределами workspace.

Если детерминированный скрипт недоступен, выполнить ручной read-only аудит и явно указать, какие проверки не были автоматизированы.
