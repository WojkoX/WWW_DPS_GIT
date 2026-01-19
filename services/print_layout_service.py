from services.nutrition_stats_service import get_nutrition_stats_grouped_by_floor

def get_print_context_for_floor(floor):
    stats = get_nutrition_stats_grouped_by_floor()

    data = stats[floor]
    residents = data["present_residents"]

    half = (len(residents) + 1) // 2

    return {
        "floor": floor,
        "presence": data["presence_summary"],
        "left_residents": residents[:half],
        "right_residents": residents[half:],
        "summary_room": data["summary_eat_in_room"],
        "summary_all": data["summary_all_present"],
    }
