from typing import List, Dict, Optional
from models.establishment import Establishment, FinancialMode
from models.finance import ExpenseType

class CostCalculator:
    """
    Service to calculate the split of expenses among tenants.
    """

    @staticmethod
    def calculate_equal_split(total_cost: float, num_tenants: int) -> float:
        """
        Splits the total cost equally among the number of tenants.

        Formula: Total Cost / Number of Tenants

        Args:
            total_cost: The total amount to split.
            num_tenants: The number of active tenants.

        Returns:
            The amount each tenant should pay. Returns 0 if no tenants.
        """
        if num_tenants <= 0:
            return 0.0
        return round(total_cost / num_tenants, 2)

    @staticmethod
    def calculate_advanced_split(
        establishment: Establishment,
        expenses: List[Dict], # List of expenses dictionaries: {'type': ExpenseType, 'amount': float}
        active_leases: List, # List of Lease objects active during the period
        redistribute_vacancy: bool = True
    ) -> Dict[int, Dict[str, float]]:
        """
        Calculates the cost split based on 'Par Chambre' mode (Fixed Rent + Variable Charges).

        Logic:
        1. Base Rent: Each tenant pays the base price of their room.
        2. Syndic/Fixed Charges: Divided by the number of people present.
        3. Variable Charges (Water, Elec, Wifi): Divided by the number of people present.

        Vacancy Logic:
        - If redistribute_vacancy is True: The landlord does NOT absorb the cost of vacant rooms' share of common expenses.
          Common expenses are simply divided by N present tenants.
        - If redistribute_vacancy is False: The landlord absorbs the share of vacant rooms.
          Common expenses are divided by Total Capacity (Occupied + Vacant).
          Tenants pay Share = Total / Total Capacity. Landlord pays (Total / Total Capacity) * Vacant Rooms.

        Args:
            establishment: The establishment object.
            expenses: List of expenses for the period.
            active_leases: List of active leases.
            redistribute_vacancy: Config option.

        Returns:
            Dictionary mapping User ID to their cost breakdown:
            {
                user_id: {
                    'rent': float,
                    'fixed_charges': float,
                    'variable_charges': float,
                    'total': float
                }
            }
        """

        # 1. Identify Occupants
        # Map user_id to their room and lease
        tenant_map = {}
        for lease in active_leases:
            tenant_map[lease.user_id] = lease

        num_active_tenants = len(active_leases)
        total_rooms = len(establishment.rooms) # Assuming establishment.rooms is populated

        # Denominator for shared costs
        # If redistributing vacancy: Denominator = Active Tenants (Costs are shared among those present)
        # If NOT redistributing: Denominator = Total Rooms (Costs are split as if full, landlord pays vacancy)
        # Note: Usually syndic/wifi is per unit, but consumption (water/elec) is per person.
        # For simplicity, we stick to the prompt's instruction: "Syndic est toujours divisé par le nombre de personnes présentes."
        # This implies Syndic ignores vacancy logic for the prompt's specific rule?
        # "Le Syndic est toujours divisé par le nombre de personnes présentes" -> This overrides general vacancy logic for Syndic.

        denominator_syndic = num_active_tenants if num_active_tenants > 0 else 1

        # For other variable charges (Water, Elec, Wifi... wait Wifi is usually fixed but treated as variable here? Prompt says "Charges variables")
        # Let's assume the Vacancy Logic applies to Water/Elec/Wifi.
        denominator_variable = num_active_tenants if redistribute_vacancy else total_rooms
        if denominator_variable == 0: denominator_variable = 1 # Avoid division by zero

        # 2. Categorize Expenses
        total_syndic = 0.0
        total_variable = 0.0

        # Add configured fixed costs from Establishment
        if establishment.syndic_cost:
            total_syndic += establishment.syndic_cost
        if establishment.wifi_cost:
            # Wifi is often considered a fixed utility, let's treat it as variable for split logic unless specified otherwise.
            # Prompt: "Syndic est toujours divisé par le nombre de personnes présentes."
            # Implicitly, other things might follow the vacancy rule.
            total_variable += establishment.wifi_cost

        # Add dynamic expenses
        for exp in expenses:
            # Assuming exp is a dict or object with 'type' and 'amount'
            e_type = exp.get('type')
            amount = exp.get('amount')

            # Use string value if it's an Enum
            e_type_val = e_type.value if hasattr(e_type, 'value') else str(e_type)

            # Logic could be more granular, but separating Syndic vs Rest as per prompt
            # Prompt doesn't explicitly say Syndic is an ExpenseType, but let's assume standard expenses are variable
            # unless it's explicitly 'Syndic' (which usually comes from establishment config, not monthly invoice).
            # But if there is a 'Travaux' or special bill, it might be variable.

            # For now, let's add all dynamic expenses to variable,
            # unless we have a specific type for Syndic in ExpenseType (we don't: EAU, ELEC, WIFI, TRAVAUX, LOYER).
            total_variable += amount

        # 3. Calculate Shares
        # Syndic Share (Always split by present people)
        syndic_share_per_person = total_syndic / denominator_syndic if num_active_tenants > 0 else 0

        # Variable Share
        # If redistribute_vacancy=False, this share is smaller because it's divided by total rooms.
        variable_share_per_person = total_variable / denominator_variable

        # 4. Build Result
        results = {}

        for user_id, lease in tenant_map.items():
            # Base Rent
            rent = lease.room.base_price

            results[user_id] = {
                'rent': round(rent, 2),
                'syndic': round(syndic_share_per_person, 2),
                'variable': round(variable_share_per_person, 2),
                'total': round(rent + syndic_share_per_person + variable_share_per_person, 2)
            }

        return results
