# MegaMart recovered frontend

Запуск:

```bash
pip install -r requirements.txt
python manage.py runserver
```

Главная страница: `http://127.0.0.1:8000/`

Frontend находится в приложении `shop`:

- `shop/templates/shop/base.html`
- `shop/templates/shop/home.html`
- `shop/templates/shop/includes/`
- `shop/static/shop/css/style.css`
- `shop/static/shop/img/`

Данные временно передаются из `shop/views.py` через `context`. Backend потом может заменить списки на запросы к базе.
