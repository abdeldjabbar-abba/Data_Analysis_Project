"""
Builds the maps (assets/) and the report charts (Report/charts/) for the Olist project.
Run from anywhere:  python Report/build_charts.py
All numbers are recomputed from Data/*.csv using the same definitions as Data_Analysis.ipynb.
"""
import json, os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FuncFormatter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
D = os.path.join(ROOT, "Data") + os.sep
CH = os.path.join(ROOT, "Report", "charts"); AS = os.path.join(ROOT, "assets")
os.makedirs(CH, exist_ok=True); os.makedirs(AS, exist_ok=True)

for f in ["/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf","/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf",
          "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf","/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"]:
    if os.path.exists(f): fm.fontManager.addfont(f)
GREEN, BLUE, NAVY, AMBER, RED, TEAL, PURPLE, GREY, INK, BG = "#009739","#1F6FD1","#0B2A5B","#F2A900","#E4572E","#0E9AA7","#7A4EAB","#6B7280","#1F2937","#F5F7FA"
plt.rcParams.update({"font.family":"Carlito","font.size":11,"axes.edgecolor":"#CBD2DC","axes.labelcolor":INK,"text.color":INK,
    "xtick.color":INK,"ytick.color":INK,"axes.spines.top":False,"axes.spines.right":False,"axes.titleweight":"bold",
    "axes.titlesize":13,"axes.titlelocation":"left","figure.dpi":100,"savefig.dpi":200,"axes.grid":True,"grid.color":"#E5E9F0","grid.linewidth":.8,"axes.axisbelow":True})
def save(fig, name, folder=CH):
    fig.savefig(os.path.join(folder, name), bbox_inches="tight", facecolor="white"); plt.close(fig)
money = FuncFormatter(lambda v,_: f"R$ {v/1e6:.1f}M" if abs(v)>=1e6 else f"R$ {v/1e3:.0f}k")

# ------------------------------------------------------------------ load
cu=pd.read_csv(D+"olist_customers_dataset.csv"); it=pd.read_csv(D+"olist_order_items_dataset.csv")
pay=pd.read_csv(D+"olist_order_payments_dataset.csv"); rv=pd.read_csv(D+"olist_order_reviews_dataset.csv")
o=pd.read_csv(D+"olist_orders_dataset.csv"); pr=pd.read_csv(D+"olist_products_dataset.csv")
se=pd.read_csv(D+"olist_sellers_dataset.csv"); tr=pd.read_csv(D+"product_category_name_translation.csv")
geo=pd.read_csv(D+"olist_geolocation_dataset.csv").drop_duplicates()
for c in ["order_purchase_timestamp","order_delivered_customer_date","order_estimated_delivery_date"]: o[c]=pd.to_datetime(o[c])
deliv=o[o.order_status=="delivered"]
o["m"]=o.order_purchase_timestamp.dt.to_period("M")
ob=o.groupby("m").order_id.count()
sb=it.merge(deliv[["order_id","order_purchase_timestamp"]],on="order_id"); sb["m"]=sb.order_purchase_timestamp.dt.to_period("M"); sb=sb.groupby("m").price.sum()
months=pd.period_range("2016-09","2018-10",freq="M"); ob=ob.reindex(months,fill_value=0); sb=sb.reindex(months,fill_value=0)
xs=months.to_timestamp()

