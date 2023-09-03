from telebot.handler_backends import State, StatesGroup


class BestState(StatesGroup):
    """
    bestdeal command class
    """
    location = State()
    offers_count = State()
    clients_count = State()
    pictures_count = State()
    minp = State()
    maxp = State()
    mind = State()
    maxd = State()


class HighState(StatesGroup):
    """
    highprice command class
    """
    location = State()
    offers_count = State()
    clients_count = State()
    pictures_count = State()


class LowState(StatesGroup):
    """
    lowprice command class
    """
    location = State()
    offers_count = State()
    clients_count = State()
    pictures_count = State()





