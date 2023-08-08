from pprint import pprint


class NotInScopeErr(Exception):
    def __init__(self, msg):
        print(msg)
        self.msg = msg


class Scope(object):
    def __init__(self, values):
        self.values = values

    def get_sym(self, x):
        result = None
        if x in self.values:
            result = self.values[x]
        elif hasattr(self, "parent"):
            result = self.parent.get_sym(x)
        if result is None:
            msg = f"symbol not defined: {x}"
            raise NotInScopeErr(msg)
        return result

    def push(self, vals):
        scope = Scope(vals)
        scope.parent = self
        return scope

    def get_flattened(self):
        vals = {k: v for k, v in list(self.values.items())}
        if not hasattr(self, "parent"):
            return vals
        parent_vals = self.parent.get_flattened()
        parent_vals.update(vals)
        return parent_vals

    def log(self):
        pprint(self.get_flattened())
