import json
from PIL import Image
from http.server import HTTPServer, BaseHTTPRequestHandler
import torch
from min_dalle import MinDalle
import hashlib
import os

# use float32 for faster rendering and float16 to save resources which is obviously slower

HOST = "localhost"
PORT = 6969

class HTTP(BaseHTTPRequestHandler):
    def do_GET(self):
        img = Image.open('image.png')
        w, h = img.size
        new = img.resize((w // 3, h // 3))
        vals = list(new.getdata())

        img_data = {
            "data": vals,
            "size": new.size,
        }

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(img_data), encoding='utf8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_data = json.loads(post_data)

        print("received post data:", post_data)

        prompt = str(post_data.get("text", ""))

        if prompt:
            try:
                _, file_path = generate_ai_image(prompt)
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(f"internal server error: {e}".encode('utf-8'))
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"no valid prompt provided")

def generate_ai_image(prompt):
    root = os.getcwd()

    model = MinDalle(models_root=root, dtype=torch.float32, device='cuda', is_mega=False, is_reusable=True)

    image = model.generate_image(text=prompt, seed=-1, grid_size=1, is_seamless=False,
                                 temperature=1, top_k=256)

    file_name = 'image.png'.format(create_hash(prompt))
    file_path = os.path.join(root, file_name)

    image.save(file_path)
    print(f"saved at: {file_path}")
    return image, file_path

def create_hash(prompt):
    return int(hashlib.sha256(prompt.encode('utf-8')).hexdigest(), 16) % 100 ** 8

if __name__ == '__main__':
    server = HTTPServer((HOST, PORT), HTTP)
    print(f"server started on http://{HOST}:{PORT}")
    server.serve_forever()
    server.server_close()
    print("Server stopped")
