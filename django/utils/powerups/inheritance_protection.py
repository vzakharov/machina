from typing import ClassVar


class Uninheritable():

    override_inheritance_protection: ClassVar[bool] = False
    intended_use: ClassVar[str | None] = None

    @classmethod
    def __init_subclass__(cls, **kwargs):

        super().__init_subclass__(**kwargs)

        is_direct_descendant = any(
            base is Uninheritable for base in cls.__bases__
        )

        if is_direct_descendant:
            if not cls.intended_use:
                raise TypeError(
                    f"{cls.__name__} is a direct descendant of {Uninheritable.__name__} "
                    f"and thus must define the `intended_use` class variable."
                )
            return

        if not cls.override_inheritance_protection:
            uninheritable_class_name = next(
                base.__name__ for base in cls.__bases__ if issubclass(base, Uninheritable)
            )
            raise TypeError(
                f"Cannot inherit directly from {uninheritable_class_name}. "
                f"Use {cls.intended_use} instead. "
                f"Alternatively, set {uninheritable_class_name}.override_inheritance_protection = True "
                "if you’re feeling lucky."
            )