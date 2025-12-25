"""
System capability checker for Whisper transcription
"""

import sys
import torch
import psutil


class SystemChecker:
    """Check system capabilities and recommend settings"""

    @staticmethod
    def check_system():
        """Check system capabilities"""
        info = {
            'python_version': sys.version,
            'torch_version': torch.__version__,
            'device': 'cpu',
            'gpu_name': None,
            'gpu_memory': 0,
            'ram_available': 0,
            'recommended_model': 'base'
        }

        # Check GPU
        if torch.cuda.is_available():
            info['device'] = 'cuda'
            info['gpu_name'] = torch.cuda.get_device_name()
            info['gpu_memory'] = torch.cuda.get_device_properties(0).total_memory / 1e9

        # Check RAM
        memory = psutil.virtual_memory()
        info['ram_available'] = memory.available / 1e9

        # Recommend model size
        if info['ram_available'] < 4:
            info['recommended_model'] = 'tiny'
        elif info['ram_available'] < 8:
            info['recommended_model'] = 'base'
        elif info['ram_available'] < 16:
            info['recommended_model'] = 'small'
        else:
            info['recommended_model'] = 'medium'

        return info
