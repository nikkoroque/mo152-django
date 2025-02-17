import os
from django.core.management.commands.runserver import Command as RunserverCommand
from django.core.servers.basehttp import WSGIServer
import ssl

class SecureWSGIServer(WSGIServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.socket = ssl.wrap_socket(
            self.socket,
            keyfile='key.pem',
            certfile='cert.pem',
            server_side=True,
            ssl_version=ssl.PROTOCOL_TLSv1_2,
        )

class Command(RunserverCommand):
    def get_handler(self, *args, **options):
        handler = super().get_handler(*args, **options)
        self.server_class = SecureWSGIServer
        return handler