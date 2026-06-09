import os
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

REQUIRED_FIELDS = {
    "id", "scholarship_name", "org_name", "source_url", "country", "source_type",
    "award_amount", "currency", "deadline", "award_year", "degree_levels",
    "eligible_nationalities", "eligible_visa_types", "fields_of_study",
    "description", "eligibility_text", "feature_manifest", "last_verified",
    "created_at", "updated_at"
}

VALID_FEATURE_TYPES = {"enum", "threshold", "boolean", "output", "range"}

def load_scholarships(data_dir: str) -> list[dict]:
    scholarships = []
    base_path = Path(data_dir)
    
    if not base_path.exists():
        logger.error(f"Directory not found: {data_dir}")
        return scholarships

    for file_path in base_path.rglob("*.json"):
        if file_path.name == "schema.json":
            continue
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {file_path}: {e}")

        # Validate required top-level fields
        missing_fields = REQUIRED_FIELDS - set(data.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields in {file_path}: {missing_fields}")

        feature_manifest = data.get("feature_manifest")
        if not isinstance(feature_manifest, dict):
            raise ValueError(f"'feature_manifest' must be an object in {file_path}")

        if "total_features" not in feature_manifest:
            raise ValueError(f"Missing 'total_features' in feature_manifest in {file_path}")
            
        if "features" not in feature_manifest:
            raise ValueError(f"Missing 'features' in feature_manifest in {file_path}")
            
        features = feature_manifest["features"]
        if not isinstance(features, list):
            raise ValueError(f"'features' must be a list in {file_path}")
            
        if feature_manifest["total_features"] != len(features):
            raise ValueError(f"'total_features' does not match len(features) in {file_path}")

        for feature in features:
            if not isinstance(feature, dict):
                raise ValueError(f"Feature must be an object in {file_path}")
                
            for req_key in ("id", "label", "type", "required"):
                if req_key not in feature:
                    raise ValueError(f"Feature missing '{req_key}' in {file_path}")
                    
            f_type = feature["type"]
            
            if f_type == "score_test":
                raise ValueError(f"Found forbidden feature type 'score_test' in {file_path}")
                
            if f_type not in VALID_FEATURE_TYPES:
                raise ValueError(f"Invalid feature type '{f_type}' in {file_path}")
                
            if f_type == "enum":
                if "student_field" not in feature:
                    raise ValueError(f"Enum feature missing 'student_field' in {file_path}")
                if "values" not in feature or not isinstance(feature["values"], list):
                    raise ValueError(f"Enum feature missing 'values' list in {file_path}")
            elif f_type == "threshold":
                if "student_field" not in feature:
                    raise ValueError(f"Threshold feature missing 'student_field' in {file_path}")
                if "min" not in feature and "max" not in feature:
                    raise ValueError(f"Threshold feature missing 'min' or 'max' in {file_path}")
            elif f_type == "boolean":
                if "student_field" not in feature:
                    raise ValueError(f"Boolean feature missing 'student_field' in {file_path}")
            elif f_type == "range":
                if "student_field" not in feature:
                    raise ValueError(f"Range feature missing 'student_field' in {file_path}")
                if "min" not in feature and "max" not in feature:
                    raise ValueError(f"Range feature missing 'min' or 'max' in {file_path}")

        scholarships.append(data)
        
    return scholarships

if __name__ == "__main__":
    try:
        data_directory = os.path.join(os.path.dirname(__file__), "..", "data", "scholarships")
        loaded = load_scholarships(data_directory)
        print(f"Loaded {len(loaded)} scholarship records.")
    except Exception as e:
        logger.error(str(e))
        exit(1)
