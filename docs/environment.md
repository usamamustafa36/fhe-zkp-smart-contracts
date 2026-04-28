# Reproducibility Documentation

**THESIS REFERENCE**: Appendix A - Reproducibility Guide

## Hardware Environment
- **CPU**: x86_64, 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended  
- **Disk**: 2GB free space
- **GPU**: Optional (TenSEAL has partial GPU support)

## Software Environment
- **OS**: Ubuntu 20.04 LTS or compatible Linux
- **Python**: 3.10.x (tested on 3.10.12)
- **pip**: 23.0+

## Dependency Versions (Pinned)
See `requirements.txt`:
```
tenseal==0.3.14
numpy==1.21.6
web3==6.0.0
eth-account==0.8.0
flask==2.3.0
joblib==1.1.1
tqdm==4.64.1
psutil==5.9.0
pandas==1.5.3
```

## Installation Steps
```bash
# 1. Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify installation
python -c "import tenseal; print('TenSEAL OK')"
python -c "from crypto.fhe_engine import AdvancedFHE; print('Imports OK')"
```

## Running Reproducible Evaluation
```bash
# Complete thesis evaluation
python demo/thesis_demo.py

# Individual modules
python evaluation/performance.py
python evaluation/scaling.py
python evaluation/cost_analysis.py
python evaluation/comparative.py
```

## Expected Runtime
- Performance benchmarks: ~5-10 minutes
- Scaling experiments: ~10-15 minutes
- Full evaluation: ~20-30 minutes

## Output Locations
```
evaluation/results/performance/  # Performance JSON/CSV
evaluation/results/scaling/      # Scaling JSON/CSV
figures/output/                  # Generated plots (if created)
```

## Reproducibility Notes
- Fixed random seeds (where applicable)
- Deterministic test data generation
- Multiple iterations for averaging
- Timestamps in all outputs

## Known Environment Issues
- **M1/M2 Macs**: TenSEAL may require Rosetta 2
- **Windows**: Use WSL2 for best compatibility
- **ARM**: Limited TenSEAL support

Last Updated: January 11, 2026
