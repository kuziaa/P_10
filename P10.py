import random
from pprint import pprint as pp

class Car(object):

    created = 0

    def __init__(self):
        Car.created += 1
        self.created = Car.created
        self.engine = self.engine_types()
        self.fuel_cost =self.cost = self.initial_parameters[self.engine]['fuel_cost']
        self.cost = self.initial_parameters[self.engine]['cost'][0]
        self.reduction_cost_after = self.initial_parameters[self.engine]['cost'][1]
        self.reduction_cost_on = self.initial_parameters[self.engine]['cost'][2]
        self.range_before_repair = self.initial_parameters[self.engine]['range_before_repair']
        self.cost_repair = self.initial_parameters[self.engine]['cost_repair']
        self.fuel_consumption_100 = self.initial_parameters[self.engine]['fuel_consumption_100'][0]
        self.change_fuel_consumption_after = self.initial_parameters[self.engine]['fuel_consumption_100'][1]
        self.change_fuel_consumption_on = self.initial_parameters[self.engine]['fuel_consumption_100'][2]
        self.tank = self.tank_sizes()

        self.amount_of_fuel = self.tank_sizes()
        self.engine_repair_was = 0 # times
        self.tank_was_filled = 0 # times
        self.was_spent_on_fuel = 0
        self.history_range = []

    def __repr__(self):
        if self.engine == 'gasoline':
            return 'car_{}; before_recycling = {}'.format(self.created, self.before_recycling())
        if self.engine == 'diesel':
            return 'car_{}; residual_value = {}'.format(self.created, self.residual_value())

    def engine_types(self):
        all_types = ('gasoline', 'diesel')
        self.initial_parameters = {
            'gasoline': {'fuel_cost': 2.4,
                    'cost': [10000, 1000, 9.5], # [cost, change_after, change_on]
                    'range_before_repair': 100000,
                    'cost_repair': 500,
                    'fuel_consumption_100': [8, 1000, 1]}, # [fuel consumption, change_after, change_on_percents]
            'diesel': {'fuel_cost': 1.8,
                       'cost': [10000, 1000, 10.5], # [cost, change_after, change_on]
                       'range_before_repair': 150000,
                       'cost_repair': 700,
                       'fuel_consumption_100': [6, 1000, 1]} # [fuel consumption, change_after, change_on_percents]
                                   }
        if self.created % 3 == 0:
            return all_types[1]
        else:
            return all_types[0]

    def tank_sizes(self):
        all_sizes = (60, 75)
        if self.created % 5 == 0:
            return all_sizes[1]
        else:
            return all_sizes[0]

    def move(self, route):

        while True:
            # have fuel for:
            fuel_remains_on = round(self.amount_of_fuel / self.fuel_consumption_100 * 100, 2)
            range_for_stop = [route]
            range_for_stop.append(fuel_remains_on)
            range_for_stop.append(self.change_fuel_consumption_after)
            range_for_stop.append(self.reduction_cost_after)
            range_for_stop.append(self.range_before_repair)
            min_range = min(range_for_stop)

            self.history_range.append(min_range)
            self.amount_of_fuel = round(self.amount_of_fuel - min_range * self.fuel_consumption_100 / 100, 2)
            self.change_fuel_consumption_after = round(self.change_fuel_consumption_after - min_range, 2)
            self.reduction_cost_after = round(self.reduction_cost_after - min_range, 2)
            self.range_before_repair = round(self.range_before_repair - min_range, 2)
            route = round(route - min_range, 2)

            if self.amount_of_fuel == 0:
                self.amount_of_fuel = self.tank_sizes()
                self.tank_was_filled += 1

                self.was_spent_on_fuel = round(self.was_spent_on_fuel + self.tank * self.fuel_cost, 2)
                continue

            if self.change_fuel_consumption_after == 0:
                self.fuel_consumption_100 = self.fuel_consumption_100 * (1 + self.change_fuel_consumption_on / 100)
                self.change_fuel_consumption_after = self.initial_parameters[self.engine]['fuel_consumption_100'][1]
                continue

            if self.reduction_cost_after == 0:
                if self.cost == 0:
                    print('the machine must be recycled')
                    break
                self.cost = round(self.cost - self.reduction_cost_on, 2)
                self.reduction_cost_after = self.initial_parameters[self.engine]['cost'][1]
                continue

            if self.range_before_repair * (self.engine_repair_was + 1) == 0:
                self.maintenance()
                continue
            break


    def maintenance(self):
        self.engine_repair_was += 1
        self.range_before_repair = self.initial_parameters[self.engine]['range_before_repair']
#        print('The car was repaired!')

    def odometr_reading(self):
        passed_distance = round(sum(self.history_range), 2)
        print('The car ran {} km'.format(passed_distance))
        return passed_distance

    def residual_value(self):
 #       print('residual value of the car is {} dollars'.format(self.cost))
        return self.cost

    def spent_on_fuel(self):
        print('{} spent_on_fuel'.format(self.was_spent_on_fuel))
        return self.was_spent_on_fuel

    def refueled(self):
        print('The car was refueled {} times'.format(self.tank_was_filled))
        return self.tank_was_filled

    def before_recycling(self):
        will_utilize_after = (self.cost / self.reduction_cost_on - 1) * self.initial_parameters[self.engine]['cost'][1] + self.reduction_cost_after
#        print('The car can run {} km before_recycling'.format(round(will_utilize_after, 2)))
        return round(will_utilize_after, 2)


car_park = []
for _ in range(200):
    car_park.append(Car())

for car in car_park:
    route = random.randint(55000, 286000)
    car.move(route)

gasoline_cars = list(filter(lambda x: x.engine == 'gasoline', car_park))
gasoline_cars.sort(key=lambda x: x.before_recycling())

diesel_cars = list(filter(lambda x: x.engine == 'diesel', car_park))
diesel_cars.sort(key=lambda x: x.residual_value())

print('GASOLINE_CARS')
pp(gasoline_cars)
print('\nDIESEL_CARS')
pp(diesel_cars)
