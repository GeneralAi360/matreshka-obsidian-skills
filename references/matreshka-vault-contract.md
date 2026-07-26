# Контракт vault Матрешка ОС

## Оглавление

- [Слои](#слои)
- [Raw, Wiki и Schema](#raw-wiki-и-schema)
- [Цепочка происхождения](#цепочка-происхождения)
- [Properties](#properties)
- [Границы записи](#границы-записи)
- [Legacy и сторонние структуры](#legacy-и-сторонние-структуры)

## Слои

| Путь | Назначение |
|---|---|
| `00_Inbox/` | новое и ещё не разобранное |
| `01_System/` | Schema, Policies, Workflows, Templates, Routing, Maps, Indexes и Logs |
| `05_Expert-Profile/` | устойчивый профессиональный контекст Alexander Shinkevich |
| `10_Personal/` | разрешённый личный контекст и рефлексия |
| `15_Idea-Garden/` | идеи после triage, но до обязательства выполнить |
| `20_Sources/00_Raw/` | неизменяемые оригиналы повторно используемых источников |
| `20_Sources/10_Source-Cards/` | происхождение, права, версии, hashes и `source_id` |
| `20_Sources/20_Derivatives/` | OCR, транскрипты, extracted text и переводы |
| `20_Sources/30_Source-Notes/` | доказательный разбор одного источника |
| `30_Wiki/` | связанное, производное и проверяемое знание |
| `40_Projects/` | конечные инициативы и project-scoped Sources |
| `50_Areas/` | постоянные сферы ответственности и активные Playbooks |
| `60_Operations/` | задачи, планы, встречи, решения и review |
| `90_Archive/` | завершённое и вытесненное с сохранением истории |
| `99_Private/` | исключённый по умолчанию чувствительный контекст |

## Raw, Wiki и Schema

Применять трёхслойную модель:

- **Raw** — доказательства и первоисточники; агент читает, но не редактирует.
- **Wiki** — накопительный слой синтеза; агент обновляет его через reviewable changes.
- **Schema** — правила структуры и операций; изменения здесь имеют широкий эффект и требуют повышенного review.

`30_Wiki` является физическим Wiki-слоем. Не создавать `30_Knowledge`.

Не считать оригинал, OCR, транскрипт, clipping, Source Note или чат-ответ автоматически проверенным знанием.

## Цепочка происхождения

```text
Raw original
  → Source Card
  → Derivative (optional)
  → Source Note
  → Wiki draft
  → reviewed Wiki
  → Project / Area / Playbook application
```

Повторно используемый внешний источник получает Source Card. Личное решение, дневниковая запись или задача не требуют фиктивного `source_id`, если не содержат доказуемого внешнего утверждения.

Не переносить в общий `20_Sources`:

- договор одного проекта;
- внутреннюю переписку;
- клиентский бриф;
- выгрузку конкретной рекламной кампании;
- чувствительный project artifact.

Хранить их в `40_Projects/<project>/Sources` с соответствующими access rules.

## Properties

До создания структурированной заметки прочитать:

1. `01_System/Schema/properties.md`;
2. `01_System/Schema/note-types.md`;
3. `01_System/Schema/statuses.md`;
4. Template выбранного `type`.

Базовые имена:

```yaml
schema_version:
id:
type:
status:
agent_use:
source_ids:
project_refs:
review_due:
created_at:
updated_at:
```

Не вводить синонимы:

- `project`, `projects`, `related_projects` вместо `project_refs`;
- `review_on`, `review_due_at` вместо `review_due`;
- `sources`, `references` вместо `source_ids`.

Сохранять wikilinks в списке как строки:

```yaml
source_ids:
  - "[[src_20260726_001]]"
```

Не использовать вложенные YAML-объекты без явного разрешения Schema. Длинные пояснения размещать в Markdown body.

## Границы записи

- Не менять Raw и стабильный `id`.
- Не удалять неизвестное property при локальной правке.
- Не переносить Inbox-item без triage.
- Не превращать идею автоматически в проект или задачу.
- Не повышать Wiki draft до verified без review.
- Не копировать private или project-scoped материал в общий индекс.
- Не читать `99_Private` при обычном query или lint.
- Не выполнять внешние действия без отдельного разрешения.

## Legacy и сторонние структуры

Если найден `30_Knowledge`:

1. отметить legacy-path;
2. не создавать там новые Matreshka OS заметки;
3. не переносить существующие файлы автоматически;
4. проверить ссылки, embeds, Bases, Maps, Templates и scripts;
5. подготовить mapping и rollback;
6. ждать явного решения пользователя.

Если vault не является Матрешка ОС, не применять это дерево как обязательное. Сначала описать его собственную модель, затем предложить необязательное сопоставление.
