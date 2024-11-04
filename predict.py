# Prediction interface for Cog ⚙️
# https://cog.run/python

from cog import BasePredictor, Input
import torch
import esm
from typing import Dict
import os
from pathlib import Path


class Predictor(BasePredictor):
    def setup(self) -> None:
        """Load the model into memory to make running multiple predictions efficient"""
        # Create cache directory if it doesn't exist
        cache_dir = Path("/root/.cache/esm")
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize model with cache directory
        self.model = None  # Lazy loading
        torch.cuda.empty_cache()  # Clear any residual memory

    def _load_model(self):
        """Lazy load the model only when needed"""
        if self.model is None:
            self.model = esm.pretrained.esmfold_v1()
            self.model = self.model.eval().cuda()
        return self.model

    def predict(
        self,
        protein_sequences: str = Input(description="Protein sequence in FASTA format"),
    ) -> Dict[str, str]:
        """Run protein structure prediction on the input sequence"""
        # Parse FASTA input
        lines = protein_sequences.strip().split('\n')
        sequence = ''
        for line in lines:
            if not line.startswith('>'):
                sequence += line.strip()

        # Clean sequence
        sequence = ''.join(char for char in sequence if char.isalpha())

        # Validate sequence
        if not sequence:
            raise ValueError("No valid protein sequence found in input")

        # Load model if not loaded
        model = self._load_model()

        # Run prediction with memory optimization
        with torch.cuda.amp.autocast():  # Use mixed precision for memory efficiency
            with torch.no_grad():  # Disable gradient computation
                output = model.infer_pdb(sequence)

        # Clear GPU memory after prediction
        torch.cuda.empty_cache()

        return {
            "pdb_string": output,
            "sequence_length": len(sequence)
        }
