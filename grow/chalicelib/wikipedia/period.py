"""Helper functions on period."""
from chalicelib.wikipedia.client import per_article, top

from chalicelib.utils.utils import (
    __days_ago__,
    __today__,
    __avg__,
    __week_list_from_day__,
    __sum_nested__,
)

from concurrent import futures


def sum_between(
    project, page, start_date, end_date, agent="all-agents", access="all-access"
):
    """Page views given start and end dates."""
    views = per_article(project, page, start_date, end_date, access=access, agent=agent)

    view_sum = sum([daily["views"] for daily in views["items"]])
    max_view = max(views.get("items"), key=lambda x: x["views"])

    views["total_views"] = view_sum
    views["max_view"] = max_view

    return views


def sum_last(project, page, last=30, agent="all-agents", access="all-access"):
    """Page views during last days."""
    views = per_article(
        project, page, __days_ago__(last), __today__(), access=access, agent=agent
    )
    return sum([daily["views"] for daily in views["items"]])


def avg_last(project, page, last=30, agent="all-agents", access="all-access"):
    """Page views during last days."""
    views = per_article(
        project, page, __days_ago__(last), __today__(), access=access, agent=agent
    )
    return __avg__([daily["views"] for daily in views["items"]])


def __unravel_top_request__(top_object):
    return top(
        top_object.get("project"),
        top_object.get("year"),
        top_object.get("month"),
        top_object.get("day"),
        top_object.get("access"),
    )


def weekly_view_sum(project, year, month, day, access="all-access"):
    datetime_str = year + "/" + month + "/" + day

    response_dates = __week_list_from_day__(datetime_str)

    request_object = []
    for date_tuple in response_dates:
        request_object.append(
            {
                "project": project,
                "year": date_tuple[0],
                "month": str(date_tuple[1]).zfill(2),
                "day": str(date_tuple[2]).zfill(2),
                "access": access,
            }
        )

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        res = executor.map(__unravel_top_request__, request_object)
    response_object = list(res)

    summed_views = __sum_nested__(response_object)
    sorted_by_views = sorted(summed_views.items(), key=lambda x: x[1], reverse=True)
    response = [
        {"article": j[0], "views": j[1], "rank": i + 1}
        for i, j in enumerate(sorted_by_views)
    ]

    result = {
        "items": [
            {
                "project": project,
                "access": access,
                "year": year,
                "month": str(month).zfill(2),
                "day": str(day).zfill(2),
                "articles": response,
            }
        ]
    }

    return result
