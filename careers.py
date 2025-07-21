"""Career system handling job titles and promotions."""

from typing import Dict, List
from entities import Player
from combat import energy_cost

# Career progression data
JOB_DATA: Dict[str, Dict] = {
    "office": {
        "titles": ["Intern", "Clerk", "Manager", "Director", "Executive"],
        "level_attr": "office_level",
        "shift_attr": "office_shifts",
        "exp_attr": "office_exp",
        "stats": ["intelligence", "charisma"],
        "base_pay": 20,
        "pay_step": 15,
        "exp_per_shift": 10,
        "exp_base": 100,
        "bonus": "intelligence",
    },
    "dealer": {
        "titles": ["Lookout", "Runner", "Dealer", "Supplier", "Kingpin"],
        "level_attr": "dealer_level",
        "shift_attr": "dealer_shifts",
        "exp_attr": "dealer_exp",
        "stats": ["strength", "charisma"],
        "base_pay": 40,
        "pay_step": 20,
        "exp_per_shift": 10,
        "exp_base": 100,
        "bonus": "charisma",
    },
    "clinic": {
        "titles": ["Assistant", "Nurse", "Doctor", "Surgeon", "Chief"],
        "level_attr": "clinic_level",
        "shift_attr": "clinic_shifts",
        "exp_attr": "clinic_exp",
        "stats": ["intelligence", "strength"],
        "base_pay": 30,
        "pay_step": 15,
        "exp_per_shift": 10,
        "exp_base": 100,
        "bonus": "strength",
    },
}


def get_job_title(player: Player, job_key: str) -> str:
    """Return the player's title for the given job."""
    data = JOB_DATA[job_key]
    level = getattr(player, data["level_attr"])
    titles: List[str] = data["titles"]
    return titles[level - 1] if level - 1 < len(titles) else f"Lv{level}"


def job_exp_needed(player: Player, job_key: str) -> int:
    """Return the experience required for the next promotion."""
    data = JOB_DATA[job_key]
    level = getattr(player, data["level_attr"])
    return data["exp_base"] * level


def job_progress(player: Player, job_key: str) -> tuple[int, int]:
    """Return current experience and required amount for the next level."""
    data = JOB_DATA[job_key]
    exp = getattr(player, data["exp_attr"])
    level = getattr(player, data["level_attr"])
    if level >= len(data["titles"]):
        need = 0
    else:
        need = job_exp_needed(player, job_key)
    return exp, need


def work_job(player: Player, job_key: str) -> str:
    """Handle working a shift and possible promotion."""
    data = JOB_DATA[job_key]
    if player.energy < 20:
        return "Too tired to work!"

    level_attr = data["level_attr"]
    shift_attr = data["shift_attr"]
    exp_attr = data["exp_attr"]
    level = getattr(player, level_attr)

    pay = data["base_pay"] + data["pay_step"] * (level - 1)
    player.money += pay
    player.energy -= energy_cost(player, 20)
    setattr(player, shift_attr, getattr(player, shift_attr) + 1)
    exp = getattr(player, exp_attr) + data["exp_per_shift"]
    setattr(player, exp_attr, exp)

    req1 = getattr(player, data["stats"][0])
    req2 = getattr(player, data["stats"][1])
    need_exp = job_exp_needed(player, job_key)
    max_level = level >= len(data["titles"])

    if not max_level and exp >= need_exp and req1 >= 5 * level and req2 >= 5 * level:
        setattr(player, level_attr, level + 1)
        setattr(player, shift_attr, 0)
        setattr(player, exp_attr, exp - need_exp)
        bonus = data.get("bonus")
        if bonus:
            setattr(player, bonus, getattr(player, bonus) + 1)
        new_title = get_job_title(player, job_key)
        return f"Promoted to {new_title}!"

    title = get_job_title(player, job_key)
    return f"Worked as {title}! +${pay}, +{data['exp_per_shift']}xp"

def job_pay(player: Player, job_key: str) -> int:
    """Return the current pay for the job based on level."""
    data = JOB_DATA[job_key]
    level = getattr(player, data["level_attr"])
    return data["base_pay"] + data["pay_step"] * (level - 1)

