from asgiref.sync import SyncToAsync, AsyncToSync
from django.db import close_old_connections


class DatabaseSyncToAsync(SyncToAsync):
    def thread_handler(self, loop, *args, **kwargs):
        close_old_connections()
        try:
            return super().thread_handler(loop, *args, **kwargs)
        finally:
            close_old_connections()


async_to_sync = AsyncToSync
database_sync_to_async = DatabaseSyncToAsync