# Рой Proof Pack — разбор реальной сессии (2026-08-06, профиль app)

Цель: собрать Proof Pack «Digital Unlock Platform» — папку-конституцию из ~46 .md,
написанную роем 12 агентов на нативном kanban до первой строки кода.

## Структура роя
- Board: `proof-pack` (профиль app). 14 карточек в 5 волн + 1 карточка W6 (догон).
- Волны через `--parent`: W1 (Vision/Research/PDD) → W2 (Product/Unlock/Campaign)
  → W3 (Economy/Domain/Flutter) → W4 (Growth/Risks/MVP) → W5 (Devil's Advocate/Simplicity).
- Все карточки: `--assignee app`, `--workspace dir:C:\Projects\lazy-unicorn\Digital Unlock Platform`,
  `--max-retries 3`, `--created-by founder`, `--json` для парсинга id.

## Хронология и сбои
1. `--skill founder-visionary` на create → воркер падал `Error: Unknown skill(s)`.
   Пересоздал все карточки без `--skill`, роль — строкой `skill_view(name='...')` в `--body`.
   Старые карточки: `reclaim` + `archive`, иначе их воркеры продолжали писать.
2. `hermes --profile app gateway run` падал: `platforms.api_server.port 8642 already in use`
   (default профиль держит 8642). Фикс: `config set platforms.api_server.port 8643`.
3. `--priority P1` → `invalid int value`; работает `--priority 1`.
4. gbrain: `gbrain export` из папки проекта → «No brain configured»; рабочий путь —
   `bash ~/brains/gb.sh app export --dir "$(cygpath -w "$HOME/Documents/Obsidian-Profiles/app")"`.
   (Также `gb.sh app status` может висеть — не паниковать.)
5. graphify: `graphify update .` строит AST-граф (765 nodes) без ключа; semantic extraction
   требует GEMINI_API_KEY — фиксировать в PROGRESS.md, не изображать успех.

## Аудит-гейт: найденные дефекты (образец чек-листа)
- **Пропущены целые файлы**: в карточки волн не были заведены `05_Design/Design System.md`
  и `05_Design/Wireframes.md` — структура Brief.md их требует. Догон карточкой W6 (frontend-design).
- Нумерация: `Risks.md` шёл 5→7 (пропущен 6) — исправлено патчем.
- Битая ссылка: `Simplicity Review.md` → `ADR-005 Plugin System.md`, реальный файл
  `ADR-005 Plugin System Registry Manifest.md` — исправлено.
- Лишний файл: `AGENT_TEMPLATE.md` в 00_Founder — оказался личным файлом Петра из другого чата
  (подтверждено out-of-band). НЕ удалять чужие файлы без подтверждения.

## Результат
- 15/15 карточек done. 46 .md, структура 00_Founder…08_MVP закрыта на 100%.
- Unlock Bible: 10 стратегий × 13 обязательных полей; Campaign Bible: 10 кампаний;
  Economy: 6 суб-экономик + 3 сценария юнит-экономики; Pinduoduo: 13 движков; Growth: 8 петель.
- gbrain: think + export (3 страницы). graphify: AST-граф обновлён.
