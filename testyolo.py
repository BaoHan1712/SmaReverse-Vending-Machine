from ultralytics import YOLO

# Load a pretrained YOLO11n model
model = YOLO(r"model\best.pt")

# # Multiple streams with batched inference (e.g., batch-size 8 for 8 streams)
# source = r"C:\Users\hanqu\Videos\Screen Recordings\coca.mp4"

# # Run inference on the source
# results = model.predict(source, conf = 0.85, show = True)  # generator of Results objects

print(model.names) 