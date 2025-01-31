#creqd lib
import gradio as gr
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import random
import emoji
from textblob import TextBlob
from deep_translator import GoogleTranslator
import datetime
import requests
from geopy.geocoders import Nominatim
import socket
import os
from dotenv import load_dotenv
import webbrowser

# Load environment variables
load_dotenv()

# Try to load the pre-trained model and processor with error handling
try:
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
except Exception as e:
    print(f"Error loading models: {str(e)}")
    raise SystemExit("Required models could not be loaded")

def get_location_weather():
    """Get current location and weather with enhanced error handling"""
    try:
        # Get IP-based location instead of "me"
        ip_request = requests.get('https://api.ipify.org?format=json', timeout=5)
        ip_address = ip_request.json()['ip']
        
        geolocator = Nominatim(user_agent=f"image_caption_{socket.gethostname()}")
        location = geolocator.geocode(ip_address)
        
        if not location:
            return "Unknown Location", "Weather data unavailable"
        
        # Use environment variable for API key
        weather_api_key = os.getenv('WEATHER_API_KEY')
        if not weather_api_key:
            return location.address, "Weather data unavailable (No API key)"
            
        # OpenWeatherMap API instead of Google Maps
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={location.latitude}&lon={location.longitude}&appid={weather_api_key}"
        
        try:
            weather_response = requests.get(weather_url, timeout=5)
            weather_response.raise_for_status()
            weather_data = weather_response.json()
            weather_description = weather_data.get('weather', [{}])[0].get('description', 'unknown weather')
            return location.address, weather_description
        except requests.exceptions.RequestException:
            return location.address, "Weather data unavailable"
            
    except Exception as e:
        print(f"Location/Weather Error: {str(e)}")
        return "Unknown Location", "Weather data unavailable"