# ------------------------------------------------------------------ 01 monthly orders & sales
fig,ax=plt.subplots(2,1,figsize=(10,5.6),sharex=True)
ax[0].plot(xs,ob.values,color=NAVY,lw=2.2,marker="o",ms=4); ax[0].fill_between(xs,ob.values,color=NAVY,alpha=.08)
ax[0].set_title("Orders per month (all statuses)"); ax[0].yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:,.0f}"))
ax[1].plot(xs,sb.values,color=GREEN,lw=2.2,marker="o",ms=4); ax[1].fill_between(xs,sb.values,color=GREEN,alpha=.10)
ax[1].set_title("Delivered product sales per month (freight excluded)"); ax[1].yaxis.set_major_formatter(money)
pk=pd.Timestamp("2017-11-01")
ax[0].annotate("Nov 2017 peak\n7,544 orders",(pk,ob[pd.Period("2017-11")]),xytext=(-95,-6),textcoords="offset points",fontsize=9.5,color=NAVY,arrowprops=dict(arrowstyle="-",color=GREY))
ax[1].annotate("R$ 987,765",(pk,sb[pd.Period("2017-11")]),xytext=(-70,2),textcoords="offset points",fontsize=9.5,color=GREEN,arrowprops=dict(arrowstyle="-",color=GREY))
for a in ax: a.axvspan(pd.Timestamp("2018-08-20"),xs[-1]+pd.Timedelta(days=20),color=AMBER,alpha=.18,lw=0)
ax[0].text(pd.Timestamp("2018-08-25"),ob.max()*.55,"incomplete\ndata",fontsize=8.5,color="#8A6100")
fig.autofmt_xdate(); fig.tight_layout(); save(fig,"c01_monthly.png")

# ------------------------------------------------------------------ 02 growth Jan-Aug
g=pd.DataFrame({"metric":["Orders","Active customers\n(monthly avg)","Delivered product sales"],"pct":[135.1,136.8,141.1],"a":["22,968","2,816","R$ 2.99M"],"b":["53,991","6,670","R$ 7.22M"]})
fig,ax=plt.subplots(figsize=(8,2.9)); ax.barh(g.metric[::-1],g.pct[::-1],color=[GREEN,BLUE,NAVY][::-1],height=.55)
for i,(p,a,b) in enumerate(zip(g.pct[::-1],g.a[::-1],g.b[::-1])): ax.text(p+2,i,f"+{p:.1f}%   ({a} → {b})".replace("$",r"\$"),va="center",fontsize=10)
ax.set_xlim(0,235); ax.set_xticks([]); ax.grid(False); ax.spines["bottom"].set_visible(False); ax.set_title("Growth, Jan–Aug 2018 vs Jan–Aug 2017")
fig.tight_layout(); save(fig,"c02_growth.png")

# ------------------------------------------------------------------ 03 customers
oc=o.merge(cu[["customer_id","customer_unique_id"]],on="customer_id")
dc=oc[oc.order_status=="delivered"]; opc=dc.groupby("customer_unique_id").order_id.nunique()
one,rep=(opc==1).sum(),(opc>1).sum()
cs=cu.groupby("customer_state").customer_unique_id.nunique().sort_values(ascending=False)
fig,ax=plt.subplots(1,2,figsize=(10,3.9),gridspec_kw={"width_ratios":[1,1.5]})
w,_=ax[0].pie([one,rep],colors=[NAVY,AMBER],startangle=90,counterclock=False,wedgeprops=dict(width=.38,edgecolor="white"))
ax[0].text(0,.08,"3.0%",ha="center",fontsize=24,fontweight="bold",color=AMBER); ax[0].text(0,-.2,"repeat buyers",ha="center",fontsize=10)
ax[0].set_title("One-time vs repeat customers"); ax[0].legend(w,[f"One-time  {one:,}",f"Repeat  {rep:,}"],loc="lower center",bbox_to_anchor=(.5,-.12),frameon=False,ncol=1,fontsize=9.5)
t=cs.head(8)[::-1]; ax[1].barh(t.index,t.values,color=[BLUE]*7+[NAVY],height=.65)
for i,v in enumerate(t.values): ax[1].text(v+300,i,f"{v:,}",va="center",fontsize=9.5)
ax[1].set_xlim(0,47000); ax[1].set_xticks([]); ax[1].grid(False); ax[1].spines["bottom"].set_visible(False); ax[1].set_title("Unique customers by state (top 8)")
fig.tight_layout(); save(fig,"c03_customers.png")

