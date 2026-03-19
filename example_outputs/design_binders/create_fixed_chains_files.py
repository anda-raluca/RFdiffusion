import glob
import json
import os

pdb_dir = "/homes/55/anda/RFdiffusion/example_outputs/design_binders/"
out_file = "/homes/55/anda/RFdiffusion/example_outputs/design_binders/chains_fixed_PDL1.json"

chain_dict = {}

for pdb in sorted(glob.glob(os.path.join(pdb_dir, "*.pdb"))):
    name = os.path.splitext(os.path.basename(pdb))[0]
    chain_dict[name] = [["B"], ["A"]]   # design B, fix A

# Write clean JSON (no BOM, valid UTF-8)
with open(out_file, "w", encoding="utf-8") as fh:
    json.dump(chain_dict, fh, separators=(",", ":"), ensure_ascii=False)

print(f"Wrote chain rules for {len(chain_dict)} PDBs to {out_file}")