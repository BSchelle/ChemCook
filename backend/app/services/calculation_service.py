from backend.app.models.common  import RoleEnum
from backend.app.models.calculation  import CalculationCreate
from backend.app.chemistry.engine import quantity_to_moles, find_limiting_reagent, build_avancement_table


def compute_reaction_calculation(payload: CalculationCreate):
    reactants = [sp for sp in payload.species if sp.role == RoleEnum.REACTANT]

    for sp in reactants:
        sp.qty.moles = quantity_to_moles(
            sp.qty,
            sp.compound.molecular_weight,
            sp.qty.density,
        )

    return payload
