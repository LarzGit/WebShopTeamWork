import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('new', 'Нове'), ('processing', 'В обробці'), ('shipped', 'Відправлено'), ('delivered', 'Доставлено'), ('cancelled', 'Скасовано')], default='new', max_length=20)),
                ('delivery_method', models.CharField(choices=[('courier', "Кур'єр"), ('pickup', 'Самовивіз'), ('post', 'Поштове відділення')], max_length=20)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('recipient_phone', models.CharField(max_length=20)),
                ('payment_method', models.CharField(choices=[('card_online', 'Картка онлайн'), ('cash_on_delivery', 'Готівкою при отриманні')], max_length=20)),
                ('total_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]