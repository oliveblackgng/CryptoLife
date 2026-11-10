
def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def simulate_cryptobiosis(humidity, temperature, state):
    """
    Educational model of environmental stress.

    This is not a biological survival prediction.
    """

    humidity = clamp(float(humidity), 0, 100)
    temperature = clamp(float(temperature), -20, 50)

    if state not in ["active", "tun"]:
        raise ValueError("Invalid tardigrade state.")

    # Higher dehydration index means lower humidity.
    dehydration = (100 - humidity) / 100

    # Reference temperature used only for this illustrative model.
    thermal_stress = min(abs(temperature - 20) / 70, 1)

    # Illustrative assumption: tun state reduces the
    # dehydration contribution in this simplified model.
    protection_factor = 1.0 if state == "active" else 0.65

    dehydration_contribution = (
        dehydration * protection_factor * 65
    )

    temperature_contribution = thermal_stress * 35

    total_stress = (
        dehydration_contribution + temperature_contribution
    )

    return {
        "dehydration": round(dehydration * 100, 2),
        "temperature_stress": round(thermal_stress * 100, 2),
        "dehydration_contribution": round(
            dehydration_contribution, 2
        ),
        "temperature_contribution": round(
            temperature_contribution, 2
        ),
        "stress_index": round(clamp(total_stress, 0, 100), 2),
        "state": state
    }


def simulate_space_conditions(
    radiation,
    vacuum,
    temperature,
    microgravity
):
    """
    Educational model of selected space environmental stresses.

    Radiation and vacuum are normalized input levels.
    The model does not predict actual biological damage.
    """

    radiation = clamp(float(radiation), 0, 10)
    vacuum = clamp(float(vacuum), 0, 1)
    temperature = clamp(float(temperature), -150, 120)

    radiation_index = radiation / 10
    vacuum_index = vacuum

    # Reference temperature is 20 degrees Celsius.
    thermal_index = min(abs(temperature - 20) / 170, 1)

    radiation_contribution = radiation_index * 45
    vacuum_contribution = vacuum_index * 25
    temperature_contribution = thermal_index * 30

    total_stress = (
        radiation_contribution
        + vacuum_contribution
        + temperature_contribution
    )

    return {
        "radiation_index": round(radiation_index * 100, 2),
        "vacuum_index": round(vacuum_index * 100, 2),
        "temperature_index": round(thermal_index * 100, 2),
        "radiation_contribution": round(
            radiation_contribution, 2
        ),
        "vacuum_contribution": round(
            vacuum_contribution, 2
        ),
        "temperature_contribution": round(
            temperature_contribution, 2
        ),
        "stress_index": round(clamp(total_stress, 0, 100), 2),
        "microgravity": bool(microgravity)
    }


def simulate_combined(
    humidity,
    biological_temperature,
    state,
    radiation,
    vacuum,
    space_temperature,
    microgravity
):
    """
    Combines the two educational models.

    This weighted index is illustrative, not experimentally validated.
    """

    crypto = simulate_cryptobiosis(
        humidity,
        biological_temperature,
        state
    )

    space = simulate_space_conditions(
        radiation,
        vacuum,
        space_temperature,
        microgravity
    )

    combined_index = (
        crypto["stress_index"] * 0.45
        + space["stress_index"] * 0.55
    )

    return {
        "cryptobiosis": crypto,
        "space": space,
        "combined_stress_index": round(
            clamp(combined_index, 0, 100), 2
        )
    }
