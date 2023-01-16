from models import GenderEnum

# Calculate BMI using the formula BMI = [Weight (lbs) / Height (in)²] x 703.
def calculateBMI(height, weight):
    return round((weight / (height ** 2)) * 703, 2)


# Calculate BMR based on gender and level of activity.
def calculateBMR(height, weight, age, level_of_activity, gender):
    if gender == GenderEnum.MALE:
        bmr = 88.362 + (13.397 * (weight / 2.205)) + (4.799 * (height * 2.54)) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * (weight / 2.205)) + (3.098 * (height * 2.54)) - (4.330 * age)

    # Little to no exercise
    if level_of_activity == 1:
        bmr *= 1.2
    # Some exercise
    elif level_of_activity == 2:
        bmr *= 1.45
    # Lots of exercise
    else:
        bmr *= 1.8

    return round(bmr)
