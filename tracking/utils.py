from django.db import models

class CarStats:
    
    @staticmethod
    def get_total_fuel_for_car(car):
        """Суммарный расход топлива по автомобилю"""
        waybills = car.waybill_set.all()
        total = 0
        for waybill in waybills:
            mileage = waybill.end_mileage - waybill.start_mileage
            total += mileage * float(car.fuel_rate)
        return total
    
    @staticmethod
    def get_total_fuel_for_car_period(car, start_date=None, end_date=None):
        """Суммарный расход топлива за период"""
        waybills = car.waybill_set.all()
        if start_date:
            waybills = waybills.filter(date__gte=start_date)
        if end_date:
            waybills = waybills.filter(date__lte=end_date)
        
        total = 0
        for waybill in waybills:
            mileage = waybill.end_mileage - waybill.start_mileage
            total += mileage * float(car.fuel_rate)
        return total