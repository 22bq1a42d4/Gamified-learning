import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from games.models import Game
from academics.models import Subject, AcademicClass
from institutes.models import Institute

def seed_master():
    print("🚀 Starting Master Seed Process...")

    # 1. Get or Create an Institute with a UNIQUE code
    # Using defaults ensures that if it doesn't exist, it creates it with a code.
    inst, created = Institute.objects.get_or_create(
        name="Rural Excellence Academy",
        defaults={'code': 'REA001'} 
    )
    if created:
        print(f"✅ Created new Institute: {inst.name}")
    else:
        print(f"ℹ️ Using existing Institute: {inst.name}")

    # 2. Master Data Mapping
    master_list = [
        # GRADES 6-10
        {"title": "Equation Archer", "sub": "Math", "type": "canvas", "grades": [6,7,8,9,10], "xp": 100},
        {"title": "Fraction Pizza", "sub": "Math", "type": "drag_drop", "grades": [6,7,8], "xp": 50},
        {"title": "Circuit Connector", "sub": "Science", "type": "drag_drop", "grades": [8,9,10], "xp": 80},
        {"title": "State Shifter", "sub": "Science", "type": "simulation", "grades": [7,8,9], "xp": 70},
        {"title": "Organelle Sort", "sub": "Biology", "type": "drag_drop", "grades": [9,10], "xp": 60},
        {"title": "Pattern Path", "sub": "Logical", "type": "canvas", "grades": [6,7,8,9,10], "xp": 50},

        # GRADES 11-12
        {"title": "Projectile Pilot", "sub": "Physics", "type": "simulation", "grades": [11,12], "xp": 150},
        {"title": "Ray Tracer", "sub": "Physics", "type": "simulation", "grades": [12], "xp": 150},
        {"title": "Bond Builder", "sub": "Chemistry", "type": "drag_drop", "grades": [11,12], "xp": 120},
        {"title": "Titration Pro", "sub": "Chemistry", "type": "simulation", "grades": [12], "xp": 140},
        {"title": "DNA Splicer", "sub": "Biology", "type": "canvas", "grades": [11,12], "xp": 130},
        {"title": "Heart Pump", "sub": "Biology", "type": "canvas", "grades": [11,12], "xp": 110},
    ]

    for item in master_list:
        for grade_num in item['grades']:
            # A. Get or Create the Academic Class
            ac_class, _ = AcademicClass.objects.get_or_create(grade=grade_num)
            
            # B. Get or Create the Subject (linked to class and institute)
            subject, _ = Subject.objects.get_or_create(
                name=item['sub'],
                academic_class=ac_class,
                institute=inst
            )

            # C. Create the Game (Using unique slug per grade)
            game_slug = f"{item['title'].lower().replace(' ', '-')}-class-{grade_num}"
            
            game, g_created = Game.objects.get_or_create(
                slug=game_slug,
                defaults={
                    'title': item['title'],
                    'subject': subject,
                    'game_type': item['type'],
                    'min_grade': grade_num,
                    'max_grade': grade_num,
                    'difficulty': "medium",
                    'xp_reward': item['xp'],
                    'is_active': True
                }
            )
            
            if g_created:
                print(f"🎮 Created: {item['title']} (Class {grade_num})")

    print("\n✅ Successfully seeded 12 Master Games across all grade levels.")

if __name__ == "__main__":
    seed_master()