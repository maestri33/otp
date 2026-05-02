"""
Pacote de modelos Tortoise.

Tortoise descobre os modelos pela lista em `app.db.TORTOISE_ORM["apps"]`,
que aponta pra `app.models`. Para um modelo aparecer na descoberta,
basta o arquivo dele estar dentro deste pacote — Tortoise faz o import.
"""

from app.models.example import Item  # noqa: F401  (registrar para Tortoise)
