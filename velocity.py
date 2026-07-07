from datetime import datetime

from config import (
    MIN_DAILY_SALES,
    SELL_OUT_REMAINING
)


def _parse_date(date_str):
    """Roblox отдаёт даты вида '2026-07-05T00:00:00Z' - убираем Z для fromisoformat."""
    if date_str.endswith("Z"):
        date_str = date_str[:-1] + "+00:00"
    return datetime.fromisoformat(date_str)


def calculate_average_sales(resale_data):
    """
    Считает СРЕДНИЕ ПРОДАЖИ В ДЕНЬ, учитывая, что между точками
    volumeDataPoints не всегда ровно 1 день (иногда 4+ дня разницы).

    Раньше: sold = previous - current (без учёта реального интервала дат) -
    для точек с разницей в несколько дней это завышало "продажи в день"
    в разы (диф за 4 дня выдавался как диф за 1 день).

    Теперь: sold_per_day = (previous - current) / кол-во_дней_между_точками.

    Возвращает (avg_per_day: float, per_day_rates: list[float])
    per_day_rates идёт в том же порядке, что и исходные точки (новые -> старые),
    используется только для отображения истории в Discord.
    """

    if not resale_data:
        return 0, []

    points = resale_data.get("volumeDataPoints", [])

    if len(points) < 2:
        return 0, []

    # Оставляем только точки, где есть и value, и date
    clean_points = [
        p for p in points
        if p.get("value") is not None and p.get("date")
    ]

    if len(clean_points) < 2:
        return 0, []

    per_day_rates = []

    for i in range(len(clean_points) - 1):
        newer = clean_points[i]
        older = clean_points[i + 1]

        try:
            newer_date = _parse_date(newer["date"])
            older_date = _parse_date(older["date"])
        except (ValueError, TypeError):
            continue

        days_gap = (newer_date - older_date).days

        if days_gap <= 0:
            # Даты совпадают или идут не по порядку - пропускаем точку,
            # чтобы не делить на ноль и не получить мусорные числа
            continue

        diff = older["value"] - newer["value"]

        if diff < 0:
            diff = 0

        rate_per_day = diff / days_gap

        per_day_rates.append(round(rate_per_day, 2))

    if not per_day_rates:
        return 0, []

    avg = sum(per_day_rates) / len(per_day_rates)

    return round(avg, 2), per_day_rates


def should_notify(

    item,

    marketplace,

    resale,

    cache_item

):

    remaining = marketplace.get("remaining")

    stock = marketplace.get("stock")

    sales = marketplace.get("sales")

    avg_sales, history = calculate_average_sales(
        resale
    )

    notify = False

    reason = ""

    # --------------------------------------------------
    # 1. Хороший обычный Limited
    # --------------------------------------------------

    if (

        stock is not None

        and

        300 <= stock <= 1500

        and

        avg_sales >= MIN_DAILY_SALES

    ):

        notify = True

        reason = "GOOD_LIMITED"

    # --------------------------------------------------
    # 2. Почти раскупили
    # --------------------------------------------------

    if (

        remaining is not None

        and

        remaining <= SELL_OUT_REMAINING

        and

        avg_sales >= MIN_DAILY_SALES

    ):

        notify = True

        reason = "SELLING_OUT"

    # --------------------------------------------------
    # 3. Остаток резко уменьшился
    # --------------------------------------------------

    if cache_item:

        old_remaining = cache_item.get(
            "remaining"
        )

        if (

            old_remaining is not None

            and

            remaining is not None

        ):

            diff = old_remaining - remaining

            if diff >= 25:

                notify = True

                reason = f"-{diff} stock"

    result = {

        "notify": notify,

        "reason": reason,

        "averageSales": avg_sales,

        "history": history,

        "remaining": remaining,

        "stock": stock,

        "sales": sales

    }

    return result