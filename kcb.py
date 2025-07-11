import pygame

# Inisialisasi Pygame
pygame.init()
screen = pygame.display.set_mode((1000, 800))
pygame.display.set_caption("Game Memasak AI - NPC Memilih Resep")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
big_font = pygame.font.SysFont(None, 48)

# Fungsi untuk load dan scale gambar bahan
def load_scaled_image(path, size=(80, 80)):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, size)

# Data resep utama
recipes = {
    "Nasi Ayam": {
        "ingredients": ["rice", "chicken"],
        "score": 9,
        "reason": "the combination of chicken + rice has an efficiency score of 9/10"
    },
    "Sup Sayur": {
        "ingredients": ["egg", "vegetable", "water"],
        "score": 8,
        "reason": "the combination of vegetable + water has an efficiency score of 8/10"
    },
    "Tumis Jamur": {
        "ingredients": ["tomato", "mushroom"],
        "score": 6,
        "reason": "simple recipe using tomato + mushroom"
    }
}

# Resep rahasia
secret_recipes = {
    "Nasi Ayam Pedas": {
        "ingredients": ["rice", "chicken", "chili"],
        "score": 12,
        "reason": "Secret combo: spicy version of Nasi Ayam"
    },
    "Omelet Jamur": {
        "ingredients": ["egg", "mushroom"],
        "score": 10,
        "reason": "Secret combo: light mushroom omelet"
    }
}

# Gabungkan semua resep
all_recipes = recipes.copy()
all_recipes.update(secret_recipes)

# Nilai kualitas bahan
ingredient_quality = {
    "rice": 3,
    "chicken": 5,
    "egg": 2,
    "vegetable": 2,
    "tomato": 2,
    "mushroom": 2,
    "water": 1,
    "chili": 4
}

# Load gambar bahan
ingredient_images = {
    "rice": load_scaled_image("assets/rice.png"),
    "chicken": load_scaled_image("assets/chicken.png"),
    "egg": load_scaled_image("assets/egg.png"),
    "vegetable": load_scaled_image("assets/vegetable.png"),
    "tomato": load_scaled_image("assets/tomato.png"),
    "mushroom": load_scaled_image("assets/mushroom.png"),
    "water": load_scaled_image("assets/water.png"),
    "chili": load_scaled_image("assets/chili.png")
}

available_ingredients = list(ingredient_images.keys())
selected_ingredients = []
cook_button_rect = pygame.Rect(440, 400, 120, 50)

player_score = 0
npc_score = 0
last_player_recipe = ""
npc_selected_ingredients = []
player_details = {}
game_over = False

start_ticks = pygame.time.get_ticks()
npc_difficulty = "medium"  # level bisa: easy, medium, hard

def draw_text(text, x, y, color=(0, 0, 0), size=font):
    screen.blit(size.render(text, True, color), (x, y))

def rule_based_decision(available, recipes):
    best_recipe = None
    best_total_score = -1
    reason = ""
    for name, info in recipes.items():
        if all(item in available for item in info["ingredients"]):
            base_score = info["score"]
            quality_score = sum(ingredient_quality.get(i, 1) for i in info["ingredients"])
            length_bonus = len(info["ingredients"])
            total_score = base_score + quality_score + length_bonus

            if total_score > best_total_score:
                best_total_score = total_score
                best_recipe = (name, info)
                reason = info.get("reason", "") + f" | Total score: {total_score}"

    return best_recipe if best_recipe else ("Tidak ada resep", {"score": 0, "ingredients": []}), reason

def evaluate_player_choice(selected, recipes):
    (recipe_name, info), _ = rule_based_decision(selected, recipes)

    correct_match = all(i in selected for i in info["ingredients"]) and len(selected) == len(info["ingredients"])
    extra_ingredients = [i for i in selected if i not in info["ingredients"]]
    missed_ingredients = [i for i in info["ingredients"] if i not in selected]

    base_score = info["score"] if correct_match else 0
    penalty = len(extra_ingredients) * 2 + len(missed_ingredients) * 3
    quality_score = sum(ingredient_quality.get(i, 1) for i in selected)

    final_score = max(0, base_score + quality_score - penalty)

    details = {
        "correct": correct_match,
        "extras": extra_ingredients,
        "missed": missed_ingredients,
        "quality": quality_score,
        "penalty": penalty
    }

    return recipe_name, final_score, details

def npc_choose_recipe(player_ingredients, all_ingredients, level="hard"):
    if level == "medium":
        remaining = [i for i in all_ingredients if i not in player_ingredients]
        (recipe, info), reason = rule_based_decision(remaining, all_recipes)
        return info["ingredients"], info["score"]
    else:
        return [], 0  

