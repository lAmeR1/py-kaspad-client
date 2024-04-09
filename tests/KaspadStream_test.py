import os

import pytest

from kaspad_client.modules.KaspadStream import KaspadStream

KASPAD_TEST_HOST = os.getenv("KASPAD_TEST_HOST") or "127.0.0.1"


@pytest.mark.asyncio
async def test_init():
    kaspad_thread = KaspadStream(KASPAD_TEST_HOST, 16110)

    await kaspad_thread.send("getBlockDagInfoRequest")
    response = await kaspad_thread.read("getBlockDagInfoResponse")

    assert response.get('getBlockDagInfoResponse').get('networkName') == "kaspa-mainnet"
