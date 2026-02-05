# app/client.py

from pybit.unified_trading import HTTP


class BybitClient:
    def __init__(self, testnet: bool):
        self.session = HTTP(testnet=testnet)

    def fetch_products(self):
        return self.session.get_earn_product_info(
            category="FlexibleSaving"
        )
