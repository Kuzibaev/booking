## Using Asyncio with Alembic

```shell
alembic init -t async <script_directory_here>
```

## Alembic auto generate migrations

```shell
alembic revision --autogenerate -m "Added account table"
```

## Alembic migrate

```shell
alembic upgrade head
```