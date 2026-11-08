"""Assemble a local ordinary roster from sealed component-export receipts.

Legacy native identifiers stay conversion metadata. The runtime sees only the
ordinary registry and typed appearance, artwork, voice and animation resources.
This operation neither installs nor publishes the result.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import struct
import tempfile

from .fighter_pack import ordinary,contract,extract


def document(path):
    path=ordinary(path)
    if path.stat().st_size>32*1024**2:raise ValueError('Conversion report exceeds budget')
    return json.loads(path.read_text(encoding='utf-8'))


def convert_roster(recomp,game,source,accounting,motion,portrait_report,voice_root,pair_root,film_root,portrait_root,destination):
    source=ordinary(source);destination=ordinary(destination)
    game=Path(game).resolve(strict=True)  # Explicit read-only game junction, as in contract().
    if destination.exists():raise ValueError('Conversion destination already exists')
    accounting,motion,portrait_report=map(document,(accounting,motion,portrait_report))
    if accounting.get('schema')!='fighter-conversion-source-accounting-1' or motion.get('schema')!='fighter-conversion-motion-audit-1':
        raise ValueError('Conversion requires explicit source accounting and motion audit receipts')
    source_files={row['path']:row for row in accounting['files']}
    actual={p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
    if actual!=source_files.keys():raise ValueError('Source population changed since accounting')
    for relative,row in source_files.items():
        path=ordinary(source/relative)
        if not path.is_relative_to(source) or path.stat().st_size!=row['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('Source changed since accounting: '+relative)
    actors={row['source_core']:row for row in motion['fighters']}
    portraits={row['source_core']:row for row in portrait_report['rows']}
    choices={}
    for role in motion['roles']:
        for owner in role['owners']:
            key=(int(owner['fighter'].rsplit('-',1)[1]),owner['slot'])
            if key in choices and choices[key]!=role['source_choice']:raise ValueError('Ambiguous source slot ownership')
            choices[key]=role['source_choice']
    activations={}
    for line in (source/'blazin_activation.txt').read_text().splitlines():
        words=line.split('#',1)[0].split()
        if words:
            if len(words) not in (3,4) or int(words[0]) in activations:raise ValueError('Ambiguous source activation mapping')
            activations[int(words[0])]=words[1:3]
    destination.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.fighter-conversion-',dir=destination.parent) as temporary:
        stage=Path(temporary)/'pack';stage.mkdir()
        identifier='vendetta-roster';pack={'schema':'fighter-registry-draft-1','id':identifier,'version':'1.0.0',
            'requires':{},'overrides':[],'fighters':[],'resources':[]}
        resources={};mapping=[]
        tag_catalog=contract(recomp,game,'tag-catalog')['rows']
        def asset(data,relative):
            path=stage/relative;path.parent.mkdir(parents=True,exist_ok=True)
            if path.exists() and path.read_bytes()!=data:raise ValueError('Conflicting converted file: '+relative)
            path.write_bytes(data);return {'path':relative,'sha256':hashlib.sha256(data).hexdigest()}
        def refs(value,folder,prefix):
            value=deepcopy(value);folder=ordinary(folder)
            def visit(node):
                if type(node) is dict:
                    if set(node)>={'path','sha256'}:
                        path=ordinary(folder/node['path'])
                        if not path.is_relative_to(folder):raise ValueError('Export file escapes its component folder')
                        data=path.read_bytes()
                        if hashlib.sha256(data).hexdigest()!=node['sha256']:raise ValueError('Export file changed: '+str(path))
                        node.update(asset(data,prefix+'/'+node['path']))
                    else:
                        for child in node.values():visit(child)
                elif type(node) is list:
                    for child in node:visit(child)
            visit(value);return value
        def resource(local,kind,compatibility,spec):
            entry={'id':local,'kind':kind,'compatibility':compatibility,'source':spec}
            if local in resources and resources[local]!=entry:raise ValueError('Conflicting shared conversion resource')
            resources[local]=entry;return identifier+'/'+local
        for actor in accounting['fighters']:
            core=actor['source_core'];local=actor['stable_key'].split('/',1)[1];donor=actor['donor'];family='retail/binding-'+donor.split('/')[1]
            if actor['stable_key']!=identifier+'/'+local or core not in actors:raise ValueError('Stable mapping differs from conversion receipts')
            model=actors[core]['model'];compat={'skeleton':family,'events':family}
            appearance={'format':'eagl-appearance-1','donor':donor}
            for role,suffix in (('model','.o'),('textures','.xsh'),('face','_F.o')):
                appearance[role]=asset((source/'assets/v2ip'/(model+suffix)).read_bytes(),'appearance/'+local+'/'+role+'.bin')
            tier=actor['source_tier']
            if type(tier) is not int or tier not in (1,2,4,8):raise ValueError('Source roster tier is unproved')
            components={'appearance':resource('appearance-'+local,'appearance',{'skeleton':family},appearance),
                        'stats':actor['source_stats'],'tier':tier}
            portrait=refs(document(Path(portrait_root)/str(core)/'portrait-source.json'),Path(portrait_root)/str(core),'portraits/'+local)
            if not portraits[core]['passed'] or len(portraits[core]['inputs'])!=24:raise ValueError('All24artwork roles require successful receipts')
            for part,info in portraits[core]['inputs'].items():
                if portrait[part]['sha256']!=info['texture_sha256']:raise ValueError('Portrait export differs from its source raster receipt')
            components['portrait']=resource('portrait-'+local,'portrait',{},portrait)
            voice=actor['source_voice']
            if voice>=600:
                voice_spec=refs(document(Path(voice_root)/str(voice)/'voice-source.json'),Path(voice_root)/str(voice),'voices/'+str(voice))
                components['voice']=resource('voice-'+str(voice)+'-'+donor.split('/')[1],'voice',{'events':family},voice_spec)
            elif actor['components']['voice']!='exactly-inherited':raise ValueError('Unproved inherited source voice')
            shots=[]
            for phase,token in enumerate([activations[core][0]]+[activations[core][1]]*3):
                fragment=refs(document(Path(film_root)/token/'cinematic-source.json'),Path(film_root)/token,'cinematics/'+token)
                fragment['template']=f'BT{phase+1}_01' if phase<3 else 'BT4C01'
                fragment['camera_policy']='native-venue' if phase==3 else 'owned-relative';fragment.pop('format',None);shots.append(fragment)
            blazin={'format':'fighter-blazin-5','shots':shots,'slots':{},'retail_slots':{}}
            for slot in range(4):
                if (core,slot) not in choices:
                    choice=actors[core]['slots'][slot]
                    if type(choice) is not int or not 0<=choice<82:raise ValueError('Unaccounted source finisher slot')
                    blazin['retail_slots'][str(slot)]=choice
                    continue
                choice=choices[(core,slot)];folder=Path(pair_root)/str(choice)
                fragment=document(folder/'pair-source.json')
                pair_report=document(folder/'pair-export.json')
                for role in ('subject','counterpart'):
                    target=pair_report['roles'][role]['source_token']
                    if target in tag_catalog:
                        timeline=refs(fragment[role+'_tags'],folder,'pairs/timelines/'+str(choice))
                        spec={'format':'fighter-tag-override-1','target':target,
                              'template':pair_report['roles'][role]['template_token'],'original_sha256':tag_catalog[target],
                              'timeline':timeline}
                        resource('tag-'+target.lower().replace('_','-'),'tag-override',{},spec)
                for role in ('subject','counterpart'):
                    descriptor=fragment[role];data=(folder/descriptor['path']).read_bytes()
                    if hashlib.sha256(data).hexdigest()!=descriptor['sha256']:raise ValueError('Pair export changed')
                    graph=json.loads(data);graph['rig_sha256']=actors[core]['context']['rig_sha256']
                    encoded=(json.dumps(graph,separators=(',',':'))+'\n').encode()
                    fragment[role]=asset(encoded,'pairs/'+graph['rig_sha256'][:16]+'/'+str(choice)+'/'+role+'.json')
                # Only timeline descriptors remain relative to the export folder.
                tail=refs({k:v for k,v in fragment.items() if k not in ('subject','counterpart')},folder,'pairs/timelines/'+str(choice))
                fragment.update(tail);blazin['slots'][str(slot)]=fragment
            components['blazin']=resource('blazin-'+local,'blazin',compat,blazin)
            for category,prefix in (('intro','CI_'),('victory','CE_')):
                token=prefix+model.removeprefix('V2IP_');folder=Path(film_root)/token
                spec=refs(document(folder/'cinematic-source.json'),folder,'cinematics/'+token)
                components[category]=resource(category+'-'+local,'cinematic',compat,spec)
            pack['fighters'].append({'id':local,'name':actor['display_name'],'inherits':donor,'components':components})
            mapping.append({**actor,'components':components})
        # Source-native appearance edits outside the added roster are explicit
        # ordinary component overrides, never silently discarded global files.
        added_models={row['model'] for row in actors.values()}
        extras=[row for row in source_files.values() if row['path'].startswith('assets/v2ip/')
                and row['path'].endswith('.o') and not row['path'].endswith('_F.o')
                and Path(row['path']).stem not in added_models and row['status']!='exactly-inherited']
        native_models=contract(recomp,game,'catalog')['native_models'] if extras else {}
        shape_number=0
        for row in extras:
            model=Path(row['path']).stem
            if model not in native_models:raise ValueError('Extra source appearance needs an explicit consumer mapping: '+model)
            donor=native_models[model];local='retail-'+donor.split('/')[1];family='retail/binding-'+donor.split('/')[1]
            spec={'format':'eagl-appearance-1','donor':donor,
                  'model':asset((source/row['path']).read_bytes(),'appearance/'+local+'/model.bin')}
            for role,suffix in (('textures','.xsh'),('face','_F.o')):
                path=Path(temporary)/(local+suffix);extract(Path(game)/'assets/v2ip.viv',model+suffix,path)
                spec[role]=asset(path.read_bytes(),'appearance/'+local+'/'+role+'.bin')
                if role=='textures':
                    texture=path.read_bytes()
                    if texture[:4]!=b'SHPX':raise ValueError('Inherited texture is not SHPX')
                    count,=struct.unpack_from('<I',texture,8)
                    if not 0<count<=4096 or 16+8*count>len(texture):raise ValueError('Inherited texture directory exceeds budget')
                    names=[texture[16+8*i:20+8*i].decode('ascii') for i in range(count)]
                    if shape_number+len(names)>4096:raise ValueError('Explicit converted texture name range exhausted')
                    spec.update(format='eagl-appearance-2',shape_names={name:f'Z{shape_number+i:03X}' for i,name in enumerate(sorted(names))})
                    shape_number+=len(names)
            key=resource('appearance-'+local,'appearance',{'skeleton':family},spec)
            pack['overrides'].append({'target':donor,'components':{'appearance':key},'supersedes':[]})
        pack['resources']=[resources[key] for key in sorted(resources)]
        (stage/'fighters.json').write_text(json.dumps(pack,indent=2)+'\n',encoding='utf-8')
        (stage/'README.txt').write_text('Local ordinary fighter conversion. Native acceptance and release approval are separate. Activation phase4 preserves the native venue-camera policy; supplied unused camera helpers remain in the typed graph.\n',encoding='utf-8')
        report=contract(recomp,game,'validate',[stage])
        # Recheck immutable source inputs before publishing the new folder.
        for relative,row in source_files.items():
            if hashlib.sha256((source/relative).read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Source changed during conversion')
        destination.mkdir()
        for path in stage.rglob('*'):
            target=destination/path.relative_to(stage)
            if path.is_dir():target.mkdir(exist_ok=True)
            else:shutil.copyfile(path,target)
    return {'schema':'fighter-ordinary-conversion-1','pack':str(destination),'fighters':len(mapping),
            'resources':len(resources),'mapping':mapping,'validation':report,'native_playtest':False,'published':False}
