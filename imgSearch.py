import requests
import json
import os
from dotenv import load_dotenv
import base64

load_dotenv()
API_KEY = os.getenv("searchKey", "")

# --- Replace with your actual credentials ---
CSE_ID = "c6fcff51d3b604e3b"                                                                                                                        
# ------------------------------------------

def download_image(image_url, save_path="media/"):
    response = requests.get(image_url, stream=True)
    response.raise_for_status() 

    content_type = response.headers.get('Content-Type', '').lower()
    
    image_data = BytesIO(response.content)
    
    try:
        img = Image.open(image_data)
    except Image.UnidentifiedImageError:
        print(f"Error: Cannot identify image file from {image_url}. Content-Type: {content_type}. Skipping conversion.")
        return None

    # Handle animated GIFs by taking the first frame
    if hasattr(img, 'is_animated') and img.is_animated:
        print(f"Warning: Animated GIF detected at {image_url}. Saving only the first frame as PNG.")
        try:
            img.seek(0) # Go to the first frame
        except EOFError:
            # Handle cases where the GIF might be corrupted or has no frames
            print(f"Warning: Could not seek to first frame of animated GIF at {image_url}.")
            pass # Proceed to save whatever frame is currently loaded

    # Remove query parameters from the URL basename for a cleaner filename
    name_without_ext = f"img-{num}"
    
    # Construct the new filename with .png extension
    file_name_png = os.path.join(save_path, f"{name_without_ext}.png")

    # Convert and save as PNG. Pillow automatically handles various input formats.
    # Ensure 'RGBA' mode for transparency if the original image has an alpha channel,
    # otherwise 'RGB' for opaque images.
    if img.mode == 'RGBA' or (img.mode == 'P' and 'transparency' in img.info):
        img = img.convert('RGBA')
    else:
        img = img.convert('RGB') # Convert to RGB for consistency if not transparent

    img.save(file_name_png, "PNG")
    
    print(f"Downloaded and converted to PNG: {file_name_png}")
    return file_name_png


def imgSearch(query,num, num_results=1, start_index=1):
    """
    Performs a Google image search using the Custom Search JSON API.

    Args:
        query (str): The search query (e.g., "cute puppies").
        num_results (int): Number of results to return (max 10 per request).
        start_index (int): The index of the first result to return (for pagination).

    Returns:
        list: A list of dictionaries, where each dictionary represents an image result.
              Returns an empty list if no images are found or an error occurs.
    """


    params = {
        'q': query,
        'cx': CSE_ID,
        'key': API_KEY,
        'searchType': 'image',
        'num': num_results,
        'start': start_index
    }

    try:
        response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        data = response.json()

        image_results = []
        if 'items' in data:
            for item in data['items']:
                # The 'pagemap' often contains more detailed image information
                # For images, 'cse_image' or 'imageobject' are common
                if 'pagemap' in item and 'cse_image' in item['pagemap']:
                    image_results.append({
                        'title': item.get('title'),
                        'link': item.get('link'),
                        'thumbnail_link': item['pagemap']['cse_image'][0].get('src'),
                        'image_width': item['pagemap']['cse_image'][0].get('width'),
                        'image_height': item['pagemap']['cse_image'][0].get('height'),
                        # You can explore more fields in 'item' or 'pagemap'
                    })
                else:
                    # Fallback if cse_image isn't directly available but link is an image
                    if item.get('fileFormat', '').startswith('image/') and item.get('link'):
                         image_results.append({
                            'title': item.get('title'),
                            'link': item.get('link'),
                            'thumbnail_link': item.get('image', {}).get('thumbnailLink') # May not always be present
                         })


        return image_results

    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return []
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

if __name__ == "__main__":
    search_query = "university of kyoto"
    images = google_image_search(search_query,-1, num_results=1)

    if images:
        for i, image in enumerate(images):

            print(f"\n--- Image {i+1} ---")
            #print(f"Title: {image.get('title', 'N/A')}")
            #print(f"Link: {image.get('link', 'N/A')}")
            downloaded_file = download_image(image.get('title', 'N/A'))
    else:
        print(f"No images found for '{search_query}'.")
