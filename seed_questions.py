import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from games.models import Game, Question

def seed_questions():
    print("🚀 Starting Question Seed Process...")

    # Data Dictionary for Questions
    game_content = {
        "Equation Archer": [
            {"q": "Solve for x: 2x + 5 = 15", "a": "4", "b": "5", "c": "10", "d": "7", "cor": "B"},
            {"q": "If 3x - 4 = 11, what is x?", "a": "3", "b": "5", "c": "4", "d": "6", "cor": "B"},
            {"q": "Solve: x/2 = 10", "a": "5", "b": "20", "c": "10", "d": "15", "cor": "B"},
            {"q": "What is x in 5x = 25?", "a": "5", "b": "4", "c": "6", "d": "1", "cor": "A"},
            {"q": "Solve for y: y + 12 = 20", "a": "6", "b": "8", "c": "10", "d": "12", "cor": "B"},
        ],
        "Organelle Sort": [
            {"q": "Which organelle is the 'Powerhouse' of the cell?", "a": "Nucleus", "b": "Ribosome", "c": "Mitochondria", "d": "Vacuole", "cor": "C"},
            {"q": "Where is DNA stored in a eukaryotic cell?", "a": "Cytoplasm", "b": "Nucleus", "c": "Cell Wall", "d": "Golgi Body", "cor": "B"},
            {"q": "Which part is found only in plant cells?", "a": "Cell Membrane", "b": "Chloroplast", "c": "Mitochondria", "d": "Nucleus", "cor": "B"},
            {"q": "What organelle is responsible for protein synthesis?", "a": "Ribosome", "b": "Lysosome", "c": "Vacuole", "d": "Nucleus", "cor": "A"},
            {"q": "What is the jelly-like substance inside the cell?", "a": "Nucleus", "b": "Cytoplasm", "c": "Cell Wall", "d": "Chloroplast", "cor": "B"},
        ],
        "Bond Builder": [
            {"q": "What type of bond involves sharing electrons?", "a": "Ionic", "b": "Covalent", "c": "Metallic", "d": "Hydrogen", "cor": "B"},
            {"q": "What is the valency of Carbon?", "a": "2", "b": "3", "c": "4", "d": "1", "cor": "C"},
            {"q": "Which gas is formed by a double covalent bond?", "a": "H2", "b": "O2", "c": "Cl2", "d": "CH4", "cor": "B"},
            {"q": "An ionic bond usually forms between a metal and a ___?", "a": "Metal", "b": "Non-metal", "c": "Noble Gas", "d": "Liquid", "cor": "B"},
            {"q": "What is the chemical formula for Methane?", "a": "CO2", "b": "H2O", "c": "CH4", "d": "NH3", "cor": "C"},
        ],
        "Projectile Pilot": [
            {"q": "At what angle is the range of a projectile maximum?", "a": "30°", "b": "45°", "c": "60°", "d": "90°", "cor": "B"},
            {"q": "Which component of velocity remains constant in a vacuum?", "a": "Vertical", "b": "Horizontal", "c": "Both", "d": "Neither", "cor": "B"},
            {"q": "What force acts on a projectile in flight (ignoring air)?", "a": "Friction", "b": "Magnetic", "c": "Gravity", "d": "Nuclear", "cor": "C"},
            {"q": "The path of a projectile is called a ___?", "a": "Circle", "b": "Straight Line", "c": "Parabola", "d": "Hyperbola", "cor": "C"},
            {"q": "What is the acceleration of a projectile at its peak?", "a": "0 m/s²", "b": "9.8 m/s² down", "c": "9.8 m/s² up", "d": "5 m/s²", "cor": "B"},
        ],
        "Circuit Connector": [
            {"q": "What is the unit of Electric Current?", "a": "Volt", "b": "Ohm", "c": "Ampere", "d": "Watt", "cor": "C"},
            {"q": "A device that opens or closes a circuit is a ___?", "a": "Battery", "b": "Switch", "c": "Resistor", "d": "Wire", "cor": "B"},
            {"q": "Which material is a good conductor?", "a": "Plastic", "b": "Wood", "c": "Copper", "d": "Rubber", "cor": "C"},
            {"q": "In a series circuit, if one bulb breaks, the others ___?", "a": "Stay on", "b": "Get brighter", "c": "Go out", "d": "Flicker", "cor": "C"},
            {"q": "Ohm's Law states V = ___?", "a": "I + R", "b": "I / R", "c": "I * R", "d": "R / I", "cor": "C"},
        ]
    }

    for game_name, questions in game_content.items():
        # Find all instances of this game (across different grades)
        target_games = Game.objects.filter(title__icontains=game_name)
        
        if not target_games.exists():
            print(f"⚠️ Game not found: {game_name}")
            continue

        for game in target_games:
            for q_data in questions:
                Question.objects.get_or_create(
                    game=game,
                    question_text=q_data["q"],
                    defaults={
                        "option_a": q_data["a"],
                        "option_b": q_data["b"],
                        "option_c": q_data["c"],
                        "option_d": q_data["d"],
                        "correct_option": q_data["cor"]
                    }
                )
            print(f"✅ Added 5 questions to: {game.title} (Class {game.min_grade})")

    print("\n🏁 Question seeding complete!")

if __name__ == "__main__":
    seed_questions()