from datetime import datetime, time
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, String, Time, orm
from sqlalchemy.orm import Mapped, mapped_column

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import GUID, auto_init

if TYPE_CHECKING:
    from group import Group


class GroupWebhooksModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "webhook_urls"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    group: Mapped[Optional["Group"]] = orm.relationship("Group", back_populates="webhooks", single_parent=True)
    group_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("groups.id"), index=True)

    enabled: Mapped[bool | None] = mapped_column(Boolean, default=False)
    name: Mapped[str | None] = mapped_column(String)
    url: Mapped[str | None] = mapped_column(String)

    # New Fields
    webhook_type: Mapped[str | None] = mapped_column(String, default="")  # Future use for different types of webhooks
    scheduled_time: Mapped[time | None] = mapped_column(Time, default=lambda: datetime.now().time())

    # Columne is no longer used but is kept for since it's super annoying to
    # delete a column in SQLite and it's not a big deal to keep it around
    time: Mapped[str | None] = mapped_column(String, default="00:00")

    @auto_init()
    def __init__(self, **_) -> None:
        ...
