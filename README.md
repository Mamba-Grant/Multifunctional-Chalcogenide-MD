# Interatomic-Potential-Training

```bash
mace_prepare_data \
          --train_file="./training_data_10.xyz" \
          --valid_fraction=0.05 \
          --test_file="./testing_data.xyz" \
          --r_max=4.5 \
          --h5_prefix="processed_data/" \
          --compute_statistics \
          --E0s="average" \
          --seed=123 \
          --forces_key=force \
          --energy_key=TotEnergy \
```

```bash
mace_run_train --config config.yaml
```

```yaml
name: "MACE_model"
train_file: "./training_data_10.xyz"
valid_fraction: 0.05
test_file: "./testing_data.xyz"
config_type_weights:
  Default: 1.0
E0s: "average"
model: "MACE"
hidden_irreps: "128x0e + 128x1o"
r_max: 5.0
batch_size: 10
max_num_epochs: 1500
stage_two: true
start_stage_two: 1200
ema: true
forces_weight: 1000
energy_weight: 10
energy_key: "TotEnergy"
forces_key: "force"
ema_decay: 0.99
amsgrad: true
restart_latest: true
device: "cpu"
```
