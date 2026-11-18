"""Builds the README visuals (banner, KPI strip, divider). Run after build_charts.py:  python Report/build_readme_assets.py"""
import os, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, Rectangle
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..")); AS=os.path.join(ROOT,"assets")
for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf","/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf","/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf","/usr/share/fonts/truetype/google-fonts/Poppins-Light.ttf"]:
    if os.path.exists(f): fm.fontManager.addfont(f)
GREEN,YEL,BLUE,NAVY="#009739","#FEDD00","#1F6FD1","#0B2A5B"

# ---------------- banner (1600 x 430)
geo=pd.read_csv(os.path.join(ROOT,"Data","olist_geolocation_dataset.csv")).drop_duplicates()
geo=geo[geo.geolocation_lat.between(-34,5.5)&geo.geolocation_lng.between(-74,-34)]
W,H=1600,430; fig=plt.figure(figsize=(W/100,H/100),dpi=100); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,W); ax.set_ylim(0,H); ax.axis("off")
grad=np.linspace(0,1,256).reshape(1,-1); ax.imshow(grad,extent=[0,W,0,H],aspect="auto",cmap=matplotlib.colors.LinearSegmentedColormap.from_list("b",["#081C40","#0B2A5B","#12408A"]),zorder=0)
# map silhouette on the right
lng=geo.geolocation_lng.values; lat=geo.geolocation_lat.values
sx=(lng+74)/(74-34)*330+1130; sy=(lat+34)/(5.5+34)*360+35
ax.scatter(sx,sy,s=.5,c="#7FD6A0",alpha=.55,linewidths=0,zorder=1)
ax.scatter(sx[(lat<-22)&(lat>-25)&(lng>-49)&(lng<-45)],sy[(lat<-22)&(lat>-25)&(lng>-49)&(lng<-45)],s=.6,c=YEL,alpha=.8,linewidths=0,zorder=2)
ax.text(70,300,"Olist E-Commerce",fontsize=50,fontfamily="Poppins",fontweight="bold",color="white",va="center")
ax.text(72,230,"Sales · Customers · Products · Delivery · Payments · Sellers",fontsize=23,fontfamily="Poppins",color="#CFE3FF",va="center")
ax.text(72,168,"A Python data-analysis case study on the Brazilian marketplace  |  Sep 2016 – Oct 2018",fontsize=17,fontfamily="Carlito",color="#9DB8E3",va="center")
for i,(t,c) in enumerate([("Python",GREEN),("Pandas",BLUE),("Matplotlib",YEL),("Seaborn",GREEN),("Jupyter",BLUE)]):
    x=72+i*152; ax.add_patch(FancyBboxPatch((x,70),136,40,boxstyle="round,pad=0,rounding_size=20",fc=c,ec="none",alpha=.95,zorder=3))
    ax.text(x+68,90,t,ha="center",va="center",fontsize=15,fontfamily="Poppins",fontweight="bold",color="#10213D" if c==YEL else "white",zorder=4)
for k,(c,w) in enumerate([(GREEN,W*.5),(YEL,W*.3),(BLUE,W*.2)]):
    ax.add_patch(Rectangle((sum([W*.5,W*.3][:k]),0),w,12,fc=c,ec="none",zorder=5))
fig.savefig(os.path.join(AS,"banner.png"),dpi=100); plt.close(fig)

# ---------------- KPI strip (1600 x 190)
kp=[("99,441","orders",NAVY),("R$ 13.2M","delivered product sales",GREEN),("96,096","unique customers",BLUE),("12.6 days","avg delivery time","#E4572E"),("8.1%","late-delivery rate","#F2A900"),("4.09 / 5","avg review score","#7A4EAB")]
fig=plt.figure(figsize=(16,1.9),dpi=100); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,1600); ax.set_ylim(0,190); ax.axis("off")
cw=250; gap=20; x0=(1600-(6*cw+5*gap))/2
for i,(v,l,c) in enumerate(kp):
    x=x0+i*(cw+gap); ax.add_patch(FancyBboxPatch((x,15),cw,160,boxstyle="round,pad=0,rounding_size=14",fc="#F5F7FA",ec="#DDE3EA",lw=1.5))
    ax.add_patch(Rectangle((x+14,15),cw-28,7,fc=c,ec="none"))
    ax.text(x+cw/2,108,v,ha="center",va="center",fontsize=26,fontfamily="Poppins",fontweight="bold",color=c)
    ax.text(x+cw/2,56,l,ha="center",va="center",fontsize=13.5,fontfamily="Carlito",color="#374151")
fig.savefig(os.path.join(AS,"kpi_strip.png"),dpi=100,transparent=False,facecolor="white"); plt.close(fig)

# ---------------- divider (1600 x 10)
fig=plt.figure(figsize=(16,.1),dpi=100); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,1600); ax.set_ylim(0,10); ax.axis("off")
for k,(c,w) in enumerate([(GREEN,800),(YEL,480),(BLUE,320)]): ax.add_patch(Rectangle((sum([800,480][:k]),0),w,10,fc=c,ec="none"))
fig.savefig(os.path.join(AS,"divider.png"),dpi=100); plt.close(fig)
print("ok")
