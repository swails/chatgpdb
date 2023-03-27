import asyncio
from collections import Counter
from typing import Optional

import parmed as pmd

from chatgpdb.settings import PARMED_CACHE_DIR


async def process_pdb_file(pdb_code: str) -> pmd.Structure:
    if len(pdb_code) != 4:
        raise ValueError(f"Silly rabbit, {pdb_code} is not a valid PDB code. Tricks are for kids!")

    pdb_path = PARMED_CACHE_DIR / f"{pdb_code.lower()}.pdb"
    cif_path = PARMED_CACHE_DIR / f"{pdb_code.lower()}.cif"

    if pdb_path.exists():
        return await asyncio.to_thread(pmd.load_file, pdb_path.as_posix())

    if cif_path.exists():
        return await asyncio.to_thread(pmd.load_file, cif_path.as_posix())

    try:
        struct = await asyncio.to_thread(pmd.download_CIF, pdb_code, saveto=pdb_path.as_posix())
    except OSError:
        struct = await asyncio.to_thread(pmd.download_PDB, pdb_code, saveto=pdb_path.as_posix())

    return struct


def describe_structure(struct: pmd.Structure, pdb_id: str) -> tuple[str, str]:
    """Get a description of a structure that we can use to seed the GPT generator."""
    n_residues = len(struct.residues)
    residue_counts = Counter([residue.name for residue in struct.residues])
    n_atoms = len(struct.atoms)
    has_hydrogens = any(atom.atomic_number == 1 for atom in struct.atoms)

    authors = struct.journal_authors
    year = "a time past, long forgotten" if struct.year is None else struct.year.split(",")[0].strip()
    experimental = struct.experimental.title().replace("Nmr", "NMR")
    resolution_passage = ""
    journal = struct.journal
    page = struct.page
    title = struct.title.split(";")[0].strip().rstrip(".")

    if struct.resolution is not None:
        if struct.resolution > 1.5:
            resolution_passage = f"They resolved only to {struct.resolution} Angstroms, but we'll let it slide in {year}. "
        else:
            resolution_passage = f"They managed to resolve to {struct.resolution} Angstroms! "

    description = (
        f"In {year}, {authors} ran a {experimental} experiment to solve the {n_residues}-residue {pdb_id}. "
        f"Doing so, they managed to find {n_atoms} atoms lurking in the protein."
        f"{' (though they forgot about the hydrogen atoms...)' if not has_hydrogens else ' '} "
        f"and rushed to tell {journal} about their great triumph, finding their way to page {page} "
        f"in a work titled \"{title}\".{resolution_passage}"
    )

    generator_prompt = create_generator_prompt(residue_counts)

    return description, generator_prompt
    

def create_generator_prompt(residue_counts: dict[str, int]) -> str:
    sorted_residues_with_counts = sorted(list(residue_counts.items()), key=lambda x: x[1], reverse=True)
    most_common_resname = None
    most_common_count = 0
    has_residue_types = set()
    n_biopolymer_residues = 0
    for resname, cnt in sorted_residues_with_counts:
        resname, residue_type = resolve_common_name(resname)
        if resname in pmd.residue.WATER_NAMES:
            continue
        if resname in pmd.residue.ALLION_NAMES:
            continue
        n_biopolymer_residues += 1
        has_residue_types.add(residue_type)
        if most_common_resname is None:
            most_common_resname = resname
            most_common_count = cnt

    has_residue_types -= {None}

    if len(has_residue_types) == 1:
        descriptor = f"The {has_residue_types.pop()}"
    elif len(has_residue_types) > 1:
        parts = []
        while has_residue_types:
            parts.append(f"part-{has_residue_types.pop()}")
        descriptor = f"The {', '.join(parts)}"
    elif not has_residue_types:
        descriptor = f"The wonky biomolecule"

    return (
        f"{descriptor}, with its {n_biopolymer_residues} biopolymer residues, at least "
        f"{most_common_count} of them {most_common_resname}, would move like "
    )


def resolve_common_name(resname: str) -> tuple[str, Optional[str]]:
    try:
        return pmd.residue.AminoAcidResidue.get(resname).name, "protein"
    except KeyError:
        pass

    try:
        return pmd.residue.DNAResidue.get(resname).name, "DNA"
    except KeyError:
        pass

    try:
        return pmd.residue.RNAResidue.get(resname).name, "RNA"
    except KeyError:
        pass

    return resname, None