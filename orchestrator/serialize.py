"""Serialization utilities for data quality reports"""
import json
from pathlib import Path
from typing import Any, Union
from dataclasses import asdict, is_dataclass
import pandas as pd


def save_json(obj: Any, filepath: Union[str, Path]) -> None:
    """Save object to JSON file, handling dataclasses and pandas objects"""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(_serialize(obj), f, indent=2, default=str)


def _serialize(obj: Any) -> Any:
    """Recursively serialize objects to JSON-compatible format"""
    if is_dataclass(obj):
        return {k: _serialize(v) for k, v in asdict(obj).items()}
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient='records')
    elif isinstance(obj, (list, tuple)):
        return [_serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    elif hasattr(obj, '__dict__'):
        return {k: _serialize(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
    else:
        return obj
