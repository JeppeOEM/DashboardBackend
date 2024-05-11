from binance.client import Client
from django.core.management.base import BaseCommand

from core.models import Base, Coin


class Command(BaseCommand):
    help = 'Seed database with coin data'

    def handle(self, *args, **options):
        flag = True
        new_coins = 0
        client = Client()
        dict_ = client.get_exchange_info()
        base_usdt = "USDT"
        base_eth = "ETH"
        Base.objects.get_or_create(name=base_usdt)
        Base.objects.get_or_create(name=base_eth)
        usdt = [i['symbol']
                for i in dict_['symbols'] if i['symbol'].endswith(base_usdt)]
        eth = [i['symbol']
               for i in dict_['symbols'] if i['symbol'].endswith(base_eth)]
        # sym = [i['symbol'] for i in dict_['symbols'] if i['symbol'].endswith('ETH')]
        sym = usdt + eth
        for symbol in sym:
            coin, created = Coin.objects.get_or_create(name=symbol)
            if created:
                flag = False
                new_coins += 1

            # else:
            #     self.stdout.write(self.style.WARNING(f'Coin already exists: {coin.name}'))
        if flag:
            self.stdout.write(self.style.WARNING(
                'No new coins inserted in database'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Created {new_coins} coins in the database'))
