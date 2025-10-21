#!/usr/bin/env python3
import requests
import base64
import json
import argparse
import io
import os
import sys
import rendertext


def image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def pil_image_to_base64(pil_image):
    """Convert PIL Image to base64 string"""
    buffer = io.BytesIO()
    pil_image.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode('utf-8')


def main():
    # Check for API key in environment
    REVE_API_KEY = os.environ.get('REVE_API_KEY')
    if not REVE_API_KEY:
        print("Error: REVE_API_KEY environment variable is not set.", file=sys.stderr)
        print("Please set it with: export REVE_API_KEY='your-api-key-here'", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Create a movie poster by adding title text to an image')
    parser.add_argument('--title', required=True, help='Title text to add to the cover')
    parser.add_argument('--image', required=True, help='Path to the input image (e.g., image.png)')
    parser.add_argument('--output', required=True, help='Output filename for the generated poster (e.g., poster.png)')
    parser.add_argument('--text-output', help='Optional: Save the intermediate text image to this filename (e.g., text.png)')

    args = parser.parse_args()

    # Generate text image using rendertext.make_text_image()
    print(f"Generating text image for title: {args.title}")
    text_image = rendertext.make_text_image(args.title)

    # Save text image if --text-output is specified
    if args.text_output:
        text_image.save(args.text_output)
        print(f"Text image saved to: {args.text_output}")

    # Convert images to base64
    print(f"Loading input image: {args.image}")
    image1_base64 = image_to_base64(args.image)
    image2_base64 = pil_image_to_base64(text_image)

    reference_images = [
        image1_base64,
        image2_base64
    ]

    # Set up headers
    headers = {
        "Authorization": f"Bearer {REVE_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Set up request payload with the specified prompt
    prompt = f'Create a movie poster by preserving the subject, scenery, style, and subject of <img>1</img> but add the title "{args.title}" as illustrated in <img>2</img>, changed to an appropriate font.'

    payload = {
        "prompt": prompt,
        "reference_images": reference_images,
        "aspect_ratio": "2:3",
        "version": "latest"
    }

    # Make the API request
    print("Sending request to REVE API...")
    try:
        response = requests.post("https://api.reve.com/v1/image/remix", headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        # Parse the response
        result = response.json()
        print(f"Request ID: {result['request_id']}")
        print(f"Credits used: {result['credits_used']}")
        print(f"Credits remaining: {result['credits_remaining']}")

        if result.get('content_violation'):
            print("Warning: Content policy violation detected")
        else:
            print("Image remixed successfully!")
            # The base64 image data is in result['image']
            if 'image' in result:
                # Decode base64 and save to file
                image_data = base64.b64decode(result['image'])
                with open(args.output, 'wb') as f:
                    f.write(image_data)
                print(f"Poster saved to: {args.output}")
            else:
                print("Warning: No image data in response")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Failed to parse response: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error saving image: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