def draw_ingredient_grid():
    for idx, ing in enumerate(available_ingredients):
        x = 80 + (idx % 3) * 100
        y = 100 + (idx // 3) * 100
        pygame.draw.rect(screen, (200, 200, 200), (x, y, 80, 80), 2)
        img = ingredient_images[ing]
        img_rect = img.get_rect(center=(x + 40, y + 40))
        screen.blit(img, img_rect)

def draw_selected_slots():
    for i in range(3):
        x = 80 + i * 100
        y = 400
        pygame.draw.rect(screen, (100, 100, 100), (x, y, 80, 80), 2)
        if i < len(selected_ingredients):
            img = ingredient_images[selected_ingredients[i]]
            img_rect = img.get_rect(center=(x + 40, y + 40))
            screen.blit(img, img_rect)

def draw_npc_slots(ingredients):
    for i in range(3):
        x = 700 + i * 90
        y = 400
        pygame.draw.rect(screen, (120, 120, 120), (x, y, 80, 80), 2)
        if i < len(ingredients):
            img = ingredient_images[ingredients[i]]
            img_rect = img.get_rect(center=(x + 40, y + 40))
            screen.blit(img, img_rect)

def draw_decision_tree():
    draw_text("IF chicken AND rice", 80, 600)
    draw_text("-> Nasi Ayam", 80, 630)
    draw_text("IF egg AND vegetable AND water", 80, 660)
    draw_text("-> Sup Sayur", 80, 690)
    draw_text("IF tomato AND mushroom", 80, 720)
    draw_text("-> Tumis Jamur", 80, 750)
    draw_text("SECRET: rice, chicken, chili", 580, 600)
    draw_text("-> Nasi Ayam Pedas", 580, 630)
    draw_text("SECRET: egg, mushroom", 580, 660)
    draw_text("-> Omelet Jamur", 580, 690)

running = True
while running:
    screen.fill((245, 235, 215))
    seconds = max(0, 60 - (pygame.time.get_ticks() - start_ticks) // 1000)

    if seconds == 0:
        game_over = True

    draw_text("PLAYER", 120, 20, (0, 0, 0), big_font)
    draw_text("NPC", 720, 20, (0, 0, 0), big_font)
    draw_text(f"0:{seconds:02}", 470, 20, (0, 0, 0), big_font)

    draw_text("Available Ingredients", 80, 60)
    draw_ingredient_grid()
    draw_selected_slots()

    pygame.draw.rect(screen, (0, 120, 255), cook_button_rect)
    draw_text("COOK", cook_button_rect.x + 25, cook_button_rect.y + 15, (255, 255, 255))
    draw_text(f"{player_score}", 500, 480, (0, 0, 0), big_font) # bagian score NPC disembunyikan

    if npc_selected_ingredients:
        draw_text("NPC Dish:", 700, 140, (0, 0, 0), big_font)
        draw_npc_slots(npc_selected_ingredients)

    draw_decision_tree()

    if last_player_recipe:
        draw_text(f"Your Dish: {last_player_recipe}", 80, 520, (0, 0, 0))
        if player_details:
            draw_text(f"Correct: {player_details.get('correct')}", 80, 550, (0, 0, 0))
            draw_text(f"Penalty: {player_details.get('penalty')}", 250, 550, (0, 0, 0))
            draw_text(f"Quality: {player_details.get('quality')}", 400, 550, (0, 0, 0))

    if game_over:
        winner = "Player" if player_score > npc_score else "NPC" if npc_score > player_score else "Draw"
        pygame.draw.rect(screen, (0, 0, 0), (300, 200, 400, 150))
        draw_text("Game Over!", 400, 220, (255, 255, 255), big_font)
        draw_text(f"Winner: {winner}", 410, 270, (255, 255, 0), big_font)
        draw_text("Press ESC to quit", 370, 320, (200, 200, 200))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        if not game_over and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for idx, ing in enumerate(available_ingredients):
                x = 80 + (idx % 3) * 100
                y = 100 + (idx // 3) * 100
                if pygame.Rect(x, y, 80, 80).collidepoint(mx, my):
                    if ing not in selected_ingredients and len(selected_ingredients) < 3:
                        selected_ingredients.append(ing)

            if cook_button_rect.collidepoint(mx, my):
                player_recipe, score_gain, details = evaluate_player_choice(selected_ingredients, all_recipes)
                player_score += score_gain
                last_player_recipe = player_recipe
                player_details = details

                npc_selected_ingredients, npc_points = npc_choose_recipe(selected_ingredients, available_ingredients, npc_difficulty)
                npc_score += npc_points
                selected_ingredients = []

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