def add_aesthetic_flair(description):
    # Enhanced keywords for better categorization
    nature_keywords = ["mountain", "sea", "sky", "ocean", "nature", "forest", "beach", "sunset", "sunrise", "flowers"]
    city_keywords = ["city", "urban", "street", "lights", "buildings", "skyscrapers", "architecture", "downtown"]
    people_keywords = ["person", "people", "portrait", "smiling", "group", "friends", "family", "crowd"]
    
    # More diverse aesthetic phrases
    aesthetic_tones = [
        "where dreams take flight",
        "capturing the poetry of life",
        "a moment of pure magic",
        "where beauty meets reality",
        "stories written in light",
        "memories carved in time",
        "where imagination roams free",
        "a canvas of emotions",
        "a little sunshine goes a long way",
        "breathe in the positivity, exhale the doubt",
        "a grateful heart makes every morning brighter",
        "let the morning set the tone for you",
        "be a voice, not an echo",
        "progress, not prefection",
        "trust the process",
        "dream big, hustle harder",
        "hard work beats talent when talent doesn't work hard",
        "move forward even if in small steps",
        "focus on the good, and the good gets better",
        "stay close to people who feel like sunshine",
        "collect memories, not things.",
        "not all who wander are lost",
        "take only memories, leave only footprints",
        "life begins at the end of your comfort zone",
        "the world is too big to stay in one place",
        "not all who wander are lost",
        "We are blessed and cursed, same things makes us laugh, make us cry.",
        "discipline beats motivation everytime",
        "sunlight spills like golden ink, writing dreams upon the day",
        "morning whispers secrets only the early birds hear",
        "the sky blushes at dawnn, kissed by the rising sun",
        "raindrops are the earth's way to sing a lullaby",
        "ki kori aso kela, uth baal! success kori bo ase",
        "the horizon holds hands with the sea, where dreams and reality meet",
        "clouds drift like unspoken thoughts acroos an endless sky",
        "leaves dance in the wind, whispering stories of old",
        "a single moment of wonder can rewrite a lifetime of doubt",
        "the ocean hums lullabies only the heart can understand",
        "time tiptoes through the day, leaving memories in its wake",
        "shadows stretch like silent echoes of the past",
        "steel bends, kingdoms fall, but a true heart never bows",
        "courage is a whisper that grows into a roar",
        "today is your day, kela own it like its yours",
        "not all who wander are lost, some are simply dancing",
        "tomorrow is a promise wrapped in the golden light of dawn",
        "life is a melody, best sung with an open heart",
        "even stars are born form the darkness",
        "the softest words can leave the deepest echoes",
        "hope is the feather that carries the soul through stroms",
        "the road less traveled hums with untold stories",
        "the past is a shadow that only light can outgrow",
        "even the smallest flame can dance against the dark",
        "a warrior’s scars are but ink on the pages of legend",
        "the storm bows before those who dare to dance in its fury",
        "blades may shatter, shields may break, but courage remains unswayed",
        "glory is not given, it is seized in the heart of battle",
        "legends are not written in ink, but in the echoes of deeds remembered",
        "stand tall, for the shadows of doubt dare not linger where courage stands strong",
        "a promise lost in time still lingers in the wind, waiting to be found",
        "a single wish upon a falling star can rewrite the fate of a thousand lifetimes",
        "stars are just echoes of wishes too bold to be forgotten",
        "the night holds secrets only the enchanted dare to hear",
        "in the hands of a dreamer, even the ordinary becomes enchanted",
        "yesterday’s whispers fade, but the dawn sings of second chances",
        "some roads lead back to where we left our dreams behind",
        "every sunrise is proof that endings are just beginnings in disguise",
        "not all forgotten words are lost; some bloom again in time’s embrace",
        "the ashes of my past pave the path to my rebirth",
        "even the most shattered soul can rise with the dawn",
        "a journey does not end where the road breaks, it begins anew",
        "shadows of loss cannot hold back a soul destined to rise",
        "even the stars envy a soul that knows its worth",
        "the only limit is the one not yet shattered",
        "a mind unchained can conquer any destiny",
        "there is no rival greater than the fear of one's own greatness",
        "the echoes of sorrow are drowned in the laughter of new beginnings",
        "no shadow lingers forever where hope dares to shine",
        "let your growth be the gift that nourishes those who stand by you",
        "grow not just for yourself, but for those who bloom beside you",
        "rise, so that those who love you never have to watch you fall",
        "become the person your loved ones already believe you to be",
        "the strongest souls are shaped by love, not just ambition",
        "even the darkest forest glows where fairy dust lingers",
        "when friends gather, every hour is golden",
        "let the music play and joy overflow",
        "good vibes, great company, and memories that last forever",
        "a toast to friendship, laughter, and the magic of tonight",
        "laughter spills like golden confetti, dancing in the air of joy",
        "a night of laughter, a dance of souls, a memory forever to behold",
        "let the music play, let worries fade",
        "good vibes, great friends, and a night that never ends",
        "Making memories, one song at a time.",
        "the map is just the beginning, the journey writes the story",
        "the road whispers, the wind calls",
        "every sunset is a promise of a new adventure",

    ]
    
    # Get current time and location context
    current_time = datetime.datetime.now()
    location, weather = get_location_weather()
    
    # Enhanced sentiment analysis with error handling
    try:
        blob = TextBlob(description)
        if len(description.split()) < 3:
            sentiment = 0  # Neutral for very short texts
        else:
            sentiment = blob.sentiment.polarity
        mood_emoji = "✨" if sentiment > 0 else "🌙" if sentiment < 0 else "🌟"
    except Exception as e:
        print(f"Sentiment Analysis Error: {str(e)}")
        mood_emoji = "🌟"  # Default emoji
    
    # Multi-language support with error handling
    translations = {}
    for lang, code in {'es': 'Spanish', 'fr': 'French', 'hi': 'Hindi'}.items():
        try:
            translated = GoogleTranslator(source='en', target=lang).translate(description)
            translations[lang] = translated if translated else description
        except Exception as e:
            print(f"Translation Error ({code}): {str(e)}")
            translations[lang] = f"Translation unavailable"
    
    # Identify tone based on image description
    if any(keyword in description.lower() for keyword in nature_keywords):
        tone = f"Nature's canvas unfolds at {location} under {weather} skies."
    elif any(keyword in description.lower() for keyword in city_keywords):
        tone = f"Urban poetry from {location}, where every street tells a story."
    elif any(keyword in description.lower() for keyword in people_keywords):
        tone = "Human connections that transcend time and space."
    else:
        tone = random.choice(aesthetic_tones)
    
    # Create enhanced caption with character limit management
    MAX_CAPTION_LENGTH = 2200
    aesthetic_caption = f"{mood_emoji} {description} {mood_emoji}\n\n"
    location_weather = f"📍 {location}\n🌤️ {weather}\n⏰ {current_time.strftime('%B %d, %Y %H:%M')}\n\n"
    tone_section = f"{tone}\n\n"
    translations_section = "🌍 Global Captions:\n" + \
                         f"🇪🇸 {translations['es']}\n" + \
                         f"🇫🇷 {translations['fr']}\n" + \
                         f"🇮🇳 {translations['hi']}\n\n"
    
    # Smart hashtag generation
    hashtags = set(["#photography", "#art", "#inspiration"])
    if any(keyword in description.lower() for keyword in nature_keywords):
        hashtags.update(["#naturelovers", "#earthcaptures", "#naturephotography"])
    if any(keyword in description.lower() for keyword in city_keywords):
        hashtags.update(["#cityscape", "#urbanphotography", "#citylights"])
    if any(keyword in description.lower() for keyword in people_keywords):
        hashtags.update(["#portraitphotography", "#peopleoftheworld", "#humanconnection"])
    
    hashtag_section = ' '.join(hashtags)
    
    # Combine sections with length checking
    final_caption = aesthetic_caption + location_weather + tone_section + translations_section + hashtag_section
    
    if len(final_caption) > MAX_CAPTION_LENGTH:
        # Truncate while preserving emoji and formatting
        return final_caption[:MAX_CAPTION_LENGTH-3] + "..."
    
    return final_caption

