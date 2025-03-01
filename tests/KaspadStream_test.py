import os

import pytest

from kaspad_client.modules.KaspadStream import KaspadStream

KASPAD_TEST_HOST = os.getenv("KASPAD_TEST_HOST") or "127.0.0.1"
KASPAD_TEST_PORT = os.getenv("KASPAD_TEST_PORT") or 16110


@pytest.mark.asyncio
async def test_init():
    kaspad_thread = KaspadStream(KASPAD_TEST_HOST, KASPAD_TEST_PORT)

    await kaspad_thread.send("getBlockDagInfoRequest", id=1234)
    response = await kaspad_thread.read(1234)

    assert response.get("getBlockDagInfoResponse").get("networkName") == "kaspa-mainnet"
