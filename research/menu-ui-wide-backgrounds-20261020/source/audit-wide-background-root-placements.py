#!/usr/bin/env python3
"""Offline APT parent-placement audit for seven named widescreen backgrounds."""
from pathlib import Path
import contextlib, io, json, runpy

REPO=Path('/Users/vlad/.codex/worktrees/01c5/DefJamFFNY-recomp')
with contextlib.redirect_stdout(io.StringIO()):
    d=runpy.run_path(str(REPO/'logs/ui-restoration-20261017/uv-audit/audit_pilot_uv.py'))
apt=d['apt']
TARGETS={
 'screens/story/choosGF2.big':[17,31],
 'screens/story/choosGF4.big':[3],
 'screens/story/choosPart.big':[3],
 'screens/story/charDec.big':[3],
 'screens/options/cribOptions.big':[5,9],
 'screens/battle/matchLoa.big':[2,10],
 'screens/battle/tips.big':[3],
}

def compose(p,c):
    # APT matrix [a,b,c,d,tx,ty]: parent * child.
    a,b,cc,dd,tx,ty=p; e,f,g,h,u,v=c
    return [a*e+cc*f,b*e+dd*f,a*g+cc*h,b*g+dd*h,a*u+cc*v+tx,b*u+dd*v+ty]

def relevant_events(frames):
    out=[]
    for fi,frame in enumerate(frames):
        for op,val in frame:
            if op in ('PlaceObject','RemoveObject'):
                out.append(dict(frame=fi,event=op,depth=val.get('depth'),character=val.get('character'),
                    name=val.get('name'),flags=val.get('flags'),matrix=list(val['matrix']) if val.get('matrix') else None,
                    clip_depth=val.get('clip_depth')))
    return out

def display_states(frames):
    """Apply authored display-list changes so each frame's live child set is explicit."""
    state={}; output=[]
    for fi,frame in enumerate(frames):
        for op,val in frame:
            dep=val.get('depth')
            if op=='RemoveObject': state.pop(dep,None)
            elif op=='PlaceObject':
                flags=val.get('flags',0); old=state.get(dep,{})
                new=dict(old)
                if flags & 2: new['character']=val.get('character')
                if flags & 4: new['matrix']=list(val.get('matrix') or (1,0,0,1,0,0))
                elif not (flags & 1) and dep not in state: new['matrix']=[1,0,0,1,0,0]
                if flags & 32: new['name']=val.get('name')
                if flags & 64: new['clip_depth']=val.get('clip_depth')
                new['depth']=dep; state[dep]=new
        output.append(dict(frame=fi,objects=[dict(v) for _,v in sorted(state.items())]))
    return output

def filtered_events(frames, wanted_depths):
    out=[]
    for fi,frame in enumerate(frames):
        for op,val in frame:
            if op in ('PlaceObject','RemoveObject') and val.get('depth') in wanted_depths:
                out.append(dict(frame=fi,event=op,depth=val.get('depth'),character=val.get('character'),
                    name=val.get('name'),flags=val.get('flags'),matrix=list(val['matrix']) if val.get('matrix') else None,
                    clip_depth=val.get('clip_depth')))
    return out

def target_depth_states(states, depths):
    return [dict(frame=s['frame'],objects=[o for o in s['objects'] if o['depth'] in depths]) for s in states]

def chains_from(target_ids, chars, main_frames):
    paths=[]
    def walk(parent_id, frames, path, parent_matrix, stack):
        if parent_id in stack: return
        for fi,frame in enumerate(frames):
            # Use authored PlaceObject events. APT display-list snapshots are also retained
            # at root; this preserves all source frame changes without guessing runtime state.
            for op,val in frame:
                if op!='PlaceObject' or val.get('character') is None: continue
                child=val['character']; mat=list(val.get('matrix') or (1,0,0,1,0,0))
                node=dict(parent_character=parent_id,parent_frame=fi,depth=val.get('depth'),
                          child_character=child,name=val.get('name'),local_matrix=mat,
                          clip_depth=val.get('clip_depth'))
                if child in target_ids:
                    paths.append(dict(chain=path+[node],effective_matrix=compose(parent_matrix,mat)))
                elif child<len(chars) and chars[child]['type']=='Sprite':
                    walk(child,chars[child].get('frames',[]),path+[node],compose(parent_matrix,mat),stack|{parent_id})
    walk(0,main_frames,[],[1,0,0,1,0,0],set())
    return paths

results=[]
for entry, targets in TARGETS.items():
    data,_,movie,chars,_=apt.load_movie('screens/screens.viv',entry)
    chosen={i:dict(character=i,type=chars[i]['type'],offset=chars[i]['offset']) for i in targets}
    paths=chains_from(set(targets),chars,movie['frames'])
    sprite_depths={}
    root_depths=set()
    for p in paths:
        for n in p['chain']:
            if n['parent_character']==0: root_depths.add(n['depth'])
            elif chars[n['parent_character']]['type']=='Sprite':
                sprite_depths.setdefault(n['parent_character'],set()).add(n['depth'])
    needed_sprites=sorted(sprite_depths)
    states=display_states(movie['frames'])
    results.append(dict(resource=entry,stage=[movie['screen_width'],movie['screen_height']],
      root_frame_count=len(movie['frames']),target_shapes=chosen,
      target_paths=paths,
      root_place_remove_events=relevant_events(movie['frames']),
      root_first_frame_display_list=states[0]['objects'] if states else [],
      target_root_display_states=target_depth_states(states,root_depths),
      target_parent_sprite_place_remove_events={str(i):filtered_events(chars[i].get('frames',[]),sprite_depths[i]) for i in needed_sprites}))

out={'schema':1,'method':"APT character graph and 2D matrix composition from the owner's archive; path matrices are source-authored local placement transforms composed parent-to-child. This does not infer loader transforms, active state, or viewport exposure.",'resources':results}
path=REPO/'logs/ui-restoration-20261020/wide-background-root-placements.json'
path.write_text(json.dumps(out,indent=2)+'\n')
print(path)
for r in results:
 print(r['resource'], 'stage',r['stage'],'rootFrames',r['root_frame_count'],'paths',len(r['target_paths']))
 for p in r['target_paths']:
  print(' ',[ (n['parent_character'],n['parent_frame'],n['depth'],n['child_character'],n['name'],n['local_matrix']) for n in p['chain'] ],'effective',p['effective_matrix'])
