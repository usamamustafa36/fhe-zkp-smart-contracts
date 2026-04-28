#!/bin/bash
#
# Full Performance Evaluation Pipeline Entrypoint
# =================================================
#
# Runs complete benchmarking suite:
# - CKKS/FHE performance
# - Scaling analysis
# - ZKP metrics
# - End-to-end latency
# - Resource utilization
# - All visualizations
#
# USAGE:
#   ./run-full-evaluation.sh          # Full evaluation
#   ./run-full-evaluation.sh --quick  # Quick test
#
# OUTPUT:
#   evaluation/results/
#     ├── performance/  - CKKS metrics CSV
#     ├── scaling/      - Scaling data CSV
#     ├── zkp/          - ZKP metrics CSV
#     ├── end_to_end/   - Pipeline latency CSV
#     ├── resources/    - Resource usage CSV
#     └── plots/        - All PNG visualizations (300 DPI)

set -e

# Navigate to project root
cd "$(dirname "$0")"

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                            ║"
echo "║        THESIS PERFORMANCE EVALUATION PIPELINE                             ║"
echo "║        Complete Benchmarking Suite                                        ║"
echo "║                                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python availability
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    echo "   Please install Python 3.7+"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Check for ZKP artifacts (optional but recommended)
if [ ! -f "zkp_prod/artifacts/range_commit_0001.zkey" ]; then
    echo "⚠️  Warning: ZKP artifacts not found"
    echo "   ZKP benchmarks will be skipped"
    echo "   To include ZKP metrics, run: ./zkp_prod/scripts/build.sh"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run pipeline
echo "Starting full evaluation pipeline..."
echo ""

python3 evaluation/run_full_benchmark.py "$@"

EXITCODE=$?

if [ $EXITCODE -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════════════╗"
    echo "║  ✓ EVALUATION COMPLETE                                                    ║"
    echo "║  All results saved to: evaluation/results/                                 ║"
    echo "╚════════════════════════════════════════════════════════════════════════════╝"
else
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════════════╗"
    echo "║  ⚠ EVALUATION INCOMPLETE                                                  ║"
    echo "║  Check error messages above                                                ║"
    echo "╚════════════════════════════════════════════════════════════════════════════╝"
fi

exit $EXITCODE
