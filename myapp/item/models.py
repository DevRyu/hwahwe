from django.db import models

class Ingredient(models.Model):
    name         = models.CharField(max_length = 50)
    oily         = models.SmallIntegerField()
    dry          = models.SmallIntegerField()
    sensitive    = models.SmallIntegerField()

    class Meta:
        db_table = "ingredient"

class Item(models.Model):
    imageId      = models.CharField(max_length = 500)
    name         = models.CharField(max_length = 150)
    price        = models.IntegerField()
    gender       = models.CharField(max_length = 50)
    category     = models.CharField(max_length = 100)
    monthlySales = models.IntegerField()
    ingredients  = models.ManyToManyField(Ingredient, through='itemingredientmapping')

    class Meta:
        db_table = "item"

class ItemIngredientMapping(models.Model):
    item       = models.ForeignKey(Item, on_delete = models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete = models.CASCADE)

    class Meta:
        db_table  = "itemingredientmapping"

class ItemSkinType(models.Model):
    item                = models.ForeignKey(Item, on_delete = models.CASCADE)
    first_skin_type     = models.CharField(max_length = 20)
    first_skin_score    = models.SmallIntegerField()

    class Meta:
        db_table  = "itemskintype"

