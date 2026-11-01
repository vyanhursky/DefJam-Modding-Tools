// Navigation is a view of the original immutable outfit selections. No new
// wardrobe IDs are persisted into saved outfits or inspection records.
export function sameSelection(a,b){
  return Boolean(a&&b&&a.item===b.item&&a.style===b.style&&a.color===b.color);
}
export function findSelection(rows,selected,preferredId=null){
  const ordered=preferredId?[...rows.filter(r=>r.id===preferredId),...rows.filter(r=>r.id!==preferredId)]:rows;
  for(const garment of ordered)for(const color of garment.colors)for(const fitting of color.fittings){
    if([fitting.selection,...(fitting.aliases||[])].some(s=>sameSelection(selected,s)))return {garment,color,fitting};
  }
  return null;
}
export function chooseSelection(garment,colorId=null,fittingId=null){
  const color=garment.colors.find(c=>c.id===colorId)||garment.colors[0];
  if(!color)return null;
  const fitting=color.fittings.find(f=>f.id===fittingId)||color.fittings[0];
  return fitting?{garment,color,fitting}:null;
}
export function selectionForChoice(choice,previous){
  const current=findSelection([choice.garment],previous);
  // Inspection of an active choice must not canonicalize a saved XML alias.
  return current?.color.id===choice.color.id&&current?.fitting.id===choice.fitting.id?previous:choice.fitting.selection;
}
