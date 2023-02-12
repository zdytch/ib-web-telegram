from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from . import keyboards
from . import templates
import services

_position_id_action = CallbackData('position', 'id', 'action')
_order_id_action = CallbackData('order', 'id', 'action')


def setup_handlers(dp: Dispatcher):
    dp.register_message_handler(_start, commands=['start'])  # TODO 'help'
    dp.register_message_handler(_positions, commands=['positions'])
    dp.register_message_handler(_orders, commands=['orders'])
    dp.register_message_handler(_unknown_message)

    dp.register_callback_query_handler(
        _position_details, _position_id_action.filter(action='view')
    )
    dp.register_callback_query_handler(
        _order_details, _order_id_action.filter(action='view')
    )


async def _start(message: Message):
    kb = keyboards.main_menu_keyboard()
    await message.answer(f'Welcome!', reply_markup=kb)


async def _positions(message: Message):
    if positions := await services.get_position_list():
        kb = keyboards.position_list_keyboard(positions, _position_id_action)
        await message.answer(f'Total Positions: {len(positions)}', reply_markup=kb)

    else:
        await message.answer('No positions')


async def _orders(message: Message):
    if orders := await services.get_order_list():
        kb = keyboards.order_list_keyboard(orders, _order_id_action)
        await message.answer(f'Total Orders: {len(orders)}', reply_markup=kb)

    else:
        await message.answer('No orders')


async def _unknown_message(message: Message):
    await message.delete()


async def _position_details(callback: CallbackQuery, callback_data: dict):
    if position := await services.get_position(int(callback_data['id'])):
        await callback.message.answer(templates.render_template(position))


async def _order_details(callback: CallbackQuery, callback_data: dict):
    if order := await services.get_order(int(callback_data['id'])):
        await callback.message.answer(templates.render_template(order))
