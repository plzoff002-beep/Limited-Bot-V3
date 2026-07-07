import os
import time
import threading

from http.server import (
    HTTPServer,
    BaseHTTPRequestHandler
)

from config import *

from roblox_api import RobloxAPI
from cache import Cache
from velocity import should_notify
from discord_webhook import DiscordWebhook


class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)

        self.end_headers()

        self.wfile.write(
            b"Running"
        )

    def log_message(self, *args):
        return


def health_server():

    port = int(

        os.environ.get(

            "PORT",

            8080

        )

    )

    server = HTTPServer(

        ("0.0.0.0", port),

        HealthHandler

    )

    print(

        "Health:",

        port

    )

    server.serve_forever()


threading.Thread(

    target=health_server,

    daemon=True

).start()


api = RobloxAPI()

cache = Cache(
    CACHE_FILE
)

discord = DiscordWebhook()


print("=" * 60)

print("Roblox UGC Monitor V3")

print("=" * 60)

while True:

    try:

        all_items = []

        # --------------------------
        # Загружаем каталог
        # --------------------------

        for taxonomy in TAXONOMIES:

            print(f"\n[{taxonomy}]")

            items = api.search(taxonomy)

            print(

                "Found:",

                len(items)

            )

            all_items.extend(items)

        if not all_items:

            print("Каталог пуст")

            time.sleep(CHECK_INTERVAL)

            continue

        # --------------------------
        # Получаем Marketplace одним POST
        # --------------------------

        collectible_ids = [

            item["collectibleId"]

            for item in all_items

        ]

        marketplace = api.get_marketplace(

            collectible_ids

        )

        print(

            "Marketplace:",

            len(marketplace)

        )

        if not marketplace:

            time.sleep(CHECK_INTERVAL)

            continue

        # ----------------------------------------
        # Анализируем каждый предмет
        # ----------------------------------------

        for item in all_items:

            cid = item["collectibleId"]
            asset_id = item["assetId"]

            if cid not in marketplace:
                continue

            market = marketplace[cid]

            # ГЛАВНЫЙ ФИКС: если по этому предмету уже слали уведомление -
            # не трогаем его вообще (не тратим запрос на get_resale, не шлём повторно)
            if cache.is_notified(asset_id):
                continue

            # Проверяем только если реально есть остаток
            if market.get("remaining") is None:
                continue

            # История продаж нужна только если предмет
            # потенциально интересный
            resale = api.get_resale(
                cid
            )

            cache_item = cache.get(asset_id)

            analysis = should_notify(

                item,

                market,

                resale,

                cache_item

            )

            # Обновляем кэш данными, но notified оставляем как было
            # (True если уже слали раньше - но мы досюда не дошли бы, см. is_notified выше)
            cache.update(

                asset_id=asset_id,

                remaining=analysis["remaining"],

                sales=analysis["sales"],

                stock=analysis["stock"]

            )

            # Не подходит
            if not analysis["notify"]:

                print(

                    "[SKIP]",

                    item["name"],

                    "|",

                    analysis["reason"]

                )

                time.sleep(
                    ITEM_DELAY
                )

                continue

            # Картинка нужна только перед Discord
            item["thumbnail"] = api.get_thumbnail(

                asset_id

            )

            discord.send(

                item,

                analysis

            )

            # СТАВИМ ФЛАГ - теперь этот предмет больше не будет
            # проверяться повторно и спамить в Discord
            cache.update(

                asset_id=asset_id,

                remaining=analysis["remaining"],

                sales=analysis["sales"],

                stock=analysis["stock"],

                notified=True

            )

            print(

                "[SEND]",

                item["name"]

            )

            time.sleep(
                ITEM_DELAY
            )

        # ----------------------------------------
        # Сохраняем кэш
        # ----------------------------------------

        cache.save()

        print(
            "\nЦикл завершён."
        )

        print(
            f"Проверено: {len(all_items)} предметов"
        )

        print(
            f"Следующая проверка через {CHECK_INTERVAL} сек..."
        )

        time.sleep(
            CHECK_INTERVAL
        )

    except KeyboardInterrupt:

        print(
            "\nОстановка..."
        )

        cache.save()

        break

    except Exception as e:

        print(
            "\n[ERROR]",
            e
        )

        try:
            cache.save()
        except:
            pass

        time.sleep(10)