# ===========================
# Discord
# ===========================

WEBHOOK_URL = "https://discord.com/api/webhooks/1523682397605068861/hOuOUpb7EiBsLKJisC5G8K8U8K_RZgeHg_RJ5Jg8OGEo_4HmzSXl6lnpfjIwlnDTFU3v"

# ===========================
# Интервалы
# ===========================

CHECK_INTERVAL = 8
ITEM_DELAY = 0.15

CACHE_FILE = "seen_items.json"

# ===========================
# HTTP
# ===========================

HEADERS = {

    "User-Agent":
    "Mozilla/5.0"

}

# ===========================
# Roblox
# ===========================

CATALOG_URL = \
"https://catalog.roblox.com/v2/search/items/details"

THUMBNAIL_URL = \
"https://thumbnails.roblox.com/v1/assets"

MARKETPLACE_ITEMS_URL = \
"https://apis.roblox.com/marketplace-items/v1/items/details"

RESALE_URL = \
"https://apis.roblox.com/marketplace-sales/v1/item/{}/resale-data"

# ===========================
# Taxonomy
# ===========================

TAXONOMIES = {

    "Accessories":
    "wNYJso48d1XnhMyFWT3oX3",

    "Emotes":
    "ioNxAT977DFP2hMnAJbsbF",

}

SEARCH = {

    "salesTypeFilter": 2,

    "limit": 120,

    "minPrice": 1,

    "maxPrice": 350,

}

# ===========================
# Фильтры
# ===========================

MIN_STOCK = 300
MAX_STOCK = 1500

SELL_OUT_REMAINING = 200

MIN_DAILY_SALES = 20

MARKETPLACE_BATCH = 1  # временно уменьшено с 40 для диагностики - см. чат
