import time
import requests

from config import (
    HEADERS,
    SEARCH,
    TAXONOMIES,
    CATALOG_URL,
    THUMBNAIL_URL,
    MARKETPLACE_ITEMS_URL,
    RESALE_URL,
    MARKETPLACE_BATCH,
    MARKETPLACE_BATCH_DELAY
)


class RobloxAPI:

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update(
            HEADERS
        )

        self.csrf = None


    def request(
        self,
        method,
        url,
        **kwargs
    ):

        for attempt in range(5):

            try:

                r = self.session.request(

                    method,

                    url,

                    timeout=20,

                    **kwargs

                )

                # Roblox требует CSRF для POST
                if (

                    r.status_code == 403

                    and

                    "x-csrf-token" in r.headers

                ):

                    self.csrf = r.headers[
                        "x-csrf-token"
                    ]

                    self.session.headers[
                        "x-csrf-token"
                    ] = self.csrf

                    print(
                        f"[CSRF] Получен токен, повторяю запрос: {url}"
                    )

                    continue

                if r.status_code == 429:

                    wait = (attempt + 1) * 3

                    print(
                        f"429 -> sleep {wait}s ({url})"
                    )

                    time.sleep(wait)

                    continue

                if r.status_code >= 400:

                    print(
                        f"[HTTP {r.status_code}] {url}"
                    )

                    print(
                        f"  Response body: {r.text[:500]}"
                    )

                r.raise_for_status()

                parsed = r.json()

                if not parsed:
                    print(f"[EMPTY 200] {url}")
                    print(f"  Raw body: {r.text[:500]}")

                return parsed

            except Exception as e:

                print(f"[REQUEST ERROR] {url} -> {e}")

                time.sleep(2)

        print(f"[FAILED] Все попытки исчерпаны: {url}")

        return None


    def search(
        self,
        taxonomy
    ):

        params = dict(
            SEARCH
        )

        params[
            "taxonomy"
        ] = TAXONOMIES[
            taxonomy
        ]

        data = self.request(

            "GET",

            CATALOG_URL,

            params=params

        )

        if not data:

            return []

        result = []

        for item in data.get(
            "data",
            []
        ):

            collectible = item.get(
                "collectibleItemId"
            )

            if not collectible:
                continue

            result.append({

                "assetId":
                    item["id"],

                "collectibleId":
                    collectible,

                "name":
                    item["name"],

                "creator":
                    item.get(
                        "creatorName",
                        "Unknown"
                    ),

                "price":
                    item.get("price"),

                "stock":
                    item.get(
                        "totalQuantity"
                    ),

                "created":
                    item.get(
                        "itemCreatedUtc"
                    ),

                "category":
                    taxonomy,

                "url":
                    f"https://www.roblox.com/catalog/{item['id']}"

            })

        return result

    def get_marketplace(self, collectible_ids):

        result = {}

        for i in range(0, len(collectible_ids), MARKETPLACE_BATCH):

            batch = collectible_ids[i:i + MARKETPLACE_BATCH]

            data = self.request(

                "POST",

                MARKETPLACE_ITEMS_URL,

                json={
                    "itemIds": batch
                }

            )

            if not data:
                print(f"[MARKETPLACE] Батч {i}-{i+len(batch)} вернул пусто ({len(batch)} id)")
                time.sleep(MARKETPLACE_BATCH_DELAY)
                continue

            time.sleep(MARKETPLACE_BATCH_DELAY)

            for item in data:

                cid = item.get("collectibleItemId")

                if not cid:
                    continue

                result[cid] = {

                    "remaining":
                        item.get("unitsAvailableForConsumption"),

                    "stock":
                        item.get("assetStock"),

                    "sales":
                        item.get("sales"),

                    "lowestPrice":
                        item.get("lowestPrice"),

                    "collectibleProductId":
                        item.get("collectibleProductId")

                }

        return result


    def get_thumbnail(self, asset_id):

        data = self.request(

            "GET",

            THUMBNAIL_URL,

            params={

                "assetIds": asset_id,

                "size": "420x420",

                "format": "Png",

                "isCircular": "false"

            }

        )

        if not data:
            return None

        images = data.get("data")

        if not images:
            return None

        return images[0].get("imageUrl")


    def get_resale(self, collectible_id):

        url = RESALE_URL.format(
            collectible_id
        )

        return self.request(

            "GET",

            url

        )
