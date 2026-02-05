Концепція (коротко)

- NORMAL MODE → 5 хв (економить ліміти)
- FAST MODE → 30 сек (коли щось почалося)
- Тригер FAST MODE:
  - зʼявився новий productId
  - новий продукт зі статусом Available
- State зберігається локально
- Алерт ТІЛЬКИ на NEW, не на кожен цикл

✅ OnChain-ready сервіс  
✅ FAST/NORMAL режим  
✅ не пропускає нові продукти  
✅ не ловить rate-limit  
✅ готовий до Telegram / Docker  

Запуск через Docker

1) Створи `.env` (файл з токенами/налаштуваннями) у корені проєкту.
2) Запусти: `bash docker compose up -d --build docker compose logs -f`


Дані стану (state)

- Стан зберігається у `data/state.json`.
- Папка `data/` монтується в контейнер, тому state зберігається між перезапусками.
