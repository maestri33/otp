"""
OTPConfig model — global OTP configuration (single-row).

Only ONE row exists in this table. Created automatically
on first initialization if it doesn't exist.
"""

from tortoise import fields
from tortoise.models import Model


class OTPConfig(Model):
    id = fields.IntField(pk=True)
    footer: str = fields.CharField(max_length=255, default="Equipe OTP")
    ttl_s: int = fields.IntField(default=300)  # 5 minutes
    num_digits: int = fields.IntField(default=6)
    max_attempts: int = fields.IntField(default=3)  # attempts before invalidation
    active: bool = fields.BooleanField(default=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "otp_config"

    def __str__(self) -> str:
        return (
            f"OTPConfig(ttl={self.ttl_s}s, digits={self.num_digits}, "
            f"active={self.active})"
        )
