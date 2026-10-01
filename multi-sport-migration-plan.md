# Миграция на мульти-спорт архитектуру

## Контекст

Изначальная модель `Workout` хранила все данные (включая cycling-специфичные метрики:
`distance_km`, `avg_watts`, `training_stress_score` и т.д.) в одной плоской таблице.
Это работало, пока приложение поддерживало только велоспорт и `.csv`-файлы.

Теперь добавляется бег (и в будущем — другие виды спорта), а также произошёл переход
с `.csv` на `.fit` файлы. Плоская модель для этого не годится: разные виды спорта имеют
принципиально разные метрики (мощность/каденс для вело, темп/шаги для бега).

## Принятые архитектурные решения

### 1. Модель данных: `Workout` + специфичные для спорта таблицы

- `Workout` — общие поля: `id`, `sport`, `started_at`, `duration`, `source_file_id`, `user_id`.
- `CyclingWorkout` — специфика велоспорта (`total_distance`, `avg_power`, `normalized_power`, ...),
  связана с `Workout` через `workout_id: int = Field(foreign_key="workout.id", unique=True)`.
  Связь 1:1.
- `CyclingWorkout` — по аналогии, для бега (темп, шаги и т.д.). Модель создана
  (`app/models/training_models.py`), но пока не используется — не хватает парсера,
  репозитория, калькулятора и DTO.

**Почему без `Relationship()` в SQLModel:** добавление `Relationship` в `Workout` на каждый
новый вид спорта означало бы раздувание модели `Workout` при каждом новом спорте
(`cycling_workout`, `running_workout`, `swimming_workout`, ...). Вместо этого связь
поднимается вручную в репозитории: узнаём `workout.sport`, затем явным запросом ищем
соответствующую специфичную запись по `workout_id`.

### 2. Как передавать данные из репозитория в сервис

**Не** пытаться "приклеить" `CyclingWorkout` к объекту `Workout` через `workout.cycling_data = ...`
— SQLModel/Pydantic по умолчанию запрещает произвольные атрибуты (`extra='allow'` — это
неявная магия, усложняющая чтение кода).

**Вместо этого** — явный контейнер: репозиторий возвращает пары
`tuple[Workout, CyclingWorkout]` (или список таких пар). Явное лучше неявного.

### 3. Калькуляторы статистики: один класс на вид спорта

По Single Responsibility — не городить `if sport == 'cycling' / elif sport == 'running'`
внутри одного класса, а сделать отдельные калькуляторы:

- `CyclingStatsCalculator` — принимает `Sequence[tuple[Workout, CyclingWorkout]]`. Готов.
- `RunningStatsCalculator` — принимает `Sequence[tuple[Workout, RunningWorkout]]` (будущее).

Каждый калькулятор знает только про свой вид спорта.

### 4. DTO: отдельный на каждый вид спорта

Не один "универсальный" `WorkoutsDTO` с кучей `Optional`-полей на все виды спорта
(это тот же анти-паттерн, из-за которого шёл рефакторинг `Workout`).

- `CyclingStatsDTO` — готов.
- `RunningStatsDTO` (будущее).

### 5. Импорт файлов: `.fit` вместо `.csv`, реестр парсеров по спорту

`.csv`-путь полностью удалён. Импорт теперь работает с бинарными `.fit`-файлами через
библиотеку `fitparse`.

Проблема "курицы и яйца" (нужно знать спорт, чтобы выбрать парсер, но чтобы узнать
спорт — нужно прочитать файл) решена разделением на два шага:

- `read_fit_file(file_path) -> tuple[dict, str]` — открывает файл один раз, валидирует,
  что в нём ровно одна `session`, достаёт `sport`. Общий для всех видов спорта.
- `parse_fit_<sport>(session_dict, user_id, uploaded_file_id) -> tuple[Workout, dict]` —
  чистая функция без файлового I/O, знает только про свой вид спорта.

`ImportService` диспетчеризует по спорту через реестры:

```python
PARSERS = {"cycling": parse_fit_cycling}
MODELS = {"cycling": CyclingWorkout}
```

Добавление нового спорта — это добавление ключа в оба словаря плюс сам парсер,
без изменения кода `ImportService`.

### 6. UI / роутер `/statistics`

- Пользователь задаёт приоритетный вид спорта в профиле — он показывается на главной
  вкладке статистики.
- Остальные виды спорта — в отдельных вкладках, либо через фильтр
  (`?sport=cycling`, `?sport=running`).
- Пока не реализовано.

## План действий (по шагам)

1. ✅ `CyclingWorkout` модель создана (`app/models/training_models.py`)
2. ✅ `CyclingWorkout` модель создана — симметрично `CyclingWorkout`, пока не используется
3. ✅ Cycling-путь доработан целиком, архитектура доказана:
   - ✅ `CyclingWorkoutRepository` — `get_workouts` / `get_statistic_workouts`,
     `join` по `workout_id`, без `Relationship`
   - ✅ `CyclingStatsCalculator` — переписан под `Sequence[tuple[Workout, CyclingWorkout]]`
   - ✅ `CyclingStatsDTO` — адаптирован
   - ✅ Переход `.csv` → `.fit`: `read_fit_file` + `parse_fit_cycling` +
     `ImportService` с реестрами `PARSERS`/`MODELS`
   - ✅ Тесты и фикстуры обновлены (`test_import_files.py` переписан под FIT,
     `test_fit_rider.py` — новый, для `read_fit_file`; весь набор — 29/29 зелёных)
4. ✅ `data/app.db` / `data/test_app.db` пересозданы под новую схему
5. ⬜ Реализовать `running` по доказанному паттерну — согласованный план из 7 шагов:
   1. `parse_fit_running(session_dict, user_id, uploaded_file_id) -> tuple[Workout, dict]`
      — по образцу `parse_fit_cycling`
   2. `RunningWorkoutRepository` (по образцу `CyclingWorkoutRepository`):
      `get_workouts` / `get_statistic_workouts`
   3. `RunningStatsCalculator` (по образцу `CyclingStatsCalculator`)
   4. `RunningStatsDTO` (по образцу DTO для cycling)
   5. Добавить `"running"` в `PARSERS` и `MODELS` в `ImportService`
   6. Тесты на каждый новый компонент
   7. Обновить этот документ по итогам

## Технические долги, не забыть

- `fake_uploaded_file` в тестовых фикстурах импорта всё ещё содержит `content_type="text/csv"`
  — не используется `validate_file_type` (проверяет только расширение `.fit`), но стоит
  почистить для консистентности
- bcrypt обрезает пароли длиннее 72 байт (лимит библиотеки) — при переходе с `passlib` на
  прямой `bcrypt` это не было обработано; потенциальный скрытый баг, не исправлено
- UI `/statistics` пока не учитывает мульти-спорт (пункт 6 архитектурных решений) —
  актуально после реализации running