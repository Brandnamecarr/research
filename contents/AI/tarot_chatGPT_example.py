import random
import pandas as pd
import openai

# key for APIs in OpenAI
OPENAI_API_KEY = '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'

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Define a tarot deck with basic interpretations for each card
tarot_deck = pd.DataFrame({
    'Card': [
        'The Fool', 'The Magician', 'The High Priestess', 'The Empress', 'The Emperor',
        'The Hierophant', 'The Lovers', 'The Chariot', 'Strength', 'The Hermit',
        'Wheel of Fortune', 'Justice', 'The Hanged Man', 'Death', 'Temperance',
        'The Devil', 'The Tower', 'The Star', 'The Moon', 'The Sun', 'Judgement', 'The World'
    ],
    'Meaning': [
        'New beginnings, innocence, spontaneity',
        'Skill, manifestation, resourcefulness',
        'Intuition, mystery, inner knowledge',
        'Nurturing, abundance, fertility',
        'Authority, structure, control',
        'Tradition, spiritual guidance, conformity',
        'Love, partnership, union',
        'Willpower, determination, control',
        'Courage, compassion, inner strength',
        'Introspection, solitude, inner guidance',
        'Change, cycles, inevitable fate',
        'Fairness, truth, law',
        'Sacrifice, letting go, new perspectives',
        'Transformation, endings, new beginnings',
        'Balance, moderation, patience',
        'Addiction, materialism, bondage',
        'Sudden change, upheaval, revelation',
        'Hope, inspiration, serenity',
        'Illusion, fear, anxiety',
        'Success, positivity, vitality',
        'Judgment, rebirth, inner calling',
        'Completion, harmony, fulfillment'
    ]
})

# Draw 3 random cards
def draw_cards(deck, num=3):
    return deck.sample(n=num)

# Interpret the cards drawn
def interpret_cards(cards):    
    # Generate interpretations based on the drawn cards
    card_descriptions = ". ".join(f"{row['Card']}: {row['Meaning']}" for _, row in cards.iterrows())
    prompt = f"The following tarot cards were drawn: {card_descriptions}. Based on these, the interpretation is:"
    
    # Call the ChatGPT API with the prompt
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract the interpretation from the response
    print(interpretation)
    interpretation = response['choices'][0]['message']['content']
    return interpretation

# Draw and interpret the cards
drawn_cards = draw_cards(tarot_deck)
print("Cards Drawn:")
print(drawn_cards[['Card', 'Meaning']])

interpretation = interpret_cards(drawn_cards)
print("\nInterpretation:")
print(interpretation)
