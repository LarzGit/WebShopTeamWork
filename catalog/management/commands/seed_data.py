import random

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from catalog.models import Category, Product, Review

User = get_user_model()
fake = Faker('uk_UA')  # генерація даних українською


CATEGORIES = [
    'Електроніка', 'Одяг', 'Взуття', 'Книги', 'Іграшки',
    'Спорт та відпочинок', 'Побутова техніка', 'Краса та здоров\'я',
    'Автотовари', 'Дім і сад',
]


class Command(BaseCommand):
    help = 'Генерує тестові дані: категорії, товари, користувачів та відгуки'

    def add_arguments(self, parser):
        parser.add_argument(
            '--products', type=int, default=50,
            help='Кількість товарів для генерації (за замовчуванням 50)'
        )
        parser.add_argument(
            '--reviews', type=int, default=150,
            help='Кількість відгуків для генерації (за замовчуванням 150)'
        )
        parser.add_argument(
            '--users', type=int, default=10,
            help='Кількість тестових користувачів (за замовчуванням 10)'
        )
        parser.add_argument(
            '--clear', action='store_true',
            help='Очистити існуючі товари/категорії/відгуки перед генерацією'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Очищення старих даних...')
            Review.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()

        # 1. Категорії
        self.stdout.write('Створення категорій...')
        categories = []
        for name in CATEGORIES:
            category, _ = Category.objects.get_or_create(name=name)
            categories.append(category)
        self.stdout.write(self.style.SUCCESS(f'  Готово: {len(categories)} категорій'))

        # 2. Тестові користувачі (для авторів відгуків)
        self.stdout.write('Створення тестових користувачів...')
        users = list(User.objects.filter(is_superuser=False)[:options['users']])
        needed = options['users'] - len(users)
        for i in range(max(needed, 0)):
            username = fake.unique.user_name()
            user = User.objects.create_user(
                username=username,
                email=fake.unique.email(),
                password='testpass123',
            )
            users.append(user)
        self.stdout.write(self.style.SUCCESS(f'  Готово: {len(users)} користувачів'))

        # 3. Товари
        self.stdout.write('Створення товарів...')
        products = []
        for _ in range(options['products']):
            product = Product.objects.create(
                name=fake.catch_phrase(),
                description=fake.paragraph(nb_sentences=5),
                price=round(random.uniform(50, 25000), 2),
                category=random.choice(categories),
                stock=random.choice([0, 0, 3, 5, 10, 25, 50, 100]),  # деякі навмисно 0 (немає в наявності)
            )
            products.append(product)
        self.stdout.write(self.style.SUCCESS(f'  Готово: {len(products)} товарів'))

        # 4. Відгуки (не для кожного товару, і не завжди)
        self.stdout.write('Створення відгуків...')
        review_count = 0
        target_reviews = options['reviews']
        attempts = 0
        while review_count < target_reviews and attempts < target_reviews * 3:
            attempts += 1
            product = random.choice(products)
            user = random.choice(users)
            # уникнення дубля відгуку одного юзера на один товар
            if Review.objects.filter(product=product, user=user).exists():
                continue
            Review.objects.create(
                product=product,
                user=user,
                rating=random.randint(1, 5),
                comment=fake.sentence(nb_words=12),
            )
            review_count += 1
        self.stdout.write(self.style.SUCCESS(f'  Готово: {review_count} відгуків'))

        self.stdout.write(self.style.SUCCESS('\nГенерація тестових даних завершена!'))
