<!-- add new  alembic migrations -->
uv run alembic revision --autogenerate -m "Update department endpoint permissions and fix user_id type in dependencies"
uv run alembic upgrade head
<!-- run alembic migrations -->

