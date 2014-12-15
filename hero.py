__author__ = 'Max'
from operator import itemgetter, attrgetter


class Param:
    def __init__(self, name, full_data):
        data = full_data[name]
        self.name = data['name']
        self.value = data['value']
        self.id = name
        self.order = data['order']
        self.cost = 1
        if 'cost' in data:
            self.cost = data['cost']

    def json(self):
        return {'name': self.name, 'value': self.value, 'id': self.id, 'order': self.order, 'cost': self.cost}


class Bar:
    def __init__(self, bar, data, hero):
        self.id = bar
        self.name = data['name']
        self.value = data['value']
        self.min = data['min']
        maximum = data['max']
        if isinstance(maximum, int):
            self.max = maximum
        else:
            try:
                self.max = eval(maximum)
            except:
                self.max = self.value
        self.percent = str(round(self.value / self.max * 100))

    def json(self):
        return {'name': self.name, 'value': self.value, 'id': self.id, 'min': self.min, 'max': self.max}


class Hero:
    @staticmethod
    def convert_to_dict(self):
        pass

    def __init__(self, row):
        self.name = row['name']
        self.params = row['params']
        self.static = row['static']
        self.inventory = row['inventory']
        self.bars = row['bars']
        self.id = row['id']
        self.exp = row['exp']

    def get(self, name):
        return Param(name, self.params).value

    def get_params(self):
        result = []
        for param in self.params:
            result.append(Param(param, self.params))
        result = sorted(result, key=attrgetter('order'))
        return result

    def increase_param(self, param_type, name, delta):
        maximum = 100
        minimum = 0
        if param_type == 'bars':
            dictionary = self.bars
            bars = self.get_bars_dict()
            bar = bars[name]
            minimum = bar.min
            maximum = bar.max
        elif param_type == 'params':
            dictionary = self.params
        dictionary[name]['value'] += delta
        if dictionary[name]['value'] > maximum:
            dictionary[name]['value'] = maximum
        elif dictionary[name]['value'] < minimum:
            dictionary[name]['value'] = minimum

        return dictionary

    def get_bars(self):
        bars = []
        for bar in self.bars:
            bars.append(Bar(bar, self.bars[bar], self))
        return bars

    def get_bars_dict(self):
        bars = {}
        for bar in self.bars:
            bars[bar] = Bar(bar, self.bars[bar], self)
        return bars

    def json(self):
        params = [p.json() for p in self.get_params()]
        params = sorted(params, key=itemgetter('order'))

        bars = [p.json() for p in self.get_bars()]
        return {'name': self.name,
                'id': self.id,
                'bars': bars,
                'params': params,
                'exp': self.exp}