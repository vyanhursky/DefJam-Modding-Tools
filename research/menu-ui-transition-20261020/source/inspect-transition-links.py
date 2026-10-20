import contextlib,io,runpy,struct
with contextlib.redirect_stdout(io.StringIO()):d=runpy.run_path('logs/ui-restoration-20261017/uv-audit/audit_pilot_uv.py')
h=d['hd_assets'];inn=dict(h.archive_entries(h.unpack_refpack(d['outer']['screens/trans/t1.big'])));data,symbols,rels,_=d['object_info'](inn['t1.o'])
for part in range(10):
 name=f'__RM:::__GP_RM_11_{part}';a=symbols[name]['offset'];print(name,hex(a),symbols[name]['size']);print([(hex(k-a),v) for k,v in rels.items() if a<=k<a+0x70]);print('words',[hex(v) for v in struct.unpack_from('<28I',data,a)])
print('vertexobjects')
for n,s in symbols.items():
 if '__GPvb_9_' in n:print(n,hex(s['offset']),[hex(v) for v in struct.unpack_from('<5I',data,s['offset'])])
