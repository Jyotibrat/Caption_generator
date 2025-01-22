#creqd lib
import gradio as gr
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import random

# Load the pre-trained-model and processor
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")


def add_aesthetic_flair(description):
    # Keywords to identify specific styles for the caption
    nature_keywords = ["mountain", "sea", "sky", "ocean", "nature", "forest", "beach", "trees", "jungle", "wildlife", "wilderness", "river", "canyon", "hills", "valley", "waterfall", "lake"]
    city_keywords = ["city", "urban", "street", "lights", "buildings", "skyscrapers", "cityscape", "skyline","construction", "metropolis", "traffic", "subway", "metro","plaza","market","billboards","nightlife","tower"]
    people_keywords = ["person", "people", "portrait", "smiling", "group", "friends", "family","crowd","community","society","gathering","celebration","adults","children","elderly","men","women","employees","volunteer","friendship"]
    
    # Defining a list of possible emotional or aesthetic phrases
    aesthetic_tones = [
        "where time stands still", 
        "capturing the essence of life", 
        "a perfect moment frozen in time", 
        "an ode to beauty", 
        "an unforgettable experience", 
        "whispers of serenity", 
        "an adventure in every frame", 
        "a snapshot of pure bliss",
        "faded photo of a classic diner",
        "single plant in a white pot",
        "cozy living room with woven rugs",
        "neon lights outside an arcade",
        "black-and-white portrait in soft light",
        "couple walking through a flower-filled park",
        "dimly lit room with candlelight",
        "graffiti-covered walls in an abandoned warehouse",
        "sleek kitchen with exposed brick",
        "woman on a rooftop at sunset",
        "soft pink bedroom with mint green accents",
        "neon-lit city skyline at night",
        "mist rolling through a quiet forest",
        "wooden cabin with a roaring fireplace",
        "floating island with waterfalls",
        "busy street with neon signs and traffic",
        "dew-covered leaves in the forest",
        "swirl of colors and shapes in motion",
        "balloons flying in a sunny park",
        "marble foyer with crystal chandeliers"
    ]
    
    # Identify the tone based on image description
    tone = ""
    if any(keyword in description.lower() for keyword in nature_keywords):
        tone = "Nature’s beauty is timeless and serene."
    elif any(keyword in description.lower() for keyword in city_keywords):
        tone = "The hustle and bustle of city life, captured in a moment."
    elif any(keyword in description.lower() for keyword in people_keywords):
        tone = "A beautiful moment with loved ones, filled with joy and laughter."
    else:
        tone = random.choice(aesthetic_tones)
    
    # Combine the description with the aesthetic tone
    aesthetic_caption = f"{description} \n\n{tone}"
    
    # Split the caption into smaller lines, aiming for 2 to 5 lines
    lines = aesthetic_caption.split("\n")
    num_lines = random.randint(2, 5)  # Randomly choose how many lines to use (between 2 and 5)
    
    # Ensure that the number of lines does not exceed the available content
    final_caption = "\n".join(lines[:num_lines])
    
    # Optionally add hashtags at the end
    hashtags = "#photography #art #inspiration #nature #urban #portrait #adventure"
    
    # Combine the caption with hashtags
    final_caption_with_hashtags = f"{final_caption}\n\n{hashtags}"
    
    # Limit the caption to Instagram's maximum character length (2200 characters)
    if len(final_caption_with_hashtags) > 2200:
        final_caption_with_hashtags = final_caption_with_hashtags[:2200] + "..."
    
    return final_caption_with_hashtags

# Function to generate the base caption from the BLIP model
def generate_caption(image):
    inputs = processor(images=image, return_tensors="pt")
    outputs = model.generate(**inputs, num_beams=5, max_length=50)
    base_caption = processor.decode(outputs[0], skip_special_tokens=True)
    full_caption = add_aesthetic_flair(base_caption)
    return full_caption

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
    Handles the user's request for either captioning or question answering.
    """
    try:
        if question.strip():  
            answer = answer_question(image, question)
            return f"Question: {question}\nAnswer: {answer}"
        else: 
            caption = generate_caption(image)
            return caption
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Gradio interface setup
iface = gr.Interface(
    fn=handle_request,
    inputs=[
        gr.Image(type="pil", label="Upload an Image"), 
        gr.Textbox(lines=2, placeholder="Ask a question about the image (optional)", label="Question (Optional)"), 
    ],
    outputs="text",
    title="Aesthetic Image Captioning with Question Answering",
    description="Upload an image to generate an aesthetic caption or ask a question about the image."
)

iface.launch()
