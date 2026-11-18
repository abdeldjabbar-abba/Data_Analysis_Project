"""Builds Report/Olist_Analysis_Report.pdf  (run build_charts.py first).   python Report/build_report.py"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
                                Image, KeepTogether, PageBreak, NextPageTemplate, Flowable)
from PIL import Image as PILImage

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
CH=os.path.join(ROOT,"Report","charts"); AS=os.path.join(ROOT,"assets"); OUT=os.path.join(ROOT,"Report","Olist_Analysis_Report.pdf")
F="/usr/share/fonts/truetype/"
for n,p in [("Carlito","crosextra/Carlito-Regular.ttf"),("Carlito-Bold","crosextra/Carlito-Bold.ttf"),("Carlito-Italic","crosextra/Carlito-Italic.ttf"),("Carlito-BoldItalic","crosextra/Carlito-BoldItalic.ttf"),
            ("Poppins","google-fonts/Poppins-Regular.ttf"),("Poppins-Med","google-fonts/Poppins-Medium.ttf"),("Poppins-Bold","google-fonts/Poppins-Bold.ttf")]:
    pdfmetrics.registerFont(TTFont(n,F+p))
pdfmetrics.registerFontFamily("Carlito",normal="Carlito",bold="Carlito-Bold",italic="Carlito-Italic",boldItalic="Carlito-BoldItalic")
pdfmetrics.registerFontFamily("Poppins",normal="Poppins",bold="Poppins-Bold",italic="Poppins",boldItalic="Poppins-Bold")

NAVY=colors.HexColor("#0B2A5B"); GREEN=colors.HexColor("#009739"); YEL=colors.HexColor("#FEDD00"); BLUE=colors.HexColor("#1F6FD1")
AMBER=colors.HexColor("#D98E04"); RED=colors.HexColor("#D64A26"); PURPLE=colors.HexColor("#7A4EAB"); TEAL=colors.HexColor("#0E9AA7")
INK=colors.HexColor("#1F2937"); GREY=colors.HexColor("#6B7280"); LIGHT=colors.HexColor("#F3F6FA"); LINE=colors.HexColor("#DDE3EA")
PW,PH=A4; MX=18*mm; W=PW-2*MX

S=dict(
 body=ParagraphStyle("body",fontName="Carlito",fontSize=10.5,leading=14.6,textColor=INK,spaceAfter=5),
 small=ParagraphStyle("small",fontName="Carlito",fontSize=8.8,leading=11.5,textColor=GREY),
 cap=ParagraphStyle("cap",fontName="Carlito-Italic",fontSize=8.6,leading=11,textColor=GREY,spaceAfter=8),
 h2=ParagraphStyle("h2",fontName="Poppins-Med",fontSize=12.5,leading=16,textColor=NAVY,spaceBefore=8,spaceAfter=4),
 th=ParagraphStyle("th",fontName="Carlito-Bold",fontSize=9.5,leading=12,textColor=colors.white),
 td=ParagraphStyle("td",fontName="Carlito",fontSize=9.5,leading=12.3,textColor=INK),
 tdb=ParagraphStyle("tdb",fontName="Carlito-Bold",fontSize=9.5,leading=12.3,textColor=INK),
 num=ParagraphStyle("num",fontName="Carlito",fontSize=10.3,leading=13.8,textColor=INK),
 lead=ParagraphStyle("lead",fontName="Carlito",fontSize=12.2,leading=17,textColor=INK,spaceAfter=8),
)
P=lambda t,s="body":Paragraph(t,S[s])

class SectionHeader(Flowable):
    def __init__(s,num,title,sub,color): super().__init__(); s.num,s.title,s.sub,s.color=num,title,sub,color; s.width=W; s.height=18*mm
    def wrap(s,aw,ah): return W,s.height
    def draw(s):
        c=self.canv if False else s.canv
        c.setFillColor(s.color); c.roundRect(0,0,3.2*mm,s.height-1*mm,1.2*mm,stroke=0,fill=1)
        c.setFillColor(s.color); c.setFont("Poppins-Bold",9); c.drawString(7*mm,s.height-6.2*mm,s.num)
        c.setFillColor(NAVY); c.setFont("Poppins-Bold",17); c.drawString(7*mm,s.height-13.2*mm+0.5*mm,s.title)
        c.setFillColor(GREY); c.setFont("Carlito-Italic",10.5); c.drawString(7*mm,-1.6*mm,s.sub)

def callout(label,text,color,bg=None):
    bg=bg or colors.HexColor("#F7F9FC")
    t=Table([[Paragraph(f'<font name="Poppins-Bold" size="8.5" color="{color.hexval().replace("0x","#")}">{label.upper()}</font><br/>{text}',S["td"])]],colWidths=[W])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),("LINEBEFORE",(0,0),(0,-1),3.2,color),("LEFTPADDING",(0,0),(-1,-1),9),("RIGHTPADDING",(0,0),(-1,-1),9),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    return KeepTogether([t,Spacer(1,6)])

def img(path,width,cap=None,align="CENTER"):
    w,h=PILImage.open(path).size; im=Image(path,width=width,height=width*h/w); im.hAlign=align
    parts=[im]+([P(cap,"cap")] if cap else [Spacer(1,6)]); return KeepTogether(parts)

def img2(p1,p2,cap=None,ratio=(1,1)):
    tot=W-6*mm; w1=tot*ratio[0]/sum(ratio); w2=tot*ratio[1]/sum(ratio)
    def mk(p,w): a,b=PILImage.open(p).size; return Image(p,width=w,height=w*b/a)
    t=Table([[mk(p1,w1),mk(p2,w2)]],colWidths=[w1+3*mm,w2+3*mm]); t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0)]))
    return KeepTogether([t]+([P(cap,"cap")] if cap else [Spacer(1,6)]))

def table(rows,widths,header=True,color=NAVY,zebra=True,align_right=()):
    data=[[Paragraph(str(c),S["th"] if (header and i==0) else S["td"]) for c in r] for i,r in enumerate(rows)]
    t=Table(data,colWidths=widths,repeatRows=1 if header else 0)
    st=[("VALIGN",(0,0),(-1,-1),"MIDDLE"),("TOPPADDING",(0,0),(-1,-1),4.5),("BOTTOMPADDING",(0,0),(-1,-1),4.5),("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),("LINEBELOW",(0,0),(-1,-1),.4,LINE)]
    if header: st+=[("BACKGROUND",(0,0),(-1,0),color)]
    if zebra: st+=[("BACKGROUND",(0,i),(-1,i),LIGHT) for i in range(1 if header else 0,len(rows),2)]
    t.setStyle(TableStyle(st)); return t

def kpi_grid(items):
    cells=[]
    for v,l,c in items:
        cells.append(Paragraph(f'<font name="Poppins-Bold" size="17" color="{c.hexval().replace("0x","#")}">{v}</font><br/><font name="Carlito" size="9.5" color="#4B5563">{l}</font>',ParagraphStyle("k",leading=21,alignment=TA_CENTER)))
    rows=[cells[i:i+3] for i in range(0,len(cells),3)]; cw=W/3
    t=Table(rows,colWidths=[cw]*3,rowHeights=[21*mm]*len(rows))
    st=[("BACKGROUND",(0,0),(-1,-1),LIGHT),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("BOX",(0,0),(-1,-1),.6,LINE),("INNERGRID",(0,0),(-1,-1),2.5,colors.white)]
    for ri,r in enumerate(rows):
        for ci,_ in enumerate(r): st.append(("LINEABOVE",(ci,ri),(ci,ri),3,items[ri*3+ci][2]))
    t.setStyle(TableStyle(st)); return t

# ---------------------------------------------------------------- page furniture
def cover(c,doc):
    c.saveState(); c.setFillColor(NAVY); c.rect(0,0,PW,PH,stroke=0,fill=1)
    c.setFillColor(colors.HexColor("#0F3677")); c.rect(0,0,PW,PH*.42,stroke=0,fill=1)
    m=os.path.join(CH,"cover_map.png"); c.drawImage(m,PW-128*mm,PH-190*mm,width=118*mm,height=118*mm,mask="auto")
    c.setFillColor(YEL); c.rect(MX,PH-52*mm,22*mm,1.6*mm,stroke=0,fill=1)
    c.setFillColor(colors.HexColor("#9DB8E3")); c.setFont("Poppins-Med",10); c.drawString(MX,PH-45*mm,"DATA ANALYSIS REPORT")
    c.setFillColor(colors.white); c.setFont("Poppins-Bold",34)
    c.drawString(MX,PH-68*mm,"Olist E-Commerce"); c.drawString(MX,PH-81*mm,"Performance Report")
    c.setFillColor(colors.HexColor("#CFE3FF")); c.setFont("Carlito",14.5)
    c.drawString(MX,PH-94*mm,"Sales, customers, products, delivery, payments and sellers")
    c.setFillColor(colors.HexColor("#9DB8E3")); c.setFont("Carlito",11.5); c.drawString(MX,PH-101*mm,"Brazilian marketplace data, September 2016 to October 2018")
    kp=[("99,441","orders analyzed"),("R$ 13.2M","delivered product sales"),("96,096","unique customers"),("12.6 days","average delivery time")]
    x0=MX; cw=(W-3*4*mm)/4; y=70*mm
    for i,(v,l) in enumerate(kp):
        x=x0+i*(cw+4*mm); c.setFillColor(colors.HexColor("#163F85")); c.roundRect(x,y,cw,24*mm,2.5*mm,stroke=0,fill=1)
        c.setFillColor(YEL if i%2==0 else colors.white); c.setFont("Poppins-Bold",14.5); c.drawCentredString(x+cw/2,y+13.5*mm,v)
        c.setFillColor(colors.HexColor("#B8CCEE")); c.setFont("Carlito",9.5); c.drawCentredString(x+cw/2,y+6.5*mm,l)
    c.setFillColor(colors.HexColor("#B8CCEE")); c.setFont("Carlito",10.5)
    c.drawString(MX,38*mm,"Prepared November 2026  |  Python, Pandas, Matplotlib, Seaborn")
    c.drawString(MX,32.5*mm,"Source: Olist Brazilian E-Commerce Public Dataset (9 relational tables)")
    for k,(col,w) in enumerate([(GREEN,.5),(YEL,.3),(BLUE,.2)]):
        c.setFillColor(col); c.rect(PW*sum([.5,.3][:k]),0,PW*w,5*mm,stroke=0,fill=1)
    c.restoreState()
def body(c,doc):
    c.saveState(); c.setStrokeColor(LINE); c.setLineWidth(.6); c.line(MX,PH-13*mm,PW-MX,PH-13*mm)
    c.setFont("Carlito",8.8); c.setFillColor(GREY); c.drawString(MX,PH-10.2*mm,"Olist E-Commerce Performance Report")
    c.drawRightString(PW-MX,PH-10.2*mm,"Data Analysis Project")
    for k,(col,w) in enumerate([(GREEN,.5),(YEL,.3),(BLUE,.2)]):
        c.setFillColor(col); c.rect(PW*sum([.5,.3][:k]),PH-2.2*mm,PW*w,2.2*mm,stroke=0,fill=1)
    c.line(MX,13*mm,PW-MX,13*mm); c.setFillColor(GREY); c.setFont("Carlito",8.8); c.drawString(MX,8.5*mm,"All figures from the Olist public dataset. Sales = delivered product value (freight excluded), not profit.")
    c.setFont("Poppins-Med",9); c.setFillColor(NAVY); c.drawRightString(PW-MX,8.3*mm,str(doc.page)); c.restoreState()

doc=BaseDocTemplate(OUT,pagesize=A4,leftMargin=MX,rightMargin=MX,topMargin=20*mm,bottomMargin=19*mm,title="Olist E-Commerce Performance Report",author="Data Analysis Project",subject="Sales, customers, products, delivery, payments and sellers")
fr=Frame(MX,19*mm,W,PH-39*mm,id="f",leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="cover",frames=[Frame(0,0,1,1)],onPage=cover),PageTemplate(id="body",frames=[fr],onPage=body)])
G=lambda n:os.path.join(CH,n)
E=[NextPageTemplate("body"),PageBreak()]

# ================================================================= EXECUTIVE SUMMARY
E+=[SectionHeader("EXECUTIVE SUMMARY","What the data says","Seven findings and what to do about them",NAVY),Spacer(1,6*mm)]
E+=[P("Olist's marketplace more than doubled between the first eight months of 2017 and the same months of 2018, but that growth was built on <b>acquiring new customers</b>: 97% bought only once. Delivery is the weak link. Speed depends on geography, <b>reliability depends on regional operations</b>, and a late order cuts the average review score from 4.29 to 2.57.","lead")]
E+=[kpi_grid([("99,441","orders, Sep 2016 to Oct 2018",NAVY),("R$ 13.2M","delivered product sales",GREEN),("+141%","sales growth, Jan-Aug 2018 vs 2017",BLUE),("3.0%","customers who bought again",AMBER),("8.1%","orders delivered late",RED),("4.09 / 5","average review score",PURPLE)]),Spacer(1,5*mm)]
finds=[("Strong growth, then a plateau.","Orders +135.1% and sales +141.1% (Jan-Aug, 2018 vs 2017); monthly orders flat at 6,167 to 7,269 through 2018."),
("Retention is the biggest untapped lever.","Only 2,801 of 93,358 customers with a delivered order bought a second time."),
("Sales are broad-based.","Top 3 of 71 categories = 25.9% of sales; top 10% of customers = 41.1%."),
("Slow is about distance; late is about operations.","Sao Paulo waits 8.8 days, Roraima 29.4. But Alagoas (23.9%) and Maranhao (19.7%) have the highest late rates."),
("Lateness is the clearest driver of unhappy customers.","46% of late orders get one star, against 7% of on-time orders."),
("Credit cards and installments dominate payments.","Cards carry 78.3% of payment value; 66.9% of card payments are split into installments."),
("The seller base is concentrated around Sao Paulo.","Top 20% of sellers = 82.3% of sales; Sao Paulo hosts 59.7% of sellers and 64.4% of sales.")]
rows=[[Paragraph(f'<font name="Poppins-Bold" color="#009739">{i+1}</font>',S["num"]),Paragraph(f"<b>{a}</b> {b}".replace("Sao Paulo","São Paulo").replace("Maranhao","Maranhão"),S["num"])] for i,(a,b) in enumerate(finds)]
t=Table(rows,colWidths=[8*mm,W-8*mm]); t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("LINEBELOW",(0,0),(-1,-1),.4,LINE),("TOPPADDING",(0,0),(-1,-1),4.2),("BOTTOMPADDING",(0,0),(-1,-1),4.2),("LEFTPADDING",(0,0),(-1,-1),2)]))
E+=[P("Key findings","h2"),t,Spacer(1,3*mm)]
E+=[callout("Where to act first","<b>1)</b> Launch retention programs for second purchases. <b>2)</b> Fix delivery reliability in the Northeast with carrier SLAs or regional fulfilment. <b>3)</b> Test tighter, state-specific delivery promises. Details and KPIs are in the Recommendations section.",GREEN,colors.HexColor("#F1FAF4")),PageBreak()]

# ================================================================= SCOPE & METHOD
E+=[SectionHeader("SCOPE AND METHOD","About the analysis","Data, definitions and quality checks",NAVY),Spacer(1,5*mm)]
E+=[P("The analysis answers <b>25 business questions across six themes</b> using nine anonymized relational tables. Orders sit at the centre and connect to customers, items, payments and reviews; items connect to products and sellers; ZIP-code prefixes connect customers and sellers to geolocation (data model in the appendix).")]
E+=[table([["Table","Rows","One row per"],["orders","99,441","order"],["customers","99,441","customer ID per order (customer_unique_id = the person)"],["order_items","112,650","item within an order"],["order_payments","103,886","payment record (an order can have several)"],["order_reviews","99,224","review (an order can have more than one)"],["products / sellers","32,951 / 3,095","product / seller"],["geolocation","1,000,163","coordinate per ZIP prefix (738,332 after de-duplication)"],["category_translation","71","Portuguese to English category name"]],[42*mm,28*mm,W-70*mm]),Spacer(1,4*mm)]
E+=[P("Definitions used throughout","h2"),table([["Metric","Definition"],["Delivered product sales","Sum of item price on delivered orders. <b>Freight excluded.</b> A sales proxy, not revenue or profit."],["Delivery time","Customer delivery timestamp minus purchase timestamp, in days (delivered orders with both dates)."],["Late delivery","Delivered after the estimated delivery date; on or before the estimate is on time."],["Unique customer","Distinct customer_unique_id. The customer_id is created per order and would overstate customers (99,441 vs 96,096)."],["Repeat customer","A unique customer with more than one delivered order in the data window."],["Low review","Review score of 1 or 2 out of 5."]],[42*mm,W-42*mm]),Spacer(1,4*mm)]
E+=[P("Data quality and method","h2"),
 P("<b>Principle: fix what is demonstrably wrong, never invent what is unknown.</b> Dates were converted with strict parsing. Missing values were kept (88% of review titles and 59% of comments are optional blanks; a few delivered orders lack timestamps: 14 approval, 2 carrier, 8 customer-delivery dates). The only exact duplicates were in the geolocation table: <b>261,831 rows removed</b> (1,000,163 to 738,332). Joins used Pandas' <i>validate</i> option to stop silent row multiplication, and review scores were averaged per order before comparisons.")]
E+=[callout("Analyst's note: know the grain","Each table has a different unit of observation, so \"how many?\" depends on the table. Every figure in this report states its unit: orders, items, payment records, seller-order pairs or customers.",BLUE,colors.HexColor("#F2F7FE")),PageBreak()]

# ================================================================= SALES
E+=[SectionHeader("1  SALES PERFORMANCE","Strong growth, then a plateau","Scale, seasonality and year-over-year growth",GREEN),Spacer(1,4*mm)]
E+=[img(G("c01_monthly.png"),W*.84,"Figure 1. Orders count all statuses; sales count delivered orders only. The shaded area (September-October 2018) is incomplete data, not a collapse in demand.")]
E+=[P("From September 2016 to August 2018 monthly orders grew from a handful to roughly 7,000, and delivered product sales from under R$ 1,000 to almost R$ 1 million. Growth was steep through 2017, <b>peaked in November 2017</b> (R$ 987,765 from 7,544 orders), then held inside a band in 2018: 6,167 to 7,269 orders a month. Next-highest sales months were May 2018 (R$ 977,545) and April 2018 (R$ 973,534)."),
 table([["Basket and scale metric (delivered orders)","Value"],["Orders in the dataset / delivered","99,441 / 96,478 (97.0%)"],["Delivered product sales","R$ 13,221,498.11"],["Average order value (median)","R$ 137.04 (R$ 86.57)"],["Items per order","1.14, with 90.0% of orders holding one item"],["Freight on top of product value","R$ 2.20M (16.6% of product value)"]],[W*.58,W*.42]),Spacer(1,4*mm)]
E+=[img(G("c02_growth.png"),W*.6,"Figure 2. Same eight months compared, so seasonality cancels out.")]
E+=[callout("Insight","Orders jumped <b>62.9% in one month</b> (4,631 in October 2017 to 7,544 in November), coinciding with Brazil's Black Friday (24 November 2017). That is a plausible driver, not a tested one. If it holds, delivery capacity and seller stock must be ready for promotion-driven surges. The mean order (R$ 137) is far above the median (R$ 87), so promotions should be designed around the typical basket.",GREEN,colors.HexColor("#F1FAF4")),PageBreak()]

# ================================================================= CUSTOMERS
E+=[SectionHeader("2  CUSTOMER ANALYTICS","A broad base of one-time buyers","Who buys, where they live, and whether they return",BLUE),Spacer(1,4*mm)]
E+=[P("Olist recorded <b>96,096 unique customers</b> across 99,441 order-level records. Average monthly active customers rose from 2,816 (Jan-Aug 2017) to 6,670 (Jan-Aug 2018), +136.8%. Yet only <b>2,801 customers (3.0%)</b> placed a second delivered order. Spend is spread out: the top customer generated R$ 13,440, and the top 10% of customers account for 41.1% of delivered product value (top 1%: 11.5%), so there is no dependence on a few whales.")]
E+=[img(G("c03_customers.png"),W*.8,"Figure 3. Repeat rate counts customers with more than one delivered order in the data window; it is not a lifetime-retention measure.")]
E+=[P("Demand is concentrated in the Southeast. <b>São Paulo</b> has 40,302 customer IDs (41.9%), followed by Rio de Janeiro (12,384; 12.9%) and Minas Gerais (11,259; 11.7%). The four Southeastern states hold roughly 69% of customers. State counts overlap slightly because some IDs appear in more than one state.")]
E+=[img(os.path.join(AS,"map_customers.png"),W*.4,"Figure 4. Bubble size = unique customers per state (map drawn from the dataset's own geolocation points).")]
E+=[callout("So what","With 97% of buyers purchasing once, almost all 2017-2018 growth came from <b>newly acquired</b> customers, the most expensive way to grow. Even a few points of extra repeat rate would add orders at a fraction of acquisition cost. Next step: a cohort analysis tracking what share of each first-purchase month returns in months 1, 2 and 3.",BLUE,colors.HexColor("#F2F7FE")),PageBreak()]

# ================================================================= PRODUCTS
E+=[SectionHeader("3  PRODUCT PERFORMANCE","Diversified categories, two routes to sales","What sells, what does not, and how categories are reviewed",AMBER),Spacer(1,4*mm)]
E+=[P("Sales are diversified across 71 categories: the top 3 hold 25.9% of delivered product sales and the top 10 hold 62.4%. <b>Health &amp; Beauty</b> leads (R$ 1.23M), ahead of <b>Watches &amp; Gifts</b> (R$ 1.17M) and <b>Bed, Bath &amp; Table</b> (R$ 1.02M). The right-hand chart splits sales into its two drivers: price and volume.")]
E+=[img(G("c04_categories.png"),W*.9,"Figure 5. Left: delivered sales. Right: delivered orders against average item price (bubble size = sales).")]
E+=[P("Categories win in different ways. <b>Watches &amp; Gifts</b> earns through a high average item price (R$ 199). <b>Bed, Bath &amp; Table</b> earns through volume, with the most orders of any category (9,417 across all statuses, followed by Health &amp; Beauty with 8,836) at a lower price (R$ 93). Pricing, promotion and logistics strategy should differ for each."),
 P("<b>Low-sales categories</b> are tiny samples: Security &amp; Services sold R$ 283 across 2 delivered orders, Fashion Children's Clothes R$ 520 across 7, and CDs, DVDs &amp; Musicals R$ 730 across 12. They are candidates for review, not confirmed poor performers. Category review scores show the same fragility: Office Furniture averaged 3.62 across 1,263 reviewed orders, while Security &amp; Services averaged 2.50 on only 2.")]
E+=[callout("Caution","Reviews describe the <b>whole order experience</b>, not a product. An order with several categories attaches its score to each, so category review scores show association, not proof that a category caused a rating. Category rankings built on very few orders should not be used for decisions.",AMBER,colors.HexColor("#FFF8E8")),PageBreak()]

# ================================================================= DELIVERY
E+=[SectionHeader("4  DELIVERY PERFORMANCE","Speed is geography, reliability is operations","Delivery time, lateness and customer satisfaction",RED),Spacer(1,4*mm)]
E+=[P("Across 96,470 delivered orders with valid dates, the average wait from purchase to delivery was <b>12.56 days</b>; the <b>median is 10.2 days</b> and the <b>90th percentile 23.1 days</b>. The distribution has a long right tail, so averages understate what the slowest customers experience: one in ten waits over three weeks. <b>8.11%</b> of orders (7,826) arrived after the estimated date.")]
E+=[img(G("c05_delivery_dist.png"),W*.92,"Figure 6. Delivery time in days. Late orders took 31.5 days on average against 10.9 days for on-time orders.")]
E+=[callout("Insight: the promise is padded","The average promised delivery window is <b>23.7 days</b>, almost twice the 12.6 days actually taken. On-time orders arrive 13.0 days early; late orders arrive 9.6 days after the promise. Conservative estimates keep the late rate low but may make Olist look slow at checkout. Whether tighter, region-specific promises would lift conversion without raising lateness is a testable hypothesis.",RED,colors.HexColor("#FEF4F1")),PageBreak()]
E+=[P("The geography of waiting","h2"),
 P("All ten states with the longest average delivery times are in the <b>North or Northeast</b>: Roraima (29.4 days), Amapá (27.2) and Amazonas (26.4), against São Paulo at 8.8. Roraima and Amapá have only 41 and 67 delivered orders, so their averages are signals rather than rankings; Pará (23.8 days over 946 orders) and Ceará (21.3 over 1,279) show the pattern holds with real volume.")]
E+=[img(os.path.join(AS,"map_delivery_time.png"),W*.5,"Figure 7. Each point is a location from the dataset's geolocation table, colored by the average delivery time of its state.")]
E+=[P("Long is not the same as late","h2"),
 P("Ranking states by <b>late rate</b> gives a different picture. The most remote states mostly meet their longer promises (Roraima 12.2%, Amapá 4.5%, Amazonas 4.1%). The worst reliability is in the Northeast: <b>Alagoas 23.9%</b> (397 orders) and <b>Maranhão 19.7%</b> (717 orders), against 5.0% to 5.9% in Paraná, Minas Gerais and São Paulo. Distance explains <i>slow</i>, not <i>unreliable</i>, which points to regional carrier performance.")]
E+=[img(G("c06_state_scatter.png"),W*.75,"Figure 8. Red bubbles: late rate of 15% or more. Amber: average delivery above 20 days. Bubble size = delivered orders."),PageBreak()]
E+=[P("Lateness and customer satisfaction","h2"),
 P("Among 95,824 delivered orders with a review, 88,163 arrived on time and 7,661 were late. On-time orders averaged <b>4.29</b> out of 5 (median 5); late orders averaged <b>2.57</b> (median 2): a gap of <b>1.72 points</b>. Nearly half (46%) of late orders received the lowest score, versus 7% of on-time orders.")]
E+=[img(G("c07_reviews_delivery.png"),W*.92,"Figure 9. Score distribution within each group (100% stacked), so the much larger on-time group does not dominate.")]
E+=[callout("Insight: expectations matter more than speed","A customer who waited 20 days for an order promised in 30 is more likely to be satisfied than one who waited 12 days for an order promised in 10. The delay itself (days beyond the estimate) is therefore a stronger KPI than raw delivery time. This is an association: product quality and seller service also shape reviews.",RED,colors.HexColor("#FEF4F1")),Spacer(1,2*mm)]
E+=[callout("What to monitor","Late rate by state, days late (beyond the estimate), and the 90th percentile of delivery time, not just the average.",TEAL,colors.HexColor("#EFF9FA")),PageBreak()]

# ================================================================= PAYMENTS
E+=[SectionHeader("5  PAYMENT ANALYSIS","Credit cards and installments dominate","How Brazilians pay, and how they finance larger baskets",PURPLE),Spacer(1,4*mm)]
E+=[P("<b>Credit cards</b> account for 73.9% of payment records and <b>78.3% of payment value</b> (R$ 12.54M of R$ 16.01M). <b>Boleto</b>, the cash-based bank slip, is the clear second at 19.0% of records and 17.9% of value (R$ 2.87M). Vouchers (5.6% of records, 2.4% of value) and debit cards (1.5%, 1.4%) are marginal. At order level, a credit card appeared in 76,505 orders (76.9%); order-level shares overlap because some orders use several methods.")]
E+=[img(G("c08_payments.png"),W*.88,"Figure 10. Left: payment mix. Right: median credit-card payment by number of installments (counts with at least 50 records).")]
E+=[P("Installments are a credit-card phenomenon: boleto, debit and voucher payments are 100% single-payment, while <b>66.9% of credit-card payments use installments</b> (average 3.5). The median single-installment payment is <b>R$ 67.87</b>, against <b>R$ 239.74</b> at 10 installments: bigger tickets are split into more installments. Counts cluster at 1 to 6, 8 and 10 (5,328 records at 10 versus 644 at 9), which hints at seller or promotion caps such as \"up to 10x\". That is a hypothesis to confirm. Above about 12 installments records are few and medians volatile.")]
E+=[callout("Do not compare payments with product sales","Payment value (R$ 16.01M) exceeds delivered product sales (R$ 13.22M) because payments also cover <b>freight</b> and orders that were never delivered. The figures answer different questions. Payment shares describe <i>payment records</i>, not customers.",PURPLE,colors.HexColor("#F7F2FC")),
 callout("So what","Installments (<i>parcelado</i>) are central to how Brazilians finance purchases. A checkout without prominent installment options would likely hurt conversion, especially for larger baskets.",GREEN,colors.HexColor("#F1FAF4")),PageBreak()]

# ================================================================= SELLERS
E+=[SectionHeader("6  SELLER PERFORMANCE","A Pareto marketplace centred on São Paulo","Concentration, reliability and service quality",TEAL),Spacer(1,4*mm)]
E+=[P("Of the <b>2,970 sellers</b> with delivered sales, the <b>top 20% generate 82.3%</b> of product value and just 533 sellers produce 80%. The biggest single seller is only 1.7% of sales (R$ 226,988 across 1,124 orders), so there is no single point of failure, but a small group carries the platform. <b>São Paulo</b> is both the demand centre (41.9% of customers) and the supply centre (59.7% of registered sellers, 64.4% of sales), which is why São Paulo customers receive the fastest delivery.")]
E+=[img2(G("c09_pareto.png"),G("c10_supply_demand.png"),"Figure 11. Left: seller concentration. Right: share of customer records, registered sellers and delivered sales by state.",ratio=(1,1.15))]
E+=[P("<b>Sales and volume leaders differ.</b> The top seller by sales earned R$ 226,988 from 1,124 orders (about R$ 202 per order); the runner-up earned R$ 217,940 from only 348 orders (about R$ 626 per order). The top seller by volume handled 1,819 orders but earned R$ 120,703. Order volume alone does not explain sales value."),
 P("<b>Reliability varies even among high-volume sellers</b> (all ten in São Paulo state): average delivery ranges from 9.6 to 15.8 days and late rates from 5.9% to 11.6%. The fastest seller on average is not the most punctual, so both measures are needed. By seller state, rates look dramatic at the edges (Amazonas 66.7%) but rest on tiny bases: that figure is 2 late orders out of 3 from a single seller, and Maranhão's 23.1% reflects one seller's 389 orders. São Paulo, with 69,395 seller-order pairs across 1,769 sellers, is the reliable comparison base at 8.67% late."),
 P("<b>Poor reviews concentrate in a few sellers.</b> Among sellers with at least 50 reviewed orders, the worst had low scores (1 or 2) on 64 of 107 orders (59.8%; average 2.39), and the second on 87 of 184 (47.3%). Across the ten worst, low-score rates ranged from 31.1% to 59.8%.")]
E+=[callout("Analyst's note: the 50-review floor matters","Without a minimum sample, sellers with two or three reviews would dominate a worst-seller list by chance. A production scorecard should add confidence intervals (such as Wilson) or shrinkage toward the platform average, and check whether poorly rated sellers are also the late ones: if so, the fix is logistics, not product.",TEAL,colors.HexColor("#EFF9FA")),PageBreak()]

# ================================================================= RECOMMENDATIONS
E+=[SectionHeader("7  RECOMMENDATIONS","From findings to actions","Ordered by expected impact, each with a KPI",NAVY),Spacer(1,4*mm)]
rec=[["#","Recommendation","Evidence","KPI to track"],
["1","<b>Build a retention engine.</b> Post-purchase CRM flows, replenishment reminders for repeat-friendly categories, voucher incentives for a second order.","Only 3.0% of customers return; 97% buy once.","90-day repeat-purchase rate"],
["2","<b>Fix reliability in the Northeast</b> (Alagoas, Maranhão, Piauí, Ceará, Sergipe) through carrier SLAs or regional fulfilment.","Late rates of 15% to 24% vs 5% to 6% in São Paulo, Minas Gerais, Paraná.","Late rate by state"],
["3","<b>Make delivery promises smarter.</b> A/B test tighter, state-specific estimated dates where Olist reliably beats its estimate.","Promise 23.7 days vs 12.6 actual; on-time orders arrive 13 days early.","Conversion and late rate"],
["4","<b>Put sellers on a scorecard</b> combining late rate, low-review rate and volume, with intervention rules.","Low-score rates up to 59.8%; late orders average 2.57 stars.","Share of sellers flagged; average score"],
["5","<b>Prepare for demand peaks.</b> Pre-position stock, brief carriers, monitor lateness during promotions.","November 2017 orders +62.9% in one month.","Late rate in peak vs baseline months"],
["6","<b>Keep installment options prominent</b> and test higher caps on large-ticket categories.","66.9% of card payments use installments; median ticket R$ 68 at 1x vs R$ 240 at 10x.","Average order value; conversion by basket"]]
E+=[table(rec,[8*mm,W*.40,W*.30,W-8*mm-W*.70],color=NAVY),Spacer(1,5*mm)]
E+=[P("Suggested sequencing","h2"),table([["Horizon","Focus","Why first"],["0 to 30 days","Seller scorecard (4); peak-readiness checklist (5)","Uses data already available; low cost; protects the next promotion."],["30 to 90 days","Northeast carrier review (2); retention pilot (1); promise A/B test (3)","Needs partner conversations and experiment design."],["90+ days","Installment strategy (6); cohort, RFM and distance models","Builds on the first results; requires deeper analysis."]],[28*mm,W*.42,W-28*mm-W*.42],color=TEAL),PageBreak()]

# ================================================================= LIMITS & NEXT
E+=[SectionHeader("8  LIMITATIONS AND NEXT STEPS","What this analysis cannot say","And where a deeper study would go",GREY),Spacer(1,4*mm)]
E+=[P("Limitations","h2")]
for t in ["<b>No cost or margin data.</b> Sales means delivered product value; profitability, commissions and marketing efficiency cannot be assessed.",
"<b>Short, incomplete window.</b> About two years, with 2018 truncated (16 orders in September, 4 in October) and 2016 sparse.",
"<b>Censoring.</b> Orders not yet delivered at the cut-off are absent from delivered metrics, which depresses the latest months.",
"<b>Association, not causation.</b> Late deliveries and low reviews move together, but product quality, seller service and distance are not controlled for.",
"<b>Small samples at the edges.</b> Some states, categories and sellers have a handful of orders; they are flagged but should not be ranked.",
"<b>Anonymized data.</b> No demographics, which limits customer segmentation."]:
    E+=[Paragraph("&bull;&nbsp; "+t,ParagraphStyle("b",parent=S["body"],leftIndent=10,firstLineIndent=-10,spaceAfter=3.5))]
E+=[P("Where a deeper analysis would go next","h2")]
for i,t in enumerate(["<b>Cohort and RFM analysis</b> to quantify retention by first-purchase month and segment customers by recency, frequency and value.",
"<b>Distance-based delivery model</b> using the geolocation table, to separate \"far\" from \"unreliable\".",
"<b>Statistical testing</b> of the late versus on-time review gap (for example Mann-Whitney U) with effect sizes.",
"<b>Review text mining</b> of the Portuguese comments to learn why customers are unhappy.",
"<b>Seasonal forecasting</b> (for example SARIMA) once more complete data is available.",
"<b>Seller risk score</b> combining delivery, review and volume signals into one early-warning indicator."]):
    E+=[Paragraph(f'<font name="Poppins-Bold" color="#009739">{i+1}.</font>&nbsp; '+t,ParagraphStyle("n",parent=S["body"],leftIndent=14,firstLineIndent=-14,spaceAfter=3.5))]
E+=[Spacer(1,3*mm),callout("Analyst's checklist applied in this report","State the unit of analysis, say what is excluded, use medians and percentiles for skewed data, set minimum sample sizes before ranking, compare like-for-like periods, and never present an association as a cause.",NAVY,colors.HexColor("#F2F5FA")),PageBreak()]

# ================================================================= APPENDIX
E+=[SectionHeader("APPENDIX","Data model and reproducibility","Where the numbers come from",GREY),Spacer(1,4*mm)]
E+=[img(os.path.join(ROOT,"Data","HRhd2Y0.png"),W*.9,"Entity-relationship diagram of the nine Olist tables (in the CSV files the customer table is olist_customers_dataset.csv)."),
 table([["Data quality log","Result"],["Date columns","Converted to datetime with strict parsing (orders, items, reviews)."],["Missing values","Kept, not imputed. Reviews: 88.34% of titles and 58.70% of comments blank. Products: 610 rows lack category and descriptors together. Orders: 14 / 2 / 8 delivered orders lack approval / carrier / delivery dates."],["Exact duplicates","Only in geolocation: 261,831 removed (1,000,163 to 738,332)."],["Joins","Validated (many-to-one) to prevent silent row multiplication."]],[34*mm,W-34*mm],color=GREY),Spacer(1,4*mm),
 P("<b>Reproducibility.</b> The full analysis is in <i>Data_Analysis.ipynb</i> (Parts A to F plus a supplementary KPI appendix). Maps and charts in this report are rebuilt from <i>Data/*.csv</i> by <i>Report/build_charts.py</i>; this PDF is built by <i>Report/build_report.py</i>. The maps are drawn from the dataset's own latitude and longitude points; no external map files are used.","small")]
doc.build(E)
print("PDF written:",OUT)
