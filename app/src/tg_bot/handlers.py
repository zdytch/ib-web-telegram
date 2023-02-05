from aiogram.types import Message, CallbackQuery
from services import crud
from . import keyboards
from . import templates


async def start(message: Message):
    kb = keyboards.main_menu_keyboard()
    await message.answer(f'Welcome!', reply_markup=kb)


async def positions(message: Message):
    if positions := await crud.get_position_list():
        kb = keyboards.position_list_keyboard(positions)
        await message.answer(f'Total Positions: {len(positions)}', reply_markup=kb)

    else:
        await message.answer('No positions')


async def orders(message: Message):
    if orders := await crud.get_order_list():
        kb = keyboards.order_list_keyboard(orders)
        await message.answer(f'Total Orders: {len(orders)}', reply_markup=kb)

    else:
        await message.answer('No orders')


async def unknown_message(message: Message):
    await message.delete()


async def inline_callback(callback: CallbackQuery):
    if position := await crud.get_position(callback.data):
        await callback.message.answer(templates.render_template(position))

    elif order := await crud.get_order(int(callback.data)):
        await callback.message.answer(templates.render_template(order))
