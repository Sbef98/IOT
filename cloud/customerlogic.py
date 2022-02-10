import datetime

from app import db
from models import Customer

# averages based on Gender-and-Age-Detection/Detect.py predictions
ageList = [1, 5, 10, 19, 29, 41, 51, 80]
gender_list = ['M', 'F']

timeInterval = datetime.timedelta(minutes=30)


def getCustomersInTimeInterval(timedelta):
    currentTime = datetime.datetime.utcnow()
    timeAgo = currentTime - timedelta
    customers = db.session.query(Customer).filter(
        Customer.timestamp > timeAgo).all()

    return customers


def getCustomerNumberInTimeInterval(timedelta):
    return len(getCustomersInTimeInterval(timedelta))


def getCurrentMainAgeAndGender():
    customers = getCustomersInTimeInterval(timeInterval)
    numbers = []
    currentTime = datetime.datetime.utcnow()
    timeAgo = currentTime - timeInterval
    for value in ageList:
        customerNumber = db.session.query(Customer).filter(
            Customer.timestamp > timeAgo,
            Customer.age == value).all()
        numbers.append(len(customerNumber))

    highestIndex = numbers.index(max(numbers))

    # TODO: Be careful whether to target parents or kids

    age = ageList[highestIndex]

    number = len(customers)

    female = len(db.session.query(Customer).filter(
        Customer.timestamp > timeAgo,
        Customer.gender == 'F').all())
    gender = 'F'
    if number / 2 >= female:
        gender = 'M'

    return age, gender
