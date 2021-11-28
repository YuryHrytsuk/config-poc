import abc
from copy import deepcopy
from inspect import isclass
from typing import Any, Dict, List, Optional, Set, Type, Union

FlatDict = Dict[str, Any]
Config = Dict[str, Any]


class ConfigManager:

    def __init__(
        self,
        init_cfg: Config,
        components: Optional[List[Union[Type["ConfigComponent"], "ConfigComponent"]]] = None
    ):
        self.init_cfg = init_cfg
        self._components: List[Union[Type["ConfigComponent"], "ConfigComponent"]] = []

        if components is not None:
            for component in components:
                self.add_component(component)

    def add_component(self, component: Union[Type["ConfigComponent"], "ConfigComponent"]) -> None:
        if any(c.name() == component.name() for c in self._components):
            raise ValueError(f"Duplicate '{component.name}' ConfigComponent")

        self._components.append(component)
        component.manager = self

    @property
    def components(self) -> List[Union[Type["ConfigComponent"], "ConfigComponent"]]:
        return self._components

    def configure_config(self) -> Config:
        cfg = deepcopy(self.init_cfg)

        for component in self.components:
            if isclass(component):
                component_obj = component()
            else:
                component_obj = component

            if component_obj.is_enabled(cfg):
                cfg.update(component_obj.configure(cfg))

        return cfg


class ConfigComponent(abc.ABC):

    def __init__(self):
        self._manager: Optional["ConfigManager"] = None

    @property
    def manager(self) -> "ConfigManager":
        if self._manager is None:
            raise RuntimeError("")

        return self._manager

    @manager.setter
    def manager(self, manager: "ConfigManager") -> None:
        self._manager = manager

    def is_enabled(self, cfg: Config) -> bool:
        return True

    @classmethod
    def name(cls) -> str:
        return cls.__name__

    @abc.abstractmethod
    def configure(self, cfg: Config) -> FlatDict:
        pass


class Component1(ConfigComponent):

    def configure(self, cfg) -> FlatDict:
        return {"foo": "bar"}


class Component2(ConfigComponent):

    def configure(self, cfg) -> FlatDict:
        return {cfg["foo"]: "baz"}


if __name__ == "__main__":
    c1 = Component1()
    cm = ConfigManager(init_cfg={}, components=[c1, Component2])
    cfg = cm.configure_config()
    print(cfg)
