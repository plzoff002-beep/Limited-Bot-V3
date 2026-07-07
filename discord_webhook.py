import requests
from datetime import datetime, timezone

from config import WEBHOOK_URL


class DiscordWebhook:

    def __init__(self):
        self.url = WEBHOOK_URL

    def send(self, item, analysis):

        color = 0x2ECC71

        if analysis["reason"] == "SELLING_OUT":
            color = 0xE74C3C

        elif analysis["reason"] == "GOOD_LIMITED":
            color = 0x3498DB

        elif "stock" in analysis["reason"]:
            color = 0xF39C12

        history = analysis["history"]

        if history:
            history = " → ".join(
                str(x)
                for x in reversed(history[:7])
            )
        else:
            history = "Нет данных"

        embed = {

            "title": item["name"],

            "url": item["url"],

            "color": color,

            "thumbnail": {

                "url": item["thumbnail"]

            } if item.get("thumbnail") else None,

            "fields": [

                {

                    "name": "📢 Причина",

                    "value": analysis["reason"],

                    "inline": False

                },

                {

                    "name": "💰 Цена",

                    "value": f'{item.get("price")} R$',

                    "inline": True

                },

                {

                    "name": "📦 Общий тираж",

                    "value": str(analysis["stock"]),

                    "inline": True

                },

                {

                    "name": "🔥 Осталось",

                    "value": str(analysis["remaining"]),

                    "inline": True

                },

                {

                    "name": "🛒 Продано",

                    "value": str(analysis["sales"]),

                    "inline": True

                },

                {

                    "name": "⚡ Продаж в день",

                    "value": str(analysis["averageSales"]),

                    "inline": True

                },

                {

                    "name": "👤 Создатель",

                    "value": item["creator"],

                    "inline": True

                },

                {

                    "name": "📂 Категория",

                    "value": item["category"],

                    "inline": True

                },

                {

                    "name": "📈 Последние продажи",

                    "value": history,

                    "inline": False

                },

                {

                    "name": "🔗 Roblox",

                    "value": item["url"],

                    "inline": False

                }

            ],

            "footer": {

                "text": "UGC Limited Monitor v2"

            },

            "timestamp": datetime.now(

                timezone.utc

            ).isoformat()

        }

        payload = {

            "embeds": [

                embed

            ]

        }

        try:

            r = requests.post(

                self.url,

                json=payload,

                timeout=20

            )

            if r.status_code not in (

                200,

                204

            ):

                print(

                    "Discord:",

                    r.status_code,

                    r.text

                )

            else:

                print(

                    "[DISCORD]",

                    item["name"]

                )

        except Exception as e:

            print(e)