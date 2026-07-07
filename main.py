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

print("Roblox UGC Monitor V3 (economy.roblox.com для остатка)")

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

        checked = 0
        skipped_cooldown = 0

        # ----------------------------------------
        # Анализируем каждый предмет
        # ----------------------------------------

        for item in all_items:

            asset_id = item["assetId"]

            # Уже отправляли уведомление - вообще не трогаем
            if cache.is_notified(asset_id):
                continue

            # "Остывание" - не долбим economy.roblox.com по одному и тому же
            # предмету каждые 8 секунд, проверяем не чаще раза в 5 минут
            if not cache.needs_recheck(asset_id, ECONOMY_RECHECK_COOLDOWN):
                skipped_cooldown += 1
                continue

            market = api.get_economy_details(asset_id)

            time.sleep(ECONOMY_ITEM_DELAY)

            checked += 1

            if not market:
                # Не лимитка или запрос не удался - помечаем как проверенное,
                # чтобы не долбить снова каждый цикл, но без notified
                cache.update(
                    asset_id=asset_id,
                    remaining=None,
                    sales=None,
                    stock=None
                )
                continue

            # История продаж нужна только если предмет
            # потенциально интересный
            resale = api.get_resale(
                item["collectibleId"]
            )

            cache_item = cache.get(asset_id)

            analysis = should_notify(

                item,

                market,

                resale,

                cache_item

            )

            cache.update(

                asset_id=asset_id,

                remaining=analysis["remaining"],

                sales=analysis["sales"],

                stock=analysis["stock"]

            )

            # Не подходит
            if not analysis["notify"]:

                print(
                    f"[SKIP] {item['name']} | stock={analysis['stock']}, "
                    f"remaining={analysis['remaining']}, avg_sales={analysis['averageSales']}"
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
            f"Проверено новых: {checked} | пропущено по cooldown: {skipped_cooldown} | всего в каталоге: {len(all_items)}"
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
