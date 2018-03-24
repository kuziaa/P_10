import random, copy
from pprint import pprint as pp

# The function is not used.
# It can count how much fuel was used
# It works up to 990000 km
def spent_fuel_func(rout, cons, change_after, change_on):
    if rout > change_after:
        return  change_after * cons / 100 + func_1(rout - change_after, cons * (1 + change_on / 100), change_after, change_on)
    else:
        return rout * cons / 100

# Assumptions:
# 1 - We have money for fuel and repair.
# 2 - Car is getting cheaper, but it costs nothing for us.


class Car(object):
    created = 0
    engine_parameters = {
        'gasoline': {'fuel_cost': 2.4,                            # dolar per liter
                     'car_cost': 10000.0,                         # new car cost
                     'car_gettind_cheaper': [1000.0, 9.5],        # every {0} km car gettind cheaper on {1} dollars
                     'repair': [100000.0, 500.0],                 # every {0} km car need be repaired on {1} dollars
                     'fuel_consumption_100': [8.0, 1000.0, 1.0]}, # [primary fuel consumption, change_after_{1}_km, change_on_{2}_percents]
        'diesel': {'fuel_cost': 1.8,
                   'car_cost': 10000.0,
                   'car_gettind_cheaper': [1000.0, 10.5],
                   'repair': [150000.0, 700],
                   'fuel_consumption_100': [6.0, 1000.0, 1.0]}
                         }
    
    def __init__(self):
        x = 2
        Car.created += 1
        self.num_of_car = Car.created
        self.engine_parameters = Car.engine_parameters
        self.have_money = 10000
        self.fuel_cost = self.engine_parameters[self.engine_type]['fuel_cost']
        self.car_cost = self.engine_parameters[self.engine_type]['car_cost']
        self.car_gettind_cheaper_after = self.engine_parameters[self.engine_type]['car_gettind_cheaper'][0]
        self.car_gettind_cheaper_on = self.engine_parameters[self.engine_type]['car_gettind_cheaper'][1]
        self.range_before_repair = self.engine_parameters[self.engine_type]['repair'][0]
        self.cost_repair = self.engine_parameters[self.engine_type]['repair'][1]
        self.fuel_consumption = self.engine_parameters[self.engine_type]['fuel_consumption_100'][0]
        self.change_fuel_consumption_after = self.engine_parameters[self.engine_type]['fuel_consumption_100'][1]
        self.change_fuel_consumption_on = self.engine_parameters[self.engine_type]['fuel_consumption_100'][2]
        self.amount_of_fuel = self.tank_sizes
        self.can_run_before_utilization = round((self.car_cost / self.car_gettind_cheaper_on) * self.car_gettind_cheaper_after, 2)

        self.engine_repair_was = 0 # times
        self.was_fueling = 0       # times
        self.spent_on_fuel = 0
        self.spent_on_repair = 0
        self.history_range = []

    @property
    def engine_type(self):
        all_types = ('gasoline', 'diesel')
        if self.num_of_car % 3 != 0:
            return all_types[0]
        else:
            return all_types[1]

    @property
    def tank_sizes(self):
        all_sizes = (60, 75)
        if self.num_of_car % 5 == 0:
            return all_sizes[1]
        else:
            return all_sizes[0]

    def move(self, rout):
        while rout != 0:
# Rout is divided on segments
            fuel_remains_on = round(self.amount_of_fuel / self.fuel_consumption * 100, 2)
            range_for_stop = [rout]
            range_for_stop.append(fuel_remains_on)
            range_for_stop.append(self.change_fuel_consumption_after)
            range_for_stop.append(self.can_run_before_utilization)
            range_for_stop.append(self.range_before_repair)

            min_range = min(range_for_stop)
            if not min_range and not self.have_money:
                break

            self.history_range.append(min_range)
            self.amount_of_fuel = round(self.amount_of_fuel - min_range * self.fuel_consumption / 100)
            self.change_fuel_consumption_after = round(self.change_fuel_consumption_after - min_range, 2)
            self.can_run_before_utilization = round(self.can_run_before_utilization - min_range, 2)
            self.range_before_repair = round(self.range_before_repair - min_range, 2)
            rout = round(rout - min_range, 2)

            if self.amount_of_fuel == 0:
                self.fueling()
                continue

            if self.change_fuel_consumption_after == 0:
                self.change_fuel_consumption()
                continue

            if self.can_run_before_utilization == 0:
                break

            if self.range_before_repair == 0:
                self.maintenance()
                continue

    def fueling(self):
        if self.have_money > self.fuel_cost * self.tank_sizes:
            self.have_money = round(self.have_money - self.fuel_cost * self.tank_sizes, 2)
            self.amount_of_fuel = self.tank_sizes
        else:
            self.amount_of_fuel = round(self.have_money / self.fuel_cost, 2)
            self.have_money = 0
        self.was_fueling += 1
        self.spent_on_fuel += self.amount_of_fuel * self.fuel_cost

    def change_fuel_consumption(self):
        self.fuel_consumption = self.fuel_consumption * (1 + self.change_fuel_consumption_on / 100)
        self.change_fuel_consumption_after = self.engine_parameters[self.engine_type]['fuel_consumption_100'][1]

    def maintenance(self):
        self.engine_repair_was += 1
        self.spent_on_repair += self.cost_repair
        self.range_before_repair = self.engine_parameters[self.engine_type]['repair'][0]

    @property
    def odometr(self):
        return round(sum(self.history_range), 2)

    @property
    def depreciated_cost(self):
        return round(self.car_cost - (sum(self.history_range) / 1000) * self.car_gettind_cheaper_on, 2)

# Able run for the remaining money
    @property
    def able_run(self):
        temp_car = copy.deepcopy(self)
        while True:
            temp_car.move(100000)
            if temp_car.have_money == 0 or temp_car.can_run_before_utilization == 0:
                return round(sum(temp_car.history_range) - sum(self.history_range))


car_park = []
for _ in range(200):
    car_park.append(Car())

for car in car_park:
    route = random.randint(5000, 286000)
    car.move(route)

gasoline_cars = list(filter(lambda x: x.engine_type == 'gasoline', car_park))
gasoline_cars.sort(key=lambda x: x.able_run)

diesel_cars = list(filter(lambda x: x.engine_type == 'diesel', car_park))
diesel_cars.sort(key=lambda x: x.depreciated_cost)

total_cost = reduce(lambda a, b: a + b.depreciated_cost, [car_park[0].depreciated_cost] + car_park[1:])

print('GASOLINE_CARS')
pp(['{}; able_run = {}; have_money = {}; rout = {}'.format(_.num_of_car, _.able_run, _.have_money, sum(_.history_range)) for _ in gasoline_cars])
print('\nDIESEL_CARS')
pp(['{}; depreciated_cost = {}; have_money = {}; rout = {}'.format(_.num_of_car, _.depreciated_cost, _.have_money, sum(_.history_range)) for _ in diesel_cars])
print('\nTotal_cost = {}'.format(total_cost))
