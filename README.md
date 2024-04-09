This is a simple gRPC client for a python application which communiactes with the Kaspa node called KASPAD.

The module is based on asyncio, since the Kaspa BlockDAG is unbelievable fast and also needs the support of notifications.

# Usage: see playground.py

    import asyncio

    from kaspad_client.modules.KaspadClient import KaspadClient
    
    
    async def main():
        kaspad_client = KaspadClient("127.0.0.1", 16110)
    
        # print the info message
        print(await kaspad_client.get_info())
    
        # returns
        # {'getInfoResponse': {'p2pId': 'a9728d7e-c07b-4641-936c-6c7442b819f8', 'serverVersion': '0.13.4',
        # 'isUtxoIndexed': True, 'isSynced': True, 'hasNotifyCommand': True, 'hasMessageId': True,
        # 'mempoolSize': '0'}, 'id': '0'}
    
    
        # now let's set up some notifications
        # the decorator registers an async callback function and requests the notification automatically

        @kaspad_client.notify_virtual_daa_score_changed
        async def received_new_daa_score(c):
            print(f"The DAA score is: {c['virtualDaaScoreChangedNotification']['virtualDaaScore']}")
    
        @kaspad_client.notify_virtual_daa_score_changed
        async def received_new_daa_score2(c):
            print(f"The DAA2 score is: {c['virtualDaaScoreChangedNotification']['virtualDaaScore']}")
    
        @kaspad_client.notify_block_added
        async def received_new_daa_score(c):
            print(f"New Kaspa block: {c['blockAddedNotification']['block']['verboseData']['hash']}")
    
        # wait to see some notifcations :-)
        await asyncio.sleep(60)
    
    
    
    asyncio.run(main())
    
    


# Donation

We are doing this in our free time. Please consider a donation if this helps! Thank you!

[kaspa:qrlsm9tvmak6909pr9f35g6scapz5t689nhhls54sfxx5m46sn085ajhn9hn8](https://explorer.kaspa.org/addresses/kaspa:qrlsm9tvmak6909pr9f35g6scapz5t689nhhls54sfxx5m46sn085ajhn9hn8?page=1)
