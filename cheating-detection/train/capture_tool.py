import cv2
import os
import time

def capture_for_dataset(source=0, output_folder="dataset/raw/new_samples", interval_ms=1000):
    """
    Tự động chụp ảnh từ camera hoặc video để làm dataset.
    Nhấn 's' để bắt đầu/dừng chụp tự động.
    Nhấn 'c' để chụp 1 tấm duy nhất.
    Nhấn 'q' để thoát.
    """
    os.makedirs(output_folder, exist_ok=True)
    cap = cv2.VideoCapture(source)
    
    auto_capture = False
    last_capture_time = 0
    count = len(os.listdir(output_folder))

    print(f"Bắt đầu capture vào: {output_folder}")
    print("Commands: [s] Toggle Auto, [c] Capture Single, [q] Quit")

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        display = frame.copy()
        if auto_capture:
            cv2.circle(display, (30, 30), 10, (0, 0, 255), -1)
            cv2.putText(display, "REC", (50, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            if (time.time() - last_capture_time) * 1000 > interval_ms:
                filename = f"img_{int(time.time()*1000)}.jpg"
                cv2.imwrite(os.path.join(output_folder, filename), frame)
                last_capture_time = time.time()
                count += 1
        
        cv2.imshow("Capture Utility", display)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('s'):
            auto_capture = not auto_capture
            print(f"Auto capture: {auto_capture}")
        elif key == ord('c'):
            filename = f"manual_{int(time.time()*1000)}.jpg"
            cv2.imwrite(os.path.join(output_folder, filename), frame)
            count += 1
            print(f"Captured: {filename}")

    cap.release()
    cv2.destroyAllWindows()
    print(f"Tổng cộng đã có {count} ảnh trong thư mục.")

if __name__ == "__main__":
    # Thay source bằng đường dẫn video nếu muốn trích từ video
    capture_for_dataset(source=0, interval_ms=2000)
