#!/usr/bin/env python3
import requests
import json
import argparse
import os
import sys
import base64


def main():
    # Check for API key in environment
    REVE_API_KEY = os.environ.get('REVE_API_KEY')
    if not REVE_API_KEY:
        print("Error: REVE_API_KEY environment variable is not set.", file=sys.stderr)
        print("Please set it with: export REVE_API_KEY='your-api-key-here'", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Generate an image from a text prompt')
    parser.add_argument('--prompt', required=True, help='Text prompt for image generation')
    parser.add_argument('--output', required=True, help='Output filename (e.g., output.png)')

    args = parser.parse_args()

    # Set up headers
    headers = {
        "Authorization": f"Bearer {REVE_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Set up request payload with 2:3 aspect ratio
    payload = {
        "prompt": args.prompt,
        "aspect_ratio": "2:3",
        "version": "latest"
    }

    # Make the API request
    print(f"Generating image with prompt: {args.prompt}")
    print("Aspect ratio: 2:3")
    try:
        response = requests.post("https://api.reve.com/v1/image/create", headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        # Parse the response
        result = response.json()
        print(f"Request ID: {result['request_id']}")
        print(f"Credits used: {result['credits_used']}")
        print(f"Credits remaining: {result['credits_remaining']}")

        if result.get('content_violation'):
            print("Warning: Content policy violation detected")
        else:
            print("Image generated successfully!")
            # The base64 image data is in result['image']
            if 'image' in result:
                # Decode base64 and save to file
                image_data = base64.b64decode(result['image'])
                with open(args.output, 'wb') as f:
                    f.write(image_data)
                print(f"Image saved to: {args.output}")
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
