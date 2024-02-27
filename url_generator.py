import base64

def generate_open_tracking_pixel(username, customer_id):
    tracking_data = {"username": username, "customer_id": customer_id}
    tracking_data_str = base64.urlsafe_b64encode(str(tracking_data).encode()).decode()
    tracking_pixel_url = f"http://139.84.133.1:5000/track/open-pixel/{tracking_data_str}"
    return tracking_pixel_url

# Example: generate tracking pixels for different users
username1 = "Manu p p"
customer_id1 = 1
open_tracking_pixel1 = generate_open_tracking_pixel(username1, customer_id1)

username2 = "jane_doe"
customer_id2 = 2
open_tracking_pixel2 = generate_open_tracking_pixel(username2, customer_id2)

html_email_content = f"""
<html>
  <body>
    <p>Hello,</p>
    <p>This is a sample email with an invisible tracking pixel. The pixel is included in the image below:</p>
    <img src="{open_tracking_pixel1}" alt="Tracking Pixel" width="1" height="1" style="display:none;">
    
    <p>Thank you!</p>
    
    <p>Hello again,</p>
    <p>This is another sample email with a different tracking pixel. The pixel is included in the image below:</p>
    <img src="{open_tracking_pixel2}" alt="Tracking Pixel" width="1" height="1" style="display:none;">
    
    <p>Thank you!</p>
  </body>
</html>
"""

print(html_email_content)
