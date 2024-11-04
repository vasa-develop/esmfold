import os
import requests
import json
from pathlib import Path

def deploy_model():
    # Set up authentication
    headers = {
        "Authorization": f"Token {os.environ['REPLICATE_API_KEY']}",
        "Content-Type": "application/json"
    }

    # API endpoints
    BASE_URL = "https://api.replicate.com/v1"
    MODELS_URL = f"{BASE_URL}/models"

    # Model configuration
    model_data = {
        "owner": "vasa-develop",
        "name": "esmfold",
        "description": "ESM-Fold protein structure prediction model with memory optimization",
        "visibility": "public",
        "hardware": "gpu-t4"
    }

    try:
        # Check if model exists
        model_response = requests.get(
            f"{MODELS_URL}/vasa-develop/esmfold",
            headers=headers
        )

        if model_response.status_code == 404:
            # Create model if it doesn't exist
            model_response = requests.post(
                MODELS_URL,
                headers=headers,
                json=model_data
            )
            if not model_response.ok:
                print(f"Failed to create model: {model_response.text}")
                return False
            print("Model created successfully")
        else:
            print("Model already exists")

        # Read model files
        with open("cog.yaml", "r") as f:
            cog_yaml = f.read()
        with open("predict.py", "r") as f:
            predict_py = f.read()

        # Create version
        version_data = {
            "cog_yaml": cog_yaml,
            "openapi_schema": {
                "input": {
                    "properties": {
                        "protein_sequences": {
                            "type": "string",
                            "description": "Protein sequence in FASTA format"
                        }
                    },
                    "required": ["protein_sequences"]
                },
                "output": {
                    "properties": {
                        "pdb_string": {
                            "type": "string",
                            "description": "Predicted protein structure in PDB format"
                        },
                        "sequence_length": {
                            "type": "integer",
                            "description": "Length of the processed protein sequence"
                        }
                    }
                }
            },
            "python_packages": [
                "torch==2.0.1",
                "fair-esm[esmfold]",
                "biotite==0.36.1",
                "biopython==1.81",
                "accelerate>=0.21.0"
            ],
            "python_version": "3.10",
            "cuda_version": "11.8",
            "files": {
                "predict.py": predict_py
            }
        }

        version_response = requests.post(
            f"{MODELS_URL}/vasa-develop/esmfold/versions",
            headers=headers,
            json=version_data
        )

        if version_response.ok:
            version_info = version_response.json()
            print(f"Version created successfully: {version_info.get('id', 'Unknown ID')}")
            return True
        else:
            print(f"Failed to create version: {version_response.text}")
            return False

    except Exception as e:
        print(f"Error during deployment: {str(e)}")
        return False

if __name__ == "__main__":
    success = deploy_model()
    if success:
        print("Model deployed successfully!")
    else:
        print("Failed to deploy model")
