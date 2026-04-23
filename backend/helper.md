<!-- add new  alembic migrations -->
uv run alembic revision --autogenerate -m "Add email verification model"
<!-- run alembic migrations -->
uv run alembic upgrade head

