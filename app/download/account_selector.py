"""Telegram account selection interface.

Keeps account scheduling independent from Telegram client and proxy plugins.
"""


class AccountSelector:
    def __init__(self, accounts=None):
        self.accounts = accounts or []

    async def select(self):
        """Return an available account.

        Real health scoring and load balancing will be implemented when the
        multi-account download pool is added.
        """
        for account in self.accounts:
            if getattr(account, "enabled", True):
                return account
        return None
