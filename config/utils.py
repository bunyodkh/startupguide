import os
import uuid
from django.utils.timezone import now
from django.utils.deconstruct import deconstructible

@deconstructible
class UploadToPath:
    def __init__(self, folder_name):
        self.folder_name = folder_name

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # Use .hex for a cleaner filename without dashes
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Structure: folder_name/YYYY/MM/uuid.ext
        date_path = now().strftime("%Y/%m")
        return os.path.join(self.folder_name, date_path, filename)