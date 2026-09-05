from tux_motd.misc.configuration import Configuration

class Module:

    @classmethod
    def init_module(cls, settings):
        name = cls.__name__.lower()
        if Configuration.get(f"{name}.show", True):
            return cls(settings)
        return None

    def get(self, key, default=None):
        keys = key.split('.')
        data = self.settings
        for k in keys:
            if isinstance(data, dict) and k in data:
                data = data[k]
            else:
                return default
        return data