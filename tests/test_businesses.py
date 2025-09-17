import random
import pygame

from entities import Player
from businesses import (
    BUSINESS_CATALOG,
    BUSINESS_DATA,
    buy_business,
    cash_out_future,
    upgrade_business,
    hire_staff,
    collect_profits,
    run_marketing_campaign,
    schedule_future_contract,
    train_staff,
)


def make_player():
    return Player(pygame.Rect(0, 0, 1, 1))


def test_buy_and_upgrade_business():
    p = make_player()
    p.money = 10000
    stall_index = BUSINESS_CATALOG.index("Stall")
    assert buy_business(p, stall_index) == "Bought Stall"
    assert "Stall" in p.businesses
    assert upgrade_business(p, "Stall") == "Upgraded Stall to Store"
    assert "Store" in p.businesses and "Stall" not in p.businesses


def test_staff_affects_profits():
    p = make_player()
    p.money = 10000
    store_index = BUSINESS_CATALOG.index("Store")
    buy_business(p, store_index)
    hire_staff(p, "Store", 2)
    p.charisma = 5

    orig_random = random.random
    random.random = lambda: 1.0  # avoid robbery
    try:
        profit, _ = collect_profits(p)
    finally:
        random.random = orig_random

    data = BUSINESS_DATA["Store"]
    expected = data.base_profit + p.charisma * 2 + (2 * 10) - (2 * data.staff_cost)
    assert profit == expected


def test_robbery_zeroes_profit():
    p = make_player()
    p.money = 10000
    stall_index = BUSINESS_CATALOG.index("Stall")
    buy_business(p, stall_index)

    orig_random = random.random
    random.random = lambda: 0.0  # force robbery
    try:
        profit, _ = collect_profits(p)
    finally:
        random.random = orig_random

    assert profit == 0


def test_marketing_campaign_boosts_profit():
    p = make_player()
    p.money = 10000
    store_index = BUSINESS_CATALOG.index("Store")
    buy_business(p, store_index)
    orig_randint = random.randint
    random.randint = lambda a, b: a
    try:
        run_marketing_campaign(p, "Store")
    finally:
        random.randint = orig_randint
    orig_random = random.random
    random.random = lambda: 1.0
    try:
        profit, _ = collect_profits(p)
    finally:
        random.random = orig_random
    data = BUSINESS_DATA["Store"]
    expected = data.base_profit + p.charisma * 2 + 10
    assert profit == expected


def test_train_staff_reduces_robbery_risk():
    p = make_player()
    p.money = 10000
    stall_index = BUSINESS_CATALOG.index("Stall")
    buy_business(p, stall_index)
    orig_random = random.random
    random.random = lambda: 0.05
    try:
        profit, _ = collect_profits(p)
    finally:
        random.random = orig_random
    assert profit == 0
    orig_randint = random.randint
    random.randint = lambda a, b: 3
    try:
        train_staff(p, "Stall")
    finally:
        random.randint = orig_randint
    random.random = lambda: 0.05
    try:
        profit_after, _ = collect_profits(p)
    finally:
        random.random = orig_random
    assert profit_after > 0


def test_schedule_and_cash_out_future_contract():
    p = make_player()
    p.money = 1000
    stall_index = BUSINESS_CATALOG.index("Stall")
    buy_business(p, stall_index)
    p.charisma = 1
    money_after_purchase = p.money

    seq = iter([5, 2, 90])
    orig_randint = random.randint
    random.randint = lambda a, b: next(seq)
    try:
        message = schedule_future_contract(p, "Stall")
    finally:
        random.randint = orig_randint

    assert "Margin" in message
    assert "Stall" in p.business_futures
    margin = max(50, int(BUSINESS_DATA["Stall"].base_profit * 0.6))
    assert p.money == money_after_purchase - margin

    # Cannot cash out before due date
    early_message = cash_out_future(p, "Stall")
    assert "matures" in early_message

    contract = p.business_futures["Stall"]
    p.day = contract["day_due"]
    money_before = p.money
    message = cash_out_future(p, "Stall")
    assert "futures" in message
    assert "Stall" not in p.business_futures
    assert p.money == money_before + contract["payout"]
    if contract["payout"] > 0 and contract["risk"] == "speculative":
        assert p.reputation["business"] > 0


def test_collect_profits_reconciles_due_futures():
    p = make_player()
    p.money = 0
    p.businesses["Stall"] = BUSINESS_DATA["Stall"].base_profit
    p.business_bonus["Stall"] = 0
    p.business_staff["Stall"] = 0
    p.business_reputation["Stall"] = 0
    p.business_skill["Stall"] = 0
    p.business_futures["Stall"] = {
        "payout": 40,
        "day_due": p.day,
        "risk": "hedged",
        "flavour": "Test hedge resolves.",
        "reputation_bonus": 0,
        "charisma_score": 0,
        "margin": 0,
    }

    orig_random = random.random
    random.random = lambda: 1.0
    try:
        profit, events = collect_profits(p)
    finally:
        random.random = orig_random

    assert "Test hedge resolves." in events[0]
    assert "Stall" not in p.business_futures
    expected_profit = BUSINESS_DATA["Stall"].base_profit + p.charisma * 2
    assert profit == expected_profit
    assert p.money == 40 + expected_profit

