Person Detection Model using YOLO11
=====================================

Overview:
---------
This package contains a trained YOLO11 model for detecting persons in images and videos.
The model was developed as part of a study on physical security and safety applications.
It has been trained to detect the presence of persons (class 0) with high accuracy.

Files Included:
---------------
1. best.pt
   - The best model checkpoint (weights) saved during training.
2. person_detection.yaml
   - The data configuration file used during training.
     It defines the dataset paths, number of classes (nc = 1), and class names.
3. readme.txt
   - This documentation file.
4. inference.py (optional)
   - A sample script showing how to load the model and run inference.
     (Include this file only if you have created one.)

Training Metrics (from best training run):
-------------------------------------------
- Train ID: train_YYYYMMDD_HHMMSS   (unique session identifier)
- Model: yolo11s.pt
- mAP50: 0.950
- mAP50-95: 0.706
- Precision: 0.899
- Recall: 0.891
- Training Time: 13.070 seconds

Usage:
------
To use the model for inference, load the model using the Ultralytics YOLO API:

    from ultralytics import YOLO
    model = YOLO("best.pt")
    results = model.predict(source="your_image.jpg", imgsz=640)
    results.show()  # or process the results as needed

Requirements:
-------------
- Python 3.7+
- PyTorch
- Ultralytics YOLO
- OpenCV, pandas, matplotlib, seaborn (for analysis and visualization)

Notes:
------
- Ensure that the 'person_detection.yaml' file is updated with the correct dataset paths if necessary.
- This package is provided as-is for research and educational purposes.
- For more details on how to use and configure the YOLO model, refer to:
  https://docs.ultralytics.com