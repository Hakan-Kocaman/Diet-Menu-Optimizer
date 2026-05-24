

HUGE_PENALTY = 1_000_000


def calculate_penalty(totals, dri):
    penalty = 0.0
    violation_details = {}

    for nutrient_id, bounds in dri.items():
        value = totals.get(nutrient_id, 0)

        rll = bounds["RLL"]
        rul = bounds["RUL"]

        if rul == rll:
            continue

        low_violation = max(0, rll - value) / (rul - rll)
        high_violation = max(0, value - rul) / (rul - rll)

        nutrient_penalty = 0.7 * low_violation + 0.3 * high_violation
        penalty += nutrient_penalty

        violation_details[nutrient_id] = {
            "name": bounds.get("name", str(nutrient_id)),
            "value": value,
            "RLL": rll,
            "RUL": rul,
            "low_violation": low_violation,
            "high_violation": high_violation,
            "penalty": nutrient_penalty
        }

    return penalty, violation_details


def calculate_objectives(menu, foods, preferences):
    preference_score = 0.0
    total_cost = 0.0
    total_prepTime = 0.0
    total_time = 0.0
    forbidden_count = 0

    for food_id in menu:
        food = foods[food_id]

        pref = preferences.get(food_id, food.get("preference", 0))

        if pref == -1:
            forbidden_count += 1
        else:
            preference_score += pref

        total_cost += food.get("cost", 0)
        total_prepTime += food.get("preparingTime", 0) or 0

        preparing_time = food.get("preparingTime", 0) or 0
        cooking_time = food.get("cookingTime", 0) or 0

        total_time += preparing_time + cooking_time

    return preference_score, total_cost, total_time, forbidden_count


def validate_objectives(objectives):
    allowed = {"preference", "cost", "prepTime"}

    if len(objectives) != 3:
        raise ValueError("Exactly 3 objectives must be selected.")

    if "preference" not in objectives:
        raise ValueError("Preference objective is mandatory.")

    for obj in objectives:
        if obj not in allowed:
            raise ValueError(f"Invalid objective: {obj}")


def fitness(
    menu,
    totals,
    foods,
    preferences,
    dri,
    lambda_=1.0,
    objectives=("preference", "cost", "prepTime")
):
    validate_objectives(objectives)

    preference_score, total_cost, total_time, forbidden_count = calculate_objectives(
        menu, foods, preferences
    )

    nutrition_penalty, violation_details = calculate_penalty(totals, dri)

    forbidden_penalty = forbidden_count * HUGE_PENALTY
    total_penalty = nutrition_penalty + forbidden_penalty
    penalty_effect = lambda_ * total_penalty

    values = {
        "preference": -preference_score + penalty_effect,
        "cost": total_cost + penalty_effect,
        "prepTime": total_time + penalty_effect
    }

    objective_values = [values[obj] for obj in objectives]

    info = {
        "raw_preference": preference_score,
        "cost": total_cost,
        "prepTime": total_time,
        "nutrition_penalty": nutrition_penalty,
        "forbidden_count": forbidden_count,
        "forbidden_penalty": forbidden_penalty,
        "total_penalty": total_penalty,
        "lambda": lambda_,
        "violation_details": violation_details,
        "selected_objectives": objectives
    }

    return objective_values, info




