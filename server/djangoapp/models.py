from django.db import models
from django.utils.timezone import now
# from .dealer import Dealer

# Car Make model with fields: Name, Description, Country, Founded Date, etc.
class CarMake(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    country = models.CharField(max_length=255)
    founded_date = models.DateField()
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return str(self.name)

class CarDealer(models.Model):
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    id = models.IntegerField(primary_key=True)
    lat = models.FloatField()
    long = models.FloatField()
    st = models.CharField(max_length=2)
    zip = models.CharField(max_length=10)
    full_name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)

    def __str__(self):
        return "Dealer name: " + self.full_name
class CarModel(models.Model):
    SEDAN = 'SD'
    SUV = 'SV'
    WAGON = 'WG'
    CAR_TYPES = [(SEDAN, 'Sedan'), (SUV, 'SUV'), (WAGON, 'Wagon')]

    # dealer = models.ForeignKey(CarDealer, on_delete=models.CASCADE)
    id = models.IntegerField(default=1, primary_key=True)
    dealer_id = models.IntegerField(null=True)  # This will store the CarDealer id
    type = models.CharField(
        null=False,
        max_length=50,
        choices=CAR_TYPES,
        default=SEDAN
    )
    year = models.IntegerField()
    engine = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    mpg = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return str(self.id)  # or str(self.type)

# Dealer Review model with fields: Dealership, Name, Purchase, Review, Purchase Date, Car Make, Car Model, Car Year, Sentiment, ID
class DealerReview(models.Model):
    """
    Represents a review of a car dealership.
    """
    dealer = models.ForeignKey(CarDealer, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    purchase = models.BooleanField()
    review = models.TextField()
    purchase_date = models.DateField()
    car_make = models.CharField(max_length=255)
    car_model = models.CharField(max_length=255)
    car_year = models.IntegerField()
    sentiment = models.CharField(max_length=255)  # The sentiment value will be determined by Watson NLU service
    id = models.AutoField(primary_key=True)
    rating = models.IntegerField()  # add this line
    dealer_name = models.CharField(max_length=255, default='Default Dealer Name')  # updated line
    review_text = models.TextField()

    def __str__(self):
        return f"Review by {self.name} on {self.purchase_date}"

# Car model with fields: Make, Model, Year, Color, Price, Mileage

class Car(models.Model):
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    model = models.ForeignKey(CarModel, on_delete=models.CASCADE)
    dealer = models.ForeignKey(CarDealer, on_delete=models.CASCADE, null=True)  # Changed from CarDealerModel to CarDealer
    year = models.IntegerField()
    color = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    mileage = models.IntegerField()

    def __str__(self):
        return f'{self.make} {self.model} ({self.year})' # Add this function to your existing code

# class Car(models.Model):
#     make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
#     model = models.ForeignKey(CarModel, on_delete=models.CASCADE)
#     dealer = models.ForeignKey(CarDealerModel, on_delete=models.CASCADE) 
#     year = models.IntegerField()
#     color = models.CharField(max_length=255)
#     price = models.DecimalField(max_digits=8, decimal_places=2)
#     mileage = models.IntegerField()

#     def __str__(self):
#         return f'{self.make} {self.model} ({self.year})'