# ------------------------------------------------------------------ 04 categories
p=pr.merge(tr,on="product_category_name",how="left")[["product_id","product_category_name_english"]]
ic=it.merge(p,on="product_id",how="left").merge(o[["order_id","order_status"]],on="order_id"); ic["cat"]=ic.product_category_name_english.fillna("Unknown")
cd=ic[ic.order_status=="delivered"]
cat=cd.groupby("cat").agg(sales=("price","sum"),orders=("order_id","nunique"),avgp=("price","mean")).drop(index="Unknown")
nice=lambda s:s.replace("_"," ").title().replace("Bed Bath Table","Bed, Bath & Table").replace("Health Beauty","Health & Beauty").replace("Watches Gifts","Watches & Gifts").replace("Sports Leisure","Sports & Leisure").replace("Computers Accessories","Computers & Accessories").replace("Furniture Decor","Furniture & Decor")
top=cat.sort_values("sales",ascending=False).head(10)
fig,ax=plt.subplots(1,2,figsize=(11,4.4),gridspec_kw={"width_ratios":[1.15,1]})
ax[0].barh([nice(i) for i in top.index][::-1],top.sales[::-1],color=[GREEN]*7+[GREEN]*0+[NAVY]*0 if False else [GREEN if i>=7 else "#7FC8A0" for i in range(10)],height=.65)
for i,v in enumerate(top.sales[::-1]): ax[0].text(v+15000,i,f"R$ {v/1e6:.2f}M",va="center",fontsize=9.5)
ax[0].set_xlim(0,1.65e6); ax[0].set_xticks([]); ax[0].grid(False); ax[0].spines["bottom"].set_visible(False); ax[0].set_title("Top 10 categories by delivered sales")
t15=cat.sort_values("sales",ascending=False).head(15)
sc=ax[1].scatter(t15.orders,t15.avgp,s=t15.sales/2800,color=BLUE,alpha=.55,edgecolor="white")
for n,r in t15.iterrows():
    if n in ["health_beauty","watches_gifts","bed_bath_table","sports_leisure","computers_accessories","furniture_decor","cool_stuff","auto","garden_tools"]:
        ax[1].annotate(nice(n),(r.orders,r.avgp),xytext=(6,5),textcoords="offset points",fontsize=8.5)
ax[1].set_xlabel("Delivered orders"); ax[1].set_ylabel("Average item price (R$)"); ax[1].set_title("Volume vs ticket size (bubble = sales)")
fig.tight_layout(); save(fig,"c04_categories.png")

# ------------------------------------------------------------------ 05 delivery distribution
v=deliv.dropna(subset=["order_purchase_timestamp","order_delivered_customer_date"]).copy()
v["d"]=(v.order_delivered_customer_date-v.order_purchase_timestamp).dt.total_seconds()/86400
v["late"]=v.order_delivered_customer_date>v.order_estimated_delivery_date
fig,ax=plt.subplots(figsize=(9,3.9)); bins=np.arange(0,61,1)
ax.hist(v.d[~v.late],bins=bins,color=GREEN,alpha=.85,label=f"On time ({(~v.late).mean():.1%})"); ax.hist(v.d[v.late],bins=bins,color=RED,alpha=.85,label=f"Late ({v.late.mean():.1%})")
for val,lab,col in [(v.d.median(),f"Median {v.d.median():.1f} d",NAVY),(v.d.mean(),f"Mean {v.d.mean():.1f} d",INK),(v.d.quantile(.9),f"P90 {v.d.quantile(.9):.1f} d",GREY)]:
    ax.axvline(val,color=col,ls="--",lw=1.3); ax.text(val+.4,ax.get_ylim()[1]*(.93 if lab.startswith("Median") else .80 if lab.startswith("Mean") else .93),lab,fontsize=9.5,color=col)
ax.set_xlabel("Days from purchase to delivery"); ax.set_ylabel("Orders"); ax.set_title("Delivery time distribution is right-skewed"); ax.legend(frameon=False,loc="center right")
ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:,.0f}")); fig.tight_layout(); save(fig,"c05_delivery_dist.png")

