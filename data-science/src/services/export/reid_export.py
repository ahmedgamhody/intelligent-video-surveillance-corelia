import sys
from boxmot.appearance import reid_export

sys.argv = [
    "reid_export.py",  # Dummy script name
    # "--batch-size", "1"
    "--imgsz", "640", "640",
    "--device", "3", # "cuda device, i.e. 0 or 0,1,2,3 or cpu"
    "--simplify", # ONNX: simplify model
    # "--optimize", # TorchScript: optimize for mobile
    "--weights", "../../static/models/reid/osnet_x1_0_market1501.pt",
    "--half",
    "--include", "engine" # "torchscript, onnx, openvino, engine"
]

reid_export.main()
