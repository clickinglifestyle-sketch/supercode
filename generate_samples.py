"""Generate sample still frames showing different visual styles."""
import math
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import sys
sys.path.insert(0, '/home/user/supercode')

F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SANS  = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
F_BOLD  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
OUT     = Path("/home/user/supercode/output/samples")
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 608   # 16:9 preview size
rng  = np.random.default_rng(7)

def font(p, s): return ImageFont.truetype(p, s)
def clamp(v):   return max(0.0, min(1.0, v))

def radial(center, edge, power=2.0):
    y = np.linspace(-1,1,H)[:,None]*(H/W)
    x = np.linspace(-1,1,W)[None,:]
    d = np.sqrt(x**2+y**2)
    t = np.clip(d/1.4,0,1)[:,:,None]**power
    return np.array(center,dtype=np.float32)*(1-t)+np.array(edge,dtype=np.float32)*t

def glow(arr,fx,fy,fr,col,intensity):
    px,py = fx*W, fy*H
    r = fr*min(W,H)
    y = np.arange(H)[:,None].astype(np.float32)
    x = np.arange(W)[None,:].astype(np.float32)
    d = np.sqrt((x-px)**2+(y-py)**2)
    mask = np.clip(1-d/r,0,1)[:,:,None]**1.8
    return arr + mask*np.array(col,dtype=np.float32)*intensity

def particles(arr,seed,n,col,size=2.5,intensity=0.7):
    rs = np.random.RandomState(seed)
    px=rs.uniform(0,W,n); py=rs.uniform(0,H,n)
    alphas=rs.uniform(0.2,0.6,n); sizes=rs.uniform(1.2,size,n)
    out=arr.copy(); c=np.array(col,dtype=np.float32)
    for i in range(n):
        ix,iy=int(px[i]),int(py[i]); r=int(sizes[i]*4)+1
        x0,x1=max(0,ix-r),min(W,ix+r); y0,y1=max(0,iy-r),min(H,iy+r)
        yy,xx=np.ogrid[y0:y1,x0:x1]
        d=np.sqrt((xx-px[i])**2+(yy-py[i])**2)
        mask=np.clip(1-d/sizes[i],0,1)[:,:,None]**1.5
        out[y0:y1,x0:x1]+=mask*c*alphas[i]*intensity*255
    return out

def vignette(arr, strength=0.65):
    y=np.linspace(-1,1,H)[:,None]; x=np.linspace(-1,1,W)[None,:]
    d=np.sqrt(x**2+(y*1.5)**2)
    v=np.clip(d**2.4*strength,0,1)[:,:,None]
    return arr*(1-v)

def grain(arr, intensity=0.028):
    noise=rng.normal(0,intensity*255,arr.shape)
    return np.clip(arr+noise,0,255)

def finalize(arr):
    arr=vignette(arr); arr=grain(arr)
    return np.clip(arr,0,255).astype(np.uint8)

def cx(draw,text,fn,y,col,alpha=255):
    w=draw.textlength(text,font=fn)
    draw.text(((W-w)/2,y),text,font=fn,fill=(*col,alpha))

def hline(draw,y,w,col,alpha=255):
    x0=(W-w)//2
    draw.rectangle([(x0,y),(x0+w,y+1)],fill=(*col,alpha))


