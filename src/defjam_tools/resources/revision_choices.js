// Shared by both viewers. Filtering history must not change a saved comparison
// or hide an approved/selected revision. This does not grant review approval.
export function visibleCandidates(candidates,{showArchived=false,pinned=[]}={}) {
  const keep=new Set(pinned);
  return candidates.filter(c=>showArchived||!c.review?.tags?.includes('archived')||
    keep.has(c.id)||c.review?.status==='approved'||c.review?.selected===true);
}
export function chooseRevision(ids,wanted,fallback='') {
  return ids.includes(wanted)?wanted:(ids.includes(fallback)?fallback:'');
}
