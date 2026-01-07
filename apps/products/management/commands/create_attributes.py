from django.core.management.base import BaseCommand

from apps.products.models import Attribute
from apps.products.models import AttributeValue

data = [
    {
        "name": "Color de guantes",
        "group": "COLOR",
        "description": (
            "Atributo que define los colores disponibles para "
            "los guantes de caucho natural."
        ),
        "values": [
            {"value": "Amarillo", "sort_order": 0},
            {"value": "Bicolor", "sort_order": 1},
        ],
    },
    {
        "name": "Tamaño de guantes",
        "group": "SIZE",
        "description": (
            "Atributo que define los tamaños disponibles para los "
            "guantes de caucho natural."
        ),
        "values": [
            {"value": "7", "sort_order": 0},
            {"value": "7.5", "sort_order": 1},
            {"value": "8", "sort_order": 2},
            {"value": "8.5", "sort_order": 3},
            {"value": "9", "sort_order": 4},
        ],
    },
    {
        "name": "Volumen del recipiente",
        "group": "VOLUME",
        "description": (
            "Atributo que define los volúmenes disponibles para los "
            "recipientes de latex."
        ),
        "values": [
            {"value": "1 Galón", "sort_order": 0},
            {"value": "5 Galones", "sort_order": 1},
        ],
    },
]


class Command(BaseCommand):
    help = "Create or update product attributes and their values in the database."

    def handle(self, *args, **kwargs):
        for entry in data:
            values_data = entry.pop("values", [])

            attribute_lookup = {"name": entry["name"]}
            attribute_defaults = {
                k: v for k, v in entry.items() if k not in attribute_lookup
            }

            attribute_obj, attribute_created = Attribute.objects.update_or_create(
                defaults=attribute_defaults,
                **attribute_lookup,
            )

            action = "Created" if attribute_created else "Updated"
            style = self.style.SUCCESS if attribute_created else self.style.WARNING
            self.stdout.write(style(f"{action} attribute: {attribute_obj}"))

            for value_entry in values_data:
                value_lookup = {
                    "attribute": attribute_obj,
                    "value": value_entry["value"],
                }
                value_defaults = {
                    k: v for k, v in value_entry.items() if k not in value_lookup
                }

                value_obj, value_created = AttributeValue.objects.update_or_create(
                    defaults=value_defaults,
                    **value_lookup,
                )

                value_action = "Created" if value_created else "Updated"
                value_style = (
                    self.style.SUCCESS if value_created else self.style.WARNING
                )
                self.stdout.write(
                    value_style(f"{value_action} attribute value: {value_obj}"),
                )
