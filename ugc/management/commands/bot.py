from collections import defaultdict
import telebot
from django.core.management import BaseCommand
from django.conf import settings
from ugc.models import Profile, Place

NAME, CORDS, PHOTO, SAVE = range(1, 5)
USER_STATE = defaultdict(lambda : 0)
PLACE = defaultdict(lambda : {})

def get_state(message):
    return USER_STATE[message.chat.id]
def update_state(message, state):
    USER_STATE[message.chat.id] = state

def update_place(user_id, key, value):
    PLACE[user_id][key] = value
def get_place(user_id):
    return PLACE[user_id]

def save_place(message):
    pr, _ = Profile.objects.get_or_create(
        external_id=message.chat.id,
        defaults = {
            'name': message.from_user.username,
        }
    )

    place = PLACE[message.chat.id]
    name = place['name']
    lat = place['lat']
    lon = place['lon']
    photo = place['photo']

    pl = Place.objects.create(
        profile=pr,
        name=name,
        lat=lat,
        lon=lon,
        file_id=photo,
    )
    pl.save()


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        bot = telebot.TeleBot(settings.TOKEN)

        @bot.message_handler(commands=['add'])
        def handle_add(message):
            bot.send_message(chat_id=message.chat.id, text='Укажите название места')
            update_state(message, NAME)

        @bot.message_handler(func=lambda message: get_state(message) == NAME)
        def handle_name(message):
            update_place(message.chat.id, 'name', message.text)
            bot.send_message(chat_id=message.chat.id, text='Введите координаты местоположения')
            update_state(message, CORDS)

        @bot.message_handler(func=lambda message: get_state(message) == CORDS, content_types=['location'])
        def handle_location(message):
            lat = message.location.latitude
            update_place(message.chat.id, 'lat', message.location.latitude)
            update_place(message.chat.id, 'lon', message.location.longitude)
            bot.send_message(chat_id=message.chat.id, text='Отправьте фотографию места')
            update_state(message, PHOTO)

        @bot.message_handler(func=lambda message: get_state(message) == PHOTO, content_types=['photo'])
        def handle_photo(message):
            fileID = message.photo[-1].file_id
            update_place(message.chat.id, 'photo', fileID)
            pl = get_place(message.chat.id)['name']
            bot.send_message(chat_id=message.chat.id, text=f'Сохранить место: {pl}?')
            update_state(message, SAVE)

        @bot.message_handler(func=lambda message: get_state(message) == SAVE)
        def handle_save(message):
            if 'да' in message.text:
                save_place(message)
                bot.send_message(chat_id=message.chat.id, text='Место сохранено')
            update_state(message, 0)

        @bot.message_handler(commands=['get'])
        def get_queryset(message):
            try:
                user = Profile.objects.get(external_id=message.chat.id)
                places = Place.objects.filter(profile=user).order_by('-pk')[:10]
                for p in places:
                    bot.send_message(chat_id=message.chat.id, text=f'{p.name}')
                    bot.send_location(chat_id=message.chat.id, latitude=p.lat, longitude=p.lon)
                    bot.send_photo(chat_id=message.chat.id, photo=p.file_id)
            except Profile.DoesNotExists:
                bot.send_message(chat_id=message.chat.id, text='Вы еще не отправляли места')

        @bot.message_handler(commands=['reset'])
        def reset_places(message):
            try:
                user = Profile.objects.get(external_id=message.chat.id)
                places = Place.objects.filter(profile=user)
                for p in places:
                    p.delete()
                bot.send_message(chat_id=message.chat.id, text='Все места удалены')
            except Profile.DoesNotExists:
                bot.send_message(chat_id=message.chat.id, text='Вы еще не отправляли места')



        bot.polling()