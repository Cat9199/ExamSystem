import requests

# Update the URL to match your Flask application
api_url = 'http://localhost:8000/api/v1/images'

# Specify the path to the image file
image_file_path = './test-img.jpg'  # Replace with the actual path

# Create a file object for the image
with open(image_file_path, 'rb') as image_file:
    files = {'img': (image_file_path, image_file, 'image/jpeg')}

    # Send a POST request with the image file
    try:
        response = requests.post(api_url, files=files)
        response_data = response.json()

        if response.status_code == 201:
            print(f"Image saved successfully. Code: {response_data['code']}")
        else:
            print(f"Error: {response_data['error']}")

    except Exception as e:
        print(f"Error sending request: {str(e)}")
