from django.db import models


class OrderField(models.PositiveIntegerField):
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields or []
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if value is None:
            qs = model_instance.__class__.objects.all()
            if self.for_fields:
                filters = {
                    field: getattr(model_instance, field) for field in self.for_fields
                }
                qs = qs.filter(**filters)
            last_item = qs.order_by(f"-{self.attname}").first()
            value = getattr(last_item, self.attname) + 1 if last_item is not None else 0
            setattr(model_instance, self.attname, value)
        return value

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.for_fields:
            kwargs["for_fields"] = self.for_fields
        return name, path, args, kwargs
