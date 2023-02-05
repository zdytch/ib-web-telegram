from jinja2 import Environment, FileSystemLoader
from schemas import Position

_template_env = Environment(loader=FileSystemLoader('templates'))


def render_position(position: Position) -> str:
    return _template_env.get_template('position.html.j2').render(position=position)
