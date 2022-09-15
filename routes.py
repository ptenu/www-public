from genericpath import isdir
from http.client import HTTPException
import os
from flask import abort, render_template, request, jsonify
from app import app, CONTENT_DIR, get_page, get_page_list
from payment import createCustomer, createPayment


@app.route("/")
def home():
    news_pages = get_page_list("news")
    info_pages = get_page_list("guides")
    return render_template(
        "home.html", context={"news": news_pages, "information": info_pages}
    )


@app.route("/<path:slug>")
def page(slug: str):
    file_path = os.path.join(CONTENT_DIR, f"{slug}.md")
    dir_path = os.path.join(CONTENT_DIR, slug)

    if os.path.isfile(file_path):
        return get_page(slug)

    if os.path.isdir(dir_path):
        pages = get_page_list(slug, limit=10)
        breadcrumb = slug.split("/")
        breadcrumb = list(filter(lambda t: t != "", breadcrumb))

        child_dirs = os.listdir(dir_path)
        children = []
        for cd in child_dirs:
            path = os.path.join(dir_path, cd)
            if not os.path.isdir(path):
                continue

            children.append({"label": cd.capitalize(), "url": f"/{slug}/{cd}"})

        context = {
            "pages": pages,
            "title": breadcrumb[-1],
            "breadcrumb": breadcrumb,
            "children": children,
        }

        return render_template(
            "list.html",
            context=context,
        )

    abort(404)
