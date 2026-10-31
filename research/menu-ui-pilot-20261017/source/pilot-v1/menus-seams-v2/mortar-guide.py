from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
p=Path(__file__).resolve().parent;center=Image.open(p.parent/'menus-v1/jukebox-center.png').convert('RGB');arr=np.array(center).astype(float)
for side in ['left','right']:
 # Average a narrow source strip; gray mortar is less red than brown bricks.
 a=arr[:,:32] if side=='left' else arr[:,-32:];gray=(a[:,:,2]-.5*a[:,:,0]-.5*a[:,:,1]).mean(1);profile=np.convolve(gray,np.ones(11)/11,'same');peaks=[]
 for lo,hi in [(30,150),(210,350),(420,550),(610,760),(810,960),(1010,1160),(1210,1360)]:peaks.append(lo+int(np.argmax(profile[lo:hi])))
 im=Image.new('RGB',(500,1440));im.paste(center.crop((0,0,200,1440)) if side=='left' else center.crop((1720,0,1920,1440)),(0,0));d=ImageDraw.Draw(im)
 for y in peaks:d.line((0,y,499,y),fill='cyan',width=2);d.text((210,y+3),str(y),fill='white')
 im.save(p/('jukebox-'+side+'-mortar-probe.png'));print(side,peaks)
