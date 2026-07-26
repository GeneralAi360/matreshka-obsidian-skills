# Matreshka Obsidian Skills

Самостоятельный кроссплатформенный Agent Skill для безопасной работы AI-агентов с Obsidian и базой знаний Matreshka OS.

**Author:** [Alexander Shinkevich](https://alexandrshinkevich.com)  
**License:** [MIT](LICENSE)  
**Supported agents:** OpenAI Codex, Claude Code, Cursor, Google Antigravity

## Что делает навык

Навык помогает агенту:

- анализировать существующую структуру Obsidian до любых изменений;
- создавать и редактировать Markdown notes без потери properties и links;
- работать с Obsidian Properties, wikilinks, embeds и attachments;
- создавать и проверять `.base` и `.canvas`;
- использовать Obsidian CLI только после проверки target;
- принимать материалы в Inbox;
- выполнять triage;
- регистрировать Sources и их provenance;
- создавать Source Notes и Wiki drafts;
- отвечать по базе с evidence;
- проводить review и lint;
- сравнивать vault с baseline и обнаруживать исчезновение или изменение файлов;
- анализировать сторонние Obsidian vault без навязывания им структуры Matreshka OS.

## Главный принцип безопасности

Любая работа начинается с read-only аудита:

1. определить точный vault root;
2. прочитать применимые `AGENTS.md`, Schema, Policies и Workflows;
3. зафиксировать структуру, типы файлов и текущие изменения;
4. проверить дубли, links и legacy paths;
5. создать inventory до записи;
6. только затем предложить или применить минимальное изменение.

Навык не должен автоматически:

- удалять заметки, папки и attachments;
- перемещать или переименовывать существующие материалы;
- объединять похожие заметки;
- удалять неизвестные properties;
- переписывать vault целиком;
- изменять Raw;
- выполнять bulk migration;
- открывать `99_Private`;
- публиковать или отправлять данные во внешние сервисы.

Structural или destructive изменение возможно только после точного плана, recoverable backup и явного решения пользователя.

## Matreshka OS

Основной knowledge lifecycle:

```text
00_Inbox
  ↓ triage
20_Sources
  ├── 00_Raw
  ├── 10_Source-Cards
  ├── 20_Derivatives
  └── 30_Source-Notes
  ↓ reviewable synthesis
30_Wiki
  ↓ application
40_Projects / 50_Areas / 60_Operations
```

Трёхслойная основа:

- **Raw** — отобранные первоисточники и доказательства; immutable;
- **Wiki** — накопительный синтез в связанных Markdown pages;
- **Schema** — правила структуры, types, properties и workflows.

`Raw` не является knowledge. OCR, transcript, clipping и Source Note также не становятся verified knowledge автоматически.

## Защита существующей структуры

Если агент видит vault, который не соответствует Matreshka OS, он обязан:

1. описать фактическую структуру;
2. определить локальные правила;
3. выполнить `generic` lint;
4. подготовить необязательное mapping к Matreshka OS;
5. не создавать, не перемещать и не удалять файлы во время анализа.

Отличие от Matreshka OS означает «другая модель», а не «ошибка».

## Установка

Копируйте весь каталог навыка, а не только `SKILL.md`.

### Codex

Workspace:

```text
<vault>/.agents/skills/matreshka-obsidian-skills/
```

User:

```text
~/.agents/skills/matreshka-obsidian-skills/
```

Вызов:

```text
$matreshka-obsidian-skills
```

### Claude Code

Workspace:

```text
<vault>/.claude/skills/matreshka-obsidian-skills/
```

User:

```text
~/.claude/skills/matreshka-obsidian-skills/
```

Вызов:

```text
/matreshka-obsidian-skills
```

Для Matreshka OS используйте короткий корневой `CLAUDE.md`, который импортирует канонический `@AGENTS.md`.

### Cursor

Workspace:

```text
<vault>/.cursor/skills/matreshka-obsidian-skills/
```

User:

```text
~/.cursor/skills/matreshka-obsidian-skills/
```

Вызов:

```text
/matreshka-obsidian-skills
```

### Google Antigravity

Workspace:

```text
<vault>/.agents/skills/matreshka-obsidian-skills/
```

User:

```text
~/.gemini/config/skills/matreshka-obsidian-skills/
```

Назовите навык в запросе или выберите его в интерфейсе. Для Matreshka OS добавьте тонкое Always-On правило в `.agents/rules/`, которое направляет агента к корневому `AGENTS.md`.

## Один источник правил

Для Matreshka OS:

- `AGENTS.md` — канонический полный контракт;
- `CLAUDE.md` — тонкий adapter для Claude;
- `.agents/rules/matreshka-os.md` — тонкий adapter для Antigravity;
- сам Skill — переносимый workflow и технические правила;
- `01_System/Schema`, `Policies`, `Workflows` и `Templates` — исполнимая спецификация конкретного vault.

Не дублируйте полный контракт во всех platform files.

## Read-only lint

Скрипт не изменяет vault.

### Auto profile

```bash
python3 scripts/lint_vault.py /absolute/path/to/vault
```

Если обнаружены признаки Matreshka OS, включаются её правила. Иначе используется generic profile.

### Сторонний Obsidian vault

```bash
python3 scripts/lint_vault.py /absolute/path/to/vault --profile generic
```

Generic проверяет YAML, duplicate IDs, ambiguous names, wikilinks и baseline integrity без требования `30_Wiki`.

### Строгая проверка Matreshka OS

```bash
python3 scripts/lint_vault.py /absolute/path/to/vault --profile matreshka
```

### JSON report

```bash
python3 scripts/lint_vault.py /absolute/path/to/vault --json
```

### Baseline до изменения

Сохраняйте baseline вне vault:

```bash
python3 scripts/lint_vault.py /absolute/path/to/vault \
  --profile auto \
  --json \
  --inventory > /temporary/location/before.json
```

После изменения:

```bash
python3 scripts/lint_vault.py /absolute/path/to/vault \
  --profile auto \
  --baseline /temporary/location/before.json
```

Сравниваются:

- путь;
- размер;
- SHA-256.

Исчезнувший файл становится `baseline.missing error`. Изменённый Raw становится `raw.modified error`. Другие изменённые файлы явно перечисляются для сверки с approved scope.

## Примеры запросов

### Анализ без изменений

```text
Используй matreshka-obsidian-skills. Проанализируй структуру этого Obsidian vault,
найди риски и предложи mapping к Matreshka OS. Ничего не изменяй.
```

### Безопасная локальная правка

```text
Используй matreshka-obsidian-skills. Сначала проанализируй структуру и создай
baseline. Затем добавь source_ids в указанную Wiki note, сохранив все
существующие properties и остальные файлы.
```

### Проверка после работы другого агента

```text
Используй matreshka-obsidian-skills. Сравни текущий vault с before.json и покажи
все missing, modified и created paths. Ничего не исправляй.
```

### Source ingest

```text
Используй matreshka-obsidian-skills. Проведи triage этого материала.
Не перемещай оригинал, пока не покажешь выбранный маршрут и не получишь решение.
```

## Состав

```text
matreshka-obsidian-skills/
├── SKILL.md
├── LICENSE
├── agents/
│   └── openai.yaml
├── references/
│   ├── change-safety.md
│   ├── platform-compatibility.md
│   ├── matreshka-vault-contract.md
│   ├── obsidian-markdown.md
│   ├── obsidian-bases.md
│   ├── json-canvas.md
│   ├── obsidian-cli.md
│   ├── web-ingest.md
│   ├── workflows.md
│   └── validation.md
└── scripts/
    └── lint_vault.py
```

## Первичные источники проектирования

- [Obsidian Help](https://obsidian.md/help)
- [Obsidian Properties](https://obsidian.md/help/properties)
- [Obsidian Internal Links](https://obsidian.md/help/links)
- [Obsidian Bases](https://obsidian.md/help/bases)
- [Obsidian CLI](https://obsidian.md/help/cli)
- [JSON Canvas 1.0](https://jsoncanvas.org/spec/1.0/)
- [Andrej Karpathy — LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [OpenAI — Build skills](https://developers.openai.com/codex/skills)
- [Claude Code — Skills](https://code.claude.com/docs/en/skills)
- [Cursor — Agent Skills](https://cursor.com/docs/skills)
- [Google Antigravity — Agent Skills](https://antigravity.google/docs/skills)

## Автор и лицензия

Автор: [Alexander Shinkevich](https://alexandrshinkevich.com).

Проект распространяется по лицензии [MIT](LICENSE). Разрешены использование,
копирование, изменение, публикация и распространение при сохранении copyright
notice и текста лицензии.
