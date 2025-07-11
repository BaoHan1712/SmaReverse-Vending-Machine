from get_library import *



class YOLOProcessor(threading.Thread):
    """
    A dedicated thread to handle YOLO model processing to avoid freezing the GUI.
    """
    def __init__(self, video_path, model_path, output_queue):
        super().__init__(daemon=True)
        self.video_path = video_path
        self.model_path = model_path
        self.output_queue = output_queue
        self.running = True

    def run(self):
        """Main loop for video processing."""
        try:
            model = YOLO(self.model_path)
        except Exception as e:
            print(f"⚠️ Lỗi tải model: {e}")
            return

        try:
            # Use 0 for webcam, or a path for a video file
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                raise IOError(f"Không thể mở video tại: {self.video_path}")
        except Exception as e:
            print(f"⚠️ Lỗi mở video: {e}")
            return
        
        track_history = {}
        line = [10, 190, 630, 190] # Adjusted line for 640 width
        count_set = set()
        total_count = 0

        while self.running and cap.isOpened():
            success, frame = cap.read()
            if not success:
                # If it's a video file, stop. If it's a webcam, maybe just wait.
                if isinstance(self.video_path, str):
                    print("⚠️ Hết video.")
                    break 
                continue

            frame = cv2.resize(frame, (640, 480))
            results = model.track(source=frame, imgsz=640, conf=0.6, verbose=False,device = "0", persist=True, tracker=r'tracking/bytetrack.yaml')[0]
             # Draw the counting line
            cv2.line(frame, (line[0], line[1]), (line[2], line[3]), (0, 255, 255), 3)
            if results.boxes and results.boxes.is_track:
                boxes = results.boxes.xywh.cpu().numpy()
                track_ids = results.boxes.id.int().cpu().tolist()
                
                # Plot tracked boxes onto the frame
                frame = results.plot(boxes=True, color_mode='instance')
                
               
                

                for box, track_id in zip(boxes, track_ids):
                    x, y, w, h = box
                    center_x = int(x)
                    center_y = int(y)
                    cv2.circle(frame, (center_x, center_y), 3, (0, 255, 0), -1)  
                    # Check if the object's center crosses the line
                    if line[1] - 10 < center_y < line[1] + 10:
                        if track_id not in count_set:
                            count_set.add(track_id)
                            total_count += 1
                            cv2.line(frame, (line[0], line[1]), (line[2], line[3]), (0, 0, 255), 3)
            
            # Put the processed frame and count into the queue
            try:
                self.output_queue.put_nowait((frame, total_count))
            except queue.Full:
                # If the queue is full, just skip this frame to avoid lag
                pass
        
        cap.release()
        print("Luồng YOLO đã dừng.")

    def stop(self):
        """Signals the thread to stop."""
        self.running = False