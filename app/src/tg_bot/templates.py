from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

_template_env = Environment(loader=FileSystemLoader('templates'))


def render_template(schema: BaseModel) -> str:
    name = schema.__class__.__name__.lower()

    return _template_env.get_template(f'{name}.html.j2').render(schema=schema)
