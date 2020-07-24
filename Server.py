import asyncio
import pickle
from Board import *


class Server:
    def __init__(self, hp=1, ip='127.0.0.1', port=8888, message_length=1e6):
        self.hp = hp
        self.current_connections = 0a
        self.players = list()
        self.board = Board()
        self.ip = ip
        self.port = port
        self.message_length = int(message_length)

    async def handle_echo(self, reader, writer):
        """
        on server side
        """
        data = await reader.read(self.message_length)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        print("received {} from {}".format(message, addr))

        sendback_message = message

        print("send: {}".format(sendback_message))
        writer.write(sendback_message.encode())
        await writer.drain()

        print("close the client socket")
        writer.close()


    async def run_forever(self):
        server = await asyncio.start_server(self.handle_echo, self.ip, self.port)

        # Serve requests until Ctrl+C is pressed
        print(f'serving on {server.sockets[0].getsockname()}')
        async with server:
            await server.serve_forever()
        # Close the server
        server.close()