# ── Sample 1: Amber particles / hook text ────────────────────────────────────
arr = radial((6,10,24),(2,2,6),power=1.8)
arr = glow(arr,0.12,0.18,0.42,(160,65,8),0.28)
arr = glow(arr,0.5,0.9,0.55,(15,8,35),0.30)
arr = particles(arr,seed=1,n=55,col=(210,145,50),size=2.8,intensity=0.55)
arr = particles(arr,seed=7,n=25,col=(255,200,100),size=1.6,intensity=0.35)
arr = finalize(arr)
img = Image.fromarray(arr).convert("RGBA")
draw = ImageDraw.Draw(img)
cx(draw,"He operated in plain sight.",font(F_SERIF,52),H//2-30,(240,240,240))
cx(draw,"For 15 years.",font(F_SERIF,38),H//2+38,(200,200,200),180)
draw.rectangle([(0,0),(W,3)],fill=(196,30,58,255))
draw.rectangle([(0,H-3),(W,H)],fill=(196,30,58,255))
img.convert("RGB").save(OUT/"01_amber_particles.jpg",quality=92)
print("✓ Sample 1")

# ── Sample 2: Blood-red radial ────────────────────────────────────────────────
arr = radial((18,3,3),(55,6,6),power=2.2)
arr = glow(arr,0.5,0.5,0.7,(90,8,8),0.55)
arr = glow(arr,0.15,0.3,0.35,(140,15,15),0.30)
arr = finalize(arr)
img = Image.fromarray(arr).convert("RGBA")
draw = ImageDraw.Draw(img)
hline(draw,H//2-52,360,(196,30,58))
cx(draw,"With the full knowledge",font(F_SERIF,50),H//2-40,(240,240,240))
cx(draw,"of those in power.",font(F_SERIF,50),H//2+26,(240,240,240))
draw.rectangle([(0,0),(W,3)],fill=(196,30,58,255))
draw.rectangle([(0,H-3),(W,H)],fill=(196,30,58,255))
img.convert("RGB").save(OUT/"02_blood_red.jpg",quality=92)
print("✓ Sample 2")

# ── Sample 3: Silver backlit bloom ───────────────────────────────────────────
arr = radial((22,20,20),(2,2,2),power=3.5)
arr = glow(arr,0.5,0.5,0.55,(255,250,240),0.42)
arr = glow(arr,0.5,0.42,0.28,(255,255,255),0.20)
arr = glow(arr,0.18,0.48,0.12,(255,240,200),0.18)
arr = glow(arr,0.78,0.52,0.10,(200,220,255),0.14)
arr = finalize(arr)
img = Image.fromarray(arr).convert("RGBA")
draw = ImageDraw.Draw(img)
cx(draw,"JEFFREY EPSTEIN",font(F_SERIF,96),H//2-60,(240,240,240))
hline(draw,H//2+52,520,(180,180,190),120)
cx(draw,"FINANCIER   ·   1953 – 2019",font(F_SANS,24),H//2+64,(150,140,135))
draw.rectangle([(0,0),(W,3)],fill=(196,30,58,255))
draw.rectangle([(0,H-3),(W,H)],fill=(196,30,58,255))
img.convert("RGB").save(OUT/"03_backlit_bloom.jpg",quality=92)
print("✓ Sample 3")

# ── Sample 4: Red interrogation side-light ───────────────────────────────────
y_grad=np.linspace(0,1,H)[:,None,None]
arr = np.array((8,6,6),dtype=np.float32)*(1-y_grad)+np.array((4,4,12),dtype=np.float32)*y_grad
arr = arr*np.ones((1,W,1))
arr = glow(arr,1.05,0.5,0.65,(190,20,10),0.75)
arr = glow(arr,0.05,0.5,0.40,(10,15,40),0.25)
arr = finalize(arr)
img = Image.fromarray(arr).convert("RGBA")
draw = ImageDraw.Draw(img)
draw.rectangle([(0,0),(5,H)],fill=(196,30,58,255))
cx(draw,"Trafficker.",font(F_SERIF,70),H//2-100,(240,240,240))
cx(draw,"Untouchable.",font(F_SERIF,70),H//2-10,(240,240,240))
cx(draw,"Protected.",font(F_SERIF,70),H//2+80,(196,30,58))
draw.rectangle([(0,0),(W,3)],fill=(196,30,58,255))
draw.rectangle([(0,H-3),(W,H)],fill=(196,30,58,255))
img.convert("RGB").save(OUT/"04_interrogation.jpg",quality=92)
print("✓ Sample 4")

# ── Sample 5: Explosive red burst ────────────────────────────────────────────
arr = radial((220,12,12),(8,2,2),power=0.9)
arr = glow(arr,0.5,0.5,0.9,(255,40,20),0.88)
arr = glow(arr,0.5,0.5,0.4,(255,180,60),0.50)
arr = glow(arr,0.5,0.5,0.2,(255,255,200),0.25)
arr = particles(arr,seed=5,n=35,col=(255,150,50),size=2.2,intensity=0.45)
arr = finalize(arr)
img = Image.fromarray(arr).convert("RGBA")
draw = ImageDraw.Draw(img)
cx(draw,"UNTIL NOW.",font(F_SERIF,110),H//2-65,(255,255,255))
draw.rectangle([(0,0),(W,3)],fill=(196,30,58,255))
draw.rectangle([(0,H-3),(W,H)],fill=(196,30,58,255))
img.convert("RGB").save(OUT/"05_red_burst.jpg",quality=92)
print("✓ Sample 5")

# ── Sample 6: Brand / closing card ───────────────────────────────────────────
arr = radial((12,4,4),(1,1,1),power=2.5)
arr = glow(arr,0.5,0.5,0.5,(150,15,15),0.35)
arr = finalize(arr)
img = Image.fromarray(arr).convert("RGBA")
draw = ImageDraw.Draw(img)
cx(draw,"FINALLY SOLVED",font(F_BOLD,56),H//2-38,(196,30,58))
hline(draw,H//2+30,400,(80,80,80),180)
cx(draw,"THE SYSTEM KNEW",font(F_BOLD,28),H//2+44,(100,95,95))
draw.rectangle([(0,0),(W,3)],fill=(196,30,58,255))
draw.rectangle([(0,H-3),(W,H)],fill=(196,30,58,255))
img.convert("RGB").save(OUT/"06_brand.jpg",quality=92)
print("✓ Sample 6")

print(f"\nAll samples saved to {OUT}")
