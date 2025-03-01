# encoding: utf-8
import asyncio

from kaspad_client.modules.KaspadStream import KaspadStream


# pipenv run python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/rpc.proto ./protos/messages.proto ./protos/p2p.proto


class KaspadClient(object):
    def __init__(self, kaspad_host: str, kaspad_port: int = 16110):
        self.kaspad_host = kaspad_host
        self.kaspad_port = kaspad_port

        self.server_version = None
        self.is_utxo_indexed = None
        self.is_synced = None
        self.p2p_id = None

        self.kaspa_stream = KaspadStream(self.kaspad_host, self.kaspad_port)
        self.__current_id = 1

    @property
    def next_id(self):
        if self.__current_id < 4294967295:  # 2^32 -1
            self.__current_id += 1
        else:
            self.__current_id = 1

        return self.__current_id

    async def request(
        self, command: str, params: dict = None, wait_for_response: bool = False
    ):
        msg_id = self.next_id if wait_for_response else None
        await self.kaspa_stream.send(command, params, msg_id)

        if wait_for_response:
            return await self.kaspa_stream.read(msg_id)

    # async def notify(self, command, params, callback):
    #     t = KaspadThread(self.kaspad_host, self.kaspad_port, async_thread=True)
    #     return await t.notify(command, params, callback)

    async def get_block_dag_info(self):
        """
        GetBlockDagInfoRequestMessage requests general information about the current state
        of this kaspad_client's DAG.
        :return:
        """
        return await self.request(
            "getBlockDagInfoRequest", "", "getBlockDagInfoResponse"
        )

    async def get_current_network(self):
        """
        GetCurrentNetworkRequestMessage requests the network kaspad_client is currently running against.

        Possible networks are: Mainnet, Testnet, Simnet, Devnet
        :return:
        """
        return await self.request(
            "getCurrentNetworkRequest", "", "getCurrentNetworkResponse"
        )

    async def submit_block(self, block: dict, allow_non_daa_blocks: bool):
        """
        SubmitBlockRequestMessage requests to submit a block into the DAG.
        Blocks are generally expected to have been generated using the getBlockTemplate call.

        See: GetBlockTemplateRequestMessage
        :param block:
        :param allow_non_daa_blocks:
        :return:
        """
        return await self.request(
            "submitBlockRequest",
            {"block": block, "allowNonDAABlocks": allow_non_daa_blocks},
            "submitBlockResponse",
        )

    async def get_block_template(self, pay_address: str, extra_data: bool):
        """
        GetBlockTemplateRequestMessage requests a current block template.
        Callers are expected to solve the block template and submit it using the submitBlock call
        :param pay_address:
        :param extra_data:
        :return:
        """
        return await self.request(
            "getBlockTemplateRequest",
            {"payAddress": pay_address, "extraData": extra_data},
            "getBlockTemplateResponse",
        )

    async def get_peer_addresses(self):
        """
        GetPeerAddressesRequestMessage requests the list of known kaspad_client addresses in the
        current network. (mainnet, testnet, etc.)
        :return:
        """
        return await self.request(
            "getPeerAddressesRequest", wait_for_response="getPeerAddressesResponse"
        )

    async def get_sink(self):
        """
        GetSinkRequestMessage requests the hash of the current virtual's
        selected parent.
        :return:
        """
        return await self.request("getSinkRequest", wait_for_response="getSinkResponse")

    async def get_mempool_entry(
        self, tx_id: str, include_orphan_pool: bool, filter_transaction_pool: bool
    ):
        """
        GetMempoolEntryRequestMessage requests information about a specific transaction
        in the mempool.
        :param tx_id:
        :param include_orphan_pool:
        :param filter_transaction_pool:
        :return:
        """
        return await self.request(
            "getMempoolEntryRequest",
            {
                "txId": tx_id,
                "includeOrphanPool": include_orphan_pool,
                "filterTransactionPool": filter_transaction_pool,
            },
            wait_for_response="getMempoolEntryResponse",
        )

    async def get_mempool_entries(
        self, include_orphan_pool: bool, filter_transaction_pool: bool
    ):
        """
        GetMempoolEntriesRequestMessage requests information about all the transactions
        currently in the mempool.
        :param include_orphan_pool:
        :param filter_transaction_pool:
        :return:
        """
        return await self.request(
            "getMempoolEntriesRequest",
            {
                "includeOrphanPool": include_orphan_pool,
                "filterTransactionPool": filter_transaction_pool,
            },
            wait_for_response="getMempoolEntriesResponse",
        )

    async def get_connected_peer_info(self):
        """
        GetConnectedPeerInfoRequestMessage requests information about all the p2p peers
        currently connected to this kaspad_client.
        :return:
        """
        return await self.request(
            "getConnectedPeerInfoRequest",
            wait_for_response="getConnectedPeerInfoResponse",
        )

    async def add_peer(self, address: str, is_permanent: bool):
        """
        AddPeerRequestMessage adds a peer to kaspad_client's outgoing connection list.
        This will, in most cases, result in kaspad_client connecting to said peer.
        :param address:
        :param is_permanent:
        :return:
        """
        return await self.request(
            "addPeerRequest",
            {"address": address, "isPermanent": is_permanent},
            wait_for_response="addPeerResponse",
        )

    async def submit_transaction(self, transaction: dict, allow_orphan: bool = False):
        """
        SubmitTransactionRequestMessage submits a transaction to the mempool
        :param transaction:
        :param allow_orphan:
        :return:
        """
        return await self.request(
            "submitTransactionRequest",
            {"transaction": transaction, "allowOrphan": allow_orphan},
            wait_for_response="submitTransactionResponse",
        )

    async def submit_transaction_replacement(self, transaction: dict):
        """
        SubmitTransactionReplacementRequestMessage submits a transaction to the mempool with RBF
        :param transaction:
        :return:
        """
        return await self.request(
            "submitTransactionReplacementRequest",
            {"transaction": transaction},
            wait_for_response="submitTransactionReplacementResponse",
        )

    async def get_block(self, hash: str, include_transactions: bool):
        """
        GetBlockRequestMessage requests information about a specific block
        :param hash:
        :param include_transactions:
        :return:
        """
        return await self.request(
            "getBlockRequest",
            {
                "hash": hash,
                "includeTransactions": include_transactions,
            },
            wait_for_response="getBlockResponse",
        )

    async def get_block_color(self, hash: str):
        """
        GetBlockColorRequestMessage requests the color (blue or red) of a given block identified by its hash.

        :param hash: The block hash for which the color is requested.
        :return: Blue or Red color of the block.
        """
        return await self.request(
            "getCurrentBlockColorRequest",
            {
                "hash": hash,
            },
            wait_for_response="getCurrentBlockColorResponse",
        )

    async def get_subnetwork(self, subnetwork_id: str):
        """
        GetSubnetworkRequestMessage requests information about a specific subnetwork
        :param subnetwork_id:
        :return:
        """
        return await self.request(
            "getSubnetworkRequest",
            {"subnetworkId": subnetwork_id},
            wait_for_response="getSubnetworkResponse",
        )

    async def get_virtual_chain_from_block(
        self, start_hash: str, include_accepted_transaction_ids: bool
    ):
        """
        GetVirtualChainFromBlockRequestMessage requests the virtual selected
        parent chain from some startHash to this kaspad_client's current virtual
        :param start_hash:
        :param include_accepted_transaction_ids:
        :return:
        """
        return await self.request(
            "getVirtualChainFromBlockRequest",
            {
                "startHash": start_hash,
                "includeAcceptedTransactionIds": include_accepted_transaction_ids,
            },
            wait_for_response="getVirtualChainFromBlockResponse",
        )

    async def get_blocks(
        self, low_hash: str, include_blocks: bool, include_transactions: bool
    ):
        """
        GetBlocksRequestMessage requests blocks between a certain block lowHash up to this
        kaspad_client's current virtual.
        :param low_hash:
        :param include_blocks:
        :param include_transactions:
        :return:
        """
        return await self.request(
            "getBlocksRequest",
            {
                "lowHash": low_hash,
                "includeBlocks": include_blocks,
                "includeTransactions": include_transactions,
            },
            wait_for_response="getBlocksResponse",
        )

    async def get_block_count(self):
        """
        GetBlockCountRequestMessage requests the current number of blocks in this kaspad_client.
        Note that this number may decrease as pruning occurs.
        :return:
        """
        return await self.request(
            "getBlockCountRequest", wait_for_response="getBlockCountResponse"
        )

    async def get_headers(self, start_hash: str, limit: int, is_ascending: bool):
        """
        GetHeadersRequestMessage requests headers between the given startHash and the
        current virtual, up to the given limit.
        :param start_hash:
        :param limit:
        :param is_ascending:
        :return:
        """
        return await self.request(
            "getHeadersRequest",
            {"startHash": start_hash, "limit": limit, "isAscending": is_ascending},
            wait_for_response="getHeadersResponse",
        )

    async def get_utxos_by_addresses(self, addresses: list[str]):
        """
        GetUtxosByAddressesRequestMessage requests all current UTXOs for the given kaspad_client addresses

        This call is only available when this kaspad_client was started with `--utxoindex`
        :param addresses:
        :return:
        """
        return await self.request(
            "getUtxosByAddressesRequest",
            {"addresses": addresses},
            wait_for_response="getUtxosByAddressesResponse",
        )

    async def get_balance_by_address(self, address: str):
        """
        GetBalanceByAddressRequest returns the total balance in unspent transactions towards a given address
        :param address:
        :return:
        """
        return await self.request(
            "getBalanceByAddressRequest",
            {"address": address},
            wait_for_response="getBalanceByAddressResponse",
        )

    async def get_balances_by_addresses(self, addresses: list[str]):
        """

        :param addresses:
        :return:
        """
        return await self.request(
            "getBalancesByAddressesRequest",
            {"addresses": addresses},
            wait_for_response="getBalancesByAddressesResponse",
        )

    async def get_sink_blue_score(self):
        """
        GetSinkBlueScoreRequestMessage requests the blue score of the current selected parent
        of the virtual block.
        :return:
        """
        return await self.request(
            "getSinkBlueScoreRequest", wait_for_response="getSinkBlueScoreResponse"
        )

    async def ban(self, ip: str):
        """
        BanRequestMessage bans the given ip.
        :param ip:
        :return:
        """
        return await self.request(
            "banRequest", {"ip": ip}, wait_for_response="banResponse"
        )

    async def get_fee_estimate(self):
        """
        GetFeeEstimateRequest retrieves a fee estimate for transactions.
        This is useful to estimate the cost required for a transaction to be included in the blockchain
         based on the current network conditions.

        :return: The response containing the estimated fee details for transactions.
        """
        return await self.request(
            "getFeeEstimateRequest", wait_for_response="getFeeEstimateResponse"
        )

    async def get_info(self):
        """
        GetInfoRequestMessage returns info about the node.
        :return:
        """
        return await self.request("getInfoRequest", wait_for_response="getInfoResponse")

    async def get_coin_supply(self):
        """
        Returns information about the circulating and the maximum supply.
        :return:
        """
        return await self.request(
            "getCoinSupplyRequest", wait_for_response="getCoinSupplyResponse"
        )

    async def ping(self):
        """
        Pings the node.
        :return:
        """
        return await self.request("pingRequest", wait_for_response="pingResponse")

    async def get_server_info(self):
        """
        Returns information about the server.
        :return:
        """
        return await self.request(
            "getServerInfoRequest", wait_for_response="getServerInfoResponse"
        )

    async def get_sync_status(self):
        """
        Returns the nodes sync status.
        :return:
        """
        return await self.request(
            "getSyncStatusRequest", wait_for_response="getSyncStatusResponse"
        )

    async def get_daa_score_timestamp_estimate(self, daa_scores: list[int]):
        """
        ???
        :param daa_scores:
        :return:
        """
        return await self.request(
            "getDaaScoreTimestampEstimateRequest",
            wait_for_response="getDaaScoreTimestampEstimateResponse",
        )

    def notify_block_added(self, f):
        asyncio.get_running_loop().create_task(
            self.kaspa_stream.register_callback("blockAddedNotification", f)
        )
        asyncio.get_running_loop().create_task(self.request("notifyBlockAddedRequest"))
        return lambda *args, **kwargs: f(*args, **kwargs)

    def notify_virtual_chain_changed(self, f):
        asyncio.get_running_loop().create_task(
            self.kaspa_stream.register_callback("virtualChainChangedNotification", f)
        )
        asyncio.get_running_loop().create_task(
            self.request("notifyVirtualChainChangedRequest")
        )
        return lambda *args, **kwargs: f(*args, **kwargs)

    def notify_finality_conflict(self, f):
        asyncio.get_running_loop().create_task(
            self.kaspa_stream.register_callback("finalityConflictNotification", f)
        )
        asyncio.get_running_loop().create_task(
            self.request("notifyFinalityConflictRequest")
        )
        return lambda *args, **kwargs: f(*args, **kwargs)

    def notify_sink_blue_score_changed(self, f):
        asyncio.get_running_loop().create_task(
            self.kaspa_stream.register_callback("sinkBlueScoreChangedNotification", f)
        )
        asyncio.get_running_loop().create_task(
            self.request("notifySinkBlueScoreChangedRequest")
        )
        return lambda *args, **kwargs: f(*args, **kwargs)

    def notify_virtual_daa_score_changed(self, f):
        asyncio.get_running_loop().create_task(
            self.kaspa_stream.register_callback("virtualDaaScoreChangedNotification", f)
        )
        asyncio.get_running_loop().create_task(
            self.request("notifyVirtualDaaScoreChangedRequest")
        )
        return lambda *args, **kwargs: f(*args, **kwargs)

    def notify_pruning_point_utxo_set_override(self, f):
        asyncio.get_running_loop().create_task(
            self.kaspa_stream.register_callback(
                "pruningPointUtxoSetOverrideNotification", f
            )
        )
        asyncio.get_running_loop().create_task(
            self.request("notifyPruningPointUtxoSetOverrideRequest")
        )
        return lambda *args, **kwargs: f(*args, **kwargs)

    def notify_new_block_template(self, f):
        asyncio.get_running_loop().create_task(
            self.kaspa_stream.register_callback("newBlockTemplateNotification", f)
        )
        asyncio.get_running_loop().create_task(
            self.request("notifyNewBlockTemplateRequest")
        )
        return lambda *args, **kwargs: f(*args, **kwargs)

    # async def estimate_network_hashes_per_second(self, window_size: int, start_hash: str):
    #     return await self.request("EstimateNetworkHashesPerSecondRequest",
    #                               {
    #                                   "windowSize": window_size,
    #                                   "startHash": start_hash
    #                               },
    #                               wait_for_response_key="EstimateNetworkHashesPerSecondResponse")
