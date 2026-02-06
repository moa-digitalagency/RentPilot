import enum
from typing import List, Dict, Any, Optional

# Assuming models are available, but to keep this logic pure and testable,
# we will accept objects that have the required attributes or dictionaries.
# Using Duck Typing for flexibility.

class VacancyStrategy(enum.Enum):
    REDISTRIBUTE = "redistribute"  # Remaining tenants pay for empty rooms' share of variable costs
    OWNER_PAYS = "owner_pays"      # Tenants only pay their 1/N share (based on total capacity), owner covers vacancy

class CostCalculator:
    """
    Core business logic for calculating cost splits in a coliving establishment.

    Handles two main financial modes:
    1. Equal Split (Part Égale): All costs (Rent + Charges) are pooled and divided equally among tenants.
    2. Per Room (Par Chambre): Specific Room Rent + Share of Variable Charges.

    Attributes logic:
    - Syndic: Always divided by the number of present people (Occupied Rooms).
    - Vacancy Logic: Determines how variable costs (Invoices) are split when rooms are empty.
    """

    def __init__(self, establishment, rooms: List[Any], invoices: List[Any], vacancy_strategy: VacancyStrategy = VacancyStrategy.REDISTRIBUTE):
        """
        :param establishment: The Establishment object (contains syndic_cost, wifi_cost, config_financial_mode).
        :param rooms: List of Room objects (must have base_price, is_vacant).
        :param invoices: List of Invoice objects (must have amount, type).
        :param vacancy_strategy: Strategy to handle variable costs when rooms are empty.
        """
        self.establishment = establishment
        self.rooms = rooms
        self.invoices = invoices
        self.vacancy_strategy = vacancy_strategy

    def calculate(self) -> Dict[str, Any]:
        """
        Main entry point. Routes to the correct calculation method based on establishment config.

        :return: A dictionary containing details of the calculation:
                 {
                     "mode": "Egal" | "Inegal",
                     "total_rent": float,
                     "total_charges": float,
                     "breakdown_per_room": { room_id: { "rent": ..., "charges": ..., "total": ... } },
                     "global_stats": { "occupied": int, "total_rooms": int }
                 }
        """
        # Determine occupied stats
        total_rooms_count = len(self.rooms)
        occupied_rooms = [r for r in self.rooms if not r.is_vacant]
        occupied_count = len(occupied_rooms)

        # Safety check for division by zero
        if occupied_count == 0 and total_rooms_count == 0:
             return self._empty_result()

        mode = getattr(self.establishment, 'config_financial_mode', 'Egal')
        # Handle Enum or String
        mode_str = mode.value if hasattr(mode, 'value') else str(mode)

        if mode_str == 'Egal':
            return self._calculate_equal_split(occupied_rooms, occupied_count)
        else:
            return self._calculate_per_room(occupied_rooms, occupied_count, total_rooms_count)

    def _calculate_equal_split(self, occupied_rooms, occupied_count) -> Dict[str, Any]:
        """
        Strategy: EQUAL SPLIT
        1. Sum ALL Rents (from all rooms, or just occupied? Usually all revenue target, but in Equal Split among TENANTS, we usually sum rents of occupied rooms or just pool everything).
           *Interpretation*: In a shared lease "Solidarity", the total amount due to the landlord is Fixed.
           If the mode is 'Equal', tenants split the TOTAL bill.
           Total Bill = Sum(Base Price of ALL rooms) + Invoices + Syndic + Wifi.
           Each Tenant Pays = Total Bill / Occupied Count.

           *Nuance*: If a room is empty, do the remaining tenants pay for it?
           Yes, in "Solidarity" leases usually.
           But if `vacancy_strategy` is OWNER_PAYS, we might adjust.

           For simplicity and robustness in this specific 'Equal' mode requested:
           We will sum everything and divide by occupied_count.
        """
        if occupied_count == 0:
             return self._empty_result()

        # 1. Calculate Total Expenses
        total_invoices = sum(inv.amount for inv in self.invoices)
        syndic = self.establishment.syndic_cost or 0.0
        wifi = self.establishment.wifi_cost or 0.0

        # In Equal Split, we typically assume the group is responsible for the entire property rent
        # irrespective of who is in which room.
        total_rent_property = sum(r.base_price for r in self.rooms)

        grand_total = total_rent_property + total_invoices + syndic + wifi

        cost_per_person = grand_total / occupied_count

        # Build Result
        breakdown = {}
        for room in occupied_rooms:
            breakdown[room.id] = {
                "rent": total_rent_property / occupied_count, # Theoretical breakdown
                "charges": (total_invoices + syndic + wifi) / occupied_count,
                "total": cost_per_person
            }

        return {
            "mode": "Egal",
            "total_global_cost": grand_total,
            "per_person_share": cost_per_person,
            "breakdown_per_room": breakdown,
            "details": {
                "comment": "Total cost (Rent + Charges) divided equally among present tenants.",
                "total_rent": total_rent_property,
                "total_invoices": total_invoices,
                "syndic": syndic,
                "wifi": wifi
            }
        }

    def _calculate_per_room(self, occupied_rooms, occupied_count, total_rooms_count) -> Dict[str, Any]:
        """
        Strategy: PER ROOM (Inegal)
        1. Rent: Each room pays its own `base_price`.
        2. Syndic: Always divided by `occupied_count` (People Present).
        3. Wifi: Treated like Syndic (Fixed service for present people) -> / `occupied_count`.
        4. Invoices (Variable): Depends on `vacancy_strategy`.
           - REDISTRIBUTE: Sum(Invoices) / `occupied_count`
           - OWNER_PAYS: Sum(Invoices) / `total_rooms_count` (Tenants pay their share, Owner absorbs empty shares)
        """
        if occupied_count == 0:
            return self._empty_result()

        # 1. Fixed Costs per Person (Syndic + Wifi)
        # "Le Syndic est toujours divisé par le nombre de personnes présentes."
        syndic = self.establishment.syndic_cost or 0.0
        wifi = self.establishment.wifi_cost or 0.0
        fixed_charges_total = syndic + wifi
        fixed_charges_share = fixed_charges_total / occupied_count

        # 2. Variable Costs (Invoices)
        total_invoices = sum(inv.amount for inv in self.invoices)

        variable_share = 0.0
        vacancy_loss_absorbed_by_owner = 0.0

        if self.vacancy_strategy == VacancyStrategy.REDISTRIBUTE:
            # Logic: Tenants cover the whole bill
            variable_share = total_invoices / occupied_count
        else:
            # Logic: OWNER_PAYS (Subtract)
            # Cost is calculated based on full capacity
            if total_rooms_count > 0:
                share_per_unit = total_invoices / total_rooms_count
                variable_share = share_per_unit
                # The rest is lost/paid by owner
                vacancy_loss_absorbed_by_owner = share_per_unit * (total_rooms_count - occupied_count)

        # 3. Build Breakdown
        breakdown = {}
        for room in occupied_rooms:
            # Step-by-step calculation for this room
            # A. Rent
            room_rent = room.base_price

            # B. Total Charges Share
            room_charges = fixed_charges_share + variable_share

            # C. Total
            total_for_room = room_rent + room_charges

            breakdown[room.id] = {
                "rent": room_rent,
                "charges": room_charges,
                "charges_breakdown": {
                    "syndic_wifi": fixed_charges_share,
                    "variable_invoices": variable_share
                },
                "total": total_for_room
            }

        return {
            "mode": "Inegal (Par Chambre)",
            "vacancy_strategy": self.vacancy_strategy.value,
            "breakdown_per_room": breakdown,
            "details": {
                "comment": f"Rent is specific. Syndic/Wifi divided by {occupied_count}. Variable costs split using {self.vacancy_strategy.value}.",
                "total_invoices": total_invoices,
                "owner_absorbed_vacancy_costs": vacancy_loss_absorbed_by_owner
            }
        }

    def _empty_result(self):
        return {
            "error": "No occupied rooms or no rooms available.",
            "breakdown_per_room": {}
        }
