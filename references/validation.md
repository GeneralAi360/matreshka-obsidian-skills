# Read-only validation

## Оглавление

- [Гарантия](#гарантия)
- [Профили](#профили)
- [Запуск](#запуск)
- [Baseline comparison](#baseline-comparison)
- [Что проверяется](#что-проверяется)
- [Границы](#границы)

## Гарантия

`scripts/lint_vault.py` только читает vault и печатает отчёт в stdout. Он не создаёт, не изменяет, не перемещает и не удаляет файлы.

Shell redirection может сохранить отчёт по выбранному пользователем пути; для baseline использовать временный каталог вне vault.

## Профили

- `auto` — определить Matreshka OS по каноническим признакам, иначе применить generic.
- `generic` — проверить общую целостность Obsidian без требования Matreshka-папок.
- `matreshka` — добавить правила Матрешка ОС.

Другой vault можно анализировать в `generic`. Его локальные Schema и rules агент проверяет семантически отдельно.

## Запуск

```bash
python3 scripts/lint_vault.py /absolute/path/to/vault
python3 scripts/lint_vault.py /absolute/path/to/vault --profile generic
python3 scripts/lint_vault.py /absolute/path/to/vault --profile matreshka
python3 scripts/lint_vault.py /absolute/path/to/vault --json
python3 scripts/lint_vault.py /absolute/path/to/vault --json --inventory
python3 scripts/lint_vault.py /absolute/path/to/vault --include-private
```

По умолчанию пропускаются `.git`, `.obsidian`, `.trash`, `__pycache__` и `99_Private`.

## Baseline comparison

Создать baseline:

```bash
python3 scripts/lint_vault.py /vault \
  --profile auto --json --inventory > /temporary/before.json
```

После разрешённых изменений:

```bash
python3 scripts/lint_vault.py /vault \
  --profile auto --baseline /temporary/before.json
```

Baseline сравнивает путь, размер и SHA-256. Missing и изменённый Raw становятся errors. Изменения других существующих файлов показываются явно и должны соответствовать approved scope.

Baseline отражает только пути, доступные в момент создания. Если Private был исключён, отчёт не доказывает его сохранность.

## Что проверяется

Generic:

- YAML frontmatter;
- duplicate `id`;
- неоднозначные basenames;
- базовая разрешимость wikilinks;
- inventory и baseline differences.

Matreshka:

- `30_Wiki` и legacy `30_Knowledge`;
- обязательные core properties в структурированных заметках;
- deprecated property aliases;
- соответствие ключевых `type` и путей;
- Source Card `src_` IDs;
- verified Wiki без `source_ids`;
- изменение или потеря Raw по baseline.

## Границы

Lint не заменяет:

- локальный Schema-specific validator;
- смысловой review;
- проверку `.base` в текущей версии Obsidian;
- проверку прав и лицензий;
- backup и restore test;
- пользовательское решение о переносе, merge или удалении.

Exit codes:

- `0` — нет errors;
- `1` — найдены errors;
- `2` — ошибка запуска или зависимости.
