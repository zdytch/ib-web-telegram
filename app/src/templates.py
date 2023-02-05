from jinja2 import Environment, FileSystemLoader
from schemas import Position, Order

_template_env = Environment(loader=FileSystemLoader('templates'))


def render_position(position: Position) -> str:
    return _template_env.get_template('position.html.j2').render(position=position)


def render_order(order: Order) -> str:
    return _template_env.get_template('order.html.j2').render(order=order)
