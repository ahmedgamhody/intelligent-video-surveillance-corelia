from ultralytics import YOLO
import os
import shutil
from config import NUM_PATCHES


class ExportYolo:
    def __init__(self, model_path, model_name=None):
        self.model_path = model_path
        self.model = YOLO(model_path)

        self.model_name = os.path.splitext(os.path.basename(model_path))[0]
        if model_name:
            os.rename(model_path, model_path.replace(self.model_name, model_name))
            print(f"Model Renamed: {self.model_name} -> {model_name}")
            self.model_name = model_name


    def export_to(self, mode):
        assert mode in ['gpu_cpu', 'cpu_only', 'mobile'], ValueError("Mode should be gpu_cpu, cpu_only, or mobile")
        export_args = {'format': {'gpu_cpu': 'engine', 'cpu_only': 'onnx', 'mobile': 'torchscript'}.get(mode),
                       'device': 'cpu' if mode == 'mobile' else 2,
                       'nms': True,
                       'batch': NUM_PATCHES,
                       'task': self.model.task,
                       }
        
        if mode == 'mobile':
            export_args['optimize'] = True
        else:
            export_args['half'] = True

        export_dir = os.path.join(os.path.dirname(os.path.dirname(self.model_path)), export_args.get('format'))
        os.makedirs(export_dir, exist_ok=True)

        self.model_name = f"{self.model_name}.{export_args.get('format')}"
        if self.model_name in list(os.listdir(export_dir)):
            print(f"✅ Model {self.model_name} already exist")
            return

        src_file = self.model_path.replace('.pt', '.' + export_args.get('format'))
        dst_file = os.path.join(export_dir, self.model_name)

        try:
            self.model.export(**export_args)
            shutil.move(src_file, dst_file)
            if mode == "gpu_cpu":
                os.makedirs(str(export_dir).replace("engine", "onnx"), exist_ok=True)
                shutil.move(str(self.model_path).replace('.pt', '.onnx'), str(dst_file).replace("engine", "onnx"))
            print(f"✅ Model exported successfully")
        except Exception as e:
            print(f"❌ Error exporting model: {e}")
            if mode == "gpu_cpu":
                os.remove(str(self.model_path).replace('.pt', '.onnx'))


if __name__ == "__main__":
    src_dir = "./static/models/pt/"

    # models = sorted(os.listdir(src_dir), key=lambda f: os.path.getsize(os.path.join(src_dir, f)))

    models = ['yolov8n.pt', 'yolov8n-seg.pt', 'yolov8n-pose.pt']
        # ['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt',
        # 'yolov8n-seg.pt', 'yolov8s-seg.pt', 'yolov8m-seg.pt', 'yolov8l-seg.pt', 'yolov8x-seg.pt',
        # 'yolov8n-pose.pt', 'yolov8s-pose.pt', 'yolov8m-pose.pt', 'yolov8l-pose.pt', 'yolov8x-pose.pt']
    models = [src_dir + model for model in models]
    
    # Define the mapping from old names to new names
    name_mapping = {
        # Detection models
        'yolov8n': 'Default detection nano',
        'yolov8s': 'Default detection small',
        'yolov8m': 'Default detection medium',
        'yolov8l': 'Default detection large',
        'yolov8x': 'Default detection x-large',
        
        # Segmentation models
        'yolov8n-seg': 'Default segmentation nano',
        'yolov8s-seg': 'Default segmentation small',
        'yolov8m-seg': 'Default segmentation medium',
        'yolov8l-seg': 'Default segmentation large',
        'yolov8x-seg': 'Default segmentation x-large',
        
        # Positioning models
        'yolov8n-pose': 'Pose estimation nano',
        'yolov8s-pose': 'Pose estimation small',
        'yolov8m-pose': 'Pose estimation medium',
        'yolov8l-pose': 'Pose estimation large',
        'yolov8x-pose': 'Pose estimation x-large',
    }

    print(models)
    for filename in models:
        if filename.endswith('.pt'):
            exporter = ExportYolo(src_dir + filename, model_name=name_mapping.get(filename.split('.')[0]))
            exporter.export_to('gpu_cpu')
            # exporter.export_to('cpu')
            # exporter.export_to('mobile')
