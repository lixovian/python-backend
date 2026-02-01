from typing import Any, Dict

from flask import Flask, jsonify, request
from dotenv import dotenv_values

from controllers import operation

app = Flask(__name__)


def _to_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    return s in {"1", "true", "yes", "y", "on"}


def get_config() -> Dict[str, Any]:
    return dict(dotenv_values(".env"))


def get_port() -> int:
    config = get_config()
    raw = config.get("PORT")
    try:
        return int(raw) if raw is not None else 5000
    except (TypeError, ValueError):
        return 5000


def get_debug() -> bool:
    config = get_config()
    return _to_bool(config.get("DEBUG"), default=True)


@app.route("/")
def server_info() -> str:
    return "My server"


@app.route("/author")
def author():
    author_data = {
        "name": "Kirill",
        "course": 2,
        "age": 19,
    }
    return jsonify(author_data)


@app.route("/sum")
def runner():
    a = request.args.get("a", type=int)
    b = request.args.get("b", type=int)
    return jsonify({"sum": operation(a, b)})


if __name__ == "__main__":
    app.run(debug=get_debug(), port=get_port())
