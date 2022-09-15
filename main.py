from datetime import date, datetime
from werkzeug.exceptions import HTTPException
import os

import frontmatter
import markdown
from flask import Flask, render_template, abort, Response

app = Flask(__name__)


@app.errorhandler(HTTPException)
def handle_errors(e):
    return Response(render_template("http_error.html", error=e), e.code)


CONTENT_DIR = os.environ.get("WWW_CONTENT_DIR", os.path.join(os.getcwd(), "content"))


class PageTree:
    def __init__(self, sort_attribute, first_item=None) -> None:
        self.sort_attribute = sort_attribute
        self.__tree = [None, first_item, None]
        self.__list = []

    def compare(self, leaf, new_item):
        if leaf[1] is None:
            return 1

        existing_item_attr = leaf[1][self.sort_attribute]
        new_item_attr = new_item[self.sort_attribute]
        if existing_item_attr > new_item_attr:
            return 0

        if existing_item_attr <= new_item_attr:
            return 2

    def add_leaf(self, new_item, leaf=None):
        if leaf is None:
            leaf = self.__tree

        new_index = self.compare(leaf, new_item)
        if new_index == 1:
            leaf[1] = new_item
            return

        if leaf[new_index] is None:
            leaf[new_index] = [None, new_item, None]
            return

        return self.add_leaf(new_item, leaf[new_index])

    def map_leaf(self, leaf=None):
        if leaf is None:
            leaf = self.__tree

        for petal in leaf:
            if petal is None:
                continue

            if isinstance(petal, list):
                self.map_leaf(petal)
                continue

            self.__list.append(petal)

    def push(self, new_item):
        """
        Add a new item to the tree
        """
        self.add_leaf(new_item)

    def get(self, order="asc"):
        """
        Flatten the tree and return a list
        """
        self.map_leaf()

        pages = self.__list

        if order == "desc":
            pages.reverse()

        return pages


def get_page_list(dir_path, sort_by="date", category=None, limit=5, order="desc"):
    content_path = os.path.join(CONTENT_DIR, dir_path)

    if not os.path.isdir(content_path):
        abort(404)

    pages = PageTree(sort_by)
    for file in os.listdir(content_path):
        if not file.endswith(".md"):
            continue

        file_path = os.path.join(content_path, file)
        with open(file_path) as f:
            page = frontmatter.load(f)
            page = page.metadata
            bare_name = file.split(".")[0]
            page["url"] = f"{dir_path}/{bare_name}"
            if not page["url"].startswith("/"):
                page["url"] = "/" + page["url"]

            if category is not None and "category" in page:
                if page["category"] != category:
                    continue

            try:
                pages.push(page)
            except:
                pass

    try:
        pages = pages.get(order=order)
    except:
        return []

    if limit is None:
        return pages

    return pages[:limit]


def get_page(path: str):
    content_path = os.path.join(CONTENT_DIR, f"{path}.md")

    try:
        with open(content_path) as f:
            page = frontmatter.load(f)
            content = markdown.markdown(page.content)

            if path.startswith("__"):
                abort(404)

            if "date" in page:
                if page["date"] > date.today():
                    abort(404)

            if "visible" in page:
                if page["visible"] != True:
                    abort(404)

            template = "page"
            if "template" in page:
                template = page["template"]

            breadcrumb = path.split("/")
            breadcrumb = list(filter(lambda t: t != "", breadcrumb))
            parent_dir = breadcrumb[:-1]
            dir_path = "/".join(parent_dir)

            siblings = get_page_list(dir_path, sort_by="title", limit=20, order="asc")

            context = {
                "content": content,
                **page.metadata,
                "siblings": siblings,
            }

            if len(parent_dir) > 0:
                context["parent"] = parent_dir[-1]

            return render_template(f"{template}.html", context=context)

    except FileNotFoundError:
        abort(404)
