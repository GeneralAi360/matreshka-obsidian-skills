# Obsidian Markdown, Properties и Links

## Оглавление

- [Перед правкой](#перед-правкой)
- [Properties](#properties)
- [Ссылки](#ссылки)
- [Embeds и callouts](#embeds-и-callouts)
- [Безопасное изменение](#безопасное-изменение)
- [Проверка](#проверка)

## Перед правкой

1. Прочитать локальный Template и Schema.
2. Снять baseline целевого файла.
3. Проверить существующую заметку, `id`, aliases и backlinks.
4. Выбрать минимальный patch.

## Properties

Obsidian хранит properties в YAML frontmatter в начале Markdown-файла:

```yaml
---
schema_version: "1.0"
id: note_20260726_001
type: concept
status: draft
aliases:
  - "Alternative title"
created_at: 2026-07-26
---
```

Соблюдать правила:

- frontmatter начинается с первой строки `---` и закрывается отдельной строкой `---`;
- одно имя property имеет один тип во всём vault;
- использовать атомарные text, list, number, checkbox, date, date-time и tags;
- не хранить Markdown-разметку и длинные объяснения в property;
- не создавать вложенные объекты, если Schema их не разрешает;
- использовать YAML-списки для многозначных полей;
- кавычить значения с wikilinks, двоеточиями или неоднозначным синтаксисом;
- не удалять неизвестные properties при локальной правке.

## Ссылки

Для внутренних связей Матрешка ОС использовать wikilinks:

```markdown
[[Concept]]
[[30_Wiki/Concepts/Concept]]
[[Concept|Отображаемое имя]]
[[Concept#Раздел]]
[[Concept#^block-id]]
```

Для внешних URL использовать Markdown links:

```markdown
[Obsidian Help](https://obsidian.md/help)
```

Перед созданием ссылки проверить:

- существует ли точный путь;
- не создаёт ли basename двусмысленность;
- не является ли нужная цель alias другой заметки;
- не указывает ли ссылка в Private или project-scoped слой без разрешения.

Obsidian может обновлять внутренние ссылки при rename, но не считать это достаточной защитой: scripts, Bases, YAML strings и внешние инструменты могут хранить путь иначе.

## Embeds и callouts

Embed создаётся префиксом `!`:

```markdown
![[Diagram.png]]
![[Concept#Краткое определение]]
```

Callout:

```markdown
> [!note] Контекст
> Короткое пояснение.
```

Не дублировать канонический текст через copy-paste, если embed или ссылка сохраняют единственный источник истины.

## Безопасное изменение

- Не менять line endings, пробелы и весь формат файла без необходимости.
- Не заменять весь frontmatter ради одного property.
- Не переставлять неизвестные поля автоматически.
- Не переписывать wikilinks в Markdown links или обратно массово.
- Не удалять пустую секцию, если Template или Workflow ожидает её.
- Не менять filename и `id` одной операцией без migration plan.
- Не перезаписывать attachment с тем же именем.

## Проверка

Проверить:

1. YAML разбирается как mapping.
2. Обязательные properties присутствуют и имеют ожидаемые типы.
3. Заголовки имеют логичную иерархию.
4. Новые wikilinks разрешаются однозначно.
5. Embeds указывают на существующие файлы.
6. `id`, source chain и неизвестные properties сохранены.
7. Diff содержит только заявленное изменение.

Официальные основы:

- https://obsidian.md/help/properties
- https://obsidian.md/help/links
