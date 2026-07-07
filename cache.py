import json
import os
from datetime import datetime


class Cache:

    def __init__(self, filename):

        self.filename = filename

        self.data = self.load()

    def load(self):

        if not os.path.exists(self.filename):
            return {}

        try:

            with open(
                self.filename,
                "r",
                encoding="utf8"
            ) as f:

                return json.load(f)

        except Exception:

            return {}

    def save(self):

        with open(
            self.filename,
            "w",
            encoding="utf8"
        ) as f:

            json.dump(

                self.data,

                f,

                indent=4,

                ensure_ascii=False

            )

    def get(self, asset_id):

        return self.data.get(
            str(asset_id)
        )

    def is_notified(self, asset_id):
        """Уже отправляли уведомление по этому предмету?"""
        entry = self.data.get(str(asset_id))
        return bool(entry and entry.get("notified"))

    def update(

        self,

        asset_id,

        remaining,

        sales,

        stock,

        notified=None

    ):

        entry = self.data.get(str(asset_id), {})

        # Если notified не передали явно - сохраняем прошлое значение
        # (чтобы обновление remaining/sales не сбрасывало флаг отправки)
        if notified is None:
            notified = entry.get("notified", False)

        self.data[str(asset_id)] = {

            "remaining": remaining,

            "sales": sales,

            "stock": stock,

            "notified": notified,

            "updated": datetime.utcnow().isoformat()

        }

    def remove(self, asset_id):

        asset_id = str(asset_id)

        if asset_id in self.data:

            del self.data[asset_id]

    def clear(self):

        self.data = {}

        self.save()