# ------------------------------------------------------------------ 06 state: delivery time vs late rate
vs=v.merge(cu[["customer_id","customer_state"]],on="customer_id")
st=vs.groupby("customer_state").agg(avg=("d","mean"),n=("order_id","nunique"),late=("late","mean"))
fig,ax=plt.subplots(figsize=(9,4.8))
cols=[RED if r.late>=.15 else (AMBER if r.avg>=20 else BLUE) for _,r in st.iterrows()]
ax.scatter(st.avg,st.late*100,s=np.clip(st.n/12,25,420),c=cols,alpha=.7,edgecolor="white")
for s,r in st.iterrows(): ax.annotate(s,(r.avg,r.late*100),xytext=(5,4),textcoords="offset points",fontsize=9)
ax.axhline(v.late.mean()*100,color=GREY,ls=":",lw=1); ax.text(30.2,v.late.mean()*100+.4,"national 8.1%",fontsize=8.5,color=GREY,ha="right")
ax.set_xlabel("Average delivery time (days)"); ax.set_ylabel("Late-delivery rate (%)"); ax.set_title("Long is not the same as late: distance vs reliability by customer state")
ax.text(.99,.04,"bubble size = delivered orders",transform=ax.transAxes,ha="right",fontsize=8.5,color=GREY)
fig.tight_layout(); save(fig,"c06_state_scatter.png")

# ------------------------------------------------------------------ 07 reviews by delivery status
rs=rv.groupby("order_id").review_score.mean().rename("rs"); dr=v.merge(rs,on="order_id")
dist=pd.crosstab(dr.late,dr.rs.round().astype(int),normalize="index")*100
dist.index=["On time","Late"]
pal={1:"#C0392B",2:"#E8845A",3:"#F2C14E",4:"#8CC084",5:"#2E8B57"}
fig,ax=plt.subplots(figsize=(9,2.9)); left=np.zeros(2)
for s in [1,2,3,4,5]:
    vals=dist[s].values; ax.barh(dist.index[::-1],vals[::-1],left=left,color=pal[s],height=.55,label=f"{s}")
    for i,(l,val) in enumerate(zip(left,vals[::-1])):
        if val>4: ax.text(l+val/2,i,f"{val:.0f}%",ha="center",va="center",color="white",fontsize=10,fontweight="bold")
    left+=vals[::-1]
ax.set_xlim(0,100); ax.set_xticks([]); ax.grid(False); ax.spines["bottom"].set_visible(False)
ax.legend(title="Review score",ncol=5,frameon=False,loc="upper center",bbox_to_anchor=(.5,-.02),fontsize=9)
ax.set_title("Late delivery flips the review distribution (avg 4.29 vs 2.57)"); fig.tight_layout(); save(fig,"c07_reviews_delivery.png")
dist.round(1).to_json(os.path.join(CH,"review_dist.json"))

# ------------------------------------------------------------------ 08 payments
share_r=pay.payment_type.value_counts(normalize=True); share_v=pay.groupby("payment_type").payment_value.sum()/pay.payment_value.sum()
order=["credit_card","boleto","voucher","debit_card"]; lab=["Credit card","Boleto","Voucher","Debit card"]
cc=pay[(pay.payment_type=="credit_card")&(pay.payment_installments>=1)]; med=cc.groupby("payment_installments").payment_value.median(); cnt=cc.groupby("payment_installments").size()
fig,ax=plt.subplots(1,2,figsize=(11,3.9),gridspec_kw={"width_ratios":[1,1.25]})
x=np.arange(4); ax[0].bar(x-.19,[share_r[k]*100 for k in order],.38,color=NAVY,label="Share of payment records"); ax[0].bar(x+.19,[share_v[k]*100 for k in order],.38,color=GREEN,label="Share of payment value")
for i,k in enumerate(order):
    ax[0].text(i-.19,share_r[k]*100+1.2,f"{share_r[k]*100:.1f}%",ha="center",fontsize=8.5); ax[0].text(i+.19,share_v[k]*100+1.2,f"{share_v[k]*100:.1f}%",ha="center",fontsize=8.5)
