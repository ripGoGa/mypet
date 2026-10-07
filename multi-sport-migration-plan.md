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
- `RunningWorkout` — по аналогии, для бега (скорость в м/с, `effort_pace`, каденс, время контакта
  с землёй и т.д.). Парсер (`parse_fit_running`), репозиторий, калькулятор, DTO и
  подключение к `ImportService` готовы.

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
- `RunningStatsCalculator` — принимает `Sequence[tuple[Workout, RunningWorkout]]`. Готов.

Каждый калькулятор знает только про свой вид спорта.

### 4. DTO: отдельный на каждый вид спорта

Не один "универсальный" `CyclingStatsDTO` с кучей `Optional`-полей на все виды спорта
(это тот же анти-паттерн, из-за которого шёл рефакторинг `Workout`).

- `CyclingStatsDTO` — готов (переименован из `WorkoutsDTO`, файл `cycling_dto.py`).
- `RunningStatsDTO` — готов (`running_dto.py`), `raw_*`-списки допускают `None`.

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
PARSERS = {"cycling": parse_fit_cycling, "running": parse_fit_running}
MODELS = {"cycling": CyclingWorkout, "running": RunningWorkout}
```

Добавление нового спорта — это добавление ключа в оба словаря плюс сам парсер,
без изменения кода `ImportService`. Файл с неподдерживаемым видом спорта отклоняется
через `UnsupportedSportError` (наследник `ParseFitError`): откат транзакции, файл удаляется,
учитывается как ошибка импорта.

### 6. Метрики бега: принятые решения

- **Скорость и пейс.** В БД скорости хранятся в м/с (числа нужны для агрегатов). В пейс
  (мин/км) они переводятся только на уровне отображения через отдельную функцию
  `format_pace` (пока не реализована). Калькулятор возвращает числа, не строки.
- **Средний пейс за период** считается как общая дистанция / общее время, а не как среднее
  по средним скоростям тренировок: простое среднее завышает результат, потому что не
  учитывает, сколько времени потрачено на медленные пробежки. Для пульса и каденса
  осознанно оставлено простое среднее («типичная тренировка»).
- **Каденс.** FIT хранит каденс бега «на одну ногу», поэтому при заполнении raw-списка
  значение умножается на 2 (чтобы список для графика и среднее давали одно число).
- **Не нужны для бега:** TSS, intensity factor, normalized power и счётчики тяжести
  (light/medium/hard). Лучший пейс не реализуется.
- **Устойчивость к `None`:** raw-списки хранят `None`, агрегаты и максимумы их пропускают,
  чтобы одна неполная запись не роняла страницу статистики.

### 7. `StatisticsService`, роутер `/statistics` и UI

- `StatisticsService` имеет отдельный метод на каждый вид спорта: `get_cycling_stats` и
  `get_running_stats` (у каждого свои репозиторий, калькулятор и DTO). Общая абстракция
  не нужна: по Rule of Three дублирование пока дешевле неверной абстракции.
- Общая статистика по всем видам спорта не объединяется в один DTO, а разбивается по видам
  спорта и показывается блоками на одной странице (например, за месяц 4 вело и 8 беговых
  тренировок: один блок с вело-статистикой, другой с беговой).
- Роутер `/statistics` пока вызывает только `get_cycling_stats`. Блок бега, `?sport=` и
  шаблоны отложены до фронтенда.
- Ранее обсуждались приоритетный вид спорта в профиле и вкладки/фильтр
  (`?sport=cycling`, `?sport=running`) — нужно решить, остаются ли они вместе с блоками.

## План действий (по шагам)

1. ✅ `CyclingWorkout` модель создана (`app/models/training_models.py`)
2. ✅ `RunningWorkout` модель создана — симметрично `CyclingWorkout`
3. ✅ Cycling-путь доработан целиком, архитектура доказана:
   - ✅ `CyclingWorkoutRepository` — `get_workouts` / `get_statistic_workouts`,
     `join` по `workout_id`, без `Relationship`
   - ✅ `CyclingStatsCalculator` — переписан под `Sequence[tuple[Workout, CyclingWorkout]]`
   - ✅ Вело-DTO — адаптирован
   - ✅ Переход `.csv` → `.fit`: `read_fit_file` + `parse_fit_cycling` +
     `ImportService` с реестрами `PARSERS`/`MODELS`
   - ✅ Тесты и фикстуры обновлены (`test_import_files.py` переписан под FIT,
     `test_fit_rider.py` — новый, для `read_fit_file`)
4. ✅ `data/app.db` / `data/test_app.db` пересозданы под новую схему
5. 🔄 Реализовать `running` по доказанному паттерну — согласованный план из 7 шагов:
   1. ✅ `parse_fit_running(session_dict, user_id, uploaded_file_id) -> tuple[Workout, dict]`
      + тест
   2. ✅ `RunningWorkoutRepository` (по образцу `CyclingWorkoutRepository`):
      `get_workouts` / `get_statistic_workouts`
   3. ✅ `RunningStatsCalculator` (по образцу `CyclingStatsCalculator`, см. решения в п. 6)
   4. ✅ `RunningStatsDTO` (по образцу вело-DTO, `raw_*`-списки допускают `None`)
   5. ✅ Добавить `"running"` в `PARSERS` и `MODELS` в `ImportService`
      (+ `UnsupportedSportError` для неподдерживаемых видов спорта)
   6. ✅ `StatisticsService`: `get_cycling_stats` и `get_running_stats`
   7. 🔄 Тесты: для парсера и репозиториев (`total_count`, изоляция по спорту и
      пользователю) готовы; остальное — в техдолге ниже
   8. ⬜ Функция `format_pace` и вывод пейса в UI

## Технические долги, не забыть

**Бег (новое):**
- Валидация в `parse_fit_running`: наличие `avg_speed`, `total_distance`, `total_timer_time`
  (отклонять файл, где их нет) + тест на файл без скорости
- Тесты на `RunningStatsCalculator`
- Тесты репозиториев: `get_statistic_workouts` (изоляция по спорту и пользователю),
  `period=0`, пустой результат, пагинация (limit/offset и порядок «новые первыми»)
- Тесты `ImportService` для бега: успешный импорт `.fit` (появляются `Workout` и
  `RunningWorkout`) и файл неподдерживаемого вида спорта (`UnsupportedSportError`:
  откат транзакции, файл удалён, учтён как ошибка импорта)
- Тест `RunningStatsDTO`: сборка из `RunningStatsCalculator` через `from_attributes`,
  в том числе с `None` в списках `raw_*`
- Тест `save_file_with_hash`: реальная запись файла в `data/fit` (текущие тесты работают
  через фейковый сервис и этот путь не покрывают)
- Тест страницы `/workouts/{id}`: проверять, что в HTML есть данные тренировки, а не только
  статус 200 (после починки фронта)
- Решить, должен ли `total_elapsed_time` быть `timedelta`
- Тесты `get_running_stats` и фикстура `running_repo` для `StatisticsService` (сейчас в
  фикстурах передаётся `running_repo=None`)

**Общие:**
- `Query()`-валидация в остальных роутах: в `/workouts` и `/statistics` уже сделана
- Верхняя граница `period` в `/statistics` и `/workouts` (возможно переполнение `timedelta`
  и 500 на огромных значениях — не проверено)
- `CyclingStatsDTO`: `raw_*: list[float]` не допускают `None`, нужно `list[float | None]`
- В будущем объединить реестры `PARSERS` и `MODELS`
- `fake_uploaded_file` в тестовых фикстурах импорта всё ещё содержит `content_type="text/csv"`
  — не используется `validate_file_type` (проверяет только расширение `.fit`), но стоит
  почистить для консистентности
- bcrypt обрезает пароли длиннее 72 байт (лимит библиотеки) — при переходе с `passlib` на
  прямой `bcrypt` это не было обработано; потенциальный скрытый баг, не исправлено
- UI `/statistics` пока не учитывает мульти-спорт (пункт 7 архитектурных решений): блок
  бега и вызов `get_running_stats` в роутере — после бэкенда, вместе с фронтендом
