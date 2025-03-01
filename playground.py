import asyncio

import grpc
from grpc import ChannelConnectivity

from kaspad_client.modules.KaspadClient import KaspadClient

MAX_MESSAGE_LENGTH = 1024 * 1024 * 1024  # 1GB

async def main():
    kaspad_client = KaspadClient("de4.kaspa.org", 8009)
    # kaspad_client = KaspadClient("104.11.218.93", 16210)

    # print the info message
    print(await kaspad_client.get_current_network())

    # returns
    # {'getInfoResponse': {'p2pId': 'a9728d7e-c07b-4641-936c-6c7442b819f8', 'serverVersion': '0.13.4',
    # 'isUtxoIndexed': True, 'isSynced': True, 'hasNotifyCommand': True, 'hasMessageId': True,
    # 'mempoolSize': '0'}, 'id': '0'}

    # now let's set up some notifications
    # the decorator registers an async callback function and requests the notification automatically
    # @kaspad_client.notify_virtual_daa_score_changed
    # async def received_new_daa_score(c):
    #     print(f"The DAA score is: {c['virtualDaaScoreChangedNotification']['virtualDaaScore']}")

    @kaspad_client.notify_block_added
    async def received_new_block(c):
        print(f"New Kaspa block: {c['blockAddedNotification']['block']['verboseData']['hash']}")

    # wait to see some notifcations :-)
    for i in range(60):
        await asyncio.sleep(3)
        # kaspad_client.kaspa_stream.reconnect()
        if kaspad_client.kaspa_stream.channel.get_state() == ChannelConnectivity.IDLE:
            print("reconnecting")
            await asyncio.sleep(5)
            kaspad_client.kaspa_stream.reconnect()
            await asyncio.sleep(5)
            print("reconnect done.")

            # kaspad_client.kaspa_stream.channel = grpc.aio.insecure_channel(f'127.0.0.1:16110',
            #                                          compression=grpc.Compression.Gzip,
            #                                          options=[
            #                                              ('kaspa_grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
            #                                              ('kaspa_grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
            #                                              ('grpc.max_connection_age_ms', 2000)
            #                                          ])
            #
            # kaspad_client.kaspa_stream.stub = messages_pb2_grpc.RPCStub(kaspad_client.kaspa_stream.channel)
            # asyncio.get_running_loop().create_task(self.__loop())

        print(await kaspad_client.get_current_network())


asyncio.run(main())
