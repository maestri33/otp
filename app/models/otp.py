"""
OTPLog model — records every OTP operation.

Status values: generated, sent, verified, expired, failed.
"""

from tortoise import fields
from tortoise.models import Model


class OTPLog(Model):
    id = fields.IntField(pk=True)
    external_id = fields.CharField(max_length=255, index=True)
    code_hash = fields.CharField(max_length=64)  # SHA256 of the code
    status = fields.CharField(
        max_length=20,
        default="generated",
    )  # generated | sent | verified | expired | failed
    message_id = fields.IntField(null=True)  # id of the message in notify
    error_detail = fields.TextField(null=True)  # failure reason if any
    verified_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "otp_logs"

    def __str__(self) -> str:
        return f"OTPLog(id={self.id}, external_id={self.external_id!r}, status={self.status!r})"
