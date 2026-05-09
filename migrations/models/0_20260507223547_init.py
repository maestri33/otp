from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "otp_config" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "footer" VARCHAR(255) NOT NULL DEFAULT 'Equipe OTP',
    "ttl_s" INT NOT NULL DEFAULT 300,
    "num_digits" INT NOT NULL DEFAULT 6,
    "max_attempts" INT NOT NULL DEFAULT 3,
    "active" INT NOT NULL DEFAULT 1,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "otp_logs" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "external_id" VARCHAR(255) NOT NULL,
    "code_hash" VARCHAR(64) NOT NULL,
    "status" VARCHAR(20) NOT NULL DEFAULT 'generated',
    "message_id" INT,
    "error_detail" TEXT,
    "verified_at" TIMESTAMP,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_otp_logs_externa_15ed47" ON "otp_logs" ("external_id");
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztl21P6jAUx78K2StMvAYR0dx3gNwrNzwYnfcajVkKK6Oxa+faqcT43W9bGGVlQ0BATH"
    "wH52E9/e2s/Z9Xy6cuxOygY1/UKOkjz/qZe7UI8KH4Mevcz1kgCLRLGjjoYhVNeeD0dFyX"
    "8RD0uPD0AWZQmFzIeiEKOKJEWEmEsTTSnghExNOmiKDHCDqcepAPYCgcd/fCjIgLXyCL/w"
    "YPTh9B7CYqRq5cW9kdPgyUrUH4LxUoV+uKEnHkEx0cDPmAkkk0IlxaPUhgCDiUj+dhJMuX"
    "1Y33Gu9oVKkOGZU4lePCPogwn9ruggwESMlPVMPUBj25yo/iYemkdHpULp2KEFXJxHLyNt"
    "qe3vsoURFo29ab8gMORhEKo+bWp5QL0jPsagMQpsPTGQZAUbYJMMY1j2Bs0Ah128QMrfpj"
    "hAKYEw1pfYClD14cDInHBxLg8fEccn8rl7XzymVeRO3JJalo6VG3t8eu4sgn8WqcnGOHLd"
    "GJk/j3m3FdLI8Khc9uR82LRL7jIg/xZaAlk7ZHrrw73GQnA86hHyxFzkzbYtftDjtxN6En"
    "OEutSimGgKST00kGs67I2hS0yV2yErc5UKqdTlMW7TP2iJWhYRun3HWrWr/MH6rDTwQhDt"
    "NpRoErdy3aapbomfBw5MN0pMlMA6s7Tj2If2yK8Qev5xACt0PwcPy25jC3G636lV1pXSTA"
    "n1XsuvQUlXVoWPNl4/KZPCT3r2Gf5+Tf3G2nXVcEKeNeqFbUcfatJWsCEacOoc8OcKdESm"
    "yNi5fqqv8wpROkoQt6D88gdJ0ZDy3SrNhZl1/0TQsgwFNvRbKVVWrZ2aRZglR63lWjmHrs"
    "W4t+NS0KX4SwJAA7aQCzBamRtilVum6YmxejPfFxOAPABsvQTCRtT+GvE2a5tADLcikTpX"
    "QlSTIOeJQitLIx6owtTkn6oWvry8IibVnI7sqCidKHjIljP/Ubz9atiaSVVOv4891mU65Z"
    "t8IwpKHjQg4QnmVni2Mw43w08lZqyO3jmyel6jd2QkXFDZdvVW72Ekqq2Wn/jsOnGrTW7F"
    "QNvE8wRGKxVZSskboGKbtbuHdIucbbnpKuypS8+IQqX20mSWZ+zySfOpOMXuyODCUV8Y33"
    "BlbKUDL27M8bSoCO+R5Jdu6OzR5JxMnOZElLKL+plK8pnzcyi8hPYwmI4/CvCfCwsIhqFl"
    "GZAJXPHOYIhyTlQvtz1WlnjXKTFAPkNREbvHNRj+/nMGL8fjexzqEodz1fAppqz7iN5AOk"
    "BPzU6+XtP8/bZRY="
)
