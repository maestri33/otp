from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
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
    "eJztl21P2zAQx79KlVdMYlPpSkF710E3mKBFkG0IhCw3dpMIxw62M6gQ3322kzSJm3Qtok"
    "ClvUv+dxff/XJ+enQihjARn0bu2QnznS+tR4fCCKsHy7LdcmAcF7oWJBwT48pkDAjzjQjH"
    "QnLoSaVPIBFYSQgLj4exDBlVKk0I0SLzlGNI/UJKaHiXYCCZj2WAuTJc3yg5pAg/YJG/xr"
    "dgEmKCKsmGSI9tdCCnsdGOqfxmHPVoY+AxkkS0cI6nMmB05h1SqVUfU8yhxPrzkic6fZ1d"
    "VmleUZpp4ZKmWIpBeAITIkvlLsnAY1TzU9kIU6CvR/nY2enudfc/97r7ysVkMlP2ntLyit"
    "rTQENg6DpPxg4lTD0MxoIbfpCYU0hAHcCDAPJ6glaYhVIVYKPMwS1imQvrgxnBB0Aw9WWg"
    "Ce7uLkD3q39+cNQ/31JeH3QxTPV02uzDzNRJbZpvwdNTkwMEUASr0KwErYtlMRnXAbPXXY"
    "Jlr9uIUpuqJIWEMhGrYCwiXo9h6aMv1pftZdqy3dyVbRtlhIWAPq6d442LZDXo34tlDdFs"
    "+r5mU77IcllaHjlnHCAsYUjm2blqGWxYH624ZzXk6+NbwMYdXLo650iIO1JuuK3T/qXpxW"
    "iaWU5Gw++5e6lBD05GXy28fzAP1WAIQDlP91CRkWGE6wlboRZglMV+yh82Dvfx6eDC7Z+e"
    "VZgf9t2BtnQqvHN1q2etCbOPtH4fu0ct/dq6Gg0HBhgT0udmxMLPvXJ0TjCRDFB2DyAql5"
    "3LuVTd+DjWaJ/xJ6uRL/Aj32IzVDWgESXTrI825M9mLT/3Y/Uxe3JbOjBqYQy923vIEZiz"
    "sA5r8p03RZ3IViBVGw3K4Oo0s6tHX81xL3BqLiWZZXvRpQQWPv+vJO9uj22+kqiVXeiUVj"
    "j5lUI28/i8lruInhorQMzcNxPgTnuZU7PyagRobPZljkpMaza0HxejYdNVbhZigfxJVYHX"
    "KPTkdouEQt68T6wLKOqqFx8B7dOetRvpD+gj4JtuL09/Ae1XCsA="
)