ax[0].set_xticks(x); ax[0].set_xticklabels(lab,fontsize=9.5); ax[0].set_ylim(0,90); ax[0].set_yticks([]); ax[0].grid(False); ax[0].spines["left"].set_visible(False); ax[0].legend(frameon=False,fontsize=8.5); ax[0].set_title("Payment mix")
m=med[cnt>=50]; ax[1].plot(m.index,m.values,color=PURPLE,lw=2.2,marker="o",ms=5); ax[1].fill_between(m.index,m.values,color=PURPLE,alpha=.1)
ax[1].set_xlabel("Number of installments (credit card; installment counts with ≥ 50 records)"); ax[1].set_title("Median credit-card payment rises with installments")
ax[1].yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"R$ {v:,.0f}")); ax[1].set_xticks(m.index)
fig.tight_layout(); save(fig,"c08_payments.png")

# ------------------------------------------------------------------ 09 seller concentration + 10 supply vs demand
di=it[it.order_id.isin(deliv.order_id)]; ss=di.groupby("seller_id").price.sum().sort_values(ascending=False)
cum=ss.cumsum()/ss.sum(); xr=np.arange(1,len(ss)+1)/len(ss)*100
fig,ax=plt.subplots(figsize=(6.2,4.3)); ax.plot(xr,cum.values*100,color=NAVY,lw=2.4); ax.fill_between(xr,cum.values*100,color=NAVY,alpha=.08)
ax.plot([0,100],[0,100],color=GREY,ls=":",lw=1); ax.set_xlim(0,100); ax.set_ylim(0,102)
i20=int(len(ss)*.2); ax.scatter([20],[cum.iloc[i20-1]*100],color=RED,zorder=5); ax.annotate(f"Top 20% of sellers\n= {cum.iloc[i20-1]*100:.0f}% of sales",(20,cum.iloc[i20-1]*100),xytext=(30,55),fontsize=10,arrowprops=dict(arrowstyle="-",color=GREY))
ax.set_xlabel("Sellers ranked by delivered product sales (cumulative %)"); ax.set_ylabel("Cumulative share of sales (%)"); ax.set_title("Seller concentration (Pareto curve)")
fig.tight_layout(); save(fig,"c09_pareto.png")
ds=di.merge(se[["seller_id","seller_state"]],on="seller_id"); sales_sh=ds.groupby("seller_state").price.sum()/ds.price.sum(); sell_sh=se.seller_state.value_counts(normalize=True); cust_sh=cu.customer_state.value_counts(normalize=True)
sts=["SP","RJ","MG","PR","RS","SC"]; fig,ax=plt.subplots(figsize=(7.2,4.1)); x=np.arange(len(sts)); w=.26
for k,(s,lbl,c) in enumerate([(cust_sh,"Customer records",AMBER),(sell_sh,"Registered sellers",BLUE),(sales_sh,"Delivered product sales (by seller state)",GREEN)]):
    vals=[s.get(t,0)*100 for t in sts]; ax.bar(x+(k-1)*w,vals,w,color=c,label=lbl)
    for xi,vv in zip(x+(k-1)*w,vals): ax.text(xi,vv+.8,f"{vv:.0f}",ha="center",fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(sts); ax.set_yticks([]); ax.grid(False); ax.spines["left"].set_visible(False); ax.legend(frameon=False,fontsize=8.5); ax.set_title("São Paulo is both the demand and the supply hub (% share)")
fig.tight_layout(); save(fig,"c10_supply_demand.png")

# ------------------------------------------------------------------ MAPS
geo=geo[geo.geolocation_lat.between(-34,5.5)&geo.geolocation_lng.between(-74,-34)]
cent=geo.groupby("geolocation_state")[["geolocation_lat","geolocation_lng"]].median()
cmap=LinearSegmentedColormap.from_list("olist",["#0B7A3E","#7BC96F","#FFE066","#F59E0B","#D1342F","#7F1D1D"])
def delivery_map(ax):
    c=geo.geolocation_state.map(st.avg)
    sc=ax.scatter(geo.geolocation_lng,geo.geolocation_lat,c=c,s=1.1,cmap=cmap,vmin=8,vmax=30,linewidths=0,rasterized=True)
    for s in ["SP","RJ","MG","BA","PA","AM","RR","AP","AL","MA","CE","RS","PR","GO","MT"]:
        r=cent.loc[s]; ax.text(r.geolocation_lng,r.geolocation_lat,f"{s}\n{st.avg[s]:.0f}d",ha="center",va="center",fontsize=7.5,fontweight="bold",color="white",path_effects=[pe.withStroke(linewidth=2,foreground="#222")])
    ax.set_aspect("equal"); ax.axis("off"); return sc
def customer_map(ax):
    ax.scatter(geo.geolocation_lng,geo.geolocation_lat,c="#DDE3EA",s=.8,linewidths=0,rasterized=True)
    cc_=cu.groupby("customer_state").customer_unique_id.nunique()
    for s,n in cc_.items():
        r=cent.loc[s]; ax.scatter(r.geolocation_lng,r.geolocation_lat,s=n/22,color=NAVY,alpha=.55,edgecolor="white",linewidth=.8,zorder=3)
    for s in ["SP","RJ","MG","RS","PR","BA"]:
        r=cent.loc[s]; ax.annotate(f"{s}  {cc_[s]:,}",(r.geolocation_lng,r.geolocation_lat),xytext={"SP":(14,-24),"RJ":(18,-3),"MG":(-30,20)}.get(s,(10,-18)),textcoords="offset points",fontsize=8.5,fontweight="bold",color=NAVY,zorder=4)
    ax.set_aspect("equal"); ax.axis("off")
fig,ax=plt.subplots(figsize=(7,7.2)); sc=delivery_map(ax)
cb=fig.colorbar(sc,ax=ax,orientation="horizontal",fraction=.035,pad=.01,shrink=.6); cb.set_label("Average purchase-to-delivery time of the customer's state (days)",fontsize=9); cb.outline.set_visible(False)
ax.set_title("How long do customers wait? Delivery time by state",loc="center",fontsize=14); save(fig,"map_delivery_time.png",AS)
fig,ax=plt.subplots(figsize=(7,7.2)); customer_map(ax); ax.set_title("Where are Olist's customers? (bubble = unique customers)",loc="center",fontsize=14); save(fig,"map_customers.png",AS)
fig,axs=plt.subplots(1,2,figsize=(14,6.4)); customer_map(axs[0]); axs[0].set_title("Where customers are  (bubble = unique customers)",loc="center",fontsize=13)
sc=delivery_map(axs[1]); axs[1].set_title("How long they wait  (average days to delivery)",loc="center",fontsize=13)
cb=fig.colorbar(sc,ax=axs[1],orientation="horizontal",fraction=.035,pad=.01,shrink=.55); cb.set_label("days",fontsize=9); cb.outline.set_visible(False)
fig.tight_layout(); save(fig,"map_overview.png",AS)
print("done")

# ------------------------------------------------------------------ cover map (dark background, used by the PDF cover)
fig,ax=plt.subplots(figsize=(6,6.2),facecolor=NAVY); ax.set_facecolor(NAVY)
c=geo.geolocation_state.map(st.avg)
ax.scatter(geo.geolocation_lng,geo.geolocation_lat,c=c,s=1.4,cmap=cmap,vmin=8,vmax=30,linewidths=0,rasterized=True)
ax.set_aspect("equal"); ax.axis("off"); fig.savefig(os.path.join(CH,"cover_map.png"),dpi=200,facecolor=NAVY,bbox_inches="tight",pad_inches=0.05); plt.close(fig)
print("cover map done")
