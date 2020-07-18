# Generated by Django 3.0.8 on 2020-07-18 01:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('topical', '0003_ingredient_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
                ('description', models.TextField(max_length=8192, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='description',
            field=models.TextField(max_length=8192, null=True),
        ),
        migrations.AlterField(
            model_name='ingredientname',
            name='ingredient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='names', to='topical.Ingredient'),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='in_products',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ingredients', to='topical.Product'),
        ),
    ]