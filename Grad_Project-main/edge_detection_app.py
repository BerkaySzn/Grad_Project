import cv2
import numpy as np
import os
import argparse
from flask import Flask, request, jsonify, send_file, render_template
import io
import base64
from PIL import Image

app = Flask(__name__, template_folder="templates")


def process_image(
    image,
    blur_kernel_size=(7, 7),
    canny_threshold1=30,
    canny_threshold2=100,
    dilation_kernel_size=(5, 5),
    dilation_iterations=2,
    edge_weight=0.3,
):

    # Save original image
    original = image.copy()

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, blur_kernel_size, 0)

    # Edge detection
    edges = cv2.Canny(blurred, canny_threshold1, canny_threshold2)

    # Create kernel for dilation
    kernel = np.ones(dilation_kernel_size, np.uint8)

    # Dilate edges
    dilated_edges = cv2.dilate(edges, kernel, iterations=dilation_iterations)

    # Additional edge enhancement
    enhanced_edges = cv2.morphologyEx(dilated_edges, cv2.MORPH_CLOSE, kernel)

    # Combine original image with enhanced edges
    edge_mask = cv2.cvtColor(enhanced_edges, cv2.COLOR_GRAY2BGR)
    enhanced_image = cv2.addWeighted(
        image, 1.0 - edge_weight, edge_mask, edge_weight, 0
    )

    # Additional contrast enhancement
    lab = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    enhanced_image = cv2.cvtColor(cv2.merge((cl, a, b)), cv2.COLOR_LAB2BGR)

    return {"original": original, "edges": enhanced_edges, "enhanced": enhanced_image}


def save_images(images, output_dir):
    """Save images to the specified directory"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    paths = {}
    for name, img in images.items():
        path = os.path.join(output_dir, f"{name}.jpg")
        cv2.imwrite(path, img)
        paths[name] = path

    return paths


def image_to_base64(image):
    """Convert OpenCV image to base64 string"""
    _, buffer = cv2.imencode(".jpg", image)
    return base64.b64encode(buffer).decode("utf-8")


@app.route("/")
def index():
    """Render the main page"""
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    """API endpoint to process an image with edge detection"""
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files["image"]
    img_bytes = file.read()

    # Convert to OpenCV image
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Get parameters from request
    params = request.form.to_dict()
    blur_size = tuple(map(int, params.get("blur_size", "7,7").split(",")))
    canny1 = int(params.get("canny1", 30))
    canny2 = int(params.get("canny2", 100))
    dilation_size = tuple(map(int, params.get("dilation_size", "5,5").split(",")))
    dilation_iter = int(params.get("dilation_iter", 2))
    edge_weight = float(params.get("edge_weight", 0.3))

    # Process image
    results = process_image(
        img,
        blur_kernel_size=blur_size,
        canny_threshold1=canny1,
        canny_threshold2=canny2,
        dilation_kernel_size=dilation_size,
        dilation_iterations=dilation_iter,
        edge_weight=edge_weight,
    )

    # Save images to temp directory
    output_dir = "temp_edge_detection"
    paths = save_images(results, output_dir)

    # Convert images to base64 for response
    response = {
        "original": image_to_base64(results["original"]),
        "edges": image_to_base64(results["edges"]),
        "enhanced": image_to_base64(results["enhanced"]),
        "paths": paths,
    }

    return jsonify(response)


@app.route("/download/<image_type>", methods=["GET"])
def download(image_type):
    """Download a processed image"""
    image_type = image_type.lower()
    if image_type not in ["original", "edges", "enhanced"]:
        return jsonify({"error": "Invalid image type"}), 400

    path = os.path.join("temp_edge_detection", f"{image_type}.jpg")
    if not os.path.exists(path):
        return jsonify({"error": "Image not found"}), 404

    return send_file(path, mimetype="image/jpeg")


def main():
    parser = argparse.ArgumentParser(description="Edge Detection Application")
    parser.add_argument(
        "--port", type=int, default=5001, help="Port to run the server on"
    )
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Host to run the server on"
    )
    args = parser.parse_args()

    print(f"Starting Edge Detection Server on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=True)


if __name__ == "__main__":
    main()