def generate_caption(image):

    try:
        # Enhanced caption generation with multiple attempts
        inputs = processor(images=image, return_tensors="pt")
        captions = []
        
        for _ in range(3):
            outputs = model.generate(
                **inputs,
                max_length=50,
                num_beams=5,
                do_sample=True,  # Enable sampling
                temperature=random.uniform(0.6, 0.8),
                top_p=0.9
            )
            caption = processor.decode(outputs[0], skip_special_tokens=True)
            captions.append(caption)
        
        # Select the most detailed caption
        base_caption = max(captions, key=len)
        full_caption = add_aesthetic_flair(base_caption)
        
        return full_caption
    except Exception as e:
        return f"Caption generation failed: {str(e)}"

def answer_question(image, question):
    """
    Answers a question based on the given image.
    """
    inputs = processor(images=image, text=question, return_tensors="pt")
    outputs = model.generate(**inputs, num_beams=5, max_length=50)
    answer = processor.decode(outputs[0], skip_special_tokens=True)
    return answer[len(question):]


def handle_request(image, question):
    """


    Enhanced image captioning with robust error handling

    """
    if image is None:
        return "Please provide a valid image"
        
    try:
        if question.strip():  
            answer = answer_question(image, question)
            return f"Question: {question}\nAnswer: {answer}"
        else: 
            caption = generate_caption(image)
            return caption
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Enhanced Gradio interface with error handling
iface = gr.Interface(


    fn=caption_image,
    inputs=gr.Image(type="pil", label="📸 Upload your image"),
    outputs=gr.Textbox(label="✨ Generated Caption"),
    title="🎨 AI-Powered Creative Caption Generator",
    description="Transform your images into engaging stories with location, weather, and multi-language support.",
    theme="default"

)

# Launch the interface and open in browser
server_port = 7860  # Default Gradio port
webbrowser.open(f'http://localhost:{server_port}')
iface.launch(server_name="0.0.0.0", server_port=server_port, share=False)
