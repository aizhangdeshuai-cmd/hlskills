"""Read endpoint identifiers from an existing OpenAPI JSON paths inventory."""

import json
from urllib.parse import unquote, urlsplit


HTTP_METHODS = frozenset("get put post delete options head patch".split())


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("OpenAPI JSON 含重复键，无法确定唯一端点清单")
        result[key] = value
    return result


def path_item(document, item):
    seen = set()
    while isinstance(item, dict) and "$ref" in item:
        ref = item["$ref"]
        if not isinstance(ref, str) or not ref.startswith("#/"):
            raise ValueError("端点引用了外部文件，请使用已解析的 OpenAPI 清单")
        if ref in seen or set(item) - {"$ref", "summary", "description", "parameters"}:
            raise ValueError("端点引用循环或包含覆盖项，请先解析 OpenAPI 引用")
        seen.add(ref)
        item = document
        for key in unquote(ref[2:]).split("/"):
            key = key.replace("~1", "/").replace("~0", "~")
            if not isinstance(item, dict) or key not in item:
                raise ValueError("OpenAPI 的本地端点引用无对应对象")
            item = item[key]
    if not isinstance(item, dict):
        raise ValueError("OpenAPI paths 内的端点定义须为对象")
    return item


def mount_prefixes(servers):
    if not isinstance(servers, list):
        raise ValueError("OpenAPI servers 必须是数组")
    prefixes = set()
    for server in servers:
        if not isinstance(server, dict) or not isinstance(server.get("url"), str):
            raise ValueError("OpenAPI server 缺少 URL")
        location = urlsplit(server["url"])
        path = location.path
        if (not server["url"] or (path and not path.startswith("/"))
                or "{" in path or "}" in path or location.query or location.fragment):
            raise ValueError("挂载前缀依赖部署上下文，请使用实际路由导出清单")
        prefixes.add(path.rstrip("/"))
    return sorted(prefixes) or [""]


def endpoint_ids(path):
    """Read HTTP operations only. Never fetch reference URLs or execute commands."""
    document = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_keys)
    if not isinstance(document, dict) or not isinstance(document.get("paths"), dict):
        raise ValueError("OpenAPI JSON 缺少 paths 对象")
    if str(document.get("openapi", "")).startswith(("3.0.", "3.1.")):
        methods = HTTP_METHODS | {"trace"}
        servers = document.get("servers", [])
    elif document.get("swagger") == "2.0":
        methods = HTTP_METHODS
        servers = [{"url": document.get("basePath", "/")}]
    else:
        raise ValueError("支持 Swagger 2.0、OpenAPI 3.0/3.1 的 JSON 端点清单")

    identifiers = []
    for route, definition in document["paths"].items():
        if route.startswith("x-"):
            continue
        if not route.startswith("/"):
            raise ValueError("OpenAPI paths 的路径须以 / 开头")
        item = path_item(document, definition)
        for key, operation in item.items():
            if key in {"parameters", "summary", "description", "servers"} or key.startswith("x-"):
                continue
            if key not in methods or not isinstance(operation, dict):
                raise ValueError("OpenAPI 路径中存在无法识别的方法或无效的操作定义")
            active_servers = operation.get("servers", item.get("servers", servers))
            for prefix in mount_prefixes(active_servers):
                identifiers.append(f"{key.upper()} {prefix}{route}")
    return identifiers
