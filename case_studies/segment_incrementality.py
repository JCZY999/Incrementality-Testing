"""Case study 3: measure heterogeneous lift across customer segments."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT=Path("outputs/segment_incrementality"); OUT.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(21)
segments={"VIP Customers":(0.28,0.015),"Affluent but Unengaged":(0.08,0.055),"Core Customers":(0.16,0.030),"Promising Spenders":(0.20,0.040),"Budget Conscious":(0.07,0.010)}
rows=[]
for segment,(base,effect) in segments.items():
    for treatment in [0,1]:
        n=2500; conversions=rng.binomial(1,base+effect*treatment,n)
        rows.extend((segment,treatment,int(y)) for y in conversions)
df=pd.DataFrame(rows,columns=["segment","treatment","converted"])
rates=df.groupby(["segment","treatment"]).converted.agg(["count","mean"]).reset_index()
pivot=rates.pivot(index="segment",columns="treatment",values="mean").rename(columns={0:"control_rate",1:"treatment_rate"})
pivot["absolute_lift"]=pivot.treatment_rate-pivot.control_rate; pivot["relative_lift"]=pivot.absolute_lift/pivot.control_rate
pivot=pivot.sort_values("absolute_lift",ascending=True); pivot.to_csv(OUT/"segment_lift.csv")
fig,ax=plt.subplots(figsize=(9,5)); colors=["#0f766e" if x>0.03 else "#64748b" for x in pivot.absolute_lift]; ax.barh(pivot.index,pivot.absolute_lift,color=colors); ax.axvline(0,color="#111827",lw=1); ax.set(xlabel="Incremental conversion lift",title="Campaign impact differs by customer segment"); ax.xaxis.set_major_formatter(lambda x,pos:f"{x:.1%}"); fig.tight_layout(); fig.savefig(OUT/"segment_lift.png",dpi=160); plt.close(fig)
print(pivot.round(4))
