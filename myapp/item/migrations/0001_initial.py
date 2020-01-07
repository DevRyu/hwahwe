# Generated by Django 2.2.4 on 2020-01-07 02:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('oily', models.SmallIntegerField()),
                ('dry', models.SmallIntegerField()),
                ('sensitive', models.SmallIntegerField()),
            ],
            options={
                'db_table': 'ingredient',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imageId', models.CharField(max_length=500)),
                ('name', models.CharField(max_length=150)),
                ('price', models.IntegerField()),
                ('gender', models.CharField(max_length=50)),
                ('category', models.CharField(max_length=100)),
                ('monthlySales', models.IntegerField()),
            ],
            options={
                'db_table': 'item',
            },
        ),
        migrations.CreateModel(
            name='ItemSkinType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_skin_type', models.CharField(max_length=20)),
                ('first_skin_score', models.SmallIntegerField()),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='item.Item')),
            ],
            options={
                'db_table': 'itemskintype',
            },
        ),
        migrations.CreateModel(
            name='ItemIngredientMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='item.Ingredient')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='item.Item')),
            ],
            options={
                'db_table': 'itemingredientmapping',
            },
        ),
        migrations.AddField(
            model_name='item',
            name='ingredients',
            field=models.ManyToManyField(through='item.ItemIngredientMapping', to='item.Ingredient'),
        ),
    ]
