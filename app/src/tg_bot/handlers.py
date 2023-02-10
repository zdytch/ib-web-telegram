from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from services import crud
from . import keyboards
from . import templates

_details_data = CallbackData('details', 'entity', 'id')


def setup_handlers(dp: Dispatcher):
    dp.register_message_handler(_start, commands=['start'])  # TODO 'help'
    dp.register_message_handler(_positions, commands=['positions'])
    dp.register_message_handler(_orders, commands=['orders'])
    dp.register_message_handler(_unknown_message)

    dp.register_callback_query_handler(
        _position_details, _details_data.filter(entity='position')
    )
    dp.register_callback_query_handler(
        _order_details, _details_data.filter(entity='order')
    )


async def _start(message: Message):
    kb = keyboards.main_menu_keyboard()
    await message.answer(f'Welcome!', reply_markup=kb)


async def _positions(message: Message):
    if positions := await crud.get_position_list():
        kb = keyboards.position_list_keyboard(positions, _details_data)
        await message.answer(f'Total Positions: {len(positions)}', reply_markup=kb)

    else:
        await message.answer('No positions')


async def _orders(message: Message):
    if orders := await crud.get_order_list():
        kb = keyboards.order_list_keyboard(orders, _details_data)
        await message.answer(f'Total Orders: {len(orders)}', reply_markup=kb)

    else:
        await message.answer('No orders')


async def _unknown_message(message: Message):
    await message.delete()


async def _position_details(callback: CallbackQuery, data: dict):
    if position := await crud.get_position(data['id']):
        await callback.message.answer(templates.render_template(position))


async def _order_details(callback: CallbackQuery, data: dict):
    if order := await crud.get_order(int(data['id'])):
        await callback.message.answer(templates.render_template(order))
