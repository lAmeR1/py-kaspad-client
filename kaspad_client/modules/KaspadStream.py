# encoding: utf-8
import asyncio
import logging

import grpc
from google.protobuf import json_format

from ..kaspa_grpc import messages_pb2_grpc
from ..kaspa_grpc.messages_pb2 import KaspadRequest

MAX_MESSAGE_LENGTH = 1024 * 1024 * 1024  # 1GB

_logger = logging.getLogger(__name__)


# pipenv run python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/rpc.proto ./protos/messages.proto ./protos/p2p.proto

class KaspadStream(object):
    def __init__(self, kaspad_host: str, kaspad_port: int = 16110):

        self.__kaspad_host = kaspad_host
        self.__kaspad_port = kaspad_port

        self.__command_queue = asyncio.queues.Queue()
        self.__read_queue = asyncio.queues.Queue()

        self.__callback_functions = {}
        self.reconnect()

    def reconnect(self):
        try:
            self.__loop_task.cancel()
        except Exception:
            pass
        self.channel = grpc.aio.insecure_channel(f'{self.__kaspad_host}:{self.__kaspad_port}',
                                                 compression=grpc.Compression.Gzip,
                                                 options=[
                                                     ('kaspa_grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
                                                     ('kaspa_grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
                                                     ('grpc.max_connection_age_ms', 2000)
                                                 ])

        self.stub = messages_pb2_grpc.RPCStub(self.channel)
        self.__loop_task = asyncio.get_running_loop().create_task(self.__loop())


    async def read(self, wait_for_response_key=None):
        while True:
            response = await self.__read_queue.get()
            if wait_for_response_key is None or wait_for_response_key in response:
                return response

    async def send(self, command: str, params: dict = None):
        print(command)
        await self.__command_queue.put((command, params))

    async def __loop(self):
        async for resp in self.stub.MessageStream(self.yield_cmd()):
            await self.__read_queue.put(msg := json_format.MessageToDict(resp, including_default_value_fields=True))
            _logger.debug(f"recv: {msg}")
            for callback in self.__callback_functions.get(next(iter(msg)), []):
                await callback(msg)

    async def yield_cmd(self):
        while True:
            (cmd, params) = await self.__command_queue.get()
            _logger.debug(f"send: {cmd}")
            msg = KaspadRequest()
            msg2 = getattr(msg, cmd)
            payload = params

            if payload:
                if isinstance(payload, dict):
                    json_format.ParseDict(payload, msg2)
                if isinstance(payload, str):
                    json_format.Parse(payload, msg2)

            msg2.SetInParent()
            yield msg

    async def register_callback(self, response, callback):
        self.__callback_functions[response] = self.__callback_functions.get(response, []) + [callback]
