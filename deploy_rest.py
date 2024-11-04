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

    try:
        # Create collection (model)
        collection_data = {
            "owner": "vasa-develop",
            "name": "esmfold",
            "description": "ESM-Fold protein structure prediction model with memory optimization",
            "visibility": "public",
            "hardware": "gpu-t4",
            "github_url": "https://github.com/vasa-develop/esmfold",
            "paper_url": "https://www.biorxiv.org/content/10.1101/2022.07.20.500902v1"
        }

        print("Creating collection...")
        collection_response = requests.post(
            f"{MODELS_URL}",
            headers=headers,
            json=collection_data
        )

        if not collection_response.ok and collection_response.status_code != 409:
            print(f"Failed to create collection: {collection_response.text}")
            if collection_response.status_code != 409:  # 409 means already exists
                return False

        # Create version
        version_data = {
            "version": {
                "cog_version": "0.8.5",
                "cuda_version": "11.8",
                "python_version": "3.10",
                "python_packages": [
                    "torch==2.0.1",
                    "fair-esm[esmfold]",
                    "biotite==0.36.1",
                    "biopython==1.81",
                    "accelerate>=0.21.0"
                ],
                "system_packages": [
                    "libgl1-mesa-glx",
                    "libglib2.0-0",
                    "git"
                ]
            },
            "hardware": {
                "gpu": "t4",
                "gpu_memory": "16GB"
            },
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
            }
        }

        print("Creating version...")
        version_response = requests.post(
            f"{MODELS_URL}/vasa-develop/esmfold/versions",
            headers=headers,
            json=version_data
        )

        if version_response.ok:
            version_info = version_response.json()
            print(f"Version created successfully: {version_info.get('id', 'Unknown ID')}")
            print("Deployment URL:", f"https://replicate.com/vasa-develop/esmfold")
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
