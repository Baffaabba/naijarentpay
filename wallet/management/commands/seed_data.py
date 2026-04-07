from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = "Seed the database with demo data for 9jaRentPay"

    def handle(self, *args, **options):
        from accounts.models import User
        from properties.models import Property, Amenity, PropertyAmenity
        from leases.models import Lease
        from applications.models import Application
        from wallet.models import Wallet, SavingsGoal, WalletTransaction
        from payments.models import Payment
        from messaging.models import Conversation, Message

        self.stdout.write("Clearing old seed data...")
        User.objects.filter(is_superuser=False).delete()
        Amenity.objects.all().delete()

        # ── Amenities ───────────────────────────────────────────────
        amenities_data = [
            ("Fully Furnished", "🛋️"),
            ("24/7 Security", "🔒"),
            ("Generator", "⚡"),
            ("Swimming Pool", "🏊"),
            ("Car Park", "🚗"),
            ("Water Supply", "💧"),
            ("Air Conditioning", "❄️"),
            ("CCTV", "📹"),
            ("Gym", "🏋️"),
            ("Playground", "🛝"),
        ]
        amenity_objs = {}
        for name, icon in amenities_data:
            a = Amenity.objects.create(name=name, icon=icon)
            amenity_objs[name] = a

        # ── Users ────────────────────────────────────────────────────
        mimi = User.objects.create_user(
            username="mimi",
            email="mimi@example.com",
            password="demo1234",
            first_name="Mimi",
            last_name="Praise",
            role="tenant",
            phone="08012345678",
            address="14 Admiralty Way, Lekki Phase 1, Lagos",
            is_kyc_verified=True,
        )
        chinenye = User.objects.create_user(
            username="chinenye",
            email="chinenye@example.com",
            password="demo1234",
            first_name="Chinenye",
            last_name="Nwa",
            role="landlord",
            phone="08098765432",
            is_kyc_verified=True,
        )
        emeka = User.objects.create_user(
            username="emeka",
            email="emeka@example.com",
            password="demo1234",
            first_name="Emeka",
            last_name="Onuoha",
            role="landlord",
            phone="08055544433",
            is_kyc_verified=True,
        )

        # ── Properties ───────────────────────────────────────────────
        prop_data = [
            {
                "landlord": chinenye,
                "title": "2 Bedroom Flat, Lekki Phase 1",
                "property_type": "2bed",
                "location": "Lekki, Lagos",
                "city": "Lagos",
                "state": "Lagos",
                "price_per_year": Decimal("4200000"),
                "bedrooms": 2,
                "bathrooms": 2,
                "sqft": 1200,
                "age": "3 years",
                "description": "Beautiful 2-bedroom flat in a serene estate in Lekki Phase 1. Fully furnished with modern finishes.",
                "image_url": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800",
                "is_verified": True,
                "rating": Decimal("4.8"),
                "amenities": ["Fully Furnished", "24/7 Security", "Car Park", "Generator"],
            },
            {
                "landlord": chinenye,
                "title": "Self-Con Apartment, Ajah",
                "property_type": "self-con",
                "location": "Ajah, Lagos",
                "city": "Lagos",
                "state": "Lagos",
                "price_per_year": Decimal("2400000"),
                "bedrooms": 1,
                "bathrooms": 1,
                "sqft": 650,
                "age": "5 years",
                "description": "Cozy self-contained apartment in Ajah. Perfect for young professionals.",
                "image_url": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800",
                "is_verified": True,
                "rating": Decimal("4.3"),
                "amenities": ["Water Supply", "Car Park", "24/7 Security"],
            },
            {
                "landlord": emeka,
                "title": "Duplex with Generator, Maitama",
                "property_type": "duplex",
                "location": "Maitama, Abuja",
                "city": "Abuja",
                "state": "FCT",
                "price_per_year": Decimal("9600000"),
                "bedrooms": 4,
                "bathrooms": 4,
                "sqft": 3200,
                "age": "2 years",
                "description": "Luxury duplex in the heart of Maitama. Features a private garden and backup generator.",
                "image_url": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800",
                "is_verified": True,
                "rating": Decimal("4.9"),
                "amenities": ["Generator", "Swimming Pool", "24/7 Security", "CCTV", "Gym"],
            },
            {
                "landlord": emeka,
                "title": "1 Bedroom Studio, Gwarinpa",
                "property_type": "1bed",
                "location": "Gwarinpa, Abuja",
                "city": "Abuja",
                "state": "FCT",
                "price_per_year": Decimal("1800000"),
                "bedrooms": 1,
                "bathrooms": 1,
                "sqft": 500,
                "age": "4 years",
                "description": "Affordable studio in Gwarinpa Estate. Ideal for singles and students.",
                "image_url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800",
                "is_verified": False,
                "rating": Decimal("4.1"),
                "amenities": ["Water Supply", "Air Conditioning"],
            },
            {
                "landlord": chinenye,
                "title": "3 Bedroom Bungalow, GRA Port Harcourt",
                "property_type": "bungalow",
                "location": "GRA, Port Harcourt",
                "city": "Port Harcourt",
                "state": "Rivers",
                "price_per_year": Decimal("7200000"),
                "bedrooms": 3,
                "bathrooms": 3,
                "sqft": 2100,
                "age": "6 years",
                "description": "Spacious bungalow in Port Harcourt GRA. Quiet neighborhood with great security.",
                "image_url": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800",
                "is_verified": True,
                "rating": Decimal("4.6"),
                "amenities": ["Car Park", "24/7 Security", "CCTV", "Water Supply"],
            },
            {
                "landlord": chinenye,
                "title": "Mini Flat, Ikeja",
                "property_type": "mini-flat",
                "location": "Ikeja, Lagos",
                "city": "Lagos",
                "state": "Lagos",
                "price_per_year": Decimal("3000000"),
                "bedrooms": 1,
                "bathrooms": 1,
                "sqft": 750,
                "age": "7 years",
                "description": "Well-maintained mini flat in Ikeja close to the airport. Good road access.",
                "image_url": "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800",
                "is_verified": True,
                "rating": Decimal("4.2"),
                "amenities": ["Air Conditioning", "Car Park"],
            },
            {
                "landlord": emeka,
                "title": "2 Bedroom Apartment, Wuse 2",
                "property_type": "2bed",
                "location": "Wuse 2, Abuja",
                "city": "Abuja",
                "state": "FCT",
                "price_per_year": Decimal("5400000"),
                "bedrooms": 2,
                "bathrooms": 2,
                "sqft": 1100,
                "age": "1 year",
                "description": "Brand new 2-bedroom apartment in Wuse 2. Modern kitchen and smart home features.",
                "image_url": "https://images.unsplash.com/photo-1560185127-6a9e5e38b6a8?w=800",
                "is_verified": True,
                "rating": Decimal("4.7"),
                "amenities": ["Fully Furnished", "Air Conditioning", "Generator", "CCTV"],
            },
            {
                "landlord": chinenye,
                "title": "Self-Con Studio, Surulere",
                "property_type": "self-con",
                "location": "Surulere, Lagos",
                "city": "Lagos",
                "state": "Lagos",
                "price_per_year": Decimal("1500000"),
                "bedrooms": 1,
                "bathrooms": 1,
                "sqft": 420,
                "age": "8 years",
                "description": "Compact self-con in Surulere. Great for budget renters.",
                "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
                "is_verified": False,
                "rating": Decimal("3.9"),
                "amenities": ["Water Supply"],
            },
            {
                "landlord": emeka,
                "title": "4 Bedroom Duplex, Asokoro",
                "property_type": "duplex",
                "location": "Asokoro, Abuja",
                "city": "Abuja",
                "state": "FCT",
                "price_per_year": Decimal("12000000"),
                "bedrooms": 4,
                "bathrooms": 5,
                "sqft": 4000,
                "age": "3 years",
                "description": "Premium duplex in Asokoro District. Diplomatic zone with top security.",
                "image_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800",
                "is_verified": True,
                "rating": Decimal("5.0"),
                "amenities": ["Swimming Pool", "Gym", "CCTV", "24/7 Security", "Generator", "Car Park"],
            },
        ]

        props = []
        for pd in prop_data:
            amenity_names = pd.pop("amenities")
            p = Property.objects.create(**pd)
            for name in amenity_names:
                if name in amenity_objs:
                    PropertyAmenity.objects.create(property=p, amenity=amenity_objs[name])
            props.append(p)

        mimi_property = props[0]

        # ── Mimi's Lease ─────────────────────────────────────────────
        lease = Lease.objects.create(
            tenant=mimi,
            rental_property=mimi_property,
            start_date=date(2025, 2, 15),
            end_date=date(2026, 2, 15),
            rent_amount=Decimal("4200000"),
            next_rent_due=date(2026, 2, 15),
            status="active",
        )

        # ── Mimi's Wallet ────────────────────────────────────────────
        wallet = Wallet.objects.create(tenant=mimi, balance=Decimal("950000"))
        SavingsGoal.objects.create(
            wallet=wallet,
            goal_name="December Rent - 2 Bedroom Flat (Lekki)",
            target_amount=Decimal("800000"),
            saved_amount=Decimal("455000"),
            due_date=date(2026, 12, 1),
            auto_save=True,
            is_active=True,
        )
        WalletTransaction.objects.create(
            wallet=wallet,
            description="Auto-save deposit",
            amount=Decimal("25000"),
            transaction_type="credit",
        )
        WalletTransaction.objects.create(
            wallet=wallet,
            description="Transfer to savings",
            amount=Decimal("5000"),
            transaction_type="debit",
        )
        WalletTransaction.objects.create(
            wallet=wallet,
            description="Refund from landlord",
            amount=Decimal("15000"),
            transaction_type="credit",
        )

        # ── Additional tenants for Chinenye's properties ─────────────
        tenant_names = [
            ("Chiamaka", "Obi", "chiamaka"),
            ("Suleiman", "Bello", "suleiman"),
            ("Amaka", "Eze", "amaka"),
            ("Tunde", "Adeyemi", "tunde"),
            ("Ngozi", "Ikenna", "ngozi"),
            ("Chidi", "Okafor", "chidi"),
            ("Fatima", "Hassan", "fatima"),
            ("Emeka", "Dibia", "emeka2"),
            ("Blessing", "Nwosu", "blessing"),
            ("Yemi", "Afolabi", "yemi"),
            ("Kemi", "Adebayo", "kemi"),
            ("Ade", "Fashola", "ade"),
        ]
        extra_tenants = []
        for fn, ln, uname in tenant_names:
            t = User.objects.create_user(
                username=uname,
                email=f"{uname}@example.com",
                password="demo1234",
                first_name=fn,
                last_name=ln,
                role="tenant",
            )
            extra_tenants.append(t)

        # Assign leases to chinenye's properties (use props 0-5)
        chinenye_props = [p for p in props if p.landlord == chinenye]
        for i, tenant in enumerate(extra_tenants[:len(chinenye_props)]):
            Lease.objects.create(
                tenant=tenant,
                rental_property=chinenye_props[i % len(chinenye_props)],
                start_date=date(2025, 1, 1),
                end_date=date(2026, 1, 1),
                rent_amount=chinenye_props[i % len(chinenye_props)].price_per_year,
                next_rent_due=date(2026, 5, 1),
                status="active",
            )

        # ── Applications (6 pending for Chinenye) ────────────────────
        for i, tenant in enumerate(extra_tenants[6:12]):
            Application.objects.create(
                tenant=tenant,
                rental_property=chinenye_props[i % len(chinenye_props)],
                status="pending",
                credit_score=700 + (i * 10),
                message="I am interested in renting this property.",
            )

        # ── Payments ─────────────────────────────────────────────────
        Payment.objects.create(
            tenant=extra_tenants[0],
            rental_property=chinenye_props[0],
            lease=Lease.objects.filter(tenant=extra_tenants[0]).first(),
            amount=Decimal("350000"),
            status="paid",
        )
        Payment.objects.create(
            tenant=extra_tenants[1],
            rental_property=chinenye_props[1],
            lease=Lease.objects.filter(tenant=extra_tenants[1]).first(),
            amount=Decimal("200000"),
            status="paid",
        )
        Payment.objects.create(
            tenant=extra_tenants[2],
            rental_property=chinenye_props[2 % len(chinenye_props)],
            lease=Lease.objects.filter(tenant=extra_tenants[2]).first(),
            amount=Decimal("600000"),
            status="pending",
        )

        # ── A sample conversation ─────────────────────────────────────
        conv = Conversation.objects.create(tenant=mimi, landlord=chinenye, rental_property=mimi_property)
        Message.objects.create(conversation=conv, sender=chinenye, content="Hello Mimi, your lease is due next month. Please confirm you'll be renewing.")
        Message.objects.create(conversation=conv, sender=mimi, content="Hi! Yes, I plan to renew. Can we discuss the new rate?")

        self.stdout.write(self.style.SUCCESS(
            "\n✅  Seed data created!\n"
            "   Tenant login:   mimi / demo1234\n"
            "   Landlord login: chinenye / demo1234\n"
            "   Landlord login: emeka / demo1234\n"
        ))
