from models.resident import Resident
from collections import defaultdict


def build_dashboard_tree():
    """
    Buduje strukturę:
    {
      floor: {
        room_number: {
          'residents': [...],
          'needs_attention': bool
        }
      }
    }
    """

    residents = (
        Resident.query
        .filter_by(is_active=True)
        .order_by(
            Resident.floor,
            Resident.room_number,
            Resident.last_name
        )
        .all()
    )

    tree = defaultdict(lambda: defaultdict(lambda: {
        'residents': [],
        'needs_attention': False
    }))

    for r in residents:
        floor = r.floor if r.floor is not None else 0
        room = r.room_number or '—'

        resident_data = {
            'id': r.id,
            'last_name': r.last_name,
            'first_name': r.first_name,

            # STATUSY POD IKONY
            'has_diet': r.has_diet,
            'needs_attention': r.needs_attention,
            'is_hospital': r.is_hospital,
            'is_pass': r.is_pass,
        }

        tree[floor][room]['residents'].append(resident_data)

        # jeśli KTOŚ w pokoju wymaga uwagi → cały pokój ❗
        if r.needs_attention:
            tree[floor][room]['needs_attention'] = True

    return tree
