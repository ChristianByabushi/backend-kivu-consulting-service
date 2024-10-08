# Generated by Django 5.1 on 2024-09-07 20:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contract', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Paiement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode_paiement', models.CharField(max_length=50)),
                ('montant', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_paiement', models.DateField()),
                ('contrat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contract.contrat')),
            ],
        ),
    ]
