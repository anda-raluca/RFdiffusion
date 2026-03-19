# #!/usr/bin/env python3
# """
# make_fixed_positions_multi_chain.py

# Generate a JSON mapping PDB_basename -> [designed_positions, fixed_positions]
# for a folder of PDBs that may contain multiple chains.

# Default behavior (changeable via variables below):
#  - design chains: ["B"]
#  - fix chains:    ["A"]

# Positions are 1-indexed **over the concatenated sequence** formed by
# joining chains in alphabetical order (ProteinMPNN convention).
# """

# import glob
# import json
# import os
# from Bio import PDB
# from collections import OrderedDict

# # --------- CONFIGURE HERE ----------
# pdb_dir = "/homes/55/anda/RFdiffusion/example_outputs/design_binders/"
# out_file = "/homes/55/anda/RFdiffusion/example_outputs/design_binders/fixed_positions_PDL1.json"

# # Which chain IDs to treat as designed vs fixed (strings, case-sensitive).
# # Default matches your example [["B"],["A"]] => design B, fix A
# DESIGN_CHAINS = ["B"]
# FIX_CHAINS = ["A"]
# # -----------------------------------

# parser = PDB.PDBParser(QUIET=True)
# ppb = PDB.PPBuilder()

# result = OrderedDict()

# for pdb_path in sorted(glob.glob(os.path.join(pdb_dir, "*.pdb"))):
#     basename = os.path.splitext(os.path.basename(pdb_path))[0]

#     structure = parser.get_structure(basename, pdb_path)
#     model = structure[0]  # first model

#     # collect chain sequences in alphabetical order of chain id
#     chains = sorted(list(model.get_chains()), key=lambda c: c.id)
#     if not chains:
#         print(f"Warning: {basename} has no chains. Skipping.")
#         continue

#     chain_seqs = OrderedDict()
#     for ch in chains:
#         chain_id = ch.id
#         polypeptides = ppb.build_peptides(ch)
#         seq = "".join(str(pp.get_sequence()) for pp in polypeptides) if polypeptides else ""
#         chain_seqs[chain_id] = seq

#     # Build concatenated indexing and assign positions per chain
#     cumulative = 0
#     designed_positions = []
#     fixed_positions = []

#     for chain_id, seq in chain_seqs.items():
#         L = len(seq)
#         if L == 0:
#             # no residues detected for this chain (e.g., non-standard residues)
#             cumulative += 0
#             continue
#         start = cumulative + 1          # 1-indexed start
#         end = cumulative + L            # inclusive
#         pos_range = list(range(start, end + 1))
#         # assign to designed or fixed depending on chain membership
#         if chain_id in DESIGN_CHAINS:
#             designed_positions.extend(pos_range)
#         if chain_id in FIX_CHAINS:
#             fixed_positions.extend(pos_range)
#         # if a chain is in neither list, it's left out of both (fully free for design if you want)
#         cumulative += L

#     # sort positions (not strictly necessary but keeps outputs deterministic)
#     designed_positions = sorted(designed_positions)
#     fixed_positions = sorted(fixed_positions)

#     # final shape: [designed_positions, fixed_positions]
#     result[basename] = [fixed_positions, designed_positions]

# # write clean JSON
# with open(out_file, "w", encoding="utf-8") as fh:
#     json.dump(result, fh, separators=(",", ":"), ensure_ascii=False)

# print(f"Wrote fixed-position rules for {len(result)} PDBs to {out_file}")

#!/usr/bin/env python3
import glob, json, os
from collections import OrderedDict
from Bio import PDB

# config
pdb_dir = "/homes/55/anda/RFdiffusion/example_outputs/design_binders/"
out_file = "/homes/55/anda/RFdiffusion/example_outputs/design_binders/fixed_positions_by_chain.json"
FIX_CHAINS = ["A"]   # chains to fix fully
# DESIGN_CHAINS = ["B"]  # not needed for this output; we just mark fixed positions

parser = PDB.PDBParser(QUIET=True)
ppb = PDB.PPBuilder()

result = OrderedDict()

for pdb_path in sorted(glob.glob(os.path.join(pdb_dir, "*.pdb"))):
    name = os.path.splitext(os.path.basename(pdb_path))[0]
    structure = parser.get_structure(name, pdb_path)
    model = structure[0]
    chains = sorted(list(model.get_chains()), key=lambda c: c.id)

    per_chain = OrderedDict()
    for chain in chains:
        cid = chain.id
        polypeptides = ppb.build_peptides(chain)
        seq = "".join(str(pp.get_sequence()) for pp in polypeptides) if polypeptides else ""
        L = len(seq)
        if cid in FIX_CHAINS:
            per_chain[cid] = list(range(1, L+1))  # fix entire chain
        else:
            per_chain[cid] = []                    # nothing fixed for this chain

    result[name] = per_chain

with open(out_file, "w", encoding="utf-8") as fh:
    json.dump(result, fh, separators=(",", ":"), ensure_ascii=False)

print(f"Wrote {len(result)} entries to {out_file}")