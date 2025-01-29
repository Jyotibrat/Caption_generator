import gradio as gr
from transformers import BlipProcessor, BlipForConditionalGeneration, DetrImageProcessor, DetrForObjectDetection
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
import torch
from PIL import ImageDraw

# Load environment variables
load_dotenv()

# Try to load the pre-trained model and processor with error handling
try:
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
    od_processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
    od_model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")
except Exception as e:
    print(f"Error loading models: {str(e)}")
    raise SystemExit("Required models could not be loaded")

def detect_objects(image):
    inputs = od_processor(images=image, return_tensors="pt")
    outputs = od_model(**inputs)
    target_sizes = torch.tensor([image.size[::-1]])  
    results = od_processor.post_process_object_detection(outputs, target_sizes=target_sizes)[0]

    # Apply threshold manually
    valid_indices = results["scores"] > 0.7
    results = {k: v[valid_indices] for k, v in results.items()}

    draw = ImageDraw.Draw(image)
    detected_objects = []
    
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        box = [round(i, 2) for i in box.tolist()]
        label_name = od_model.config.id2label[label.item()]
        detected_objects.append(label_name)
        draw.rectangle(box, outline="red", width=3)
        draw.text((box[0], box[1]), f"{label_name} ({score:.2f})", fill="red")
    
    return  detected_objects


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
        "a canvas of emotions"
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


def handle_request(image, question, mode):
    """


    Enhanced image captioning with robust error handling

    """
    if image is None:
        return "Please provide a valid image"
        
    try:
        if mode == "Object Detection":
            detected_objects = detect_objects(image.copy())  # Work on a copy to avoid modifying original
            return  f"Detected Objects: {', '.join(detected_objects)}"
        if question:
            question=question.strip()  
            answer = answer_question(image, question)
            return f"Question: {question}\nAnswer: {answer}"
        else: 
            caption = generate_caption(image)
            return caption
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Gradio interface with an option for Object Detection
iface = gr.Interface(
    fn=handle_request,
    inputs=[
        gr.Image(type="pil", label="📸 Upload your image"),
        gr.Textbox(label="❓ Ask a question (Optional)"),
        gr.Radio(["Caption Generation", "Object Detection"], label="Select Mode", value="Caption Generation"),
    ],
    outputs=[
        gr.Textbox(label="✨ Output"),
    ],
    title="🎨 AI-Powered Creative Caption & Object Detection",
    description="Upload an image to generate captions, answer questions, or detect objects.",

)

# Launch the interface and open in browser
server_port = 7860  # Default Gradio port
webbrowser.open(f'http://localhost:{server_port}')
iface.launch(server_name="0.0.0.0", server_port=server_port, share=False)