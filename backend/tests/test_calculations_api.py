from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.calculation import CalculationCreate, CalculationRead
from backend.app.models.common import CompoundRefBase, QtyBase, RoleEnum, SpeciesQtyBase, UnitEnum
from backend.app.services import calculation_service


client = TestClient(app)


def _payload() -> CalculationCreate:
    return CalculationCreate(
        reaction_id=42,
        species=[
            {
                "compound": CompoundRefBase(compound_id=1, preferred_name="Reactant A", molecular_weight=50),
                "role": RoleEnum.REACTANT,
                "coeff": 1,
                "qty": SpeciesQtyBase(qty=QtyBase(value=10, unit=UnitEnum.MASS_G)),
            },
            {
                "compound": CompoundRefBase(compound_id=2, preferred_name="Product B", molecular_weight=100),
                "role": RoleEnum.PRODUCT,
                "coeff": 1,
                "qty": SpeciesQtyBase(qty=QtyBase(value=1, unit=UnitEnum.MASS_G)),
            },
        ],
    )


def test_preview_calculation_returns_serialized_calculation(monkeypatch):
    payload = _payload()
    captured_payloads = []

    def fake_compute(received_payload: CalculationCreate) -> CalculationRead:
        captured_payloads.append(received_payload)
        return CalculationRead(
            id=received_payload.reaction_id,
            reaction_id=received_payload.reaction_id,
            species=received_payload.species,
            target_yield_percent=received_payload.target_yield_percent,
            scale_factor=received_payload.scale_factor,
            target_mass_product_g=received_payload.target_mass_product_g,
            created_at="2026-06-25T12:00:00Z",
            updated_at=None,
            limiting_reactant_id=1,
            limiting_reactant_name="Reactant A",
            xmax=0.2,
            theoretical_yield_moles=0.2,
            theoretical_yield_mass_g=20,
            species_results=[],
            avancement_table=[],
            scaled_quantities=None,
        )

    monkeypatch.setattr(calculation_service, "compute_reaction_calculation", fake_compute)

    response = client.post("/api/v1/calculations/preview", json=payload.model_dump(mode="json"))

    assert response.status_code == 200
    assert response.json()["reaction_id"] == 42
    assert response.json()["limiting_reactant_name"] == "Reactant A"
    assert captured_payloads == [payload]


def test_preview_calculation_returns_400_for_business_value_error(monkeypatch):
    payload = _payload()

    def fake_compute(_payload: CalculationCreate) -> CalculationRead:
        raise ValueError("No valid reactant quantities")

    monkeypatch.setattr(calculation_service, "compute_reaction_calculation", fake_compute)

    response = client.post("/api/v1/calculations/preview", json=payload.model_dump(mode="json"))

    assert response.status_code == 400
    assert response.json() == {"detail": "No valid reactant quantities"}


def test_openapi_schema_is_generated():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/calculations/preview" in response.json()["paths"]
