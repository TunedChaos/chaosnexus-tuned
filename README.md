// chaosnexus-tuned/README.md

<img src="./assets/banner.png" alt="ChaosNexus Tuned Banner" />

# ChaosNexus Tuned

Local dataset generation and fine-tuning pipeline for ChaosNexus (Unsloth / PEFT), targeting IBM Granite 4.1-8B for Rhai tooling under roughly 6GB VRAM.

> **Status:** **ChaosNexus Tuned v1** (`ChaosNexus_Tuned_v1`) cleared the Anvil full-version gate (mean **0.944**, smoke clear). Adapter weights stay out of git; Hub card lives under `launch/model/ChaosNexus_Tuned_v1/`.

- **Docs:** [chaosnexus.ai](https://chaosnexus.ai)
- **Contribute:** [codeberg.org/TunedChaos/chaosnexus-tuned](https://codeberg.org/TunedChaos/chaosnexus-tuned) (primary)
- **Mirror:** [github.com/TunedChaos/chaosnexus-tuned](https://github.com/TunedChaos/chaosnexus-tuned)
- **Release card:** `../launch/model/ChaosNexus_Tuned_v1/README.md`
- **Reproduce Anvil bench:** `./scripts/run_v1_benchmarks.sh --anvil-only`

Please open issues and pull requests on **Codeberg**. Publish the adapter to Hugging Face Hub as `TunedChaos/ChaosNexus_Tuned_v1` after confirming the card Evaluation section.
## Dataset generation

```bash
uv sync
python3 generate_datasets.py
python3 generate_eval_dataset.py
```

## Training

See `train_granite.py` and `ChaosTuner_Training_Rules.md`. Keep `.venv/`, `models/`, and compiled Unsloth caches out of version control.

## AI assistance

Some code in this project was generated with assistance from AI. Humans directed architecture, review, and maintenance. See [AI_ASSISTANCE.md](AI_ASSISTANCE.md).

## License

AGPL-3.0-or-later. See [LICENSE](LICENSE).
