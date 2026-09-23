from desk_radar.config import Settings
from desk_radar.models import PairSnapshot
from desk_radar.rug import RugGate


def _pair(chain: str = "base") -> PairSnapshot:
    return PairSnapshot(
        chain=chain,
        pair_address="0xpair",
        base_address="0xbase",
        base_symbol="TEST",
        quote_symbol="WETH" if chain == "base" else "SOL",
        price_usd=0.01,
        liquidity_usd=50_000,
        volume_5m_usd=8_000,
    )


def test_honeypot_blocked():
    def fetcher(_url: str):
        return {"result": {"0xbase": {"is_honeypot": "1", "buy_tax": "0", "sell_tax": "0"}}}

    gate = RugGate(Settings(), fetcher=fetcher)
    verdict = gate.check(_pair())
    assert verdict.accepted is False
    assert "is_honeypot" in verdict.reasons


def test_clean_token_passes():
    def fetcher(_url: str):
        return {"result": {"0xbase": {"is_honeypot": "0", "buy_tax": "0", "sell_tax": "0"}}}

    gate = RugGate(Settings(), fetcher=fetcher)
    verdict = gate.check(_pair())
    assert verdict.accepted is True


def test_fail_closed_on_outage():
    def fetcher(_url: str):
        raise RuntimeError("down")

    gate = RugGate(Settings(rug_fail_closed=True), fetcher=fetcher)
    verdict = gate.check(_pair())
    assert verdict.accepted is False
    assert any("rug_unavailable" in r for r in verdict.reasons)


def test_solana_freezeable_blocked():
    def fetcher(_url: str):
        return {"result": {"mint": {"freezable": "1", "mintable": "0"}}}

    gate = RugGate(Settings(), fetcher=fetcher)
    verdict = gate.check(_pair("solana"))
    assert verdict.accepted is False
    assert "freezable" in verdict.reasons
